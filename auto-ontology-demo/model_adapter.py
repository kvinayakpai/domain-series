"""A small adapter between Auto-Ontology and a local Ollama server.

Auto-Ontology calls three kinds of model, all through this adapter:

- /v1/chat/completions passes chat requests to Ollama's OpenAI-compatible endpoint.
  It caps each answer's length (a small model under a JSON schema can repeat itself
  until the cap; NVIDIA's code asks for up to 8192 tokens, hours on a CPU), adds a
  presence penalty and a fixed seed when the request sets none, and logs each call.
  POST /admin/chat-model {"model": ...} sends every later chat request to another
  model, so the draft and the answers can use different models.
- /v1/embeddings embeds with a local model through Ollama. It adds the query or
  document prefix the model was trained with (Auto-Ontology sends NVIDIA's
  input_type field for this), and pads each vector with zeros to the 2048
  dimensions Auto-Ontology's vector tables are created with. Zero padding leaves
  cosine similarity unchanged.
- /v1/rerank (and NVIDIA's /v1/ranking) scores each document by its cosine
  similarity to the query, using the same embedding model.

Standard library only, so it runs on a plain python image.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

OLLAMA = os.environ.get("OLLAMA_URL", "http://ollama:11434").rstrip("/")
CHAT_MAX_TOKENS = int(os.environ.get("CHAT_MAX_TOKENS", "1536"))
CHAT_PRESENCE_PENALTY = float(os.environ.get("CHAT_PRESENCE_PENALTY", "0.5"))
CHAT_SEED = int(os.environ.get("CHAT_SEED", "42"))
CHAT_MODEL_OVERRIDE: dict[str, str | None] = {"model": None}
MODEL = os.environ.get("EMBED_LOCAL_MODEL", "nomic-embed-text")
DIM = int(os.environ.get("PAD_TO", "2048"))
QUERY_PREFIX = os.environ.get("QUERY_PREFIX", "search_query: ")
DOC_PREFIX = os.environ.get("DOC_PREFIX", "search_document: ")
BATCH = 32


def log(message: str) -> None:
    print(time.strftime("%H:%M:%S"), message, flush=True)


def embed(texts: list[str]) -> list[list[float]]:
    vectors: list[list[float]] = []
    for start in range(0, len(texts), BATCH):
        body = json.dumps({"model": MODEL, "input": texts[start : start + BATCH], "truncate": True})
        request = Request(
            f"{OLLAMA}/api/embed", data=body.encode(), headers={"Content-Type": "application/json"}
        )
        with urlopen(request, timeout=900) as response:
            vectors.extend(json.load(response)["embeddings"])
    return vectors


def pad(vector: list[float]) -> list[float]:
    if len(vector) > DIM:
        raise ValueError(f"{MODEL} returns {len(vector)} dimensions, more than {DIM}")
    return list(vector) + [0.0] * (DIM - len(vector))


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


def text_of(item: object) -> str:
    if isinstance(item, dict):
        return str(item.get("text") or "")
    return str(item or "")


def scores(query: str, documents: list[str]) -> list[float]:
    vectors = embed([QUERY_PREFIX + query] + [DOC_PREFIX + d for d in documents])
    return [cosine(vectors[0], v) for v in vectors[1:]]


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args: object) -> None:  # quiet default access log
        pass

    def reply(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path.rstrip("/") in ("", "/health", "/v1/health"):
            self.reply(200, {"status": "ok", "model": MODEL, "dimensions": DIM})
        else:
            self.reply(404, {"error": f"no route {self.path}"})

    def chat(self, payload: dict, started: float) -> None:
        if CHAT_MODEL_OVERRIDE["model"]:  # set after the draft, to answer with another model
            payload["model"] = CHAT_MODEL_OVERRIDE["model"]
        asked = payload.get("max_tokens") or payload.get("max_completion_tokens")
        payload.pop("max_completion_tokens", None)
        payload["max_tokens"] = min(int(asked or CHAT_MAX_TOKENS), CHAT_MAX_TOKENS)
        payload.setdefault("presence_penalty", CHAT_PRESENCE_PENALTY)
        payload.setdefault("seed", CHAT_SEED)
        schema = ((payload.get("response_format") or {}).get("json_schema") or {}).get("name", "text")
        request = Request(
            f"{OLLAMA}/v1/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            upstream = urlopen(request, timeout=3600)
        except HTTPError as error:
            body = error.read()
            self.send_response(error.code)
            self.send_header("Content-Type", error.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            log(f"chat {schema} error {error.code} {body[:200]!r}")
            return
        with upstream:
            if payload.get("stream"):
                self.send_response(upstream.status)
                self.send_header("Content-Type", upstream.headers.get("Content-Type", "text/event-stream"))
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                while True:
                    chunk = upstream.read1(65536) if hasattr(upstream, "read1") else upstream.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(f"{len(chunk):x}\r\n".encode() + chunk + b"\r\n")
                    self.wfile.flush()
                self.wfile.write(b"0\r\n\r\n")
                log(f"chat {schema} streamed {time.time() - started:.0f}s")
                return
            body = upstream.read()
            self.send_response(upstream.status)
            self.send_header("Content-Type", upstream.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        try:
            answer = json.loads(body)
            usage = answer.get("usage") or {}
            finish = answer["choices"][0].get("finish_reason")
            note = f"chat {schema} {usage.get('prompt_tokens')}+{usage.get('completion_tokens')} tokens {finish} {time.time() - started:.0f}s"
            if finish == "length":
                note += f" | {answer['choices'][0]['message'].get('content', '')[:300]!r}"
            log(note)
        except Exception:
            log(f"chat {schema} {time.time() - started:.0f}s (unreadable answer)")

    def do_POST(self) -> None:
        started = time.time()
        path = self.path.rstrip("/")
        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length) or b"{}")
            if path == "/admin/chat-model":
                CHAT_MODEL_OVERRIDE["model"] = payload.get("model") or None
                log(f"chat model now {CHAT_MODEL_OVERRIDE['model'] or 'as requested'}")
                self.reply(200, {"model": CHAT_MODEL_OVERRIDE["model"]})
            elif path.endswith("/chat/completions"):
                self.chat(payload, started)
            elif path.endswith("/embeddings"):
                inputs = payload.get("input")
                texts = [inputs] if isinstance(inputs, str) else [str(t) for t in inputs or []]
                prefix = QUERY_PREFIX if payload.get("input_type") == "query" else DOC_PREFIX
                vectors = embed([prefix + t for t in texts])
                data = [
                    {"object": "embedding", "index": i, "embedding": pad(v)}
                    for i, v in enumerate(vectors)
                ]
                self.reply(
                    200,
                    {
                        "object": "list",
                        "data": data,
                        "model": payload.get("model", MODEL),
                        "usage": {"prompt_tokens": 0, "total_tokens": 0},
                    },
                )
                log(f"embeddings {payload.get('input_type')} x{len(texts)} {time.time() - started:.1f}s")
            elif path.endswith("/rerank"):
                documents = [text_of(d) for d in payload.get("documents") or []]
                ranked = sorted(
                    enumerate(scores(text_of(payload.get("query")), documents)),
                    key=lambda pair: pair[1],
                    reverse=True,
                )
                top = payload.get("top_n") or len(ranked)
                results = [{"index": i, "relevance_score": s} for i, s in ranked[:top]]
                self.reply(200, {"results": results})
                log(f"rerank x{len(documents)} {time.time() - started:.1f}s")
            elif path.endswith("/ranking") or path.endswith("/reranking"):
                passages = [text_of(p) for p in payload.get("passages") or []]
                ranked = sorted(
                    enumerate(scores(text_of(payload.get("query")), passages)),
                    key=lambda pair: pair[1],
                    reverse=True,
                )
                self.reply(200, {"rankings": [{"index": i, "logit": s} for i, s in ranked]})
                log(f"ranking x{len(passages)} {time.time() - started:.1f}s")
            else:
                self.reply(404, {"error": f"no route {self.path}"})
        except Exception as error:  # report to the caller, which picks its own fallback
            log(f"error on {path}: {type(error).__name__}: {error}")
            self.reply(500, {"error": f"{type(error).__name__}: {error}"})


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    log(f"model adapter on :{port}, embedding model {MODEL}, padded to {DIM}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    sys.exit(main())

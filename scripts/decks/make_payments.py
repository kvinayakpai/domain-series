"""Build the payments deck (Slides artifact data files) from the blog's payments.json and payments-ai.json."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "decks" / "payments" / "project"
(OUT / "slides").mkdir(parents=True, exist_ok=True)
d = json.loads((ROOT / "src" / "data" / "payments.json").read_text())
ai = json.loads((ROOT / "src" / "data" / "payments-ai.json").read_text())
M, F, SC = ai["matcher"], ai["find"], ai["assistant"]["score"]
Q = {q["id"]: q for q in ai["assistant"]["questions"]}
GREEN = "#1a9e70"
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 7: "seven", 10: "ten"}
S = {s["key"]: s for s in d["scenarios"]}
A, CHK, BREF = S["retry|manual"], S["check|manual"], S["retry|bill_ref"]
st = d["story"]
sc = st["scene"]
slow, june, ref, mdr = st["slowdown"], st["june"], st["refunds"], st["mdr_on_june_bills"]
upi, second = sc["attempts"][0], sc["attempts"][1]


def pct(v):
    return f"{round(v * 100)}%"


def pct1(v):
    return f"{round(v * 1000) / 10:.1f}%"


def inr(v):
    return f"₹{round(v):,}".replace(",", "X").replace("X", ",")


def inr_in(v, dec=False):
    """Indian digit grouping."""
    neg = v < 0
    v = abs(v)
    whole = round(v * 100) // 100 if dec else round(v)
    frac = f".{round(v * 100) % 100:02d}" if dec else ""
    s = str(whole)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return f"{'−' if neg else ''}₹{s}{frac}"


def hms(iso):
    return iso[11:19]


def secs(a, b):
    return round((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds())


def dayname(iso):
    return datetime.fromisoformat(iso[:10]).strftime("%a %-d %b")


SIGN = "font-family:'Anek Latin', Arial, sans-serif"
MONO = "font-family:'IBM Plex Mono', 'Courier New', monospace"
SERIF = "font-family:'Literata', Georgia, serif"
INK, PAPER, PANEL, MUTED, RECORD, RED, HL = "#1b2430", "#f5f6f4", "#eceeea", "#59626d", "#2f55a4", "#c8372d", "#ffe14d"


def section(sid, body, notes, bg=PAPER, fg=INK, gap=48, center=False):
    jc = "justify-content:center;" if center else ""
    return (f'<section id="{sid}" data-transition="fade" style="background:{bg};color:{fg};{SERIF};'
            f'padding:128px 128px 160px;display:flex;flex-direction:column;{jc}gap:{gap}px">\n{body}\n<aside>{notes}</aside>\n</section>\n')


def h2(text, color=INK):
    return f'<h2 style="{SIGN};font-size:72px;font-weight:700;line-height:1.05;color:{color}">{text}</h2>'


def foot(text):
    return (f'<p style="position:absolute;left:128px;bottom:64px;width:1664px;{SIGN};font-size:24px;color:{MUTED}">{text}</p>')


slides = {}
late_s = secs(upi["ts"], sc["credited_ts"])
plus30 = (datetime.fromisoformat(upi["ts"]) + timedelta(seconds=30)).isoformat()[11:19]

slides["cover"] = section("cover", "\n".join([
    '<div style="display:flex;flex-direction:column;gap:16px">',
    f'<p style="{SIGN};font-size:32px;font-weight:600;color:{MUTED}">Why Domain Matters, part 3</p>',
    f'<h1 style="{SIGN};font-size:120px;font-weight:700;line-height:1;color:{INK}">Payments</h1>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:12px">',
    f'<p style="{SIGN};font-size:28px;color:{MUTED}">The record says</p>',
    f'<p style="{MONO};font-size:44px;line-height:1.2;color:{RECORD}">Payment failed.</p>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:12px;align-items:start">',
    f'<p style="{SIGN};font-size:28px;color:{MUTED}">What actually happened</p>',
    f'<p style="font-size:44px;line-height:1.25;color:{INK};background:{HL};padding:4px 16px">The customer’s account was debited.</p>',
    '</div>',
    foot("kvinayakpai.github.io/domain-series. Every number comes from a synthetic, seeded world."),
]), "This is the third post in the series on why domain knowledge matters, in the same synthetic world: the fictional Store 014 in Jayanagar, Bengaluru, now with every one of its June bills paid at the tills. The headline is the story: the till recorded a failed payment, and the customer’s bank had already taken the money.",
    gap=56, center=True)

slides["scene"] = section("scene", "\n".join([
    f'<p style="{SIGN};font-size:32px;font-weight:500;color:#a3adb8">{datetime.fromisoformat(upi["ts"]).strftime("%A %-d %B, %-I:%M %p").replace("AM", "am").replace("PM", "pm")}. Store 014, Jayanagar.</p>',
    f'<h2 style="{SIGN};font-size:72px;font-weight:700;line-height:1.1;color:#e6eaee">The till said the payment failed. Her bank had already taken the money.</h2>',
    '<div style="background:#222c37;border-left:6px solid #8db0f0;padding:32px 40px;width:1200px">',
    f'<p style="{MONO};font-size:32px;line-height:1.5;white-space:pre;color:#8db0f0">{hms(upi["ts"])}  UPI   {inr_in(sc["amount_inr"], True)}  failed: no response<br>{hms(second["ts"])}  {second["tender"]}  {inr_in(sc["amount_inr"], True)}  approved</p>',
    '</div>',
    f'<p style="font-size:32px;line-height:1.45;color:#e6eaee;width:1400px">{late_s} seconds after she approved the UPI payment, the store was credited. Nobody at the till saw it. She had paid twice.</p>',
]), f"Saturday evening, the rush. A customer’s basket comes to {inr_in(sc['amount_inr'], True)}. She scans the QR code at the till and approves the payment on her phone, and her bank takes the money. The till waits thirty seconds, hears nothing back, and shows payment failed, no response. The cashier asks for another way to pay; she pays by card and leaves. {late_s} seconds after she approved the UPI payment, the store’s bank confirms the credit. Nobody at the till sees it. She has paid twice, and it takes a phone call and eight days to get the money back.",
    bg=INK, fg="#e6eaee", center=True)

d20 = next(x for x in A["daily"] if x["date"] == "2026-06-20")
d21 = next(x for x in A["daily"] if x["date"] == "2026-06-21")
hours = {h["hour"]: h for h in st["slowdown_day_by_hour"]}
twice = sum(1 for c in A["complaints"] if c["kind"] == "charged twice")
refunds = sum(f["amount_inr"] for f in A["refunds"])
gen, dom = ai["tests"]["generic"], ai["tests"]["domain"]
passed = sum(t["pass"] for t in gen)
a18, a19 = (pct(hours[h]["approved_at_till"] / hours[h]["upi_attempts"]) for h in (18, 19))
suspense = d20["unmatched"] + d21["unmatched"]
rows = [
    ("Payments dashboard", f"Approvals at the tills {pct1(june['four_ways']['till'])} for June; {a18} and {a19} in the 18:00 and 19:00 hours on 20 June, normal by eight", "“Incident closed.”"),
    ("Data tests", f"{passed} of {len(gen)} pass: one approved payment per bill, every approval a success at the provider, settlements add up", "“The pipeline is green.”"),
    ("Reconciliation report", f"{d20['provider_credits']} credits against {d20['till_approved']} approvals on Saturday, {d21['provider_credits']} against {d21['till_approved']} on Sunday", f"“Park the {suspense} in suspense.”"),
    ("Customer support", f"{len(A['complaints'])} payment complaints in June, {twice} of them “charged twice”; {inr_in(refunds)} of refunds", "“Screenshot, check, refund.”"),
    ("AI assistant, given the till’s schema", f"All {june['bills']:,} bills have exactly one approved payment", "“Nobody paid twice.”"),
]
table = [f'<table style="font-size:28px;color:{INK}">',
         f'<tr><th style="width:24%;text-align:left;font-weight:600;color:{MUTED}">Data product</th><th style="width:48%;text-align:left;font-weight:600;color:{MUTED}">What it reads</th><th style="width:28%;text-align:left;font-weight:600;color:{MUTED}">What it concludes</th></tr>']
table += [f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in rows]
table.append('</table>')
slides["readings"] = section("readings", "\n".join([h2("Five readings of one payment"), *table,
    foot("Each conclusion follows from the records in front of it. None of them sees a customer charged twice.")]),
    f"As in the other posts, nobody here is careless, and each data product reads the records in front of it. The payments dashboard shows approvals at the tills: {pct1(june['four_ways']['till'])} of June’s UPI attempts, falling to {a18} and {a19} in the 18:00 and 19:00 hours on Saturday 20 June and back to normal by eight, so the incident is closed. The data tests pass, all {WORDS[len(gen)]}: every bill has exactly one approved payment, every UPI payment the till approved is a success in the provider’s report, and the settlements add up. The reconciliation report matches the provider’s credits to the till’s approvals by reference number, and parks the {suspense} credits with no approval behind them in suspense. Customer support takes {twice} calls from people charged twice and asks for screenshots. And an AI assistant, given the till’s schema, says nobody paid twice: all {june['bills']:,} bills have exactly one approved payment.",
    gap=40)

boxes = [("Her app", "sends the payment"), ("NPCI", "routes it"), ("Her bank", "debits her account"), ("Store’s bank", "slow to answer"), ("The till", "gives up at 30 s")]
flow = ['<div style="display:flex;gap:16px;align-items:stretch">']
for i, (a, b) in enumerate(boxes):
    border = RED if i >= 3 else INK
    flow.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:8px;background:{PANEL};border-top:6px solid {border};padding:24px 24px"><p style="{SIGN};font-size:32px;font-weight:600">{a}</p><p style="font-size:26px;line-height:1.35;color:{MUTED}">{b}</p></div>')
    if i < len(boxes) - 1:
        flow.append(f'<p style="{SIGN};font-size:44px;color:{MUTED};align-self:center">→</p>')
flow.append('</div>')
slides["happened"] = section("happened", "\n".join([h2("A slow answer is not a failed payment"), *flow,
    '<p style="font-size:32px;line-height:1.45;width:1550px">When the debit has happened and the answer is late, UPI settles it afterwards: the store’s bank confirms the credit, or the money goes back. RBI requires it back within five days of the payment, with ₹100 a day after that. The money is never lost. For a while it is in two places, and the till is the last to know.</p>',
    foot(f"{slow['upi_timeouts']} of {slow['upi_attempts']} UPI attempts at Store 014 got no answer within 30 seconds between 18:20 and 19:50. RBI/2019-20/67 (2019): merchant payments reversed within T+5.")]),
    "A UPI payment at a till passes through several systems: the customer’s app, NPCI’s switch, her bank, which debits her account, and the store’s bank, which credits the store and sends the answer back to the till. On Saturday evening the store’s bank was slow. A slow answer is not a failed payment. When the debit has happened and the answer is late, UPI settles it afterwards: the store’s bank confirms the credit or returns the money, and RBI requires the money back within five days for a payment to a merchant, with a hundred rupees a day in compensation after that. The money is never lost; for a while it is in two places, and the till is the last to know.",
    gap=48)

settled = (datetime.fromisoformat(sc["credited_ts"][:10]) + timedelta(days=1)).isoformat()
trows = [
    ("The till", f"{hms(upi['ts'])}  UPI {inr_in(sc['amount_inr'], True)}  failed: no response at {plus30}"),
    ("The till", f"{hms(second['ts'])}  {second['tender']} {inr_in(sc['amount_inr'], True)}  approved"),
    ("Provider’s report", f"{hms(sc['credited_ts'])}  UPI {sc['rrn']}  success"),
    ("Settlement", f"{dayname(settled)}: credited with Saturday’s UPI payments"),
    ("Customer support", f"{dayname(sc['complaint']['complaint_ts'])}, {hms(sc['complaint']['complaint_ts'])[:5]}: “charged twice”"),
    ("Refund", f"{dayname(sc['refunded_ts'])}, {hms(sc['refunded_ts'])[:5]}: {inr_in(sc['amount_inr'], True)} back"),
]
tt = ['<div style="display:flex;flex-direction:column">']
tt += [f'<div style="display:flex;gap:32px;align-items:baseline;border-top:2px solid #d5d9d4;padding:12px 0 12px 0"><p style="width:400px;{SIGN};font-size:30px;font-weight:500">{a}</p><p style="{MONO};font-size:28px;color:{RECORD}">{b}</p></div>' for a, b in trows]
tt.append(f'<div style="display:flex;gap:32px;align-items:baseline;background:{HL};border-top:4px solid {INK};padding:16px 16px 16px 16px"><p style="width:368px;{SIGN};font-size:30px;font-weight:700;color:{INK}">Her money</p><p style="font-size:32px;color:{INK}">Taken twice, for eight days</p></div>')
tt.append('</div>')
slides["timeline"] = section("timeline", "\n".join([h2("Every record was right about what it saw"), *tt]),
    f"Here is that one basket in every record that holds it. The till recorded a failed UPI payment and an approved card payment. The provider’s report recorded a successful UPI payment, confirmed {late_s} seconds after it started. The settlement paid it to the store the next day with the rest of Saturday’s payments. On Tuesday she called customer support; on Sunday the 28th she got her money back. Each record is right. The till never saw the credit, the provider never saw the card payment, and only the customer saw both debits.",
    gap=36)

# Chart: hourly approved at till vs credited, 15:00-21:00.
hrs = [h for h in st["slowdown_day_by_hour"] if h["hour"] >= 15]
W, PH, TOP = 1664, 420, 48
H = PH + TOP
ymax = 80
band = W / len(hrs)
bw = 70
labels = []
svg = [f'<svg aria-label="Bar chart: UPI payments approved at the till and credited by the bank, each hour from 15:00 to 21:00 on Saturday 20 June. At 18:00 and 19:00 the bank credited more payments than the tills approved." width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
for v in (20, 40, 60, 80):
    y = H - v / ymax * PH
    svg.append(f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}" stroke="#dde1dc" stroke-width="2"/>')
    labels.append(f'<p style="position:absolute;left:0px;top:{y - 38:.0f}px;width:80px;{SIGN};font-size:24px;color:{MUTED}">{v}</p>')
svg.append(f'<line x1="0" y1="{H - 1}" x2="{W}" y2="{H - 1}" stroke="#b9bfb7" stroke-width="2"/>')
for i, hr in enumerate(hrs):
    for k, (key, color) in enumerate((("approved_at_till", "#2f55a4"), ("credited", "#d9661f"))):
        v = hr[key]
        x0 = i * band + band / 2 - bw - 4 + k * (bw + 8)
        top = H - v / ymax * PH
        svg.append(f'<path d="M{x0:.0f},{H}V{top + 6:.0f}Q{x0:.0f},{top:.0f} {x0 + 6:.0f},{top:.0f}H{x0 + bw - 6:.0f}Q{x0 + bw:.0f},{top:.0f} {x0 + bw:.0f},{top + 6:.0f}V{H}Z" fill="{color}"/>')
        gap = hr["credited"] - hr["approved_at_till"]
        if key == "credited" and gap > 0:
            labels.append(f'<p style="position:absolute;left:{x0 + bw / 2 - 60:.0f}px;top:{top - 46:.0f}px;width:120px;text-align:center;{SIGN};font-size:28px;font-weight:600;color:{INK}">+{gap}</p>')
svg.append('</svg>')
slides["chart"] = section("chart", "\n".join([
    h2("The bank was paid for more than the tills approved"),
    f'<div style="position:relative;width:{W}px;height:{H}px">', *svg, *labels, '</div>',
    '<div style="display:flex;gap:0">' + "".join(f'<p style="flex:1;text-align:center;{SIGN};font-size:24px;color:{MUTED}">{h["hour"]:02d}:00</p>' for h in hrs) + '</div>',
    '<div style="display:flex;gap:48px;align-items:center">'
    + f'<div style="display:flex;gap:16px;align-items:center"><div style="width:32px;height:32px;background:#2f55a4"></div><p style="{SIGN};font-size:26px">Approved at the till</p></div>'
    + f'<div style="display:flex;gap:16px;align-items:center"><div style="width:32px;height:32px;background:#d9661f"></div><p style="{SIGN};font-size:26px">Credited by the bank</p></div></div>',
    foot("UPI payments at Store 014’s tills, Saturday 20 June 2026, by hour. +N: credited by the bank, marked failed at the till. Synthetic world, seed 42."),
]), f"Hour by hour on Saturday: blue is UPI payments the tills approved, orange is payments the bank actually credited to the store. Through the afternoon they match. In the 18:00 and 19:00 hours the orange bars are taller: {hours[18]['credited'] - hours[18]['approved_at_till']} and {hours[19]['credited'] - hours[19]['approved_at_till']} payments the bank credited that the tills had marked failed. Each of those is a customer who was asked to pay again.",
    gap=24)

slides["cost"] = section("cost", "\n".join([
    h2("What 90 minutes cost the customers"),
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:96px">',
    '<div style="display:flex;flex-direction:column;gap:40px">',
    f'<div style="display:flex;flex-direction:column;gap:4px"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1">{slow["charged_twice"]}</p><p style="{SIGN};font-size:32px;color:{MUTED}">customers charged twice, two of them three times: {slow["extra_charges"]} extra charges, {inr_in(slow["charged_twice_inr"])}</p></div>',
    f'<div style="display:flex;flex-direction:column;gap:4px"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1">{ref["median_days_to_refund"]}</p><p style="{SIGN};font-size:32px;color:{MUTED}">median days to a refund, which came only after a complaint</p></div>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:24px">',
    f'<h3 style="{SIGN};font-size:36px;font-weight:600;line-height:1.2">All of June</h3>',
    f'<table style="font-size:30px;color:{INK}">',
    *[f'<tr><td style="width:56%">{a}</td><td style="width:44%;text-align:right">{b}</td></tr>' for a, b in [
        ("Customers charged twice", june["charged_twice"]),
        ("Extra charges", f'{june["extra_charges"]} ({inr_in(june["charged_twice_inr"])})'),
        ("Debited, then returned by their bank", f'{june["debited_and_returned"]}, within {max(r["days"] for r in A["returns"])} days'),
        ("Payment complaints", ref["complaints"]),
        ("Still in suspense when June closed", f'{ref["unrefunded_at_month_end"]} ({inr_in(ref["unrefunded_inr"])})'),
    ]],
    '</table>', '</div>', '</div>',
    foot(f"Between {slow['start'][11:]} and {slow['end'][11:]} Store 014 took {slow['bills']} bills; the tills gave up on {slow['upi_timeouts']} of {slow['upi_attempts']} UPI attempts."),
]), f"In those ninety minutes Store 014 took {slow['bills']} bills. The tills gave up on {slow['upi_timeouts']} of {slow['upi_attempts']} UPI attempts, and {slow['charged_twice']} customers paid twice, two of them three times: {slow['extra_charges']} extra charges, {inr_in(slow['charged_twice_inr'])}. Across June, {june['charged_twice']} customers paid twice. The store refunded them only when they complained: a median of {ref['median_days_to_refund']} days, the longest {ref['max_days_to_refund']}, and when June closed {ref['unrefunded_at_month_end']} extra charges, {inr_in(ref['unrefunded_inr'], True)}, were still in suspense.",
    bg=PANEL)

slides["normal"] = section("normal", "\n".join([
    h2("This is the normal case"),
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:64px">',
    f'<div style="display:flex;flex-direction:column;gap:12px;border-top:4px solid {INK};padding:24px 0 0 0"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1">24.07 bn</p><p style="font-size:30px;line-height:1.4">UPI transactions in September 2026, about 802 million a day</p></div>',
    f'<div style="display:flex;flex-direction:column;gap:12px;border-top:4px solid {INK};padding:24px 0 0 0"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1">0.7–0.8%</p><p style="font-size:30px;line-height:1.4">technical declines, NPCI’s chief executive said in November 2024</p></div>',
    f'<div style="display:flex;flex-direction:column;gap:12px;border-top:4px solid {INK};padding:24px 0 0 0"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1">90 s</p><p style="font-size:30px;line-height:1.4">before the first status check NPCI allows on a payment, since its 2025 rules</p></div>',
    '</div>',
    f'<p style="font-size:32px;line-height:1.45;color:{INK};background:{PANEL};padding:24px 32px">On 12 April 2025 UPI’s success rate fell to about 50% for nearly two hours, the third disruption in a week. NPCI blamed banks flooding it with status checks, and rationed them.</p>',
    foot("Sources: NPCI via Outlook Money (2 Oct 2026); Inc42 (20 Nov 2024); MediaNama on NPCI OC 215 (Apr 2025); Outlook Money (16 Apr 2025)."),
]), "At UPI’s scale small rates are large numbers. UPI handled 24.07 billion transactions in September 2026, about 802 million a day. NPCI’s chief executive put technical declines at 0.7 to 0.8 percent in November 2024; at September’s volume, three quarters of a percent would be about 180 million failed attempts a month. Whole-system slowdowns happen too: on 12 April 2025 success fell to about half for nearly two hours, the third disruption in a week, and NPCI blamed banks for flooding it with status checks. Its answer was to ration them: the first check no sooner than ninety seconds after a payment, and preferably no more than three in two hours. A till cannot simply ask again until it knows.",
    gap=56)

fw, jw = slow["four_ways"], june["four_ways"]
ways = [("The till", "till", "UPI attempts the till marked approved", "#8db0f0"),
        ("The bank", "bank", "UPI attempts that ended as a credit, late ones included", "#e6eaee"),
        ("Bills paid", "bills_paid", "Bills the store was paid for, one way or another", "#e6eaee"),
        ("Charged once", "charged_once", "Bills where no customer’s money moved twice", HL)]
cells = [f'<div style="display:flex;flex-direction:column;gap:16px;border-top:4px solid {c};padding:24px 0 0 0"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1;color:{c}">{pct(fw[key])}</p><p style="{SIGN};font-size:32px;font-weight:600">{label}</p><p style="font-size:26px;line-height:1.4;color:#a3adb8">{how}. June: {pct1(jw[key])}</p></div>' for label, key, how, c in ways]
slides["fourways"] = section("fourways", "\n".join([
    h2("One name, four numbers", "#e6eaee"),
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:48px">', *cells, '</div>',
    '<p style="font-size:34px;line-height:1.45;width:1500px">Payment success during the slowdown, Saturday 18:20–19:50. Over the month the four sit within a few points; in the 90 minutes that mattered they spread from 61% to 100%.</p>',
]), f"Payment success rate sounds like one number. The dashboard reports approvals at the till: {pct(fw['till'])} during the slowdown. The bank’s settlement includes the late credits: {pct(fw['bank'])}. The sales report shows every bill paid: one hundred percent. Only the fourth, customers charged once, {pct(fw['charged_once'])}, is what customers lived through, and no system computes it. Over all of June the four sit within a few points of each other; in the ninety minutes that mattered they spread from {pct(fw['till'])} to a hundred.",
    bg=INK, fg="#e6eaee", gap=64)

rule = mdr["rule"]
fee = lambda a: (min(rule["cap"], a * rule["rate"]) if a > rule["above"] else 0.0)
ex = [1999, 2000, 2001, 5000, 75000]
slides["mdr"] = section("mdr", "\n".join([
    h2("Same store, different cost: the new UPI fee"),
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:96px">',
    '<div style="display:flex;flex-direction:column;gap:24px">',
    f'<p style="{SIGN};font-size:120px;font-weight:700;line-height:1">{inr_in(mdr["fee_inr"])}</p>',
    f'<p style="{SIGN};font-size:32px;color:{MUTED}">a month for Store 014 at June’s mix: 0.4% on {mdr["bills_above"]} UPI bills above ₹2,000</p>',
    '<p style="font-size:30px;line-height:1.45">From 15 October 2026: 0.4% on payments to a merchant above ₹2,000, capped at ₹300. Merchants receiving up to ₹1 lakh a month through UPI QR are exempt.</p>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:24px">',
    f'<h3 style="{SIGN};font-size:36px;font-weight:600;line-height:1.2">The fee on one payment</h3>',
    f'<table style="font-size:30px;color:{INK}">',
    f'<tr><th style="width:50%;text-align:left;font-weight:600;color:{MUTED}">Payment</th><th style="width:50%;text-align:right;font-weight:600;color:{MUTED}">Fee</th></tr>',
    *[f'<tr><td>{inr_in(a)}</td><td style="text-align:right">{inr_in(fee(a), True)}</td></tr>' for a in ex],
    '</table>', '</div>', '</div>',
    foot("NPCI UPI and Services Steering Committee, reported by Deccan Chronicle (15 Sep 2026) and Business Standard (16 Sep 2026)."),
]), f"Until this month UPI payments to merchants from bank accounts carried no merchant discount rate. From the fifteenth of October 2026, payments to a merchant above two thousand rupees carry 0.4 percent, capped at three hundred rupees, and small merchants receiving up to a lakh a month through UPI QR are exempt. For Store 014, June’s bills would have cost about {inr_in(mdr['fee_inr'])}. The shape matters more than the size: the fee applies to the whole payment once it crosses two thousand, so a basket of 2,001 rupees costs eight rupees to accept and a basket of 2,000 costs nothing.",
    gap=48)

cards = [
    ("Wait for the status check", f"{A['kpis']['june']['charged_twice']} → {CHK['kpis']['june']['charged_twice']}", "customers charged twice in June", f"Till time in the slowdown: {round(A['kpis']['slowdown']['till_minutes'])} → {round(CHK['kpis']['slowdown']['till_minutes'])} minutes, at the worst moment.", "#1a9e70"),
    ("Bill ID on every UPI request", f"{A['kpis']['refunds']['median_days_to_refund']} → {BREF['kpis']['refunds']['median_days_to_refund']}", "median days to a refund", f"Nothing left in suspense; complaints {A['kpis']['refunds']['complaints']} → {BREF['kpis']['refunds']['complaints']}. Double charges still happen; every one is found the next morning.", "#1a9e70"),
]
cardhtml = [f'<div style="display:flex;flex-direction:column;gap:18px;background:{PANEL};padding:48px;border-top:8px solid {c}"><h3 style="{SIGN};font-size:44px;font-weight:600;line-height:1.2">{t}</h3><p style="{SIGN};font-size:72px;font-weight:700;line-height:1.05">{big}</p><p style="font-size:28px;line-height:1.4">{small}</p><p style="font-size:28px;line-height:1.4;color:{MUTED}">{note}</p></div>' for t, big, small, note, c in cards]
slides["helped"] = section("helped", "\n".join([
    h2("One change prevents most double charges. The other finds them all."),
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:64px">', *cardhtml, '</div>',
    foot("Same customers, baskets and banks in every scenario; the changes start on 1 June. Try them in the demo."),
]), f"The demo lets you try two changes. Waiting for the status check NPCI allows at ninety seconds, before asking for another payment, cuts customers charged twice in June from {A['kpis']['june']['charged_twice']} to {CHK['kpis']['june']['charged_twice']}, but during the slowdown the tills spend {round(CHK['kpis']['slowdown']['till_minutes'])} minutes taking payment instead of {round(A['kpis']['slowdown']['till_minutes'])}, exactly when the queue is longest. Putting the bill ID on every UPI request doesn’t stop double charges, but every one is matched the next morning and refunded: the median wait falls from {A['kpis']['refunds']['median_days_to_refund']} days to {BREF['kpis']['refunds']['median_days_to_refund']}, nothing is left in suspense, and complaints fall from {A['kpis']['refunds']['complaints']} to {BREF['kpis']['refunds']['complaints']}. A payment that carries a reference to what it is for can always be matched to it.",
    gap=48)

slides["data"] = section("data", "\n".join([
    h2("Nothing in the records says “charged twice”"),
    '<div style="display:grid;grid-template-columns:1.15fr 1fr;gap:72px;align-items:start">',
    f'<div style="background:{PANEL};border-left:6px solid {RECORD};padding:24px 32px;display:flex;flex-direction:column;gap:20px">',
    f'<p style="{MONO};font-size:26px;line-height:1.5;white-space:pre;color:{RECORD}">Till, bill {sc["bill_id"]}<br>{hms(upi["ts"])}  UPI   failed: no response<br>          reference: none<br>{hms(second["ts"])}  card  approved</p>',
    f'<p style="{MONO};font-size:26px;line-height:1.5;white-space:pre;color:{RECORD}">Provider’s UPI report<br>{sc["rrn"]}  {hms(upi["ts"])}<br>success, confirmed {hms(sc["credited_ts"])}</p>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:28px">',
    '<p style="font-size:32px;line-height:1.45">A till that hears nothing back never learns the payment’s reference number, the RRN, so there is nothing to join on.</p>',
    '<p style="font-size:32px;line-height:1.45">Data tests check that records agree, and these agree. The only record of the double charge was in the customer’s bank statement.</p>',
    '</div>', '</div>',
    foot("Identifiers in the data are synthetic. Download June’s till payments and the provider’s report to try the match."),
]), "If you work with payments data, slow down here. The till recorded the UPI attempt as failed, with no reference number, because it never heard back. The provider’s report has the reference number and a success. There is nothing to join on. Every record is right about what it saw: the till saw no answer, the provider saw a success, and the bill was paid once at the till. Data tests check that records agree, and these agree. The only record of the double charge was in the customer’s bank statement.",
    gap=48)

dom_short = [
    ("Every success in the provider’s report has an approved till payment", f"{len(dom[0]['failing'])} credits"),
    ("Every UPI attempt joins the provider’s status by RRN", f"{len(dom[1]['failing'])} timeouts"),
    ("No bill is paid twice, once timeouts are matched", f"{M['customers']} bills"),
    ("Every extra charge comes back within five days of the debit", f"{F['over_tat'] + F['not_refunded']} charges"),
    ("No hour has a burst of timeouts", f"{len(dom[4]['failing'])} hours"),
]
slides["tests"] = section("tests", "\n".join([
    h2("The pipeline is green"),
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:start">',
    f'<div style="display:flex;flex-direction:column;gap:16px;border-top:6px solid {GREEN};padding:24px 0 0 0"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1;color:{GREEN}">{passed} of {len(gen)}</p><p style="{SIGN};font-size:32px;font-weight:600">data tests pass</p><p style="font-size:28px;line-height:1.4">Keys, statuses and reconciliations across the till, the provider’s report, settlements, refunds and complaints. They agree, because each records only what it saw.</p></div>',
    f'<div style="display:flex;flex-direction:column;gap:16px;border-top:6px solid {RED};padding:24px 0 0 0"><p style="{SIGN};font-size:120px;font-weight:700;line-height:1;color:{RED}">0 of {len(dom)}</p><p style="{SIGN};font-size:32px;font-weight:600">tests about how UPI works pass</p>'
    + '<ul style="font-size:26px;line-height:1.4">' + "".join(f'<li>{x} <span style="color:{MUTED}">(fails on {n})</span></li>' for x, n in dom_short) + '</ul></div>',
    '</div>',
    foot(f"All {len(gen) + len(dom)} tests use only the records. The five days are what RBI allows for a failed payment to a merchant, used as the store’s own clock."),
]), f"The first thing a data team would do is test the data, and the payment records pass: all {WORDS[len(gen)]} tests a dbt project ships on day one, keys, statuses and reconciliations across the till, the provider’s report, the settlements, the refunds and the complaints. They agree with each other, because each records only what it saw. Five tests that encode how UPI works all fail on the same records. {len(dom[0]['failing'])} successes in the provider’s report have no approved till payment behind them. {len(dom[1]['failing'])} timeouts cannot join the provider’s status, because a till that hears nothing back never learns the reference number. {M['customers']} bills were paid twice, once the timeouts are matched. {F['over_tat'] + F['not_refunded']} extra charges did not come back within five days of the debit. And two hours on Saturday evening had a burst of timeouts that the month’s rate hides.",
    gap=48)

O = M["outcomes"]
fates = [(O["late credit"], "credited to the store late", "an extra charge whenever the bill was paid again", RED),
         (O["debited and returned"], "debited, then returned", "by the customer’s bank, within days", INK),
         (O["never debited"], "never left the account", "the only true failures", INK)]
fcells = [f'<div style="display:flex;flex-direction:column;gap:8px;border-top:4px solid {c};padding:20px 0 0 0"><p style="{SIGN};font-size:96px;font-weight:700;line-height:1;color:{c}">{n}</p><p style="{SIGN};font-size:30px;font-weight:600">{a}</p><p style="font-size:26px;line-height:1.35;color:{MUTED}">{b}</p></div>' for n, a, b, c in fates]
pc = next(x for x in F["per_charge"] if x["rrn"] == sc["rrn"])
alarms = "no" if M["false_positives"] == 0 else WORDS.get(M["false_positives"], str(M["false_positives"]))
slides["match"] = section("match", "\n".join([
    h2("Treat a timeout as a question"),
    f'<p style="font-size:32px;line-height:1.4;width:1550px">Match each of June’s {M["timeouts"]} timeouts to the provider row no till payment claims, with the same amount and a start within five seconds. All {M["matched"]} match:</p>',
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:56px">', *fcells, '</div>',
    f'<div style="background:{PANEL};border-left:6px solid {GREEN};padding:24px 32px;display:flex;flex-direction:column;gap:12px">',
    f'<p style="{SIGN};font-size:30px;font-weight:600">Then the double charges are a query: late credits on bills paid again</p>',
    f'<p style="font-size:28px;line-height:1.4">{M["extra_charges"]} extra charges on {M["customers"]} customers, {inr_in(M["extra_inr"], True)}: the answer key’s {M["answer_key"]["extra_charges"]}, with {alarms} false alarms. Run each morning on the provider’s file, it finds them a median {F["matcher_median_days"]} days after the debit, against {round(F["complaint_median_days"])} for complaints, and {WORDS[F["never_complained"]]} customers never complained.</p>',
    f'<p style="{MONO};font-size:24px;color:{RECORD}">{hms(upi["ts"])} timeout {inr_in(sc["amount_inr"], True)} → {sc["rrn"]} success {hms(sc["credited_ts"])} → bill {sc["bill_id"]} paid again by {second["tender"]}</p>',
    '</div>',
]), f"Here is the change that finds them. A UPI payment the till gave up on is not a failure until the provider says so. Match each of June’s {M['timeouts']} timeouts to the provider row that no till payment claims, with the same amount and a start within five seconds, one to one, and every one matches: {O['late credit']} were credited to the store late, {O['debited and returned']} were debited and returned by the customer’s bank, and {O['never debited']} never left the customer’s account. The answer key agrees on all {M['outcomes_right']}. Then the double charges are a query: a late credit on a bill the customer paid again is an extra charge. It finds {M['extra_charges']}, on {M['customers']} customers, {inr_in(M['extra_inr'], True)}, the same {M['answer_key']['extra_charges']} the answer key has, with no false alarms. Run each morning on the provider’s file, it finds them a median {F['matcher_median_days']} days after the debit. Complaints found them a median {round(F['complaint_median_days'])} days after, and {WORDS[F['never_complained']]} customers never complained. The customer from Saturday evening is on the next morning’s list, {pc['matcher_days']} days after her debit; her complaint came {pc['complaint_days']} days after it.",
    gap=36)

wait = Q["wait"]
b18, b19 = (pct(b["share"]) for b in ai["hours"]["bursts"])
tech = f"{june['upi_technical_failures'] / june['upi_attempts'] * 100:.2f}%"
refunded = M["extra_charges"] - F["not_refunded"]


def pair(title, a_big, a_label, b_big, b_label, note):
    return (f'<div style="display:flex;flex-direction:column;gap:28px">'
            f'<h3 style="{SIGN};font-size:40px;font-weight:600;line-height:1.2">{title}</h3>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:40px">'
            f'<div style="display:flex;flex-direction:column;gap:10px;border-top:4px solid #b9bfb7;padding:20px 0 0 0"><p style="{SIGN};font-size:88px;font-weight:700;line-height:1;color:{MUTED}">{a_big}</p><p style="font-size:26px;line-height:1.35;color:{MUTED}">{a_label}</p></div>'
            f'<div style="display:flex;flex-direction:column;gap:10px;border-top:4px solid {RED};padding:20px 0 0 0"><p style="{SIGN};font-size:88px;font-weight:700;line-height:1;color:{RED}">{b_big}</p><p style="font-size:26px;line-height:1.35">{b_label}</p></div>'
            f'</div><p style="font-size:28px;line-height:1.4">{note}</p></div>')


slides["clocks"] = section("clocks", "\n".join([
    h2("Two KPIs, read the way the money moves"),
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:96px;align-items:start">',
    pair("Refund wait", f"{round(wait['naive']['value'])} days", "median, from the complaint, as support reports it",
         f"{F['refund_median_days_from_debit']} days", "median, from the extra debit, when the customer lost the money",
         f"{F['over_tat']} of {refunded} refunds took longer than RBI’s five days; {WORDS[F['not_refunded']]}, {inr_in(F['not_refunded_inr'], True)}, were not refunded by month end."),
    pair("UPI decline rate", tech, "technical declines in June, in line with UPI as a whole; timeouts not counted",
         f"{b18}, {b19}", "no answer, 18:00 and 19:00 on 20 June, timeouts counted",
         f"A monthly rate hides the two hours in which {slow['charged_twice']} customers paid twice."),
    '</div>',
    foot("Same records, same month. Grey: what the store reports. Red: the clock started at the debit, and the attempts counted the way UPI works."),
]), f"Two of the store’s KPIs change when they are read the way the money moves. Refund wait, as support reports it, runs from the complaint: a median of {round(wait['naive']['value'])} days. The customer lost the money at the extra debit, and from there the median is {F['refund_median_days_from_debit']} days; when June closed, {WORDS[F['not_refunded']]} extra charges, {inr_in(F['not_refunded_inr'], True)}, were still unrefunded. RBI gives banks five days to return a failed payment to a customer; by that clock, {F['over_tat']} of the {refunded} refunds were late. And June’s technical decline rate, {tech}, is in line with UPI as a whole, and it counts no timeouts at all. Read by the hour, with timeouts counted, the tills got no answer on {b18} and {b19} of attempts in the 18:00 and 19:00 hours on 20 June, the two hours in which {slow['charged_twice']} customers paid twice.",
    gap=48)

qt = Q["twice"]


def curly(t):
    return t.replace("'", "’")


slides["assistant"] = section("assistant", "\n".join([
    h2("Give the assistant a domain layer", "#e6eaee"),
    '<div style="display:grid;grid-template-columns:1fr 1.2fr;gap:72px;align-items:start">',
    '<div style="display:flex;flex-direction:column;gap:24px">',
    f'<p style="{SIGN};font-size:96px;font-weight:700;line-height:1;color:#e6eaee">{SC["naive"]} → {SC["domain"]} <span style="color:#a3adb8">of {SC["of"]}</span></p>',
    f'<p style="{SIGN};font-size:28px;color:#a3adb8">questions answered right at the month-end review, schema only → with the domain layer</p>',
    '<ul style="font-size:26px;line-height:1.4;color:#e6eaee"><li>“A timeout is a question, not an answer”</li><li>“A provider success with no approved till payment is a customer’s money”</li><li>“Read payment rates by the hour, with timeouts counted”</li><li>The provider’s UPI report, and two views: the timeouts matched, the extra charges</li></ul>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:24px">',
    f'<div style="background:#222c37;border-left:6px solid {RED};padding:24px 32px;display:flex;flex-direction:column;gap:10px">',
    f'<p style="{SIGN};font-size:24px;font-weight:600;color:#a3adb8">{qt["question"]} Schema only:</p>',
    f'<p style="{SIGN};font-size:26px;line-height:1.45;color:#e6eaee">{curly(qt["naive"]["answer"])}</p>',
    '</div>',
    f'<div style="background:#222c37;border-left:6px solid {GREEN};padding:24px 32px;display:flex;flex-direction:column;gap:10px">',
    f'<p style="{SIGN};font-size:24px;font-weight:600;color:#a3adb8">With the domain layer:</p>',
    f'<p style="{SIGN};font-size:26px;line-height:1.45;color:#e6eaee">{curly(qt["domain"]["answer"])}</p>',
    '</div>', '</div>', '</div>',
    foot("The assistant is scripted so the run can be repeated; the technical companion shows every query.").replace(MUTED, "#a3adb8"),
]), f"The same assistant, asked the same seven questions at the month-end review, now given a domain layer: definitions, such as a timeout is a question, not an answer; rules, such as a provider success with no approved till payment is a customer’s money; the provider’s UPI report; and two views built from them, the timeouts matched to the provider’s report and the extra charges. Given the till’s schema alone it answered {WORDS[SC['naive']]} of seven: how many UPI payments the tills attempted. With the domain layer it answers all seven: {M['customers']} customers paid twice, the credits in suspense are extra charges on customers, refunds took {F['refund_median_days_from_debit']} days from the debit, and {WORDS[len(Q['refund_now']['domain']['value'])]} bills should be refunded now, without waiting for a complaint.",
    bg=INK, fg="#e6eaee", gap=48)

questions = [
    "Which of our “failed” statuses are answers, and which are only timeouts?",
    "When a key is missing, which other fields can join the records, and who checks the match?",
    "Do we measure customer outcomes, such as paying twice, or only system outcomes, such as approvals?",
    "Do our clocks start when the customer is harmed or when the customer complains?",
    "What does our AI assistant know about how payments settle, and how do we test that?",
]
slides["questions"] = section("questions", "\n".join([
    h2("Five questions to ask your team"),
    '<div style="display:flex;flex-direction:column">',
    *[f'<div style="display:grid;grid-template-columns:72px 1fr;gap:24px;border-top:2px solid #d5d9d4;padding:22px 0 22px 0">'
      f'<p style="{SIGN};font-size:38px;font-weight:700;line-height:1.2;color:{RECORD}">{i}</p>'
      f'<p style="font-size:36px;line-height:1.3">{q}</p></div>' for i, q in enumerate(questions, 1)],
    '</div>',
    foot("For data and AI leaders. The technical companion answers each one for Saturday 20 June."),
]), "For data and AI leaders, five questions to take back to your team. Which of our failed statuses are answers, and which are only timeouts? When a key is missing, which other fields can join the records, and who checks the match? Do we measure customer outcomes, such as paying twice, or only system outcomes, such as approvals? Do our clocks start when the customer is harmed or when the customer complains? And what does our AI assistant know about how payments settle, and how do we test that?",
    gap=48)

slides["close"] = section("close", "\n".join([
    f'<h2 style="{SIGN};font-size:88px;font-weight:700;line-height:1.08;color:#e6eaee;width:1500px">Every record was right about what it saw. Only the customer saw both debits.</h2>',
    '<div style="display:flex;flex-direction:column;gap:16px">',
    '<p style="font-size:34px;line-height:1.45">The tests in SQL, the matcher and a notebook on the payment records:</p>',
    f'<p style="{MONO};font-size:36px;color:#8db0f0"><a href="https://kvinayakpai.github.io/domain-series/payments/technical/"><span style="color:#8db0f0">kvinayakpai.github.io/domain-series/payments/technical</span></a></p>',
    '</div>',
    f'<div style="display:flex;flex-direction:column;gap:8px;border-left:6px solid {HL};padding:8px 0 8px 32px">',
    f'<p style="{SIGN};font-size:32px;font-weight:600;color:#a3adb8">Next: all three on one map</p>',
    '<p style="font-size:36px;line-height:1.35">Who saw what: which records copy each other, and which look at the world.</p>',
    '</div>',
]), "Every record was right about what it saw, and only the customer saw both debits. The technical companion on the series site has the tests in SQL, the matcher, every query the assistant ran and a notebook that runs on June’s payment records, with an answer key to score your own work, and the demo lets you match the timeouts and watch the suspense account turn into a list of customers. The last post puts all three domains, the shelf, the delivery and the money, on one map of which records copy each other and which look at the world.",
    bg=INK, fg="#e6eaee", gap=56, center=True)

order = ["cover", "scene", "readings", "happened", "timeline", "chart", "cost", "data", "tests", "match", "clocks", "assistant",
         "normal", "fourways", "mdr", "helped", "questions", "close"]
for sid in order:
    (OUT / "slides" / f"{sid}.html").write_text(slides[sid])
for f in (OUT / "slides").glob("*.html"):
    if f.stem not in order:
        f.unlink()
prev = OUT / "deck.json"
deck = json.loads((prev if prev.exists() else ROOT / "decks" / "retail" / "project" / "deck.json").read_text())
if not prev.exists():
    deck["createdOnFiles"] = {"v": 1, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
deck["title"] = "Why Domain Matters: Payments"
deck["order"] = order
deck["sections"] = {
    "s1": {"description": "The scene, and five readings of one payment by the data products", "start": "cover"},
    "s2": {"description": "What actually happened, what it cost, and why the data could not say so", "start": "happened"},
    "s3": {"description": "What domain knowledge changes: tests about the world, the matcher, the clocks, the assistant", "start": "tests"},
    "s4": {"description": "Why it is normal, payment success four ways, the new UPI fee, what would have helped, and questions for leaders", "start": "normal"},
}
prev.write_text(json.dumps(deck))
print(f"wrote {OUT.relative_to(ROOT)}: {len(order)} slides")

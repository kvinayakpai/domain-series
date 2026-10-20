"""Build the retail deck (Slides artifact data files) from retail.json and retail-ai.json.

The deck follows the post: the Monday review, five readings of one week by the data products,
what actually happened, why the data could not say so, and what domain knowledge changes in the
data work, each scored against the world's answer key.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "decks" / "retail" / "project"
(OUT / "slides").mkdir(parents=True, exist_ok=True)
d = json.loads((ROOT / "src" / "data" / "retail.json").read_text())
ai = json.loads((ROOT / "src" / "data" / "retail-ai.json").read_text())
S = {s["key"]: s for s in d["scenarios"]}
AS_IS, BINS = S["off|today"], S["off|scanned"]
st, ep = d["story"], d["story"]["episode"]
hero = ai["forecast"]["by_sku"]["ATTA-WW-5KG"]
made = {m["date"]: m for m in ai["forecast"]["made_5kg"]}
opts = {o["label"]: o for o in ai["detector"]["options"]}
rerun = {o["label"]: o for o in d["detectors"]}
qs = {q["id"]: q for q in ai["assistant"]["questions"]}
score = ai["assistant"]["score"]
av = ai["availability"]
rec5 = st["kpis"]["weekly"]["recorded_sales"]["ATTA-WW-5KG"]
w = st["kpis"]["weekly"]["recorded_sales"]
share = [rec5[k] / (rec5[k] + w["ATTA-WW-1KG"][k] + w["ATTA-WW-10KG"][k]) for k in range(4)]
base = [x["true"] for x in ai["forecast"]["series_5kg"]]
week = [sum(base[k * 7:k * 7 + 7]) for k in range(4)]
generic = ai["tests"]["generic"]
passed = sum(t["pass"] for t in generic)
milk_rows = next(t for t in generic if not t["pass"])["failing_rows"]
audit = next(a for a in ai["tests"]["domain"][1]["failing"] if a["sku"] == "ATTA-WW-5KG")
flag = ai["detector"]["hero_flags"][0]
hourly = opts["hourly, 1 in 1,000"]
nightly = opts["daily rule, 1 day"]
upto = ai["forecast"]["order_up_to_month_end"]
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 11: "Eleven", 12: "twelve", 14: "fourteen"}


def pct(v):
    return f"{round(abs(v) * 100)}%"


def signed(v):
    return f"{'−' if v < 0 else '+'}{pct(v)}"


def when(iso):
    return datetime.fromisoformat(iso[:16]).strftime("%a %-d %b, %H:%M")


SIGN = "font-family:'Anek Latin', Arial, sans-serif"
MONO = "font-family:'IBM Plex Mono', 'Courier New', monospace"
SERIF = "font-family:'Literata', Georgia, serif"
INK, PAPER, PANEL, MUTED, RECORD, HL = "#1b2430", "#f5f6f4", "#eceeea", "#59626d", "#2f55a4", "#ffe14d"
ORANGE, GREEN, RULE = "#d9661f", "#1a9e70", "#d5d9d4"
NIGHT, NIGHT_TEXT, NIGHT_MUTED, NIGHT_RECORD, NIGHT_PANEL = INK, "#e6eaee", "#a3adb8", "#8db0f0", "#222c37"


def section(sid, body, notes, bg=PAPER, fg=INK, gap=48, center=False):
    jc = "justify-content:center;" if center else ""
    return (f'<section id="{sid}" data-transition="fade" style="background:{bg};color:{fg};{SERIF};'
            f'padding:128px 128px 160px;display:flex;flex-direction:column;{jc}gap:{gap}px">\n{body}\n<aside>{notes}</aside>\n</section>\n')


def h2(text, color=INK):
    return f'<h2 style="{SIGN};font-size:72px;font-weight:700;line-height:1.05;color:{color}">{text}</h2>'


def foot(text, color=MUTED):
    return f'<p style="position:absolute;left:128px;bottom:64px;width:1664px;{SIGN};font-size:24px;color:{color}">{text}</p>'


def stat(big, small, color=INK, border=INK, size=120):
    return (f'<div style="display:flex;flex-direction:column;gap:12px;border-top:4px solid {border};padding:24px 0 0 0">'
            f'<p style="{SIGN};font-size:{size}px;font-weight:700;line-height:1;color:{color}">{big}</p>'
            f'<p style="font-size:28px;line-height:1.4">{small}</p></div>')


slides = {}
fall = 1 - rec5[1] / rec5[0]

slides["cover"] = section("cover", "\n".join([
    '<div style="display:flex;flex-direction:column;gap:16px">',
    f'<p style="{SIGN};font-size:32px;font-weight:600;color:{MUTED}">Why Domain Matters, part 1</p>',
    f'<h1 style="{SIGN};font-size:120px;font-weight:700;line-height:1;color:{INK}">Retail and grocery</h1>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:12px">',
    f'<p style="{SIGN};font-size:28px;color:{MUTED}">The record says</p>',
    f'<p style="{MONO};font-size:44px;line-height:1.2;color:{RECORD}">5 kg atta: sales −{pct(fall)} week on week.</p>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:12px;align-items:start">',
    f'<p style="{SIGN};font-size:28px;color:{MUTED}">What actually happened</p>',
    f'<p style="font-size:44px;line-height:1.25;color:{INK};background:{HL};padding:4px 16px">The shelf was empty for {round(ep["empty_open_hours"])} open hours.</p>',
    '</div>',
    foot("kvinayakpai.github.io/domain-series. Every number comes from a synthetic, seeded world with an answer key."),
]), "This series looks at domain knowledge from the side of the people who build on a business’s data: the pipelines, the dashboards, the models and now the AI assistants. Each part takes one failure that only domain knowledge explains, shows what each data product made of it, and measures what changes when the domain is built in. The numbers come from a synthetic world: one fictional supermarket in Jayanagar, Bengaluru, its warehouse and its milk route, simulated hour by hour through June 2026 and calibrated against published studies. Being synthetic, it has what real data never has, an answer key, and every model here is scored against it.",
    gap=56, center=True)

why = qs["why"]
slides["review"] = section("review", "\n".join([
    f'<p style="{SIGN};font-size:32px;font-weight:500;color:{NIGHT_MUTED}">Monday 15 June, 9 a.m. Store 014’s weekly trading review.</p>',
    f'<h2 style="{SIGN};font-size:72px;font-weight:700;line-height:1.1;color:{NIGHT_TEXT}">5 kg atta sold {pct(fall)} less than the week before. The AI assistant explained why.</h2>',
    f'<div style="background:{NIGHT_PANEL};border-left:6px solid {NIGHT_RECORD};padding:32px 40px;width:1560px;display:flex;flex-direction:column;gap:16px">',
    f'<p style="{SIGN};font-size:26px;font-weight:600;color:{NIGHT_MUTED}">AI assistant, given the warehouse schema</p>',
    f'<p style="{SIGN};font-size:32px;line-height:1.45;color:{NIGHT_TEXT}">{why["naive"]["answer"]}</p>',
    '</div>',
    f'<p style="font-size:34px;line-height:1.45;color:{NIGHT_TEXT}">Every number in that answer is right. The conclusion is not.</p>',
]), f"It is Monday the fifteenth of June, and Store 014’s weekly review opens on the sales dashboard. Whole wheat atta in five kilo bags is down {pct(fall)} on the week: {rec5[1]} bags against {rec5[0]}. The overnight pipeline ran green, and the demand forecast has eased. Someone asks the store’s AI assistant why sales fell. It queries the warehouse and answers in seconds: sales fell, the books showed stock all week, so it is not a supply problem, and five kilo’s share of atta fell, so shoppers are moving to other pack sizes. Every number in that answer is right. The conclusion is not.",
    bg=NIGHT, fg=NIGHT_TEXT, center=True)

rows = [
    ("The pipeline", f"{passed} of {len(generic)} data tests pass; the failure is full-cream milk below zero", "“Healthy.”"),
    ("The dashboard", f"Sales −{pct(fall)}; on-shelf availability {pct(AS_IS['kpis']['osa']['system_in_stock'])}, from book stock", "“Demand fell, with stock on hand.”"),
    ("The forecast", f"28-day mean: {made['2026-06-09']['naive']} → {hero['month_end']['naive']} bags a day, {pct(hero['naive_vs_recorded']['bias'])} above recorded sales", "“Tune it down.”"),
    ("The mix analysis", f"5 kg share of atta units: {pct(share[0])} → {pct(share[1])} in a week", "“Give 1 kg more shelf.”"),
    ("The AI assistant", "Seven questions about the first half of June", f"{WORDS[score['naive']].capitalize()} of seven right"),
]
table = [f'<table style="font-size:28px;color:{INK}">',
         f'<tr><th style="width:22%;text-align:left;font-weight:600;color:{MUTED}">Data product</th><th style="width:50%;text-align:left;font-weight:600;color:{MUTED}">What it reports</th><th style="width:28%;text-align:left;font-weight:600;color:{MUTED}">What it concludes</th></tr>']
table += [f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in rows]
table.append('</table>')
slides["readings"] = section("readings", "\n".join([h2("Five readings of one week"), *table,
    foot("Each reads its inputs correctly. None of them can see the shelf.")]),
    f"Nobody here is careless; each data product reads its inputs correctly. The pipeline runs twelve data tests every night, keys, values, reconciliations, and the book against its own ledger. {WORDS[passed]} pass, and the one failure is full-cream milk below zero, a familiar scan-error symptom. The dashboard computes on-shelf availability from book stock: {pct(AS_IS['kpis']['osa']['system_in_stock'])}. The forecast, a 28-day mean of recorded sales, eases from {made['2026-06-09']['naive']} to {hero['month_end']['naive']} bags a day, and scored against recorded sales it looks {pct(hero['naive_vs_recorded']['bias'])} too high, so the obvious tuning lowers it. The mix analysis sees five kilo’s share of atta fall from {pct(share[0])} to {pct(share[1])}. And the AI assistant, asked seven questions about the first half of June, gets {WORDS[score['naive']]} right: the one about what the tills scanned.",
    gap=40)

tl = [
    (when(st["misplaced"]["ts"]), f"{st['misplaced']['cases']} cases ({st['misplaced']['units']} bags) from the morning truck are put away behind the rice stack, in the wrong bay"),
    (when(ep["start"]), f"The shelf runs out. The books say {ep['book_on_hand_max']} bags, above the reorder point of {ep['reorder_point'][1]}, so nothing is ordered"),
    (f"{round(ep['empty_open_hours'])} open hours", "The shelf stands empty while the system shows stock"),
    (when(ep["end"]), "Staff restacking the rice find the cases and fill the shelf"),
]
tt = ['<div style="display:flex;flex-direction:column">']
tt += [f'<div style="display:flex;gap:32px;align-items:baseline;border-top:2px solid {RULE};padding:14px 0 14px 0"><p style="width:360px;{SIGN};font-size:30px;font-weight:500;color:{RECORD}">{a}</p><p style="width:1270px;font-size:30px;line-height:1.35">{b}</p></div>' for a, b in tl]
tt.append(f'<div style="display:flex;gap:32px;align-items:baseline;background:{HL};border-top:4px solid {INK};padding:16px 16px 16px 16px"><p style="width:328px;{SIGN};font-size:30px;font-weight:700;color:{INK}">Shoppers</p><p style="font-size:32px;color:{INK}">asked for {ep["lost_units"]} bags they could not find</p></div>')
tt.append('</div>')
slides["happened"] = section("happened", "\n".join([
    h2("What actually happened"), *tt,
    f'<p style="font-size:30px;line-height:1.45;width:1560px">Demand did ease after the month-start shop: shoppers came for {week[0]} bags in the first week and {week[1]} in the second. The rest of the drop was a shelf with nothing on it.</p>',
]), f"Here is what the answer key holds. On Tuesday the ninth at 06:17, {WORDS[st['misplaced']['cases']]} cases of five kilo atta from the morning truck were put away behind the rice stack, in the wrong bay. On Wednesday at 15:48 the shelf ran out. The books said {ep['book_on_hand_max']} bags, above the reorder point of {ep['reorder_point'][1]}, so nothing was ordered, and the shelf stood empty for {round(ep['empty_open_hours'])} open hours while the system showed stock, until staff restacking the rice found the cases on Saturday morning. Shoppers asked for {ep['lost_units']} bags they could not find. Demand did ease that week, after the first week of the month when households stock up: {week[0]} bags wanted in the first week, {week[1]} in the second. That explains part of the drop in sales. The rest was an empty shelf.",
    gap=36)

# Chart: book, shelf and misplaced stock, every open hour from Monday 8 to Sunday 14 June.
H_DAY = len(d["meta"]["hours"])
lo, hi = 7 * H_DAY, 14 * H_DAY
hr = AS_IS["hourly"]
CW, CH, YMAX = 1664, 520, 100
n = hi - lo


def x(i):
    return i * CW / (n - 1)


def y(v):
    return CH - v / YMAX * CH


empty = [i for i in range(lo, hi) if hr["empty"][i] > 0.5]
runs = []
for i in empty:
    if runs and i == runs[-1][1] + 1:
        runs[-1][1] = i
    else:
        runs.append([i, i])
svg = [f'<svg aria-label="Line chart, 8 to 14 June, every open hour. Book stock stays at {ep["book_on_hand_min"]} to {ep["book_on_hand_max"]} bags while the shelf sits at zero from Wednesday afternoon to Saturday morning; {st["misplaced"]["units"]} bags sit behind the rice the whole time, until they are found on Saturday." width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}">']
for a, b in runs:
    if b - a >= 2:
        svg.append(f'<rect x="{x(a - lo):.0f}" y="0" width="{x(b - lo) - x(a - lo) + CW / (n - 1):.0f}" height="{CH}" fill="#fbe68a"/>')
for v in (25, 50, 75, 100):
    svg.append(f'<line x1="0" y1="{max(2, y(v)):.0f}" x2="{CW}" y2="{max(2, y(v)):.0f}" stroke="#dde1dc" stroke-width="2"/>')
svg.append(f'<line x1="0" y1="{CH - 1}" x2="{CW}" y2="{CH - 1}" stroke="#b9bfb7" stroke-width="2"/>')
for key, color in (("misplaced", GREEN), ("shelf", ORANGE), ("book", RECORD)):
    path = "".join(f"{'M' if k == 0 else 'L'}{x(k):.0f},{y(hr[key][lo + k]):.0f}" for k in range(n))
    svg.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="5" stroke-linejoin="round"/>')
svg.append('</svg>')
days = [datetime.fromisoformat(dd).strftime("%a %-d") for dd in d["meta"]["days"][7:14]]
legend = [("On the books", RECORD), ("On the shelf", ORANGE), ("Behind the rice", GREEN)]
slides["chart"] = section("chart", "\n".join([
    h2("The books never fell to the reorder point"),
    *svg,
    '<div style="display:flex;gap:0">' + "".join(f'<p style="flex:1;{SIGN};font-size:24px;color:{MUTED}">{t}</p>' for t in days) + '</div>',
    '<div style="display:flex;gap:48px;align-items:center">'
    + "".join(f'<div style="display:flex;gap:16px;align-items:center"><div style="width:48px;height:6px;background:{c}"></div><p style="{SIGN};font-size:26px">{t}</p></div>' for t, c in legend)
    + f'<div style="display:flex;gap:16px;align-items:center"><div style="width:32px;height:32px;background:#fbe68a"></div><p style="{SIGN};font-size:26px">Shelf empty</p></div></div>',
    foot("5 kg atta at Store 014, bags, every open hour from 8 to 14 June 2026. Grid lines every 25 bags. Synthetic world, seed 42."),
]), f"This is the same week, hour by hour, from the answer key. The blue line is what the books said; it jumps on Tuesday morning when the delivery is booked. The green line is the {st['misplaced']['units']} bags behind the rice. The orange line is what was actually on the shelf, which hits zero on Wednesday afternoon and stays there until Saturday morning. Through the whole yellow band the books sit at {ep['book_on_hand_min']} or {ep['book_on_hand_max']}, above the reorder point of about {ep['reorder_point'][1]}, so the system never orders.",
    gap=24)

traps = [
    ("Sales are censored demand", "A till records a sale, not a shopper. When the shelf is empty, sales measure the shelf, and every model trained on them inherits the gap: forecasts, elasticities, mix shares."),
    ("Book stock is a belief", "It is computed: the last count plus receipts, minus sales and write-offs. It agreed with every transaction and was wrong about the shelf for three days. No data test looks at the shelf."),
    ("The holdout is censored too", f"Scored on recorded sales, the forecast looks {pct(hero['naive_vs_recorded']['bias'])} too high. Scored on the shoppers who came, it is {pct(hero['naive_vs_true']['bias'])} too low. The better a model fits the holdout, the worse it gets."),
]
cards = [f'<div style="display:flex;flex-direction:column;gap:20px;background:{PAPER};padding:40px;border-top:8px solid {RECORD}"><h3 style="{SIGN};font-size:40px;font-weight:650;line-height:1.15">{a}</h3><p style="font-size:28px;line-height:1.45">{b}</p></div>' for a, b in traps]
slides["traps"] = section("traps", "\n".join([
    h2("Why the data could not say so"),
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:40px">', *cards, '</div>',
    foot("Conlon and Mortimer (2013) on demand estimation when availability changes; DeHoratius and Raman (2008) on inventory record inaccuracy."),
]), f"Three traps sit under this week, and anyone who has built on transaction data has stepped in at least one. Sales are censored demand: a till records a sale, not a shopper, so when the shelf is empty, sales measure the shelf, and every model trained on sales inherits the gap. Book stock is a belief, not an observation: it is computed from the last count, receipts, sales and write-offs, which is why every reconciliation test passes; it agreed with every transaction and was wrong about the shelf for three days. And the evaluation data is censored too: scored against recorded sales the store’s forecast looks {pct(hero['naive_vs_recorded']['bias'])} too high, scored against the shoppers who came for the item it is {pct(hero['naive_vs_true']['bias'])} too low. The holdout set has the same hole as the training set.",
    bg=PANEL, gap=48)

slides["normal"] = section("normal", "\n".join([
    h2("None of this is rare"),
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:64px">',
    stat("8.3%", "of grocery items out of stock on average, in a worldwide study that traced most out-of-stocks to the store itself"),
    stat("65%", "of nearly 370,000 inventory records wrong, across 37 stores of one retailer"),
    stat(f"{d['meta']['realism'][0]['detail'].split('.')[0]}%", "of open hours with an empty shelf across the world’s seven warehouse items in June, the rate it was calibrated to"),
    '</div>',
    foot("FMI, GMA and CIES (2002), worldwide out-of-stock study; DeHoratius and Raman (2008), Management Science 54(4); Store 014, June 2026."),
]), "None of this is unusual. A worldwide study of grocery out-of-stocks put the average rate at 8.3 percent and traced most of them to the store itself: ordering, forecasting and shelf replenishment. In a study of nearly 370,000 inventory records from 37 stores of one retailer, 65 percent were wrong. The world behind this deck is calibrated to figures like these: across its seven warehouse items, shelves stood empty for about five percent of open hours in June.",
    gap=56)

trow = [
    ("Nothing, as today", "–", AS_IS["kpis"]["lost_units"]),
    ("Nightly rule, one day", f"{nightly['caught']} of {nightly['gaps']}", rerun["daily rule, 1 day"]["hero_lost_units"]),
    ("Hourly, 1 in 100", f"{opts['hourly, 1 in 100']['caught']} of {opts['hourly, 1 in 100']['gaps']}", rerun["hourly, 1 in 100"]["hero_lost_units"]),
    ("Hourly, 1 in 1,000", f"{hourly['caught']} of {hourly['gaps']}", rerun["hourly, 1 in 1,000"]["hero_lost_units"]),
    ("Hourly, 1 in 10,000", f"{opts['hourly, 1 in 10,000']['caught']} of {opts['hourly, 1 in 10,000']['gaps']}", rerun["hourly, 1 in 10,000"]["hero_lost_units"]),
]
dt = [f'<table style="font-size:28px;color:{INK}">',
      f'<tr><th style="width:46%;text-align:left;font-weight:600;color:{MUTED}">Acting on</th><th style="width:27%;text-align:right;font-weight:600;color:{MUTED}">Gaps found</th><th style="width:27%;text-align:right;font-weight:600;color:{MUTED}">5 kg bags lost</th></tr>']
dt += [f'<tr><td>{a}</td><td style="text-align:right">{b}</td><td style="text-align:right">{c}</td></tr>' for a, b, c in trow]
dt.append('</table>')
slides["detector"] = section("detector", "\n".join([
    h2("Model how the data is observed"),
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:start">',
    '<div style="display:flex;flex-direction:column;gap:32px">',
    '<p style="font-size:30px;line-height:1.45">A gap detector learns each item’s hourly pattern from May’s till lines, adds up the sales it expects over every silence while the books show stock, and alerts once a silence that long is less likely than 1 in 1,000.</p>',
    stat(flag["flag_ts"][11:16], f"on Wednesday: the 5 kg gap flagged {WORDS[round(flag['open_hours_to_flag'])]} open hours in", size=96),
    stat(f"{hourly['true']} of {hourly['flags']}", f"alerts in June at an empty shelf, across seven items; {hourly['caught']} of the {hourly['gaps']} gaps found", size=96),
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:20px">',
    f'<h3 style="{SIGN};font-size:36px;font-weight:600;line-height:1.2">June rerun, checking the shelf at every alert</h3>',
    *dt,
    '</div>', '</div>',
    foot("The threshold is a business decision: a false alarm costs a walk to a full shelf; a missed gap costs bags."),
]), f"The first change models how the data is observed. A gap detector learns each item’s usual hourly sales from May’s till lines. It adds up the sales it expects over every run of open hours with no sales while the books show stock, and raises an alert once a zero that long is less likely than one in a thousand. On June’s records it flags five kilo atta at {flag['flag_ts'][11:16]} on Wednesday, {WORDS[round(flag['open_hours_to_flag'])]} open hours after the shelf emptied. Across the seven warehouse items it raises {hourly['flags']} alerts; {hourly['true']} fall in real gaps, and it finds {hourly['caught']} of the {hourly['gaps']} gaps that lasted three open hours or more. Rerun June with someone checking the shelf within an hour of each alert, and five kilo atta loses {rerun['hourly, 1 in 1,000']['hero_lost_units']} bags instead of {AS_IS['kpis']['lost_units']}. The threshold is a business decision: one in a hundred finds more gaps and sends staff to more full shelves. The nightly rule a BI team might ship first never cried wolf, but found {nightly['caught']} of the {nightly['gaps']} gaps, a median {round(nightly['median_open_hours_to_flag'])} open hours in.",
    gap=40)

ft = [f'<table style="font-size:28px;color:{INK}">',
      f'<tr><th style="width:40%;text-align:left;font-weight:600;color:{MUTED}">Bias over June</th><th style="width:30%;text-align:right;font-weight:600;color:{MUTED}">Against recorded sales</th><th style="width:30%;text-align:right;font-weight:600;color:{MUTED}">Against shoppers</th></tr>',
      f'<tr><td>Store’s forecast</td><td style="text-align:right">{signed(hero["naive_vs_recorded"]["bias"])}</td><td style="text-align:right">{signed(hero["naive_vs_true"]["bias"])}</td></tr>',
      f'<tr><td>On unconstrained demand</td><td style="text-align:right">{signed(hero["aware_vs_recorded"]["bias"])}</td><td style="text-align:right">{signed(hero["aware_vs_true"]["bias"])}</td></tr>',
      '</table>']
slides["forecast"] = section("forecast", "\n".join([
    h2("Unconstrain demand before you train"),
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:64px">',
    stat(f"{hero['month_end']['naive']}", "bags a day: the store’s 28-day forecast on 28 June, trained on recorded sales", color=RECORD, border=RECORD),
    stat(f"{hero['month_end']['aware']}", "bags a day, trained on unconstrained demand: the expected sales filled into every censored hour", color=GREEN, border=GREEN),
    stat(f"{hero['month_end']['true_june_mean']}", "bags a day that shoppers came for in June, from the answer key", color=ORANGE, border=ORANGE),
    '</div>',
    *ft,
    foot(f"Scored on recorded sales, the better forecast looks worse. Order-up-to level at month end: {upto['naive'][1]} → {upto['aware'][1]} bags."),
]), f"The second change unconstrains demand before training. Keep the store’s rule, a 28-day mean, and change its input: fill every censored hour, the runs the detector flagged and the hours the books show no stock, with the sales the detector expected. The forecast holds: {hero['month_end']['aware']} bags a day at the end of June instead of {hero['month_end']['naive']}, against the {hero['month_end']['true_june_mean']} that shoppers came for; it runs a little high because some shoppers who found the shelf empty came back later and are counted twice. Over June its bias against shoppers falls from {signed(hero['naive_vs_true']['bias'])} to {signed(hero['aware_vs_true']['bias'])}. Now look at the other column: scored on recorded sales, the unconstrained forecast looks worse, {signed(hero['aware_vs_recorded']['bias'])} instead of {signed(hero['naive_vs_recorded']['bias'])}. A team that evaluates on recorded sales would reject the better model. The order-up-to level the reorder rule would set rises from {upto['naive'][1]} bags to {upto['aware'][1]}.",
    gap=48)

layer = ["Definitions: “sales measure demand only while the item is on the shelf”; “book stock is a belief, not an observation”",
         "Three rules, among them: treat a silence the item’s usual rate cannot explain as censored",
         "The tables that observe the shelf: till lines, shelf audits, receipts, counts",
         "Four views: hourly sales, the hourly book, censored hours, a demand estimate"]
slides["assistant"] = section("assistant", "\n".join([
    h2("Give the assistant a domain layer", NIGHT_TEXT),
    '<div style="display:grid;grid-template-columns:1fr 1.15fr;gap:72px;align-items:start">',
    '<div style="display:flex;flex-direction:column;gap:28px">',
    f'<p style="{SIGN};font-size:96px;font-weight:700;line-height:1;color:{NIGHT_TEXT}">{score["naive"]} → {score["domain"]} <span style="color:{NIGHT_MUTED}">of {score["of"]}</span></p>',
    f'<p style="{SIGN};font-size:28px;color:{NIGHT_MUTED}">questions answered right, schema only → with the domain layer</p>',
    f'<ul style="font-size:26px;line-height:1.4;color:{NIGHT_TEXT}">' + "".join(f"<li>{t}</li>" for t in layer) + '</ul>',
    '</div>',
    f'<div style="background:{NIGHT_PANEL};border-left:6px solid {GREEN};padding:32px 36px;display:flex;flex-direction:column;gap:14px">',
    f'<p style="{SIGN};font-size:24px;font-weight:600;color:{NIGHT_MUTED}">Why did 5 kg atta sales fall? With the domain layer:</p>',
    f'<p style="{SIGN};font-size:26px;line-height:1.45;color:{NIGHT_TEXT}">{why["domain"]["answer"]}</p>',
    '</div>', '</div>',
    foot("BIRD (Li and others, 2023): best model 40% execution accuracy, people 93%. Sequeda, Allemang and Jacob (2023): GPT-4 16% on the SQL schema, 54% on a knowledge graph.", NIGHT_MUTED),
]), f"The third change gives the assistant the domain. Same assistant, same seven questions, now given a domain layer: definitions, such as sales measure demand only while the item is on the shelf, and book stock is a belief, not an observation; three rules; the tables that observe the shelf, the till lines and shelf audits; and four views built from them: hourly sales, the hourly book, the censored hours and a demand estimate. It answers all seven. Asked why sales fell, it finds the {flag['open_hours']} open hours with {WORDS[flag['recorded']]} bag recorded against {round(flag['expected_total'])} expected while the books showed stock, the audit that found the bay empty, and no delivery before sales resumed, so the bags were in the store but not on the shelf; with those hours filled in, the empty shelf explains about half the fall. Published work points the same way: on the BIRD text-to-SQL benchmark, the best model of 2023 reached 40 percent execution accuracy against 93 for people; on enterprise insurance questions, GPT-4 answered 16 percent correctly from the SQL schema and 54 from a knowledge graph of the same data. The assistant here is scripted so the run can be repeated; the companion shows every query.",
    bg=NIGHT, fg=NIGHT_TEXT, gap=48)

ways = [("On the books", av["on_the_books"], "Open hours with stock on the books", NIGHT_RECORD),
        ("Shelf audits", av["shelf_audits"], f"{av['audits']} audits, Tuesdays and Fridays at 11:00", NIGHT_TEXT),
        ("Books and tills", av["books_and_tills"], "Stock on the books, outside the gaps the tills show", NIGHT_TEXT),
        ("On the shelf", av["true_open_hours"], "Open hours with a bag on the shelf: answer key", HL),
        ("Demand served", av["true_demand_served"], "Bags wanted that shoppers found: answer key", HL)]
cells = [f'<div style="display:flex;flex-direction:column;gap:14px;border-top:4px solid {c};padding:24px 0 0 0"><p style="{SIGN};font-size:100px;font-weight:700;line-height:1;color:{c}">{pct(v)}</p><p style="{SIGN};font-size:30px;font-weight:600">{label}</p><p style="font-size:24px;line-height:1.4;color:{NIGHT_MUTED}">{how}</p></div>' for label, v, how, c in ways]
slides["fiveways"] = section("fiveways", "\n".join([
    h2("One name, five numbers", NIGHT_TEXT),
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr;gap:40px">', *cells, '</div>',
    '<p style="font-size:34px;line-height:1.45;width:1500px">On-shelf availability of 5 kg atta in June. Whichever one your semantic layer encodes is the one the business will see.</p>',
]), f"On-shelf availability sounds like one number. Store 014’s records give three honest answers for five kilo atta in June, and the answer key two more. Hours with stock on the books: {pct(av['on_the_books'])}, because the cases behind the rice count as available. The shelf audits, twice a week at eleven: {pct(av['shelf_audits'])}. Book stock outside the gaps the tills show, which uses the detector: {pct(av['books_and_tills'])}. From the answer key, open hours with a bag on the shelf: {pct(av['true_open_hours'])}, and bags wanted that shoppers found: {pct(av['true_demand_served'])}. The two record-based measures that come closest use an independent observation, the audits, or a model of how the data is observed, the tills. Whichever one the semantic layer encodes is the one the business will see.",
    bg=NIGHT, fg=NIGHT_TEXT, gap=64)

cap = [
    ("Join the observation you already have", f"The 11:00 audit on {datetime.fromisoformat(audit['audit_ts']).strftime('%A %-d June')} found the 5 kg bay empty while the books showed {audit['book']}. The audit table was in the warehouse all along. Nothing joined it.", None),
    ("Capture the missing event", "Scan every case into a numbered backroom bin at put-away, and the record knows where the stock is. Sometimes the best model is a barcode scan.",
     (f"{BINS['kpis']['lost_units']} bag", f"lost in June instead of {AS_IS['kpis']['lost_units']}")),
]
cc = []
for t, body, big in cap:
    inner = [f'<h3 style="{SIGN};font-size:44px;font-weight:650;line-height:1.15">{t}</h3>']
    if big:
        inner.append(f'<p style="{SIGN};font-size:96px;font-weight:700;line-height:1">{big[0]}</p><p style="{SIGN};font-size:30px;color:{MUTED}">{big[1]}</p>')
    inner.append(f'<p style="font-size:30px;line-height:1.45">{body}</p>')
    cc.append(f'<div style="display:flex;flex-direction:column;gap:20px;background:{PAPER};padding:48px;border-top:8px solid {GREEN}">' + "".join(inner) + '</div>')
slides["capture"] = section("capture", "\n".join([
    h2("Or change what gets recorded"),
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:start">', *cc, '</div>',
    foot("Bags lost come from rerunning June in the world, on the same shoppers, with bin scans from 1 June."),
]), f"Two more changes need no model at all. The store audits its shelves at eleven every Tuesday and Friday; on Friday the twelfth the audit found the five kilo bay empty while the books showed {audit['book']}. The audit table was in the warehouse all along, and no pipeline, dashboard or model joined it. And if every case is scanned into a numbered backroom bin at put-away, the record knows where the stock is: rerun June that way and five kilo atta loses {BINS['kpis']['lost_units']} bag instead of {AS_IS['kpis']['lost_units']}. Sometimes the best model is a barcode scan.",
    bg=PANEL, gap=48)

questions = [
    "Which of our tables are observations, and which are beliefs computed from other tables?",
    "Where does our data stop recording what we are trying to measure?",
    "Which independent observation do we have, and does anything join to it?",
    "What do we score our models against, and does it share their blind spot?",
    "What does our AI assistant know about how the business works, and how do we test that?",
]
slides["questions"] = section("questions", "\n".join([
    h2("Five questions to ask your team"),
    '<div style="display:flex;flex-direction:column">',
    *[f'<div style="display:grid;grid-template-columns:72px 1fr;gap:24px;border-top:2px solid {RULE};padding:22px 0 22px 0">'
      f'<p style="{SIGN};font-size:40px;font-weight:700;line-height:1.2;color:{RECORD}">{i}</p>'
      f'<p style="font-size:38px;line-height:1.3">{q}</p></div>' for i, q in enumerate(questions, 1)],
    '</div>',
    foot("For data and AI leaders. The technical companion answers each one for Store 014."),
]), "For data and AI leaders, five questions to take back to your team. Which of our tables are observations, and which are beliefs computed from other tables? Where does our data stop recording what we are trying to measure? Which independent observation do we have, and does anything join to it? What do we score our models against, and does it share their blind spot? And what does our AI assistant know about how the business works, and how do we test that?",
    gap=48)

slides["close"] = section("close", "\n".join([
    f'<h2 style="{SIGN};font-size:88px;font-weight:700;line-height:1.08;color:{NIGHT_TEXT};width:1500px">Sales are not demand. The book is not the shelf.</h2>',
    '<div style="display:flex;flex-direction:column;gap:16px">',
    '<p style="font-size:34px;line-height:1.45">The tests in SQL, the models in Python, and a notebook on the records:</p>',
    f'<p style="{MONO};font-size:36px;color:{NIGHT_RECORD}"><a href="https://kvinayakpai.github.io/domain-series/retail/technical/"><span style="color:{NIGHT_RECORD}">kvinayakpai.github.io/domain-series/retail/technical</span></a></p>',
    '</div>',
    f'<div style="display:flex;flex-direction:column;gap:8px;border-left:6px solid {HL};padding:8px 0 8px 32px">',
    f'<p style="{SIGN};font-size:32px;font-weight:600;color:{NIGHT_MUTED}">Next: logistics</p>',
    '<p style="font-size:36px;line-height:1.35">Delivered on time, in full. One pallet line held the wrong pack size.</p>',
    '</div>',
]), "Sales are not demand, and the book is not the shelf. The technical companion on the series site has the tests in SQL, the detector and the unconstrained forecast in Python, every query the assistant ran, and a notebook that runs on Store 014’s records, with an answer key to score your own work. The demo lets you change what the data team does and rerun June with the store acting on it. The next part traces the month’s second empty shelf back to the warehouse, where every record said the delivery was on time and in full.",
    bg=NIGHT, fg=NIGHT_TEXT, gap=56, center=True)

order = ["cover", "review", "readings", "happened", "chart", "traps", "normal", "detector", "forecast", "assistant",
         "fiveways", "capture", "questions", "close"]
for sid in order:
    (OUT / "slides" / f"{sid}.html").write_text(slides[sid])
for f in (OUT / "slides").glob("*.html"):
    if f.stem not in order:
        f.unlink()
prev = OUT / "deck.json"
deck = json.loads(prev.read_text())
if "createdOnFiles" not in deck:
    deck["createdOnFiles"] = {"v": 1, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
deck["title"] = "Why Domain Matters: Retail and grocery"
deck["order"] = order
deck["sections"] = {
    "s1": {"description": "The Monday review, and five readings of one week by the data products", "start": "cover"},
    "s2": {"description": "What actually happened, and why the data could not say so", "start": "happened"},
    "s3": {"description": "What domain knowledge changes: the detector, the forecast and the assistant, scored", "start": "detector"},
    "s4": {"description": "Availability five ways, changing what gets recorded, and questions for leaders", "start": "fiveways"},
}
prev.write_text(json.dumps(deck))
print(f"wrote {OUT.relative_to(ROOT)}: {len(order)} slides")

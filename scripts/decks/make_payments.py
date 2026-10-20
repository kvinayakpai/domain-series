"""Build the payments deck (Slides artifact data files) from the blog's payments.json."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "decks" / "payments" / "project"
(OUT / "slides").mkdir(parents=True, exist_ok=True)
d = json.load(open(ROOT / "src" / "data" / "payments.json"))
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
    whole = int(round(v * 100)) // 100 if dec else int(round(v))
    frac = f".{int(round(v * 100)) % 100:02d}" if dec else ""
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
    f'<p style="{MONO};font-size:32px;line-height:1.5;color:#8db0f0">{hms(upi["ts"])}  UPI   {inr_in(sc["amount_inr"], True)}  failed: no response<br>{hms(second["ts"])}  {second["tender"]}  {inr_in(sc["amount_inr"], True)}  approved</p>',
    '</div>',
    f'<p style="font-size:32px;line-height:1.45;color:#e6eaee;width:1400px">{late_s} seconds after she approved the UPI payment, the store was credited. Nobody at the till saw it. She had paid twice.</p>',
]), f"Saturday evening, the rush. A customer’s basket comes to {inr_in(sc['amount_inr'], True)}. She scans the QR code at the till and approves the payment on her phone, and her bank takes the money. The till waits thirty seconds, hears nothing back, and shows payment failed, no response. The cashier asks for another way to pay; she pays by card and leaves. {late_s} seconds after she approved the UPI payment, the store’s bank confirms the credit. Nobody at the till sees it. She has paid twice, and it takes a phone call and eight days to get the money back.",
    bg=INK, fg="#e6eaee", center=True)

d20 = next(x for x in A["daily"] if x["date"] == "2026-06-20")
d21 = next(x for x in A["daily"] if x["date"] == "2026-06-21")
hours = {h["hour"]: h for h in st["slowdown_day_by_hour"]}
twice = sum(1 for c in A["complaints"] if c["kind"] == "charged twice")
refunds = sum(f["amount_inr"] for f in A["refunds"])
rows = [
    ("Cashier", f"“Failed: no response” {slow['upi_timeouts']} times in 90 minutes; another payment taken {slow['second_payments']} times", "“Take another payment.”"),
    ("Payments operations", f"Approvals at {pct(hours[18]['approved_at_till'] / hours[18]['upi_attempts'])} and {pct(hours[19]['approved_at_till'] / hours[19]['upi_attempts'])} for two hours, normal by eight", "“Incident closed.”"),
    ("Reconciliation analyst", f"{d20['unmatched'] + d21['unmatched']} UPI credits with no approved payment at the till", "“Park them in suspense.”"),
    ("Customer support", f"{len(A['complaints'])} complaints in June, {twice} of them “charged twice”", "“Send a screenshot; five days.”"),
    ("Finance controller", f"UPI fees of ₹0 in June; {inr_in(refunds)} of refunds", "“UPI is free; refunds are small.”"),
]
table = [f'<table style="font-size:28px;color:{INK}">',
         f'<tr><th style="width:24%;text-align:left;font-weight:600;color:{MUTED}">Who</th><th style="width:46%;text-align:left;font-weight:600;color:{MUTED}">What they see</th><th style="width:30%;text-align:left;font-weight:600;color:{MUTED}">What they conclude</th></tr>']
table += [f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in rows]
table.append('</table>')
slides["readings"] = section("readings", "\n".join([h2("Five readings of one evening"), *table,
    foot("Each conclusion follows from the record in front of that person. None of them sees a customer charged twice.")]),
    f"Nobody here is careless. The cashier sees a screen that says failed and takes another payment, as every cashier does: {slow['second_payments']} times in ninety minutes. Payments operations sees approvals fall to {pct(hours[18]['approved_at_till'] / hours[18]['upi_attempts'])} and {pct(hours[19]['approved_at_till'] / hours[19]['upi_attempts'])} for two hours and recover, and closes the incident. The reconciliation analyst finds {d20['unmatched'] + d21['unmatched']} UPI credits with no approved payment behind them and parks them in suspense. Customer support takes {twice} calls from people charged twice and asks for screenshots. Finance sees UPI settle with no fees and small refunds.",
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
    f'<p style="font-size:32px;line-height:1.45;width:1550px">When the debit has happened and the answer is late, UPI settles it afterwards: the store’s bank confirms the credit, or the money goes back. RBI requires it back within five days of the payment, with ₹100 a day after that. The money is never lost. For a while it is in two places, and the till is the last to know.</p>',
    foot("40% of UPI attempts at Store 014 got no answer within 30 seconds between 18:20 and 19:50. RBI/2019-20/67 (2019): merchant payments reversed within T+5.")]),
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
    f'<p style="font-size:30px;line-height:1.45">From 15 October 2026: 0.4% on payments to a merchant above ₹2,000, capped at ₹300. Merchants receiving up to ₹1 lakh a month through UPI QR are exempt.</p>',
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
    f'<p style="{MONO};font-size:26px;line-height:1.5;color:{RECORD}">Till, bill {sc["bill_id"]}<br>{hms(upi["ts"])}  UPI   failed: no response<br>          reference: none<br>{hms(second["ts"])}  card  approved</p>',
    f'<p style="{MONO};font-size:26px;line-height:1.5;color:{RECORD}">Provider’s UPI report<br>{sc["rrn"]}  {hms(upi["ts"])}<br>success, confirmed {hms(sc["credited_ts"])}</p>',
    '</div>',
    '<div style="display:flex;flex-direction:column;gap:28px">',
    '<p style="font-size:32px;line-height:1.45">A till that hears nothing back never learns the payment’s reference number, so there is nothing to join on.</p>',
    '<p style="font-size:32px;line-height:1.45">The double charge appears only when you match the provider’s successes to the till’s approvals, find a credit with no approval, and find its bill by amount and time.</p>',
    '</div>', '</div>',
    foot("Identifiers in the data are synthetic. Download June’s till payments and the provider’s report to try the match."),
]), "If you work with payments data, slow down here. The till recorded the UPI attempt as failed, with no reference number, because it never heard back. The provider’s report has the reference number and a success. There is nothing to join on. The double charge appears only when you match the provider’s successes to the till’s approvals, find a credit with no approval behind it, and then find its bill by amount and time. Every table is right on its own. Knowing that a failed UPI payment is a question, not an answer, is the domain knowledge.",
    gap=48)

learn = [
    ("How UPI moves money", "The parties in a payment: app, NPCI, the customer’s bank, the merchant’s bank, the provider. Then NPCI’s 2017 circular on deemed approval."),
    ("Cards, for contrast", "Glenbrook, <i>Payments Systems in the U.S.</i>: authorisation, clearing, settlement and the four-party model."),
    ("When payments fail", "RBI’s 2019 circular on turnaround times and compensation; NPCI’s 2025 circulars on status checks and response times."),
    ("Reconciliation", "The keys that join payment records: RRN, the merchant’s reference, settlement dates. Credits with no sale; sales with no credit."),
    ("Practice", "Download June’s payment records and find every customer who paid twice."),
]
slides["learn"] = section("learn", "\n".join([
    h2("How to learn this domain"),
    '<div style="display:flex;flex-direction:column;gap:22px">',
    *[f'<div style="display:grid;grid-template-columns:340px 1fr;gap:40px;border-top:2px solid #d5d9d4;padding:20px 0 0 0"><p style="{SIGN};font-size:32px;font-weight:600">{a}</p><p style="font-size:28px;line-height:1.4">{b}</p></div>' for a, b in learn],
    '</div>',
    foot("A rough plan for a few evenings a week over about two months. Links in the post: kvinayakpai.github.io/domain-series/payments"),
]), "A rough plan for a few evenings a week over about two months. Learn the parties in a UPI payment and read NPCI’s circular on how a payment that times out is settled afterwards. Read Glenbrook’s Payments Systems in the U.S. for the card side. Read RBI’s 2019 circular on failed transactions and NPCI’s 2025 circulars on status checks. Learn the keys that join payment records. Then practise on Store 014’s June payment records.",
    gap=44)

slides["close"] = section("close", "\n".join([
    f'<h2 style="{SIGN};font-size:88px;font-weight:700;line-height:1.08;color:#e6eaee;width:1500px">Every record was right about what it saw. Only the customer saw both debits.</h2>',
    '<div style="display:flex;flex-direction:column;gap:16px">',
    '<p style="font-size:34px;line-height:1.45">Run the scenarios and download the records:</p>',
    f'<p style="{MONO};font-size:36px;color:#8db0f0"><a href="https://kvinayakpai.github.io/domain-series/demo/#payments"><span style="color:#8db0f0">kvinayakpai.github.io/domain-series</span></a></p>',
    '</div>',
    f'<div style="display:flex;flex-direction:column;gap:8px;border-left:6px solid {HL};padding:8px 0 8px 32px">',
    f'<p style="{SIGN};font-size:32px;font-weight:600;color:#a3adb8">The series so far</p>',
    '<p style="font-size:36px;line-height:1.35">Retail: the shelf. Logistics: the delivery. Payments: the money. One store, one month.</p>',
    '</div>',
]), "Every record was right about what it saw, and only the customer saw both debits. The demo on the series site lets you take each person’s view of the same evening, change what the till and the back office do, and download June’s payment records to find the double charges yourself. That completes the three domains of this series, in one store and one month: the shelf, the delivery and the money.",
    bg=INK, fg="#e6eaee", gap=56, center=True)

order = ["cover", "scene", "readings", "happened", "timeline", "chart", "cost", "normal", "fourways", "mdr", "helped", "data", "learn", "close"]
for sid in order:
    (OUT / "slides" / f"{sid}.html").write_text(slides[sid])
prev = OUT / "deck.json"
deck = json.loads((prev if prev.exists() else ROOT / "decks" / "retail" / "project" / "deck.json").read_text())
if not prev.exists():
    deck["createdOnFiles"] = {"v": 1, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
deck["title"] = "Why Domain Matters: Payments"
deck["order"] = order
deck["sections"] = {
    "s1": {"description": "The scene, and five readings of one evening", "start": "cover"},
    "s2": {"description": "What actually happened, in every record, and what it cost customers", "start": "happened"},
    "s3": {"description": "Why it is normal, payment success four ways, and the new UPI fee", "start": "normal"},
    "s4": {"description": "What would have helped, what the data looks like, and how to learn the domain", "start": "helped"},
}
prev.write_text(json.dumps(deck))
print(f"wrote {OUT.relative_to(ROOT)}: {len(order)} slides")

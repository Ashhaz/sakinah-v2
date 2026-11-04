#!/usr/bin/env python3
"""Generates the static Sakina site into ../site from the content files."""
import html, os, sys, shutil

sys.path.insert(0, os.path.dirname(__file__))
from common import SURAHS, COLLECTIONS, Q, H, ra
from duas import DUAS
from topics_a import TOPICS_A
from topics_b import TOPICS_B
from topics_c import TOPICS_C
from topics_d import TOPICS_D
from remedies import REMEDIES, FEEL

GROUPS = [("mind", "Heart & mind"), ("people", "People & relationships"), ("faith", "Faith & the soul"), ("body", "Body")]
GROUP_NAME = dict(GROUPS)
CONTACT = ""   # put a contact email here to turn the ⚑ buttons into mailto links

STARTS = {
    "depression": dict(v=0, h=2, d="karb", plain="You are allowed to feel this heavily. Allah knows, and so did His Messenger ﷺ. Reach for help from Him and from people."),
    "anxiety": dict(v=0, h=0, d="hasbuna", plain="Do your part, then hand the rest to Allah. Breathe slowly and remember Him."),
    "pressure": dict(v=0, h=2, d="musa", plain="Effort counts, and so does rest. Small and steady beats panicked and exhausted."),
    "money": dict(v=0, h=1, d="ali_debt", plain="Work honestly, plan carefully, and know that provision is written. Your worth is not your balance."),
    "comparison": dict(v=0, h=1, d=None, plain="The only ranking Allah announces is taqwā. A feed can’t show your heart."),
    "behind": dict(v=0, h=1, d="qadar", plain="Your timeline is yours. Keep taking the next small step."),
    "burnout": dict(v=0, h=1, d="hamm", plain="Rest is a right, not a reward. The Prophet ﷺ told us to ease off when tired."),
    "loneliness": dict(v=0, h=0, d="zakariya", plain="You are remembered and near to Allah, even when no one else is near. Then take one small step towards people."),
    "future": dict(v=0, h=0, d="istikhara", plain="Think, plan, consult, decide, then rely on Allah. The future is in kind hands."),
    "attention": dict(v=5, h=2, d="hamm", plain="Come back without shame. Allah loves the one who returns, and the prayers are built-in resets."),
    "overwhelm": dict(v=5, h=0, d="hasbuna", plain="Care, then step back. You are not asked to carry the whole world."),
    "sleep": dict(v=0, h=3, d="sleep", plain="Rest is mercy. Put the phone away, say the bedtime words and let go of the day."),
    "eyes": dict(v=0, h=0, d=None, plain="Your eyes have a right over you. Rest them, and see a professional if they trouble you."),
    "posture": dict(v=0, h=0, d=None, plain="Your body has rights too. Stand, stretch and be gentle with it."),
    "movement": dict(v=0, h=1, d=None, plain="Move a little every day. The Prophet ﷺ even raced his wife."),
}

TOPICS = TOPICS_A + TOPICS_B + TOPICS_C + TOPICS_D
for _t in TOPICS:
    _t.setdefault("start", STARTS.get(_t["slug"]))
BY_SLUG = {t["slug"]: t for t in TOPICS}
OUT = os.path.join(os.path.dirname(__file__), "..", "site")
esc = lambda s: html.escape(s, quote=True)

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">')

MOODS = [
    ("Heavy & sad", "depression"), ("Anxious", "anxiety"), ("Lonely", "loneliness"),
    ("Exhausted", "burnout"), ("Behind in life", "behind"), ("Comparing myself", "comparison"),
    ("Scared of the future", "future"), ("Stuck scrolling", "attention"), ("Can’t sleep", "sleep"),
    ("Overwhelmed by news", "overwhelm"), ("Angry", "anger"), ("Heartbroken", "heartbreak"),
    ("Guilty or ashamed", "guilt"), ("Hopeless", "hopeless"), ("Who am I?", "identity"), ("No purpose", "purpose"), ("Far from Allah", "distant"), ("Grieving", "grief"), ("Trouble at home", "family"),
    ("Pressure from friends", "peer"), ("Can’t quit a habit", "habit"), ("Self-conscious", "bodyimage"),
]

HERO_VERSES = [
    dict(ref="94:5-6", ayahs=["94:5", "94:6"], en="For indeed, with hardship [will be] ease. Indeed, with hardship [will be] ease."),
    dict(ref="13:28", ayahs=["13:28"], en="Truly, in the remembrance of Allah do hearts find peace."),
    dict(ref="2:286", ayahs=["2:286"], en="Allah does not charge a soul except [with that within] its capacity."),
    dict(ref="93:3", ayahs=["93:3"], en="Your Lord has not taken leave of you, nor has He detested [you]."),
    dict(ref="2:153", ayahs=["2:153"], en="O you who have believed, seek help through patience and prayer. Indeed, Allah is with the patient."),
    dict(ref="9:40", ayahs=[], en="“Do not grieve; indeed Allah is with us.” (the Prophet ﷺ to Abū Bakr in the cave – part of verse 9:40)", arabic=False),
    dict(ref="50:16", ayahs=["50:16"], en="…and We are closer to him than [his] jugular vein."),
    dict(ref="39:53", ayahs=["39:53"], en="Say, “O My servants who have transgressed against themselves [by sinning], do not despair of the mercy of Allah.” (part of verse 39:53)", arabic=False),
]


# ───────────────────────── helpers ─────────────────────────
def quran_url(ref):
    s, a = ref.split(":")
    return f"https://quran.com/{s}/{a}"


def quran_label(ref):
    return "Qur’an " + ref.replace("-", "–")


def src_chip(src):
    coll, n = src
    if coll == "quran":
        return f'<a class="ref" href="{quran_url(n)}" target="_blank" rel="noopener">{esc(quran_label(n))}</a>'
    if coll is None:
        return f'<span class="ref plain">{esc(n)}</span>'
    return (f'<a class="ref" href="https://sunnah.com/{coll}:{n}" target="_blank" rel="noopener">'
            f'{esc(COLLECTIONS[coll])} {n}</a>')


def grade_tag(h):
    if h.get("grade"):
        return f'<span class="grade" title="Grading of the narration">{esc(h["grade"])}</span>'
    colls = {c for c, _ in h["srcs"] if c}
    if colls and colls <= {"bukhari", "muslim"}:
        return '<span class="grade" title="Found in Ṣaḥīḥ al-Bukhārī and/or Ṣaḥīḥ Muslim">Ṣaḥīḥ</span>'
    return ""


def report_btn(label, page):
    return (f'<button class="report" type="button" data-ref="{esc(label)}" data-page="{esc(page)}" '
            f'title="Report a possible mistake" aria-label="Report a possible mistake in {esc(label)}">⚑</button>')


def verse_card(v, page=""):
    s = int(v["ref"].split(":")[0])
    if v["arabic"] and v["ayahs"]:
        ar = f'<div class="ar" lang="ar" dir="rtl" data-ayahs="{",".join(v["ayahs"])}"><span class="ar-ph">…</span></div>'
    else:
        ar = (f'<p class="ar-note">Only part of this verse is quoted. '
              f'<a href="{quran_url(v["ref"])}" target="_blank" rel="noopener">Read the full verse in Arabic on Quran.com ↗</a></p>')
    why = f'<p class="why">{esc(v["why"])}</p>' if v["why"] else ""
    note = f'<p class="why small">{esc(v["note"])}</p>' if v.get("note") else ""
    return f'''<article class="card verse reveal tilt">
  {ar}
  <p class="en">{esc(v["en"])}</p>
  {why}{note}
  <footer><a class="ref" href="{quran_url(v["ref"])}" target="_blank" rel="noopener">{esc(quran_label(v["ref"]))}</a>
  <span class="surah">Sūrat {esc(SURAHS[s])}</span>{report_btn(quran_label(v["ref"]), page)}</footer>
</article>'''


def hadith_card(h, page=""):
    en = h["en"]
    if en.startswith("^"):
        text = esc(en[1:])
    else:
        text = f"“{esc(en)}”"
    why = f'<p class="why">{esc(h["why"])}</p>' if h["why"] else ""
    chips = " ".join(src_chip(s) for s in h["srcs"])
    label = " / ".join((COLLECTIONS[c] + " " + str(n)) if c else str(n) for c, n in h["srcs"])
    return f'''<article class="card hadith reveal tilt">
  <p class="en">{text}</p>
  <p class="by">Narrated by {esc(h["by"])}</p>
  {why}
  <footer>{chips}{grade_tag(h)}{report_btn(label, page)}</footer>
</article>'''


def dua_card(d, key=None, used_in=None):
    if d.get("ayahs"):
        ar = f'<div class="ar" lang="ar" dir="rtl" data-ayahs="{",".join(d["ayahs"])}"><span class="ar-ph">…</span></div>'
    elif d.get("ar"):
        ar = f'<div class="ar static" lang="ar" dir="rtl">{esc(d["ar"])}</div>'
    else:
        ar = ""
    tr = f'<p class="translit">{esc(d["tr"])}</p>' if d.get("tr") else ""
    note = f'<p class="why">{esc(d["note"])}</p>' if d.get("note") else ""
    chips = " ".join(src_chip(s) for s in d["srcs"])
    grade = f'<span class="grade">{esc(d["grade"])}</span>' if d.get("grade") else (
        '<span class="grade" title="Found in Ṣaḥīḥ al-Bukhārī and/or Ṣaḥīḥ Muslim">Ṣaḥīḥ</span>'
        if {c for c, _ in d["srcs"] if c and c != "quran"} and {c for c, _ in d["srcs"] if c and c != "quran"} <= {"bukhari", "muslim"} else "")
    used = ""
    if used_in:
        used = '<p class="used">Used on: ' + " · ".join(
            f'<a href="{s}.html">{esc(BY_SLUG[s]["title"])}</a>' for s in used_in) + "</p>"
    return f'''<article class="card dua reveal tilt" id="{key or ""}">
  <h3>{esc(d["title"])}</h3>
  {ar}{tr}
  <p class="en">{esc(d["en"])}</p>
  {note}{used}
  <footer>{chips}{grade}</footer>
</article>'''


def remedy_card(k):
    r = REMEDIES[k]
    ar = ""
    if r.get("ayahs"):
        ar = f'<div class="ar" lang="ar" dir="rtl" data-ayahs="{",".join(r["ayahs"])}"><span class="ar-ph">…</span></div>'
    elif r.get("ar"):
        ar = f'<div class="ar static" lang="ar" dir="rtl">{esc(r["ar"])}</div>'
    tr = f'<p class="translit">{esc(r["tr"])}</p>' if r.get("tr") else ""
    en = f'<p class="en">{esc(r["en"])}</p>' if r.get("en") else ""
    quote = ""
    if r.get("quote"):
        quote = f'<p class="why">“{esc(r["quote"])}” <span class="by-inline">({esc(r["quote_by"])})</span></p>'
    elif r.get("quote_by"):
        quote = f'<p class="why">{esc(r["en"])} <span class="by-inline">({esc(r["quote_by"])})</span></p>'
        en = ""
    extra = f'<p class="why small">{esc(r["extra"])}</p>' if r.get("extra") else ""
    cs = ""
    if r.get("counters"):
        btns = "".join(
            f'<button type="button" class="tasbih" data-target="{c["target"] or 0}"><span class="tl" lang="ar">{esc(c["label"])}</span><span class="tn">0{" / " + str(c["target"]) if c["target"] else ""}</span></button>'
            for c in r["counters"])
        cs = f'<div class="tasbihs" aria-label="Tap counters">{btns}<button type="button" class="tasbih-reset" title="Reset counters">↺</button></div>'
    chips = " ".join(src_chip(x) for x in r["srcs"])
    g = f'<span class="grade">{esc(r["grade"])}</span>' if r.get("grade") else ""
    label = r["title"]
    return f'''<article class="card remedy reveal tilt">
  <h3>{esc(r["title"])}</h3>
  <p class="do">{esc(r["do"])}</p>
  {ar}{tr}{en}{quote}{extra}{cs}
  <footer>{chips}{g}{report_btn(label, "remedies")}</footer>
</article>'''


CRISIS = '''<section class="crisis reveal" id="crisis">
  <h2>If it feels like too much right now</h2>
  <p>If you are thinking about ending your life or harming yourself, or you are in danger, please <strong>contact your local emergency number or a crisis line now</strong>, and tell someone near you. You deserve support, and reaching out is a strength.</p>
  <ul class="lines">
    <li><strong>India:</strong> Tele-MANAS, <a href="tel:14416">14416</a> (toll-free; also 1800-891-4416)</li>
    <li><strong>USA:</strong> call or text <a href="tel:988">988</a></li>
    <li><strong>UK &amp; Ireland:</strong> Samaritans, <a href="tel:116123">116 123</a></li>
    <li><strong>Anywhere:</strong> <a href="https://findahelpline.com" target="_blank" rel="noopener">findahelpline.com</a> lists services by country</li>
  </ul>
  <p class="small">Numbers can change, so please check one is current for your country. Allah says: “…and do not kill yourselves. Indeed, Allah is ever Merciful to you” (<a href="https://quran.com/4/29" target="_blank" rel="noopener">Qur’an 4:29</a>, part of the verse). You can also speak to a trusted imam, teacher or family member, and to a doctor or counsellor.</p>
</section>'''


def head(title, desc, hue, depth_note=""):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#060914">
<meta name="color-scheme" content="dark">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%23080c1c'/%3E%3Cpath d='M50 12 L58 34 L80 26 L72 48 L90 56 L68 62 L72 86 L52 72 L38 90 L34 66 L10 62 L28 48 L20 26 L42 34 Z' fill='none' stroke='%23e9cf8a' stroke-width='4' stroke-linejoin='round'/%3E%3C/svg%3E">
{FONTS}
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body data-hue="{hue}">
<canvas id="bg" aria-hidden="true"></canvas>
<div class="vignette" aria-hidden="true"></div>
<div class="glow" aria-hidden="true"></div>
<div class="progress" aria-hidden="true"><i></i></div>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <a class="brand" href="index.html"><span class="mark">✶</span><span>Sakīna</span></a>
  <nav>
    <a href="index.html#topics">Topics</a>
    <a href="prayer-times.html">Prayer times</a>
    <a href="duas.html">Du’as</a>
    <a href="about.html">About &amp; sources</a>
    <button class="calm-btn" type="button" aria-pressed="false" title="Turn off 3D background and animations">Calm mode</button>
  </nav>
</header>
<main id="main">
'''


def foot():
    return '''</main>
<footer class="site-footer">
  <div class="verse-line">
    <span lang="ar" dir="rtl">أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ</span>
    <em>“Truly, in the remembrance of Allah do hearts find peace.” (Qur’an 13:28)</em>
  </div>
  <p>Sakīna was made with the intention of comfort. It is a collection of references, not a source of fatwā or medical advice. Please verify any reference on <a href="https://quran.com" target="_blank" rel="noopener">Quran.com</a> and <a href="https://sunnah.com" target="_blank" rel="noopener">Sunnah.com</a> and ask qualified scholars about religious rulings.</p>
  <p><a href="about.html#crisis">In crisis? Get help now →</a> · <a href="about.html">About &amp; sources</a> · <a href="references.html">All references (for reviewers)</a></p>
  <p class="small">Status: a personal project, not yet formally reviewed by a qualified scholar. Please verify before relying on anything here.</p>
</footer>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script src="assets/vendor/three.min.js"></script>
<script src="assets/js/main.js"></script>
</body>
</html>
'''


def breath_widget():
    return '''<section class="breath-wrap reveal" aria-label="Breathing exercise">
  <h2>Take a breath first</h2>
  <p class="muted">Slow breathing helps your body calm down. Tap the circle, breathe with it, and if you like, remember Allah in your heart as you do (<a href="https://quran.com/13/28" target="_blank" rel="noopener">13:28</a>).</p>
  <button class="breath" type="button" aria-label="Start or stop the breathing guide">
    <span class="ring r1"></span><span class="ring r2"></span><span class="orb"></span>
    <span class="cue">Tap to begin</span>
  </button>
</section>'''


# ───────────────────────── pages ─────────────────────────
def topic_page(i, t):
    nverse, nhad = len(t["verses"]), len(t["hadith"])
    prev_t, next_t = TOPICS[(i - 1) % len(TOPICS)], TOPICS[(i + 1) % len(TOPICS)]
    o = [head(f'{t["title"]} · Sakīna', f'{t["tagline"]}. Qur’an and Hadith references for {t["title"].lower()}, with sources.', t["hue"])]
    o.append(f'''<section class="hero topic-hero">
  <a class="crumb" href="index.html#topics">← All topics</a>
  <p class="eyebrow">{esc(GROUP_NAME[t["group"]])}</p>
  <h1 class="split">{esc(t["title"])}</h1>
  <p class="tagline">{esc(t["tagline"])}</p>
  <p class="intro">{esc(t["intro"])}</p>
  <div class="chips"><a href="#start">Start here</a><a href="#feel">To feel better</a><a href="#quran">{nverse} Qur’an passages</a><a href="#hadith">{nhad} hadith</a>{'<a href="#duas">Du’as</a>' if t["duas"] else ""}<a href="#steps">Gentle steps</a></div>
  <div class="scroll-cue" aria-hidden="true"><i></i></div>
</section>''')
    if t.get("callout"):
        c = t["callout"]
        o.append(f'<aside class="callout reveal"><h3>{esc(c["title"])}</h3><p>{esc(c["body"])}</p></aside>')
    if t.get("widget") == "breath":
        o.append(breath_widget())
    st = t.get("start")
    if st:
        sc = [verse_card(t["verses"][st["v"]], t["slug"]), hadith_card(t["hadith"][st["h"]], t["slug"])]
        if st.get("d"):
            sc.append(dua_card(DUAS[st["d"]]))
        o.append(f'''<section class="block start reveal" id="start"><div class="sec-head"><span class="num">★</span><h2>Start here</h2></div>
<p class="plain">{esc(st["plain"])}</p><p class="muted">If you only have a minute, read these. The full library follows.</p>
<div class="grid">{"".join(sc)}</div><p><a class="btn" href="#quran">The full library ↓</a></p></section>''')
    fl = FEEL.get(t["slug"], [])
    if fl:
        o.append(f'''<section class="block feel" id="feel"><div class="sec-head reveal"><span class="num">✺</span><h2>To feel better: do this</h2></div>
<p class="muted reveal">Don’t try everything. Pick one that feels doable, and do it now. Fixed numbers are given only where the hadith gives them; otherwise say it as often as you like.</p>
<div class="grid">{"".join(remedy_card(k) for k in fl)}</div></section>''')
    o.append('<section class="block" id="quran"><div class="sec-head reveal"><span class="num">I</span><h2>From the Qur’an</h2></div><div class="grid">')
    o += [verse_card(v, t["slug"]) for v in t["verses"]]
    o.append('</div></section>')
    o.append('<section class="block" id="hadith"><div class="sec-head reveal"><span class="num">II</span><h2>From the Prophet <span class="pbuh">ﷺ</span></h2></div><div class="grid">')
    o += [hadith_card(h, t["slug"]) for h in t["hadith"]]
    o.append('</div></section>')
    if t.get("story"):
        s = t["story"]
        paras = "".join(f"<p>{esc(p)}</p>" for p in s["body"])
        chips = " ".join(src_chip(x) for x in s["src"])
        o.append(f'<section class="block story reveal"><div class="sec-head"><span class="num">✦</span><h2>{esc(s["title"])}</h2></div>{paras}<footer>{chips}</footer></section>')
    if t["duas"]:
        o.append('<section class="block" id="duas"><div class="sec-head reveal"><span class="num">III</span><h2>Du’as for this moment</h2></div><div class="grid">')
        o += [dua_card(DUAS[k], k) for k in t["duas"]]
        o.append('</div></section>')
    steps = "".join(f"<li>{esc(s)}</li>" for s in t["steps"])
    med = '<p class="small muted">These are general wellbeing suggestions, not religious rulings or medical advice. If symptoms persist, please see a health professional.</p>'
    o.append(f'<section class="block steps reveal" id="steps"><div class="sec-head"><span class="num">❋</span><h2>Gentle, practical steps</h2></div><p class="muted">Small things you can try today. Not religious rulings, just ordinary wellbeing help that sits well alongside the guidance above.</p><ol>{steps}</ol>{med if t.get("note_medical") else ""}</section>')
    if t.get("crisis"):
        o.append(CRISIS)
    rel = "".join(f'<a class="rel" href="{r}.html"><span>{BY_SLUG[r]["glyph"]}</span>{esc(BY_SLUG[r]["title"])}</a>' for r in t["related"])
    o.append(f'<section class="block related reveal"><h2>You might also need</h2><div class="rel-row">{rel}</div></section>')
    o.append(f'''<nav class="pager reveal"><a href="{prev_t["slug"]}.html"><small>← Previous</small>{esc(prev_t["title"])}</a><a href="{next_t["slug"]}.html"><small>Next →</small>{esc(next_t["title"])}</a></nav>''')
    o.append(foot())
    return "".join(o)


def topic_card(t):
    return f'''<a class="topic-card reveal tilt" href="{t["slug"]}.html" style="--h:{t["hue"]}">
  <span class="glyph">{t["glyph"]}</span>
  <h3>{esc(t["title"])}</h3>
  <p>{esc(t["tagline"])}</p>
  <span class="go">Open →</span>
</a>'''


def index_page():
    hv = "|".join(f'{v["ref"]}' for v in HERO_VERSES)
    o = [head("Sakīna · Comfort from the Qur’an & Sunnah for hard days", "A calm place for Gen Z: Qur’an and Hadith references, with sources, for depression, anxiety, burnout, loneliness, comparison, sleep and more.", 45)]
    o.append('''<section class="hero home-hero">
  <p class="eyebrow">Qur’an &amp; Sunnah · for the heaviest days</p>
  <h1 class="split">You are not alone in the dark.</h1>
  <p class="tagline">A quiet corner of the internet with verses, hadith and du’as for the things young people actually carry, each with its source.</p>
  <div class="cta"><a class="btn primary" href="#feel">How are you feeling?</a><a class="btn" href="#topics">Browse all topics</a></div>
  <div class="scroll-cue" aria-hidden="true"><i></i></div>
</section>''')
    mood = "".join(f'<a class="mood" href="{s}.html">{esc(l)}</a>' for l, s in MOODS)
    o.append(f'<section class="block" id="feel"><div class="sec-head reveal"><span class="num">♡</span><h2>How are you feeling right now?</h2></div><div class="moods reveal">{mood}</div></section>')
    o.append('''<section class="block pt-mini reveal" id="pt-mini"><div class="sec-head"><span class="num">☪</span><h2>Prayer times</h2></div>
<p class="muted">Your times by country and city, with the next prayer counting down.</p>
<div id="pt-mini-body" class="pt-mini-body"><a class="btn primary" href="prayer-times.html">Set your location</a></div></section>''')
    # verse of the moment
    items = []
    for v in HERO_VERSES:
        arabic = v.get("arabic", True) and v["ayahs"]
        items.append(f'<div class="vom-item" data-ref="{v["ref"]}" data-ayahs="{",".join(v["ayahs"])}" data-arabic="{1 if arabic else 0}" data-en="{esc(v["en"])}"></div>')
    o.append(f'''<section class="block vom reveal" id="vom" aria-live="polite">
  <p class="eyebrow">A verse for right now</p>
  <div class="ar big" id="vom-ar" lang="ar" dir="rtl"></div>
  <p class="en big" id="vom-en"></p>
  <p class="vom-ref"><a id="vom-link" target="_blank" rel="noopener" href="#"></a></p>
  <button class="btn" id="vom-next" type="button">Show another ↻</button>
  <div hidden id="vom-data">{"".join(items)}</div>
</section>''')
    for gi, (gk, gname) in enumerate(GROUPS):
        ts = [t for t in TOPICS if t["group"] == gk]
        idattr = ' id="topics"' if gi == 0 else ""
        o.append(f'<section class="block"{idattr}><div class="sec-head reveal"><span class="num">{["I","II","III","IV"][gi]}</span><h2>{esc(gname)}</h2></div><div class="cards">' + "".join(topic_card(t) for t in ts) + '</div></section>')
    o.append('''<section class="block principles reveal"><div class="sec-head"><span class="num">✦</span><h2>How this site works</h2></div>
  <div class="three">
    <div><h3>Sourced</h3><p>Every Qur’an passage shows surah and verse. Every hadith shows its collection and number, with a link to check it.</p></div>
    <div><h3>Honest</h3><p>Where a hadith is not from the two Ṣaḥīḥ collections, the grading is stated. Partial verses are marked as partial.</p></div>
    <div><h3>Gentle</h3><p>Each page opens with a short “Start here”. Faith and professional help go together, and crisis support is one click away.</p></div>
  </div></section>''')
    o.append(foot())
    return "".join(o)


def duas_page():
    used = {}
    for t in TOPICS:
        for k in t["duas"]:
            used.setdefault(k, []).append(t["slug"])
    o = [head("Du’as · Sakīna", "Supplications from the Qur’an and authentic Sunnah for worry, grief, debt, loneliness, sleep and more.", 45)]
    o.append('''<section class="hero topic-hero">
  <a class="crumb" href="index.html">← Home</a>
  <p class="eyebrow">Supplications</p>
  <h1 class="split">Du’as for hard moments</h1>
  <p class="tagline">Words you can say when you have none of your own, and also in your own language.</p>
  <p class="intro">You can always speak to Allah in your own words. These are words taught by Allah and His Messenger ﷺ. Arabic Qur’an text is loaded live from a Qur’an API; the other Arabic is short and well-known, and each du’a lists its source.</p>
</section>''')
    o.append('<section class="block"><div class="grid">')
    for k, d in DUAS.items():
        o.append(dua_card(d, k, used.get(k)))
    o.append('</div></section>')
    o.append(foot())
    return "".join(o)


def about_page():
    o = [head("About & sources · Sakīna", "How Sakīna’s references work, how to verify them, and where to find help in a crisis.", 45)]
    o.append('''<section class="hero topic-hero">
  <a class="crumb" href="index.html">← Home</a>
  <p class="eyebrow">About</p>
  <h1 class="split">About &amp; sources</h1>
  <p class="tagline">What this is, how to check it, and what it is not.</p>
</section>
<section class="block prose reveal">
  <h2>Why Sakīna exists</h2>
  <p>Sakīna (سكينة) means tranquility, the calm Allah places in hearts. This site gathers Qur’an and Hadith references on problems many young people face today: stress, loneliness, comparison, burnout, sleep, screens and more. The aim is comfort in dark times.</p>
  <h2>How references are written</h2>
  <ul>
    <li><strong>Qur’an:</strong> shown as <em>surah:verse</em> (for example 94:5–6), each linking to Quran.com. The Arabic text is fetched live from the Qur’an API so that no letter is typed by hand. English is a translation of the meaning, not the Qur’an itself.</li>
    <li><strong>Hadith:</strong> shown as collection + number (for example Ṣaḥīḥ al-Bukhārī 5641), each linking to Sunnah.com. Numbering follows Sunnah.com; some editions number hadith differently, so if a number looks off in your printed copy, search by the wording.</li>
    <li><strong>Grading:</strong> hadith found in Ṣaḥīḥ al-Bukhārī or Ṣaḥīḥ Muslim are marked Ṣaḥīḥ. Others carry the grade given by scholars (for example Ḥasan). Weak hadith are not used.</li>
    <li><strong>Partial verses:</strong> where only part of a verse is quoted, the card says so and sends you to the full verse.</li>
    <li><strong>Interpretations:</strong> the short notes under each reference are reflections, not tafsīr or fatwā.</li>
  </ul>
  <h2>Review status</h2>
  <p><strong>This is a personal project and has not yet been formally reviewed by a qualified scholar or a mental health professional.</strong> Please treat it as a work in progress. The <a href="references.html">references page</a> lists every verse and hadith so a reviewer can check them.</p>
  <h2>Please verify and ask</h2>
  <p>Please check anything important yourself on <a href="https://quran.com" target="_blank" rel="noopener">Quran.com</a> and <a href="https://sunnah.com" target="_blank" rel="noopener">Sunnah.com</a>, and ask a qualified scholar about religious rulings. If you find a mistake, please report it so that it can be corrected.</p>
  <h2>What this site is not</h2>
  <p>It is not medical or psychological advice and it is not a substitute for therapy, medication or professional care. Depression, anxiety and other conditions are real health issues. Seeking treatment is encouraged in the Sunnah: “Allah has not sent down a disease except that He has also sent down its cure” (<a href="https://sunnah.com/bukhari:5678" target="_blank" rel="noopener">Ṣaḥīḥ al-Bukhārī 5678</a>).</p>
</section>''')
    o.append(CRISIS)
    o.append(foot())
    return "".join(o)


COUNTRIES = ["Afghanistan","Algeria","Argentina","Australia","Austria","Azerbaijan","Bahrain","Bangladesh","Belgium","Bosnia and Herzegovina","Brazil","Brunei","Canada","China","Denmark","Egypt","France","Germany","Ghana","India","Indonesia","Iran","Iraq","Ireland","Italy","Japan","Jordan","Kazakhstan","Kenya","Kuwait","Lebanon","Libya","Malaysia","Maldives","Morocco","Nepal","Netherlands","New Zealand","Nigeria","Norway","Oman","Pakistan","Palestine","Philippines","Qatar","Russia","Saudi Arabia","Senegal","Singapore","Somalia","South Africa","Spain","Sri Lanka","Sudan","Sweden","Switzerland","Syria","Tanzania","Tunisia","Turkey","UAE","Uganda","United Kingdom","United States","Uzbekistan","Yemen"]


def prayer_page():
    o = [head("Prayer times · Sakīna", "Prayer times for your country and city, with the next prayer counting down.", 45)]
    opts = "".join(f'<option value="{c}">' for c in COUNTRIES)
    o.append(f'''<section class="hero topic-hero">
  <a class="crumb" href="index.html">← Home</a>
  <p class="eyebrow">Ṣalāh</p>
  <h1 class="split">Prayer times</h1>
  <p class="tagline">Choose your country and city, or use your location.</p>
  <p class="intro">Prayer is the anchor of the day and a built-in rest from the screen. Times are calculated for your place, and methods differ between countries, so please also check with your local masjid.</p>
</section>
<section class="block pt" id="pt-app">
  <form class="pt-form reveal" id="pt-form" autocomplete="off">
    <label>Country<input id="pt-country" list="countries" placeholder="e.g. India" required></label>
    <label>City<input id="pt-city" placeholder="e.g. Hyderabad" required></label>
    <label>Calculation method
      <select id="pt-method">
        <option value="auto">Automatic (by location)</option>
        <option value="1">University of Islamic Sciences, Karachi</option>
        <option value="2">ISNA (North America)</option>
        <option value="3">Muslim World League</option>
        <option value="4">Umm al-Qura, Makkah</option>
        <option value="5">Egyptian General Authority</option>
        <option value="8">Gulf Region</option>
        <option value="9">Kuwait</option>
        <option value="10">Qatar</option>
        <option value="11">Singapore (MUIS)</option>
        <option value="13">Turkey (Diyanet)</option>
        <option value="15">Moonsighting Committee</option>
      </select></label>
    <label>Asr time
      <select id="pt-school"><option value="0">Standard (Shāfiʿī, Mālikī, Ḥanbalī)</option><option value="1">Ḥanafī (later Asr)</option></select></label>
    <div class="pt-actions"><button class="btn primary" type="submit">Show times</button><button class="btn" type="button" id="pt-geo">Use my location</button><button class="btn" type="button" id="pt-12h">12 / 24 hour</button></div>
    <datalist id="countries">{opts}</datalist>
  </form>
  <p class="pt-status" id="pt-status" role="status"></p>
  <div class="pt-next" id="pt-next" hidden><span class="eyebrow">Next prayer</span><strong id="pt-next-name"></strong><span id="pt-next-in"></span></div>
  <div class="pt-grid" id="pt-grid"></div>
  <p class="small muted" id="pt-meta"></p>
</section>
<section class="block"><div class="sec-head reveal"><span class="num">I</span><h2>About the prayers</h2></div><div class="grid">''')
    pv = Q("4:103", ["4:103"], "And when you have completed the prayer, remember Allah standing, sitting, or [lying] on your sides. But when you become secure, re-establish [regular] prayer. Indeed, prayer has been decreed upon the believers at specified times.", "Prayer has appointed times, which is why accurate times matter.")
    ph = H("^Ibn Masʿūd asked the Prophet ﷺ: “Which deed is most beloved to Allah?” He said: “Prayer at its proper time.” He asked: “Then what?” He said: “Kindness to parents.” He asked: “Then what?” He said: “Jihad in the cause of Allah.”",
           ra("ʿAbdullāh ibn Masʿūd"), [("bukhari", 527), ("muslim", 85)], "The first answer is the one to remember: prayer on time.")
    ph2 = H("^The Prophet ﷺ asked: “What do you think if there were a river at the door of one of you in which he bathed five times every day; would any dirt remain on him?” They said, “No dirt would remain.” He said: “That is like the five prayers; by them Allah erases sins.”",
            ra("Abū Hurayrah"), [("bukhari", 528), ("muslim", 667)])
    o.append(verse_card(pv, "prayer-times") + hadith_card(ph, "prayer-times") + hadith_card(ph2, "prayer-times"))
    o.append('''</div></section>
<section class="block prose reveal"><h2>About these times</h2>
<p>Times come from the free <a href="https://aladhan.com/prayer-times-api" target="_blank" rel="noopener">AlAdhan prayer-times service</a>. Countries and communities use different calculation methods, and some masjids follow their own timetable. If the times here differ from your local masjid, please follow your masjid. Your chosen city is saved only in this browser.</p></section>''')
    o.append(foot())
    return "".join(o)


def references_page():
    rows = {}
    def add(key, kind, label, url, excerpt, grade, slug):
        r = rows.setdefault(key, dict(kind=kind, label=label, url=url, excerpt=excerpt, grade=grade, pages=[]))
        if slug not in r["pages"]:
            r["pages"].append(slug)
    for t in TOPICS:
        for v in t["verses"]:
            add(("q", v["ref"]), "Qur’an", quran_label(v["ref"]), quran_url(v["ref"]), v["en"], "partial verse" if not v["arabic"] else "", t["slug"])
        for h in t["hadith"]:
            colls = {c for c, _ in h["srcs"] if c}
            g = h.get("grade") or ("Ṣaḥīḥ" if colls and colls <= {"bukhari", "muslim"} else "")
            lab = " / ".join((COLLECTIONS[c] + " " + str(n)) if c else str(n) for c, n in h["srcs"])
            first = h["srcs"][0]
            url = f"https://sunnah.com/{first[0]}:{first[1]}" if first[0] else ""
            add(("h",) + tuple(h["srcs"]), "Hadith", lab, url, h["en"].lstrip("^"), g, t["slug"])
    for k, r in REMEDIES.items():
        for sr in r["srcs"]:
            if sr[0] == "quran":
                add(("q", sr[1]), "Qur’an", quran_label(sr[1]), quran_url(sr[1]), r.get("en", r["title"]), "", "remedies-" + k)
            else:
                lab = COLLECTIONS.get(sr[0], "") + " " + str(sr[1])
                add(("r", k, sr), "Dhikr / action source", lab, f"https://sunnah.com/{sr[0]}:{sr[1]}", r.get("quote") or r["title"], r.get("grade", ""), "remedies-" + k)
    for k, d in DUAS.items():
        for sr in d["srcs"]:
            if sr[0] != "quran":
                lab = COLLECTIONS.get(sr[0], "") + " " + str(sr[1]) if sr[0] else str(sr[1])
                url = f"https://sunnah.com/{sr[0]}:{sr[1]}" if sr[0] else ""
                add(("d", k, sr), "Du’a source", lab, url, d["title"] + ": " + d["en"], d.get("grade", ""), "duas")
    trs = []
    for i, (key, r) in enumerate(sorted(rows.items(), key=lambda kv: (kv[1]["kind"], kv[1]["label"]))):
        pages = ", ".join(f'<a href="{p.split("-")[0] if p.startswith("remedies") else p}.html">{p}</a>' if not p.startswith("remedies") else "to-feel-better: " + p.split("-", 1)[1] for p in r["pages"])
        lab = f'<a href="{r["url"]}" target="_blank" rel="noopener">{esc(r["label"])}</a>' if r["url"] else esc(r["label"])
        ex = esc(r["excerpt"][:170] + ("…" if len(r["excerpt"]) > 170 else ""))
        trs.append(f'<tr><td><input type="checkbox" class="rv" data-k="{i}-{esc(r["label"])}" aria-label="Mark reviewed"></td><td>{r["kind"]}</td><td>{lab}</td><td class="ex">{ex}</td><td>{esc(r["grade"])}</td><td>{pages}</td></tr>')
    o = [head("All references · Sakīna", "Every Qur’an verse and hadith used on Sakīna, for reviewers.", 45)]
    o.append(f'''<section class="hero topic-hero"><a class="crumb" href="about.html">← About</a><p class="eyebrow">For reviewers</p>
<h1 class="split">Every reference, in one place</h1>
<p class="tagline">{len(rows)} references to check</p>
<p class="intro">Tick each row after checking the wording and the source. Ticks are saved only in this browser, so use it as a personal checklist, and print the page if you need a record. Wording shown is the English used on the site.</p>
<p class="rv-count" id="rvc"></p></section>
<section class="block"><div class="tablewrap reveal"><table class="reftable"><thead><tr><th>✓</th><th>Type</th><th>Reference</th><th>English on site</th><th>Grade</th><th>Used on</th></tr></thead><tbody>{"".join(trs)}</tbody></table></div></section>''')
    o.append(foot())
    return "".join(o)


def main():
    if os.path.isdir(OUT):
        for f in os.listdir(OUT):
            if f.endswith(".html"):
                os.remove(os.path.join(OUT, f))
    os.makedirs(OUT, exist_ok=True)
    pages = {"index.html": index_page(), "duas.html": duas_page(), "about.html": about_page(), "references.html": references_page(), "prayer-times.html": prayer_page()}
    for i, t in enumerate(TOPICS):
        pages[f'{t["slug"]}.html'] = topic_page(i, t)
    for name, content in pages.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)
    print("built", len(pages), "pages")


if __name__ == "__main__":
    main()

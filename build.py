#!/usr/bin/env python3
"""Build The Voice of Becoming Studio site.

HOW TO UPDATE (no other tools needed, plain Python 3):
  New article : add a .md file to content/posts/ (copy an existing one; keep the --- header with
                title, date YYYY-MM-DD, summary, tag). Then run:  python3 build.py
  New talk    : add an entry to data/events.json, then run:  python3 build.py
  Then republish the site/ folder.
Markdown supported in posts: paragraphs, ## headings, 1. / - lists, **bold**, *italic*, [text](url).
"""
import html, json, os, re, datetime, glob
import hashlib as _hl

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSET_V = _hl.md5(b"".join(open(os.path.join(ROOT, "site", "assets", f), "rb").read() for f in ("styles.css", "site.js"))).hexdigest()[:8]
SITE = os.path.join(ROOT, "site")
TODAY = datetime.date.today()

KIT = "/newsletter.html#join"  # v23: signup form lives on newsletter.html (#join); /letter/ redirects there
KIT_ACTION = "https://app.kit.com/forms/10090058/subscriptions"  # Kit form uid 042d6cefac (4 AM / Articulation Gap workbook)
TOPMATE_CALL = "https://topmate.io/fathima_samreen/504857"
TOPMATE = "https://topmate.io/fathima_samreen"
EMAIL = "fathima@voiceofbecoming.com"
SITE_URL = os.environ.get("SITE_URL", "https://voiceofbecoming.com").rstrip("/")  # preview: SITE_URL=https://vob-site.sites.tab.bot python3 build.py

SOCIALS = [
    ("Instagram · @thediaryoffathima", "https://instagram.com/thediaryoffathima", "ig"),
    ("Instagram · @thevoiceofbecomingstudio", "https://instagram.com/thevoiceofbecomingstudio", "ig"),
    ("LinkedIn · Fathima Samreen", "https://www.linkedin.com/in/fathimasamreen", "li"),
    ("YouTube · The Voice of Becoming", "https://www.youtube.com/@thevoiceofbecomingstudio", "yt"),
    ("Substack · The Voice of Becoming", "https://thevoiceofbecoming.substack.com/", "ss"),
]
ICONS = {
 "ig": '<path d="M12 2.2c3.2 0 3.6 0 4.8.1 3.3.1 4.8 1.7 4.9 4.9.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-3.3-.1-4.8-1.7-4.9-4.9C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8C2.4 3.9 3.9 2.4 7.2 2.3 8.4 2.2 8.8 2.2 12 2.2zm0 4.9a4.9 4.9 0 1 0 0 9.8 4.9 4.9 0 0 0 0-9.8zm0 8.1a3.2 3.2 0 1 1 0-6.4 3.2 3.2 0 0 1 0 6.4zm5.1-9.4a1.2 1.2 0 1 0 0 2.3 1.2 1.2 0 0 0 0-2.3z"/>',
 "li": '<path d="M20.4 2H3.6C2.7 2 2 2.7 2 3.6v16.8c0 .9.7 1.6 1.6 1.6h16.8c.9 0 1.6-.7 1.6-1.6V3.6c0-.9-.7-1.6-1.6-1.6zM8 19H5V9.5h3V19zM6.5 8.2a1.7 1.7 0 1 1 0-3.5 1.7 1.7 0 0 1 0 3.5zM19 19h-3v-4.6c0-1.1 0-2.5-1.5-2.5S12.8 13 12.8 14.3V19h-3V9.5h2.8v1.3h.1c.4-.7 1.4-1.5 2.8-1.5 3 0 3.6 2 3.6 4.6V19z"/>',
 "yt": '<path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12a31 31 0 0 0 .5 4.8 3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8zM9.7 15V9l5.8 3-5.8 3z"/>',
 "ss": '<path d="M3 3h18v2.5H3zm0 4.8h18v2.5H3zM3 12.6h18V22l-9-5-9 5z"/>',
 "tm": '<path d="M19 4h-1V2h-2v2H8V2H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 16H5V10h14v10zM7 12h5v5H7z"/>',
 "mail": '<path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4.2-8 5-8-5V6l8 5 8-5v2.2z"/>',
}
def icon(k): return '<svg viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % ICONS[k]

NAV = [("Home", "index.html"), ("Work with me", "authority/"), ("Newsletter", "newsletter.html"), ("About", "about.html")]

def esc(s): return html.escape(s, quote=True)

NL_OG = "/assets/og-newsletter-4am.jpg"  # v25: newsletter link preview = the 4 AM hero (1200x630 jpg); og.png stays for every other page

def og_tags(img=None):
    if not img:
        return '<meta property="og:image" content="%s/og.png">' % SITE_URL
    u = SITE_URL + img
    return ('<meta property="og:image" content="{u}">\n<meta property="og:image:secure_url" content="{u}">\n'
            '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
            '<meta property="og:image:type" content="image/jpeg">\n<meta property="og:image:alt" content="4 AM. For Muslim women who build in the quiet.">').format(u=u)

def tw_tags(img=None):
    t = '<meta name="twitter:card" content="summary_large_image">'
    return t + ('\n<meta name="twitter:image" content="%s%s">' % (SITE_URL, img) if img else "")

def page(title, desc, body, current, rel="", path="index.html", bodycls="", og_img=None):
    bodyattr = ' class="%s"' % bodycls if bodycls else ""
    _pf = ("anton", "bric-400", "inst-italic")
    preloads = "\n".join('<link rel="preload" href="%sassets/fonts/%s.woff2" as="font" type="font/woff2" crossorigin>' % (rel, f) for f in _pf)
    nav = "".join('<a href="%s%s"%s>%s</a>' % (rel, h, ' aria-current="page"' if h == current else "", n) for n, h in NAV)
    cta = '<a class="btn" href="%sauthority/#apply">Apply</a>' % rel
    socials = "".join('<li><a href="%s" target="_blank" rel="noopener">%s<span>%s</span></a></li>' % (u, icon(k), esc(n)) for n, u, k in SOCIALS)
    socials += '<li><a href="mailto:%s">%s<span>%s</span></a></li>' % (EMAIL, icon("mail"), EMAIL)
    links = "".join('<li><a href="%s%s">%s</a></li>' % (rel, h, n) for n, h in NAV)
    full_title = title if "Voice of Becoming" in title else "%s · The Voice of Becoming Studio" % title
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#141414">
<meta property="og:type" content="website">
<meta property="og:site_name" content="The Voice of Becoming Studio">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
{og_tags(og_img)}
<meta property="og:url" content="{SITE_URL}/{path}">
{tw_tags(og_img)}
<link rel="canonical" href="{SITE_URL}/{path}">
<link rel="icon" href="{rel}assets/img/favicon.png">
{preloads}
<link rel="stylesheet" href="{rel}assets/styles.css?v={ASSET_V}">
<script>document.documentElement.classList.add("js");setTimeout(function(){{if(!window.__vob)document.documentElement.classList.remove("js")}},4000)</script>
</head>
<body{bodyattr}>
<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"></div>
<header class="site-header">
 <div class="wrap bar">
  <a class="brand" href="{rel}index.html" aria-label="The Voice of Becoming Studio, home"><span class="brand-mark">VOB</span><span>The Voice of Becoming<small>Studio · Fathima Samreen</small></span></a>
  <nav class="nav" aria-label="Main">{nav}{cta}</nav>
  <details class="menu"><summary>Menu</summary><nav aria-label="Main (mobile)">{nav}{cta}</nav></details>
 </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
 <div class="wrap">
  <div class="foot-cta">
   <div class="foot-cta-copy">
    <span class="eyebrow">4 AM · The letter</span>
    <p class="foot-cta-line">A weekly letter for Muslim women ready to be <span class="serif">seen for what they know.</span></p>
    <p class="small">For Muslim women who build in the quiet. Join 4 AM and get the free Articulation Gap workbook.</p>
   </div>
   <a class="btn" href="{KIT}">Join 4 AM</a>
  </div>
  <div class="foot-grid">
   <div class="foot-brand">
    <a class="brand" href="{rel}index.html"><span class="brand-mark">VOB</span><span>The Voice of Becoming Studio<small>Fathima Samreen · Ghostwriter, brand &amp; book strategist</small></span></a>
    <p class="foot-mission">Helping Muslim women executives turn their expertise into a voice people follow. From Warangal, for leaders everywhere.</p>
   </div>
   <div class="foot-col">
    <h2>Pages</h2>
    <ul class="foot-links">{links}</ul>
   </div>
   <div class="foot-col">
    <h2>Connect</h2>
    <ul class="socials">{socials}</ul>
   </div>
   <div class="foot-col">
    <h2>Contact</h2>
    <ul class="foot-links">
     <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
     <li><a href="{KIT}">Join 4 AM</a></li>
    </ul>
    <p class="small foot-loc">Warangal, India · working worldwide</p>
   </div>
  </div>
 </div>
 <div class="foot-bottom"><div class="wrap foot-bottom-in"><span>© {TODAY.year} The Voice of Becoming Studio. All rights reserved.</span><span><a href="mailto:{EMAIL}">{EMAIL}</a></span></div></div>
</footer>
<script src="{rel}assets/site.js?v={ASSET_V}" defer></script>
</body>
</html>
"""

# ---------- markdown (small, safe subset) ----------
def inline(s):
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: '<a href="%s"%s>%s</a>' % (m.group(2), ' target="_blank" rel="noopener"' if m.group(2).startswith("http") else "", m.group(1)), s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", s)
    return s

def md(text):
    out, blocks = [], re.split(r"\n\s*\n", text.strip())
    for b in blocks:
        lines = [l.rstrip() for l in b.strip().split("\n")]
        if lines[0].startswith("## "):
            out.append("<h2>%s</h2>" % inline(lines[0][3:]))
            rest = [l for l in lines[1:] if l]
            if rest: out.append("<p>%s</p>" % "<br>".join(inline(l) for l in rest))
        elif all(re.match(r"\d+\.\s", l) for l in lines):
            out.append("<ol>%s</ol>" % "".join("<li>%s</li>" % inline(re.sub(r"^\d+\.\s", "", l)) for l in lines))
        elif all(re.match(r"[-*]\s", l) for l in lines):
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(l[2:]) for l in lines))
        else:
            out.append("<p>%s</p>" % "<br>".join(inline(l) for l in lines))
    return "\n".join(out)

def load_posts():
    posts = []
    for f in sorted(glob.glob(os.path.join(ROOT, "content", "posts", "*.md"))):
        raw = open(f, encoding="utf-8").read()
        m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
        if not m: continue
        meta = dict((k.strip(), v.strip()) for k, v in (l.split(":", 1) for l in m.group(1).split("\n") if ":" in l))
        if meta.get("draft", "").lower() in ("true", "yes"): continue
        meta["slug"] = os.path.splitext(os.path.basename(f))[0]
        meta["body"] = m.group(2)
        meta["d"] = datetime.date.fromisoformat(meta["date"])
        posts.append(meta)
    return sorted(posts, key=lambda p: p["d"], reverse=True)

def nice(d): return d.strftime("%-d %B %Y")
def read_mins(t): return max(1, round(len(t.split()) / 200))

# ---------- shared blocks ----------
def workbook_band(rel=""):
    return f"""<section><div class="wrap"><div class="cta-band">
 <div><span class="eyebrow">Free workbook</span>
 <h2 class="display">Close your<br>articulation gap.</h2>
 <p class="lead">Five stories you already own, turned into post ideas and a profile that speaks for you while you do your job.</p>
 <div class="btns"><a class="btn" href="{KIT}">Get the free workbook</a><a class="btn ghost" href="{rel}newsletter.html">What's inside</a></div></div>
 <img src="{rel}assets/img/workbook.webp" alt="Cover of The Articulation Gap workbook" width="600" height="848" loading="lazy">
</div></div></section>"""

TESTIMONIALS = [
 ("The ideas and experiences in the book were mine, but she helped me shape them into something people could truly connect with … she helped turn the book into a complete authority platform.", "Parvez Siraj", "VP, Lupin · author &amp; speaker", "parvez.jpg"),
 ("We hired Fathima and her team as our marketing manager. She really helped us find our brand voice and set us up for success.", "Negar Farahmand", "CEO, AHX Partners · ex-Accenture MD", "negar.jpg"),
 ("She takes the time to carefully understand the objectives of each piece of content … She has been a true gift to our team, and our growth on social media.", "Bhavna Toor", "Founder &amp; CEO, Shenomics", "bhavna.webp"),
 ("I thank Fathima Samreen, my ghostwriter, who has done an exceptional job of framing the entire story so beautifully and deftly weaving my thoughts into words.", "Akhauri Mritunjay Kumar", "Author, <em>Rekha Dares to Dream Again</em> (from the book's acknowledgements)", None),
 ("Fathima has done a wonderful job of designing and optimizing my LinkedIn profile … I strongly recommend her as a dedicated, professional and capable artist.", "Dr. Sujata Sinha", "LinkedIn profile client", None),
 ("She found the perfect balance between content creation and Art. She possesses a unique way with words and an insatiable passion for writing.", "Shijohn Williams", "Client", None),
]
def testimonials(rel="", n=6):
    cards = []
    for q, who, role, img in TESTIMONIALS[:n]:
        face = '<img src="%sassets/img/%s" alt="" width="48" height="48">' % (rel, img) if img else '<span class="initial" aria-hidden="true">%s</span>' % ("".join(w[0] for w in re.sub(r"&amp;|Dr\.", "", who).split()[:2]))
        cards.append(f'<figure class="card quote"><blockquote>{q}</blockquote><figcaption>{face}<span><strong>{who}</strong>{role}</span></figcaption></figure>')
    return '<div class="grid g3 quotes">%s</div>' % "".join(cards)

# ---------- pages ----------
def home(posts):
    cards = "".join(f'<a class="post-card" href="blog/{p["slug"]}.html"><span class="meta"><span class="tag">{esc(p.get("tag","Article"))}</span> · {nice(p["d"])}</span><h2>{esc(p["title"])}</h2><p>{esc(p["summary"])}</p><span class="more red">Read the article →</span></a>' for p in posts[:2])
    read_more = f"""<section id="articles"><div class="wrap"><div class="section-head"><span class="eyebrow">Read more</span><h2 class="display">From <span class="red">the journal.</span></h2></div><div class="grid g2">{cards}</div></div></section>""" if cards else ""
    body = f"""
<section class="hero"><div class="wrap hero-grid">
 <div class="hero-copy">
  <span class="eyebrow">For Muslim women leaders</span>
  <h1 class="display">Muslim women leaders: <span class="red">be known for what you know.</span></h1>
  <p class="lead">I build your voice, your profile, your book and your audience, so the right clients find you.</p>
  <div class="btns"><a class="btn" href="authority/#retainer">See the two offers</a><a class="btn ghost" href="newsletter.html">Get the free workbook</a></div>
  <div class="award-chip"><b>SIWAA 2025</b> Changemaker Award · South India Women Achievers</div>
 </div>
 <div class="hero-photo hero-cut"><img src="assets/img/fathima-hero-cutout.webp" alt="Fathima Samreen, founder of The Voice of Becoming Studio" width="872" height="1055" fetchpriority="high"></div>
</div>
<div class="wordmark" aria-hidden="true"><span>Voice of Becoming</span></div>
<div class="wordmark wm-o" aria-hidden="true"><span>Voice of Becoming</span></div>
</section>
<div class="stats" role="list">
 <div role="listitem"><strong data-count="7" data-suffix="+">7+</strong><span>years ghostwriting</span></div>
 <div role="listitem"><strong data-count="3">3</strong><span>countries</span></div>
 <div role="listitem"><strong data-count="2019" data-from="2000">2019</strong><span>writing books since</span></div>
 <div role="listitem"><strong data-count="4">4</strong><span>pillars of authority</span></div>
</div>
<div class="marquee" aria-hidden="true"><div class="mq-row mq-co"><div class="mq-track"><span><em>Lupin</em> <b>&middot;</b> Director <b class="ar">&rarr;</b> VP</span><i>✦</i><span><em>Shenomics</em> <b>&middot;</b> 36K <b class="ar">&rarr;</b> 105K followers</span><i>✦</i><span><em>AHX Partners</em> <b>&middot;</b> +100 paid members</span><i>✦</i><span><em>Lupin</em> <b>&middot;</b> Director <b class="ar">&rarr;</b> VP</span><i>✦</i><span><em>Shenomics</em> <b>&middot;</b> 36K <b class="ar">&rarr;</b> 105K followers</span><i>✦</i><span><em>AHX Partners</em> <b>&middot;</b> +100 paid members</span><i>✦</i><span><em>Lupin</em> <b>&middot;</b> Director <b class="ar">&rarr;</b> VP</span><i>✦</i><span><em>Shenomics</em> <b>&middot;</b> 36K <b class="ar">&rarr;</b> 105K followers</span><i>✦</i><span><em>AHX Partners</em> <b>&middot;</b> +100 paid members</span><i>✦</i></div></div><div class="mq-row rev"><div class="mq-track"><span>Strategy</span><i>✦</i><span>Psychology</span><i>✦</i><span>Narrative</span><i>✦</i><span>Executive Presence</span><i>✦</i><span>Strategy</span><i>✦</i><span>Psychology</span><i>✦</i><span>Narrative</span><i>✦</i><span>Executive Presence</span><i>✦</i><span>Strategy</span><i>✦</i><span>Psychology</span><i>✦</i><span>Narrative</span><i>✦</i><span>Executive Presence</span><i>✦</i></div></div></div>

<section class="sand"><div class="wrap">
 <div class="section-head"><span class="eyebrow">Two ways to work together</span><h2 class="display">Pick <span class="red">your level.</span></h2></div>
 <div class="grid g2 offers">
  <article class="card offer">
   <span class="eyebrow">Ongoing</span>
   <h3>The Visibility Retainer</h3>
   <p class="offer-price">$700 a month · 3 months minimum</p>
   <ul class="checks">
    <li>Month 1 Foundation: positioning, messaging, LinkedIn profile, 9 content ideas</li>
    <li>Every month: 20 pieces of content, about 5 a week</li>
    <li>A monthly review and a plan for the next month</li>
   </ul>
   <a class="btn" href="authority/#retainer">See the Visibility Retainer</a>
  </article>
  <article class="card offer">
   <span class="eyebrow">Fully customised</span>
   <h3>Complete Authority</h3>
   <p class="offer-price">Application only · 6 months to 1 year · 3 clients max</p>
   <ul class="checks">
    <li>Strategy, profile and brand</li>
    <li>Monthly content, your email list and community</li>
    <li>Your book, and your stage</li>
   </ul>
   <a class="btn ghost" href="authority/#authority">See Complete Authority</a>
  </article>
 </div>
</div></section>

<section class="feat feat-r"><div class="feat-photo" style="--fp:50% 5%"><img src="assets/img/fathima-desk.jpg" alt="Fathima Samreen writing at her desk" width="640" height="1137" loading="lazy"></div>
<div class="wrap feat-grid">
<div class="feat-copy">
  <span class="eyebrow">Who I help</span>
  <h2 class="display">Brilliant inside. <span class="red">Invisible outside.</span></h2>
  <p class="lead">Inside her company, everyone knows what she is worth. Outside, almost nobody can see it. I call that the articulation gap. Closing it is my work.</p>
  <p>I work with Muslim women leaders, senior executives and founders who:</p>
  <ul class="checks">
   <li>Have lived enough to know shortcuts don't work</li>
   <li>Don't want to sound like everyone else online</li>
   <li>Care more about clarity than constant visibility</li>
   <li>Feel there is a book inside them, but haven't named it yet</li>
   <li>Want their work to outlive platforms and algorithms</li>
  </ul>
 </div>
</div></section>

<section><div class="wrap">
 <div class="section-head"><span class="eyebrow">Results</span><h2 class="display">Real leaders. <span class="red">Real results.</span></h2></div>
 <div class="grid g3">
  <div class="card result"><span class="meta">Lupin</span><span class="big">Director → VP</span><p>A book, a weekly newsletter and a profile that made a leader's expertise visible. 4,500+ newsletter subscribers and 800+ community members.</p></div>
  <div class="card result"><span class="meta">Shenomics · Bhavna Toor</span><span class="big">36K → 105K</span><p>LinkedIn followers for Bhavna, over 14 to 18 months of partnership, with the profile updated each time her offer evolved.</p></div>
  <div class="card result"><span class="meta">AHX Partners</span><span class="big">+100</span><p>Paid members added to a founder-led community, through strategy, content, design and positioning.</p></div>
 </div>
 <div class="btns"><a class="btn ghost" href="authority/#results">All results and the full offers</a></div>
</div></section>

<section><div class="wrap">
 <div class="section-head"><span class="eyebrow">What people say</span><h2 class="display">In their <span class="red">words.</span></h2></div>
 {testimonials("", 6)}
 <p class="swipe-hint">Swipe for more →</p>
</div></section>

{workbook_band("")}

<section class="sand feat feat-l"><div class="feat-photo" style="--fp:50% 8%"><img src="assets/img/fathima-standing.jpg" alt="Fathima Samreen in a maroon abaya, holding a book" width="754" height="1024" loading="lazy"></div>
<div class="wrap feat-grid">
 <div class="feat-copy">
  <span class="eyebrow">4 AM · The newsletter</span>
  <h2 class="display">A letter for Muslim women who build <span class="red">in the quiet.</span></h2>
  <p class="lead">You know a lot, and too few people see it yet. Get 4 AM, my weekly letter on voice and authority, so you are known for your work without losing your haya.</p>
  <div class="btns"><a class="btn" href="{KIT}">Join 4 AM</a><a class="btn ghost" href="newsletter.html">About 4 AM</a></div>
 </div>
</div></section>
{read_more}
"""
    return page("The Voice of Becoming Studio · Fathima Samreen, Ghostwriter for Muslim Women Executives",
                "Fathima Samreen builds the voice, profile, book and audience of Muslim women leaders, so the right clients find them.", body, "index.html", "", "")

def about():
    body = f"""
<section class="page-head feat feat-r"><div class="feat-photo" style="--fp:50% 8%"><img src="assets/img/fathima-standing.jpg" alt="Fathima Samreen in a maroon abaya, holding a book" width="754" height="1024" fetchpriority="high"></div>
<div class="wrap feat-grid">
 <div class="feat-copy"><span class="eyebrow">About</span><h1 class="display">The writer behind <span class="red">the leaders' words.</span></h1>
 <p class="lead">I'm Fathima Samreen, founder of The Voice of Becoming Studio. A self-taught writer from Warangal, Telangana, working with Muslim women leaders from home.</p></div>
</div></section>

<section class="sand"><div class="wrap prose" style="max-width:760px">
 <p>For more than 7 years I have ghostwritten for founders and leaders across 3 countries, and I have been writing books with leaders since 2019.</p>
 <p>Today I work with Muslim women executives. Inside their companies everyone knows what they are worth. Outside, almost nobody can see it. I call that <strong>the articulation gap</strong>. Closing it is my work.</p>
 <p>I am not a coach. I am a ghostwriter, a brand and book strategist and an authority strategist. Nothing goes out without your yes.</p>
 <p>I'm also writing my own book, <strong>What's Your Aukaath?</strong> Aukaath, to me, is knowing your worth and owning your place.</p>
 <p>SIWAA Award 2025, Changemaker category, South India Women Achievers Awards.</p>
 <div class="btns"><a class="btn" href="authority/">See the two offers</a><a class="btn ghost" href="newsletter.html">Join 4 AM</a></div>
</div></section>
"""
    return page("About · Fathima Samreen", "About Fathima Samreen, ghostwriter, brand and book strategist for Muslim women leaders, from Warangal.", body, "about.html", "", "about.html")

def authority():
    rel = "../"
    FORM_EP = "https://formsubmit.co/236e3bcab1127516384d8fdd66449ff6"
    pills = [("Voice", "Voice and content"), ("Book", "Book"), ("List", "Email list"), ("Community", "Community"), ("Stage", "Stage and speaking")]
    pill_html = "".join(f'<label class="ap-pill"><input type="checkbox" name="Matters most" value="{v}"><span>{t}</span></label>' for v, t in pills)
    def radios(name, opts, req=True):
        return "".join(f'<label class="ap-pill"><input type="radio" name="{name}" value="{o}"{" required" if req else ""}><span>{o}</span></label>' for o in opts)
    def step(n, t, items):
        return f'<article class="card"><span class="num">{n}</span><h3>{t}</h3><ul class="checks">' + "".join(f"<li>{i}</li>" for i in items) + "</ul></article>"
    month1 = [
        ("Positioning", ["Who you help and what you are known for", "Your 3 core topics", "Your audience, in one paragraph"]),
        ("Messaging", ["Your promise line", "Your About section, in your voice", "Your services in plain words", "A tone guide: how you sound"]),
        ("LinkedIn profile", ["Headline rewrite", "About, Experience and Skills cleaned up", "Custom banner and profile picture", "2 Featured cards and 3 services graphics"]),
        ("Ideas and handover", ["9 content ideas", "A handover PDF guide", "One round of changes"]),
    ]
    m1 = "".join(f'<article class="card"><h3>{t}</h3><ul class="checks">' + "".join(f"<li>{i}</li>" for i in items) + "</ul></article>" for t, items in month1)
    monthly = [
        ("20 pieces, about 5 a week", "Carousels, videos, text and image posts. The mix depends on what is working for you. We start with 4 carousels and 4 videos, and adjust each month."),
        ("Videos", "If you record, we edit and caption them. If you'd rather not be on camera, we create them from stock footage and design tools, in your voice."),
        ("A monthly review", "What worked, what to change, and what comes next."),
    ]
    mo = "".join(f'<article class="card"><h3>{t}</h3><p>{d}</p></article>' for t, d in monthly)
    scope = [
        ("01", "Strategy", ["Your voice and positioning", "A 6-month plan for your book, content, list and stage", "Your proof, gathered and used"]),
        ("02", "Profile and brand", ["LinkedIn and Instagram: headline, banner, picture and Featured", "Your brand look and template set", "A simple page with an application form"]),
        ("03", "Content, every month", ["Weekly videos and reels, scripted in your voice", "LinkedIn posts, with comments on others' posts", "Carousels, quote cards and your newsletter"]),
        ("04", "Book", ["Core message and outline", "Voice notes and interviews, then drafting in your voice", "Editing, proofreading, cover and layout", "Publishing route, upload and launch", "Scholar review for anything Islamic"]),
        ("05", "List and community", ["Email setup and a welcome sequence", "A lead magnet", "An optional community"]),
        ("06", "Stage", ["A speaker one-pager and your topics", "A pitch list of podcasts and events, which you send yourself"]),
    ]
    sc = "".join(f'<article class="card"><span class="num">{n}</span><h3>{t}</h3><ul class="checks">' + "".join(f"<li>{i}</li>" for i in items) + "</ul></article>" for n, t, items in scope)
    body = f"""
<section class="page-head ax-head"><div class="wrap ax-hero">
 <div class="ax-photo"><img src="{rel}assets/img/fathima-arms-folded.webp" alt="Fathima Samreen in a maroon coat, arms folded" width="723" height="1146" fetchpriority="high" decoding="async"></div>
 <div class="ax-copy">
 <span class="eyebrow">Work with me</span>
 <h1 class="display">Muslim women leaders: <span class="red">be known for what you know.</span></h1>
 <p class="lead">I build your voice, your profile, your book and your audience, so the right clients find you. Two ways to work together, depending on where you are.</p>
 <div class="btns"><a class="btn" href="#retainer">Visibility Retainer</a><a class="btn ghost" href="#authority">Complete Authority</a></div>
 </div>
</div></section>

<section class="sand" id="retainer"><div class="wrap">
 <span class="eyebrow">You lead with knowledge</span>
 <h2 class="display">You've built the expertise. <span class="red">Let me build how you're seen.</span></h2>
 <p class="lead">Your profile may be outdated, your headline unclear and your Featured section silent. Strategy, words and design, handled for Muslim women leaders.</p>
 <div class="cta-band" style="margin:34px 0">
  <div><span class="eyebrow">The Visibility Retainer</span>
  <h3 class="display">You share your voice. <span class="serif">I turn it into visibility.</span></h3>
  <p class="lead">You answer a short questionnaire. I shape your positioning, write your messaging and design your look.</p></div>
 </div>
 <div class="section-head"><span class="eyebrow">Month 1 · Foundation</span><h3 class="display">Done for you, <span class="red">in 7 working days.</span></h3><p class="lead">Delivered within 7 working days of your questionnaire.</p></div>
 <div class="grid g2">{m1}</div>
 <div class="section-head" style="margin-top:56px"><span class="eyebrow">Every month, from month 1</span><h3 class="display">Consistent <span class="red">visibility.</span></h3></div>
 <div class="grid g3">{mo}</div>
 <div class="card offer-box" style="margin-top:34px">
  <p class="offer-price">$700 a month · 3 months minimum · limited spots</p>
  <p>Month 1 includes the Foundation. Every month after that is the cycle above.</p>
  <p class="small">Not included: book work (that's Complete Authority). We don't promise results, leads or sales.</p>
  <a class="btn btn-xl" href="#apply">Apply for the Visibility Retainer</a>
 </div>
</div></section>

<section id="authority"><div class="wrap">
 <span class="eyebrow">Fully customised</span>
 <h2 class="display">Complete Authority, <span class="red">built around you.</span></h2>
 <p class="lead">We plan your book and your content together. 6 months to 1 year minimum. 3 clients at a time. Application only.</p>
 <div class="grid g3" style="margin-top:30px">{sc}</div>
 <div class="card offer-box" style="margin-top:34px">
  <p class="small">No result promises. We build the work; what it brings depends on you, your offer and your follow-up.</p>
  <a class="btn btn-xl" href="#apply">Apply for Complete Authority</a>
 </div>
</div></section>

<section class="sand" id="results"><div class="wrap">
 <div class="section-head"><span class="eyebrow">Results</span><h2 class="display">Real leaders. <span class="red">Real results.</span></h2><p class="lead">Every leader starts at a different step. Here is what we built together, and what it did.</p></div>
 <div class="grid g3 ax-res">
  <article class="card ax-rc">
   <div class="ax-who"><img src="{rel}assets/img/parvez.jpg" alt="Parvez Siraj" width="56" height="56" loading="lazy"><div><strong>Parvez Siraj</strong><span>VP, Lupin · author &amp; speaker</span></div></div>
   <ol class="ax-eco" aria-label="Steps used: Voice, Book, List, Community, Stage"><li class="on">Voice</li><li class="on">Book</li><li class="on">List</li><li class="on">Community</li><li class="on">Stage</li></ol>
   <div class="ax-nums"><div><span class="big">Director → VP</span><p>at Lupin, via Chief of Staff</p></div><div><span class="big"><span class="ax-cn" data-count="4500">4,500</span>+</span><p>subscribers to his ASCEND newsletter</p></div><div><span class="big"><span class="ax-cn" data-count="800">800</span>+</span><p>members in his WhatsApp community</p></div></div><p class="ax-extra">And his second book launched to a ready audience.</p>
   <h3 class="ax-did">What we did</h3>
   <ul class="ax-tactics"><li><span class="ax-tag-s">Voice</span>LinkedIn content and profile optimisation</li><li><span class="ax-tag-s">Book</span>His first book, written together</li><li><span class="ax-tag-s">List</span>The weekly ASCEND newsletter, written and designed</li><li><span class="ax-tag-s">Community</span>Starting his WhatsApp community</li><li><span class="ax-tag-s">Stage</span>Talks and paid speaking</li></ul>
   <blockquote class="ax-rq">“She helped turn the book into a complete authority platform.”</blockquote>
  </article>
  <article class="card ax-rc">
   <div class="ax-who"><img src="{rel}assets/img/bhavna.webp" alt="Bhavna Toor" width="56" height="56" loading="lazy"><div><strong>Bhavna Toor</strong><span>Founder &amp; CEO, Shenomics</span></div></div>
   <ol class="ax-eco" aria-label="Steps used: Voice"><li class="on">Voice</li><li>Book</li><li>List</li><li>Community</li><li>Stage</li></ol>
   <div class="ax-nums"><div><span class="big">36K → <span class="ax-cn" data-count="105" data-from="36">105</span>K</span><p>LinkedIn followers, over 14 to 18 months together</p></div></div>
   <h3 class="ax-did">What we did</h3>
   <ul class="ax-tactics"><li><span class="ax-tag-s">Voice</span>LinkedIn profile optimisation, updated each time her offer evolved</li><li><span class="ax-tag-s">Voice</span>Content strategy and design, as her partner for over a year</li></ul>
   <blockquote class="ax-rq">“She has been a true gift to our team, and our growth on social media.”</blockquote>
  </article>
  <article class="card ax-rc">
   <div class="ax-who"><img src="{rel}assets/img/negar.jpg" alt="Negar Farahmand" width="56" height="56" loading="lazy"><div><strong>Negar Farahmand</strong><span>Ex-Accenture Managing Director · CEO, AHX Partners · Founder, The Portfolio Career Collective</span></div></div>
   <ol class="ax-eco" aria-label="Steps used: Voice"><li class="on">Voice</li><li>Book</li><li>List</li><li>Community</li><li>Stage</li></ol>
   <div class="ax-nums"><div><span class="big">+<span class="ax-cn" data-count="100">100</span></span><p>paid members added to her community</p></div></div>
   <h3 class="ax-did">What we did</h3>
   <ul class="ax-tactics"><li><span class="ax-tag-s">Voice</span>Voice strategy: her brand voice and positioning for senior professionals made redundant or at risk</li><li><span class="ax-tag-s">Voice</span>Content: strategy and LinkedIn content in her voice</li></ul>
   <blockquote class="ax-rq">“She really helped us find our brand voice and set us up for success.”</blockquote>
  </article>
 </div>
 <div style="margin-top:56px">{testimonials("../", 6)}</div>
</div></section>

<section><div class="wrap split">
 <div><span class="eyebrow">How we work</span><h2 class="display">Boutique, <span class="red">on purpose.</span></h2>
 <p class="lead">I don't promise a set number of clients or a full waitlist. Your offer and follow-up matter too. I build the trust that brings the right people to you.</p></div>
 <dl class="ax-how">
  <div><dt>3</dt><dd>Complete Authority: 3 clients at a time.</dd></div>
  <div><dt>3 mo</dt><dd>Visibility Retainer: 3 months minimum. Complete Authority: 6 months to 1 year.</dd></div>
  <div><dt>Me</dt><dd>Strategy, ideas and voice come from me. Nothing goes out without your yes.</dd></div>
 </dl>
</div></section>

<section id="apply" class="ap-sec"><div class="wrap ap-grid">
 <div class="ap-intro">
  <span class="eyebrow">Apply</span>
  <h2 class="display">Tell me about <span class="red">you.</span></h2>
  <p class="lead">Pick the offer that fits, and tell me why you're applying. I read every application myself.</p>
  <ol class="ap-next">
   <li><span><strong>You apply.</strong> About 2 minutes.</span></li>
   <li><span><strong>I read it myself.</strong> Every answer, personally.</span></li>
   <li><span><strong>If it fits,</strong> you hear from me within 3 working days with a time for one focused call.</span></li>
  </ol>
 </div>
 <div class="ap-card">
 <form class="ap-form" id="ap-form" action="{FORM_EP}" method="POST" data-ajax="{FORM_EP.replace('formsubmit.co/', 'formsubmit.co/ajax/')}">
  <input type="hidden" name="_subject" value="New Authority application">
  <input type="hidden" name="_template" value="table">
  <input type="hidden" name="_captcha" value="false">
  <input type="hidden" name="_next" value="https://voiceofbecoming.com/authority/?applied=1#apply">
  <input type="text" name="_honey" class="ap-hp" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div class="ap-row2">
   <label class="ap-f"><span>Full name *</span><input type="text" name="Full name" autocomplete="name" required maxlength="120"></label>
   <label class="ap-f"><span>Email *</span><input type="email" name="email" autocomplete="email" required maxlength="160"></label>
  </div>
  <label class="ap-f"><span>LinkedIn or website *</span><input type="text" name="LinkedIn or website" inputmode="url" placeholder="linkedin.com/in/yourname" required maxlength="300"></label>
  <label class="ap-f"><span>Current role and industry *</span><input type="text" name="Role and industry" placeholder="e.g. Founder, fintech" required maxlength="200"></label>
  <fieldset class="ap-set"><legend>Which offer are you applying for? *</legend><div class="ap-pills">{radios("Offer", ["Visibility Retainer", "Complete Authority", "Not sure yet"])}</div></fieldset>
  <label class="ap-f"><span>Why are you applying? *</span><textarea name="Why are you applying" rows="3" placeholder="A line or two is plenty." required maxlength="1200"></textarea></label>
  <label class="ap-f"><span>What do you want to be known for? *</span><textarea name="Wants to be known for" rows="3" placeholder="One or two lines is plenty." required maxlength="1200"></textarea></label>
  <fieldset class="ap-set" id="ap-matters"><legend>Which part matters most right now? *</legend><div class="ap-pills">{pill_html}</div><p class="ap-err" hidden>Pick at least one.</p></fieldset>
  <fieldset class="ap-set"><legend>Timeline *</legend><div class="ap-pills">{radios("Timeline", ["Now", "Next 3 months", "Just exploring"])}</div></fieldset>
  <fieldset class="ap-set"><legend>Are you ready for the minimum term of that offer? *</legend><div class="ap-pills">{radios("Ready for 6 months", ["Yes", "Want to know more first"])}</div></fieldset>
  <label class="ap-f"><span>Anything else? <em>(optional)</em></span><textarea name="Anything else" rows="2" maxlength="2000"></textarea></label>
  <button class="btn btn-xl ap-send" type="submit">Send my application</button>
  <p class="ap-fail small" role="alert" hidden>That didn't go through. Please try again, or email <a href="mailto:fathima@voiceofbecoming.com">fathima@voiceofbecoming.com</a>.</p>
 </form>
 <div class="ap-done" id="ap-done" tabindex="-1" hidden>
  <span class="ap-tick" aria-hidden="true"></span>
  <p class="ap-thanks">Thank you. I read every application personally. If it looks like a fit, you'll hear from me within 3 working days with a time for one focused call.</p>
  <p class="ap-sign serif">Fathima</p>
 </div>
 </div>
</div></section>
"""
    return page("Work with me · Visibility Retainer and Complete Authority", "Work with Fathima Samreen: the Visibility Retainer, from $700 a month, and Complete Authority, a custom program for Muslim women leaders. Apply here.", body, "authority/", rel, "authority/")

def stub(target, title):
    # v26: removed pages stay as redirects so old links land on a live page
    t = SITE_URL + "/" + target
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(title)} | Fathima Samreen</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{t}">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0; url={t}">
<script>location.replace("{t}");</script>
<style>body{{background:#141414;color:#F3E9DD;font-family:system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;margin:0}}a{{color:#F3E9DD}}</style></head>
<body><p>Taking you to <a href="{t}">the right page</a>.</p></body></html>
"""

def blog_index(posts):
    return stub("index.html#articles", "Articles")

def calendar(events=None):
    return stub("index.html", "Calendar")

def freebies():
    return stub("newsletter.html#join", "Freebies")

def article(p, posts):
    others = [o for o in posts if o["slug"] != p["slug"]][:2]
    more = ""
    if others:
        more = '<section class="sand"><div class="wrap" style="max-width:860px"><span class="eyebrow">Keep reading</span><div class="post-list">%s</div></div></section>' % "".join(
            f'<a class="post-card" href="{o["slug"]}.html"><span class="meta">{nice(o["d"])}</span><h2>{esc(o["title"])}</h2><p>{esc(o["summary"])}</p></a>' for o in others)
    body = f"""
<article><section><div class="wrap article">
 <a href="../index.html" class="meta" style="text-decoration:none">← Home</a>
 <p class="meta" style="margin-top:22px"><span class="tag">{esc(p.get("tag","Article"))}</span> · {nice(p["d"])} · {read_mins(p["body"])} min read</p>
 <h1>{esc(p["title"])}</h1>
 <p class="lead" style="margin-bottom:34px">{esc(p["summary"])}</p>
 <div class="prose">{md(p["body"])}</div>
 <div class="card" style="display:flex;gap:18px;align-items:center;margin-top:44px;flex-wrap:wrap">
  <img src="../assets/img/fathima-avatar.jpg" alt="" width="72" height="72" style="width:72px;height:72px;border-radius:50%;object-fit:cover">
  <div style="flex:1;min-width:220px"><strong>Fathima Samreen</strong><br><span class="small">Ghostwriter, brand &amp; book strategist and authority strategist. Founder, The Voice of Becoming Studio.</span></div>
  <a class="btn" href="{KIT}">Join 4 AM</a>
 </div>
</div></section></article>
{more}
"""
    return page(p["title"], p["summary"], body, "", "../", "blog/%s.html" % p["slug"])

def newsletter():
    body = f"""
<section class="am4 am4-nl" aria-label="4 AM, the newsletter"><span class="am4-glow" aria-hidden="true"></span>
<span class="am4-eb">The letter · Free workbook</span>
<div class="am4-stage">
 <p class="am4-word"><span class="am4-n">4</span><span class="am4-am">AM</span></p>
 <img class="am4-cut" src="assets/img/fathima-hero-cutout.webp" alt="Fathima Samreen" width="872" height="1055" fetchpriority="high">
 <div class="am4-copy"><div class="l"><p class="am4-tag">For Muslim women who build in the quiet.</p></div></div>
</div></section>
<section class="hero"><div class="wrap hero-grid">
 <div class="hero-copy">
  <span class="eyebrow">The newsletter · Free workbook</span>
  <h1 class="display">Get the free Articulation Gap <span class="red">workbook.</span></h1>
  <p class="lead">For Muslim women leaders and founders who know a lot and stay unseen. Start with 5 signature stories you already own, 30 LinkedIn post ideas and a profile checklist, so what you know becomes words people trust.</p>
  <div class="lt-card nl-join" id="join">
  <form id="lt-form" class="lt-form" method="POST" action="{KIT_ACTION}" data-kit="{KIT_ACTION}" novalidate>
   <label class="ap-f"><span>First name</span><input name="fields[first_name]" type="text" autocomplete="given-name" required placeholder="Your first name"></label>
   <label class="ap-f"><span>Email</span><input name="email_address" type="email" autocomplete="email" inputmode="email" required placeholder="you@example.com"></label>
   <p class="ap-err lt-err" hidden>Please add your first name and a valid email.</p>
   <button class="btn btn-xl lt-send" type="submit">Send me the workbook →</button>
   <p class="small nl-fine">Free. Add your email and it lands in your inbox, with 4 AM. Unsubscribe any time.</p>
   <p class="ap-fail lt-fail" hidden>That did not go through. Please try again in a moment.</p>
   <div class="lt-guard" hidden><p class="small">One quick check to confirm you are human:</p><iframe title="Quick check" loading="eager"></iframe></div>
  </form>
  <div id="lt-done" class="lt-done" tabindex="-1" hidden>
   <span class="ap-tick" aria-hidden="true"></span>
   <h2 class="lt-ch">You're <span class="serif">in.</span></h2>
   <p class="lt-thanks">Check your inbox now. Your Articulation Gap workbook is on its way. Tap the button in that email to download it.</p>
   <p class="small">Can't see it? Look in Promotions or Updates, and move it to Primary so the letters find you.</p>
   <p class="serif ap-sign">Fathima</p>
  </div>
  </div>
 </div>
 <div class="nl-mock" role="img" aria-label="A laptop screen showing a 4 AM letter from Fathima">
  <span class="nl-glow" aria-hidden="true"></span>
  <div class="lap"><div class="lap-lid"><span class="lap-cam" aria-hidden="true"></span><div class="lap-screen"><div class="mail">
   <div class="mail-bar"><i></i><i></i><i></i><span>Inbox</span></div>
   <div class="mail-head"><span class="mail-av">F</span><div class="mail-from"><b>Fathima Samreen</b><small>to you · 4:00 AM</small></div></div>
   <p class="mail-subj">4 AM · For Muslim women who build in the quiet</p>
   <div class="mail-body">
    <p class="mail-mark">4 AM</p>
    <p class="mail-h">Haya is not silence.</p>
    <p class="mail-p">It's 4 AM, the quiet hour before Fajr. The house is asleep, the chai is still hot, and this is when I write to you.</p>
    <p class="mail-p">This week: you can stay modest and still be known for what you know. Your expertise deserves a voice.</p>
    <p class="mail-sign">With love, Fathima</p>
   </div>
  </div></div></div>
  <div class="lap-base"><span></span></div></div>
 </div>
</div></section>
<section><div class="wrap">
 <div class="section-head"><span class="eyebrow">What you'll get</span><h2 class="display">In your <span class="red">inbox.</span></h2></div>
 <div class="grid g3">
  <div class="card"><span class="num">01</span><h3>Seen for what you know</h3><p>How to build authority in your own voice, without shouting and without shrinking. Haya is not silence.</p></div>
  <div class="card"><span class="num">02</span><h3>Write-this-down prompts</h3><p>Small prompts to turn what you know into posts, one line at a time, before the day takes over.</p></div>
  <div class="card"><span class="num">03</span><h3>From the strategist's desk</h3><p>What 7+ years of writing for leaders has taught me about voice and authority. You do the work, and leave the reach to Allah.</p></div>
 </div>
</div></section>
<section class="sand"><div class="wrap"><div class="signup">
 <img class="cover" src="assets/img/workbook.webp" alt="Cover of The Articulation Gap workbook" width="600" height="848" loading="lazy">
 <div><span class="eyebrow">Welcome gift</span><h2 class="display">Join 4 AM and get the <span class="red">workbook.</span></h2>
 <p class="lead">5 signature stories, 30 LinkedIn post ideas and a profile checklist, made for Muslim women ready to be seen for their work. It comes with your welcome email, free.</p>
 <a class="btn" href="#join" data-join>Send me the workbook</a></div>
</div></div></section>
"""
    return page("4 AM: the newsletter for Muslim women who build in the quiet", "4 AM, a weekly letter by Fathima Samreen for Muslim women leaders and founders who know a lot and stay unseen. Join and get the free Articulation Gap workbook: 5 signature stories, 30 LinkedIn post ideas and a profile checklist.", body, "newsletter.html", "", "newsletter.html", og_img=NL_OG)

def letter():
    # v23: /letter/ merged into newsletter.html; kept as a redirect so old links work
    t = SITE_URL + "/newsletter.html#join"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>The 4 AM Letter | Fathima Samreen</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{SITE_URL}/newsletter.html">
<meta name="description" content="4 AM, a weekly letter by Fathima Samreen for Muslim women who build in the quiet.">
<meta property="og:type" content="website"><meta property="og:site_name" content="The Voice of Becoming Studio">
<meta property="og:title" content="4 AM: the newsletter for Muslim women who build in the quiet">
<meta property="og:description" content="A weekly letter by Fathima Samreen. Join and get the free Articulation Gap workbook.">
<meta property="og:url" content="{SITE_URL}/newsletter.html">
{og_tags(NL_OG)}
{tw_tags(NL_OG)}
<meta http-equiv="refresh" content="0; url={t}"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>location.replace("{SITE_URL}/newsletter.html"+(location.search||"")+"#join");</script>
<style>body{{background:#141414;color:#F3E9DD;font-family:system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;margin:0}}a{{color:#F3E9DD}}</style></head>
<body><p>Taking you to <a href="{t}">the 4 AM newsletter</a>.</p></body></html>
"""

def main():
    posts = load_posts()
    out = {"index.html": home(posts), "about.html": about(), "authority/index.html": authority(), "newsletter.html": newsletter()}
    os.makedirs(os.path.join(SITE, "authority"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "letter"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "blog"), exist_ok=True)
    for old in glob.glob(os.path.join(SITE, "blog", "*.html")): os.remove(old)
    for p in posts: out["blog/%s.html" % p["slug"]] = article(p, posts)
    for name, h in out.items():
        open(os.path.join(SITE, name), "w", encoding="utf-8").write(h)
    # removed pages: stubs that redirect to the right new place
    open(os.path.join(SITE, "letter", "index.html"), "w", encoding="utf-8").write(letter())
    open(os.path.join(SITE, "blog.html"), "w", encoding="utf-8").write(blog_index(posts))
    open(os.path.join(SITE, "calendar.html"), "w", encoding="utf-8").write(calendar([]))
    open(os.path.join(SITE, "freebies.html"), "w", encoding="utf-8").write(freebies())
    urls = "".join("<url><loc>%s/%s</loc></url>" % (SITE_URL, n.replace("index.html", "")) for n in out)
    open(os.path.join(SITE, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>' % urls)
    open(os.path.join(SITE, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE_URL)
    print("built %d pages (%d articles)" % (len(out), len(posts)))

if __name__ == "__main__":
    main()

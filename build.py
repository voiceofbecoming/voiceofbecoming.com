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

KIT = "https://becoming-her-again-4.kit.com/042d6cefac"
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
    ("Topmate · book a call", TOPMATE, "tm"),
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

NAV = [("Home", "index.html"), ("About us", "about.html"), ("Articles", "blog.html"),
       ("Calendar", "calendar.html"), ("Freebies", "freebies.html"), ("Newsletter", "newsletter.html")]

def esc(s): return html.escape(s, quote=True)

def page(title, desc, body, current, rel="", path="index.html"):
    nav = "".join('<a href="%s%s"%s>%s</a>' % (rel, h, ' aria-current="page"' if h == current else "", n) for n, h in NAV)
    cta = '<a class="btn" href="%s" target="_blank" rel="noopener">Book a free call</a>' % TOPMATE_CALL
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
<meta property="og:image" content="{SITE_URL}/og.png">
<meta property="og:url" content="{SITE_URL}/{path}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE_URL}/{path}">
<link rel="icon" href="{rel}assets/img/favicon.png">
<link rel="preload" href="{rel}assets/fonts/anton.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{rel}assets/fonts/bric-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{rel}assets/fonts/inst-italic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel}assets/styles.css?v={ASSET_V}">
<script>document.documentElement.classList.add("js");setTimeout(function(){{if(!window.__vob)document.documentElement.classList.remove("js")}},4000)</script>
</head>
<body>
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
    <span class="eyebrow">Newsletter</span>
    <p class="foot-cta-line">Stories, prompts and strategy for women who carry <span class="serif">many roles at once.</span></p>
    <p class="small">Subscribe and get the free Articulation Gap workbook.</p>
   </div>
   <a class="btn" href="{KIT}">Subscribe free</a>
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
     <li><a href="{TOPMATE_CALL}" target="_blank" rel="noopener">Book a free Clarity Call</a></li>
     <li><a href="{KIT}">Join the newsletter</a></li>
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
 <div class="btns"><a class="btn" href="{KIT}">Get the free workbook</a><a class="btn ghost" href="{rel}freebies.html">What's inside</a></div></div>
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
    latest = ""
    if posts:
        cards = "".join(f'<a class="post-card" href="blog/{p["slug"]}.html"><span class="meta"><span class="tag">{esc(p.get("tag","Article"))}</span> · {nice(p["d"])}</span><h2>{esc(p["title"])}</h2><p>{esc(p["summary"])}</p><span class="more red">Read the article →</span></a>' for p in posts[:2])
        latest = f"""<section><div class="wrap"><div class="section-head"><span class="eyebrow">From the journal</span><h2 class="display">Latest <span class="red">articles.</span></h2></div><div class="grid g2">{cards}</div><div class="btns"><a class="btn ghost" href="blog.html">All articles</a></div></div></section>"""
    body = f"""
<section class="hero"><div class="wrap hero-grid">
 <div class="hero-copy">
  <span class="eyebrow">Ghostwriter for Muslim women executives</span>
  <h1 class="display">Your title belongs to your company. <span class="red">Your voice belongs to you.</span></h1>
  <p class="lead">I'm Fathima Samreen. I turn what you know into words people trust, so your name opens doors your title can't.</p>
  <div class="btns"><a class="btn" href="{TOPMATE_CALL}" target="_blank" rel="noopener">Book a free Clarity Call</a><a class="btn ghost" href="{KIT}">Get the free workbook</a></div>
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
<div class="marquee" aria-hidden="true"><div class="mq-row mq-co"><div class="mq-track"><span><em>Lupin</em> <b>&middot;</b> Director <b class="ar">&rarr;</b> VP</span><i>✦</i><span><em>Shenomics</em> <b>&middot;</b> 36K <b class="ar">&rarr;</b> 105K followers</span><i>✦</i><span><em>AHX Partners</em> <b>&middot;</b> +100 paid members</span><i>✦</i><span><em>Lupin</em> <b>&middot;</b> Director <b class="ar">&rarr;</b> VP</span><i>✦</i><span><em>Shenomics</em> <b>&middot;</b> 36K <b class="ar">&rarr;</b> 105K followers</span><i>✦</i><span><em>AHX Partners</em> <b>&middot;</b> +100 paid members</span><i>✦</i><span><em>Lupin</em> <b>&middot;</b> Director <b class="ar">&rarr;</b> VP</span><i>✦</i><span><em>Shenomics</em> <b>&middot;</b> 36K <b class="ar">&rarr;</b> 105K followers</span><i>✦</i><span><em>AHX Partners</em> <b>&middot;</b> +100 paid members</span><i>✦</i><span><em>Lupin</em> <b>&middot;</b> Director <b class="ar">&rarr;</b> VP</span><i>✦</i><span><em>Shenomics</em> <b>&middot;</b> 36K <b class="ar">&rarr;</b> 105K followers</span><i>✦</i><span><em>AHX Partners</em> <b>&middot;</b> +100 paid members</span><i>✦</i></div></div><div class="mq-row rev"><div class="mq-track"><span>Strategy</span><i>✦</i><span>Psychology</span><i>✦</i><span>Narrative</span><i>✦</i><span>Executive Presence</span><i>✦</i><span>Strategy</span><i>✦</i><span>Psychology</span><i>✦</i><span>Narrative</span><i>✦</i><span>Executive Presence</span><i>✦</i><span>Strategy</span><i>✦</i><span>Psychology</span><i>✦</i><span>Narrative</span><i>✦</i><span>Executive Presence</span><i>✦</i><span>Strategy</span><i>✦</i><span>Psychology</span><i>✦</i><span>Narrative</span><i>✦</i><span>Executive Presence</span><i>✦</i></div></div></div>
<section class="statement"><span class="big-q" aria-hidden="true">&ldquo;</span><div class="wrap"><p class="statement-text">Helping Muslim women executives turn their expertise into <span class="pill">a voice people follow.</span></p></div></section>

<section class="feat feat-r"><div class="feat-photo" style="--fp:50% 5%"><img src="assets/img/fathima-desk.jpg" alt="Fathima Samreen writing at her desk" width="640" height="1137" loading="lazy"></div>
<div class="wrap feat-grid">
<div class="feat-copy">
  <span class="eyebrow">Who I help</span>
  <h2 class="display">Brilliant inside. <span class="red">Invisible outside.</span></h2>
  <p class="lead">Inside her company, everyone knows what she is worth. Outside, almost nobody can see it. I call that the articulation gap. Closing it is my work.</p>
  <p>I work with Muslim women executives, senior leaders and founders who:</p>
  <ul class="checks">
   <li>Have lived enough to know shortcuts don't work</li>
   <li>Don't want to sound like everyone else online</li>
   <li>Care more about clarity than constant visibility</li>
   <li>Feel there is a book inside them, but haven't named it yet</li>
   <li>Want their work to outlive platforms and algorithms</li>
  </ul>
 </div>
 </div></section>

<section class="sand"><div class="wrap">
 <div class="section-head"><span class="eyebrow">Services</span><h2 class="display">I don't just <span class="red">create content.</span></h2><p class="lead">I help leaders make sense of the road they have walked. Ghostwriting, brand &amp; book strategy and authority strategy. Each one starts with your story.</p></div>
 <div class="grid g3 stack">
  <div class="card"><span class="num">01</span><h3>Books &amp; book strategy</h3><p>Books you don't rush to finish. Books you return to. I ghostwrite transformation and leadership books that feel honest and grounded, planned with you first: the idea, the structure and the audience it is for.</p></div>
  <div class="card"><span class="num">02</span><h3>Ghostwriting &amp; personal brand</h3><p>LinkedIn thought leadership, newsletters, long-form essays and visual assets, all rooted in one clear story. A brand that sounds like you, stays consistent and never feels performative.</p></div>
  <div class="card"><span class="num">03</span><h3>Authority strategy</h3><p>Authority comes from being understood, wherever you show up. The goal is simple: when people hear your name, they know what you stand for.</p></div>
 </div>
 <div class="grid g3" style="margin-top:22px">
  <div class="card result"><span class="meta">Lupin</span><span class="big">Director → VP</span><p>A book, a weekly newsletter and a profile that made a leader's expertise visible. 4,500+ newsletter subscribers and 800+ community members.</p></div>
  <div class="card result"><span class="meta">Shenomics · Bhavna Toor</span><span class="big">36K → 105K</span><p>LinkedIn followers for Bhavna, over 14 to 18 months of partnership, with the profile updated each time her offer evolved.</p></div>
  <div class="card result"><span class="meta">AHX Partners</span><span class="big">+100</span><p>Paid members added to a founder-led community, through strategy, content, design and positioning.</p></div>
 </div>
 <div class="btns"><a class="btn" href="{TOPMATE_CALL}" target="_blank" rel="noopener">Start with a free Clarity Call</a><a class="btn ghost" href="about.html">How I work</a></div>
</div></section>

<section><div class="wrap">
 <div class="section-head"><span class="eyebrow">What people say</span><h2 class="display">In their <span class="red">words.</span></h2></div>
 {testimonials("", 6)}
 <p class="swipe-hint">Swipe for more →</p>
</div></section>

{workbook_band("")}
{latest}
<section class="sand feat feat-l"><div class="feat-photo" style="--fp:50% 8%"><img src="assets/img/fathima-standing.jpg" alt="Fathima Samreen in a maroon abaya, holding a book" width="754" height="1024" loading="lazy"></div>
<div class="wrap feat-grid">
 <div class="feat-copy">
  <span class="eyebrow">The newsletter</span>
  <h2 class="display">Stories for women who carry <span class="red">many roles.</span></h2>
  <p class="lead">Executive, mother, wife, daughter. None of it is worthless. Every role you carry is part of your story. Get my letters on voice, worth and building a career from where you are.</p>
  <div class="btns"><a class="btn" href="{KIT}">Subscribe free</a><a class="btn ghost" href="newsletter.html">About the newsletter</a></div>
 </div>
</div></section>
"""
    return page("The Voice of Becoming Studio · Fathima Samreen, Ghostwriter for Muslim Women Executives",
                "Fathima Samreen is a ghostwriter, brand & book strategist and authority strategist helping Muslim women executives turn their expertise into a voice people follow.", body, "index.html", "", "")

def about():
    body = f"""
<section class="page-head feat feat-r"><div class="feat-photo" style="--fp:50% 8%"><img src="assets/img/fathima-standing.jpg" alt="Fathima Samreen in a maroon abaya, holding a book" width="754" height="1024" fetchpriority="high"></div>
<div class="wrap feat-grid">
 <div class="feat-copy"><span class="eyebrow">About us</span><h1 class="display">The writer behind <span class="red">the leaders' words.</span></h1>
 <p class="lead">I'm Fathima Samreen, founder of The Voice of Becoming Studio. A self-taught writer from Warangal, Telangana, running a global studio from home.</p></div>
</div></section>

<section class="feat feat-l"><div class="feat-photo" style="--fp:50% 15%"><img src="assets/img/fathima-award.jpg" alt="Fathima Samreen with her SIWAA 2025 Changemaker award" width="640" height="853" loading="lazy"></div>
<div class="wrap feat-grid">
 <div class="prose feat-copy">
  <span class="eyebrow">My story</span>
  <p>Before I wrote for leaders, I trained people to speak. As a soft-skills trainer and a zonal in-charge for a chain of schools in Telangana, I helped young people and teachers speak with confidence.</p>
  <p>Then I started writing. For more than 7 years I have ghostwritten for founders and leaders across 3 countries, and I have been writing books with leaders since 2019. LinkedIn thought leadership, books and personal brands, always in my client's own voice. All of it from my home in Warangal.</p>
  <p>Today I work with Muslim women executives. I have sat with many brilliant women who hold teams together and make hard calls every week. Inside their companies everyone knows what they are worth. Outside, almost nobody can see it. I call that <strong>the articulation gap</strong>. Closing it is my work.</p>
  <p>I am not a coach. I am a ghostwriter, a brand and book strategist and an authority strategist. You talk, I listen, and I write what only your life could have written. Nothing goes out without your yes.</p>
  <p>And I'm writing my own book, <strong>What's Your Aukaath?</strong> Aukaath, to me, is knowing your worth and owning your place.</p>
 </div>
</div></section>

<section class="sand"><div class="wrap split">
 <div><span class="eyebrow">Recognition</span><h2 class="display">SIWAA Award <span class="red">2025.</span></h2>
 <p class="lead">South India Women Achievers Awards, Bangalore. Category: Changemaker.</p>
</div>
 <div class="card"><span class="eyebrow">The mission</span>
 <h3 style="font-size:26px">To show Muslim girls and women that they can build a real career from home, and stand tall while staying rooted in their faith.</h3>
 <p style="margin-top:14px">Every role a woman carries is part of her story. Executive, mother, wife, daughter-in-law, daughter. None of it is worthless. The Voice of Becoming Studio helps women turn their lived story into a voice, a brand and their own income.</p></div>
</div></section>

<section><div class="wrap">
 <div class="section-head"><span class="eyebrow">How I think</span><h2 class="display">Four pillars of <span class="red">authority.</span></h2><p class="lead">Every book, post and profile I build stands on the same four pillars.</p></div>
 <div class="grid g4">
  <div class="pillar"><span class="display">Strategy</span><p>What you want to be known for, who it is for, and the door it should open a year from now.</p></div>
  <div class="pillar"><span class="display">Psychology</span><p>How your reader thinks and what builds trust, so your words land with the right people.</p></div>
  <div class="pillar"><span class="display">Narrative</span><p>The moments that shaped your leadership, structured into a story only your life could have written.</p></div>
  <div class="pillar"><span class="display">Executive Presence</span><p>Choosing what people get to see of you. Visible without being exposed.</p></div>
 </div>
</div></section>

<section class="sand"><div class="wrap">
 <div class="section-head"><span class="eyebrow">How I work</span><h2 class="display">The process behind <span class="red">every voice.</span></h2></div>
 <div class="grid g4">
  <div class="card"><span class="num">01</span><h3>NDA first</h3><p>Your story stays private before we talk details.</p></div>
  <div class="card"><span class="num">02</span><h3>Conversations first</h3><p>I listen before I write a word.</p></div>
  <div class="card"><span class="num">03</span><h3>Your voice</h3><p>Built from your ideas and your experience.</p></div>
  <div class="card"><span class="num">04</span><h3>Your yes</h3><p>Nothing goes out without your approval.</p></div>
 </div>
 <div class="btns"><a class="btn" href="{TOPMATE_CALL}" target="_blank" rel="noopener">Book a free Clarity Call</a></div>
</div></section>

<section><div class="wrap">
 <div class="section-head"><span class="eyebrow">Questions I hear most</span><h2 class="display">FAQ</h2></div>
 <details class="faq"><summary>Will it sound like me?</summary><p>Yes. Every piece is built from our conversations, your ideas and your experience. I learn how you speak before I write. If a line doesn't sound like you, it doesn't go out.</p></details>
 <details class="faq"><summary>Is my story kept private?</summary><p>Every engagement starts with an NDA, before we talk details. Many of my clients trust me with stories that aren't meant just for the internet.</p></details>
 <details class="faq"><summary>I'm busy. How much of my time does this take?</summary><p>We start with a context meeting and then regular conversations. I do the writing, design and scheduling. Your part is to talk, review and approve.</p></details>
 <details class="faq"><summary>I don't know if I'm ready for a book.</summary><p>That's OK. We can build your personal brand first, focus only on content or find your book together through your experience. The free Clarity Call is where we work out what fits.</p></details>
 <details class="faq"><summary>How do we start?</summary><p>Book the free 20 minute Clarity Call on Topmate. If you'd like to try something first, get the free workbook.</p></details>
</div></section>
"""
    return page("About us", "Fathima Samreen: ghostwriter, brand & book strategist and authority strategist from Warangal. 7+ years, 3 countries, SIWAA 2025 Changemaker.", body, "about.html", "", "about.html")

def blog_index(posts):
    if posts:
        items = "".join(f'<a class="post-card" href="blog/{p["slug"]}.html"><span class="meta"><span class="tag">{esc(p.get("tag","Article"))}</span> · {nice(p["d"])} · {read_mins(p["body"])} min read</span><h2>{esc(p["title"])}</h2><p>{esc(p["summary"])}</p><span class="more red">Read the article →</span></a>' for p in posts)
        content = f'<div class="post-list">{items}</div>'
    else:
        content = '<div class="empty"><h2>First articles coming soon</h2><p>Subscribe to the newsletter and you will get them first.</p></div>'
    body = f"""
<section class="page-head"><div class="wrap"><span class="eyebrow">Articles</span><h1 class="display">Notes from the <span class="red">ghostwriting desk.</span></h1>
<p class="lead">On voice, authority, books and the stories women keep for later. Written for leaders who think deeply.</p></div></section>
<section><div class="wrap" style="max-width:860px">{content}</div></section>
{workbook_band("")}
"""
    return page("Articles", "Articles by Fathima Samreen on voice, authority, books and the articulation gap.", body, "blog.html", "", "blog.html")

def article(p, posts):
    others = [o for o in posts if o["slug"] != p["slug"]][:2]
    more = ""
    if others:
        more = '<section class="sand"><div class="wrap" style="max-width:860px"><span class="eyebrow">Keep reading</span><div class="post-list">%s</div></div></section>' % "".join(
            f'<a class="post-card" href="{o["slug"]}.html"><span class="meta">{nice(o["d"])}</span><h2>{esc(o["title"])}</h2><p>{esc(o["summary"])}</p></a>' for o in others)
    body = f"""
<article><section><div class="wrap article">
 <a href="../blog.html" class="meta" style="text-decoration:none">← All articles</a>
 <p class="meta" style="margin-top:22px"><span class="tag">{esc(p.get("tag","Article"))}</span> · {nice(p["d"])} · {read_mins(p["body"])} min read</p>
 <h1>{esc(p["title"])}</h1>
 <p class="lead" style="margin-bottom:34px">{esc(p["summary"])}</p>
 <div class="prose">{md(p["body"])}</div>
 <div class="card" style="display:flex;gap:18px;align-items:center;margin-top:44px;flex-wrap:wrap">
  <img src="../assets/img/fathima-avatar.jpg" alt="" width="72" height="72" style="width:72px;height:72px;border-radius:50%;object-fit:cover">
  <div style="flex:1;min-width:220px"><strong>Fathima Samreen</strong><br><span class="small">Ghostwriter, brand &amp; book strategist and authority strategist. Founder, The Voice of Becoming Studio.</span></div>
  <a class="btn" href="{KIT}">Get my letters</a>
 </div>
</div></section></article>
{more}
"""
    return page(p["title"], p["summary"], body, "blog.html", "../", "blog/%s.html" % p["slug"])

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
def event_html(e, past=False):
    d = datetime.date.fromisoformat(e["date"])
    link = ('<p style="margin:10px 0 0"><a class="more" href="%s" target="_blank" rel="noopener">%s →</a></p>' % (esc(e["link"]), esc(e.get("link_label") or "Details"))) if e.get("link") else ""
    bits = " · ".join(esc(x) for x in [e.get("format",""), e.get("time",""), e.get("place","")] if x)
    desc = "<p style='margin:8px 0 0'>%s</p>" % esc(e["description"]) if e.get("description") else ""
    return f'<div class="event{" past" if past else ""}" data-date="{e["date"]}"><div class="date-box"><b>{d.day}</b><span>{MONTHS[d.month-1]} {d.year}</span></div><div><h3>{esc(e["title"])}</h3><p class="meta" style="margin:0">{bits}</p>{desc}{link}</div></div>'

def calendar(events):
    events = sorted(events, key=lambda e: e["date"])
    up = [e for e in events if datetime.date.fromisoformat(e["date"]) >= TODAY]
    past = [e for e in events if datetime.date.fromisoformat(e["date"]) < TODAY][::-1]
    empty = '<div class="empty" id="no-upcoming"%s><h2>Upcoming talks will be announced here</h2><p>Fathima speaks at colleges, women\'s groups and organisations. Want her at yours? Send a speaking enquiry below.</p></div>'
    up_html = "".join(event_html(e) for e in up) + (empty % ("" if not up else " hidden"))
    past_html = ('<h2 style="margin-top:50px;font-size:22px;font-weight:800">Past talks</h2><div class="grid">%s</div>' % "".join(event_html(e, True) for e in past)) if past else ""
    subject = "Speaking enquiry for Fathima Samreen"
    mail = "mailto:%s?subject=%s" % (EMAIL, subject.replace(" ", "%20"))
    body = f"""
<section class="page-head"><div class="wrap"><span class="eyebrow">Calendar</span><h1 class="display">Talks &amp; <span class="red">events.</span></h1>
<p class="lead">Where to hear Fathima speak, in person and online.</p></div></section>
<section><div class="wrap" style="max-width:860px">
 <h2 style="font-size:22px;font-weight:800">Upcoming</h2>
 <div class="grid" id="upcoming">{up_html}</div>
 {past_html}
</div></section>
<section class="sand"><div class="wrap">
 <div class="section-head"><span class="eyebrow">Invite Fathima to speak</span><h2 class="display">Talks &amp; <span class="red">workshops.</span></h2>
 <p class="lead">A real woman from Warangal who built a career from home, and who can teach your audience to find their voice. Each talk runs as a 20, 45 or 90 minute session or workshop.</p></div>
 <div class="grid g3">
  <div class="card"><span class="num">01</span><h3>Rooted and Rising: Building a Career From Home</h3><p>Your home, your town and your values are not your limits. A real career can start from exactly where you are.</p><p class="small">Best for girls' colleges, women's clubs and community groups.</p></div>
  <div class="card"><span class="num">02</span><h3>The Articulation Gap: Say What You Know So People Follow</h3><p>You are smarter than your words. Learn to put what you know into clear, simple sentences people remember. It is about clarity, not accent.</p><p class="small">Best for universities, MBA and placement cells.</p></div>
  <div class="card"><span class="num">03</span><h3>Your Name Is a Brand: Personal Branding for Young Women</h3><p>Before your first job, let your name stand for something, online and offline, while keeping your values and your privacy.</p><p class="small">Best for final-year students and management departments.</p></div>
 </div>
 <div class="btns"><a class="btn" href="{mail}">Send a speaking enquiry</a><a class="btn ghost" href="{TOPMATE}" target="_blank" rel="noopener">Message on Topmate</a></div>
</div></section>
"""
    return page("Calendar: talks & events", "Upcoming talks and workshops by Fathima Samreen, and how to invite her to speak.", body, "calendar.html", "", "calendar.html")

def freebies():
    body = f"""
<section class="page-head"><div class="wrap"><span class="eyebrow">Freebies</span><h1 class="display">Free tools to find <span class="red">your voice.</span></h1>
<p class="lead">Start here. Free resources from The Voice of Becoming Studio.</p></div></section>
<section><div class="wrap">
 <div class="signup" id="workbook">
  <img class="cover" src="assets/img/workbook.webp" alt="Cover of The Articulation Gap workbook" width="600" height="848">
  <div>
   <span class="eyebrow">Free workbook</span>
   <h2 class="display">The Articulation <span class="red">Gap.</span></h2>
   <p class="lead">The distance between the brilliance in your head and the words the world can see. This workbook helps you close it.</p>
   <ul class="checks" style="margin:22px 0">
    <li>Five stories you already own, turned into post ideas</li>
    <li>A profile that speaks for you while you do your job</li>
    <li>Start with Story 01 in 20 minutes</li>
   </ul>
   <a class="btn" href="{KIT}">Send me the workbook</a>
   <p class="small" style="margin-top:14px">Enter your email on the next page and the workbook comes straight to your inbox. You'll also get my newsletter. Unsubscribe any time.</p>
  </div>
 </div>
</div></section>
<section class="sand"><div class="wrap">
 <div class="section-head"><span class="eyebrow">More ways to start</span><h2 class="display">Free, <span class="red">and personal.</span></h2></div>
 <div class="grid g2">
  <div class="card"><span class="num">20 min</span><h3>Book &amp; Authority Clarity Call</h3><p>Bring your story and your goal. We work out whether a book, your LinkedIn or your brand comes first.</p><a class="more" href="{TOPMATE_CALL}" target="_blank" rel="noopener">Book the call →</a></div>
  <div class="card"><span class="num">3 fixes</span><h3>LinkedIn Profile Teardown</h3><p>Send me your profile. I send back 3 written fixes so it builds trust.</p><a class="more" href="https://topmate.io/fathima_samreen/2368492" target="_blank" rel="noopener">Ask for a teardown →</a></div>
 </div>
</div></section>
"""
    return page("Freebies: The Articulation Gap workbook", "Get the free Articulation Gap workbook by Fathima Samreen: five stories you already own, turned into post ideas and a profile that speaks for you.", body, "freebies.html", "", "freebies.html")

def newsletter():
    body = f"""
<section class="hero"><div class="wrap hero-grid">
 <div class="hero-copy">
  <span class="eyebrow">Free workbook · The Voice of Becoming newsletter</span>
  <h1 class="display">Get the free Articulation Gap <span class="red">workbook.</span></h1>
  <p class="lead">5 signature stories you already own, 30 LinkedIn post ideas and a profile checklist, so the brilliance in your head becomes words people trust.</p>
  <div class="btns"><a class="btn btn-xl" href="{KIT}">Send me the workbook <span aria-hidden="true">→</span></a></div>
  <p class="small" style="margin-top:14px">Free. Add your email on the next page and it lands in your inbox, with my newsletter. Unsubscribe any time.</p>
 </div>
 <div class="hero-photo"><img src="assets/img/fathima-hero.jpg" alt="Fathima Samreen" width="1024" height="1366" fetchpriority="high"></div>
</div></section>
<section><div class="wrap">
 <div class="section-head"><span class="eyebrow">What you'll get</span><h2 class="display">In your <span class="red">inbox.</span></h2></div>
 <div class="grid g3">
  <div class="card"><span class="num">01</span><h3>Stories, not content</h3><p>Real moments from the many roles women carry, and the truth behind them.</p></div>
  <div class="card"><span class="num">02</span><h3>Write-this-down prompts</h3><p>Small prompts to put your own story on paper, one line at a time.</p></div>
  <div class="card"><span class="num">03</span><h3>From the ghostwriting desk</h3><p>What 7+ years of writing for leaders has taught me about voice and authority.</p></div>
 </div>
</div></section>
<section class="sand"><div class="wrap"><div class="signup">
 <img class="cover" src="assets/img/workbook.webp" alt="Cover of The Articulation Gap workbook" width="600" height="848" loading="lazy">
 <div><span class="eyebrow">Welcome gift</span><h2 class="display">Subscribe and get the <span class="red">workbook.</span></h2>
 <p class="lead">5 signature stories, 30 LinkedIn post ideas and a profile checklist. It comes with your welcome email, free.</p>
 <a class="btn" href="{KIT}">Send me the workbook</a></div>
</div></div></section>
"""
    return page("Newsletter: free Articulation Gap workbook", "Get the free Articulation Gap workbook by Fathima Samreen: 5 signature stories, 30 LinkedIn post ideas and a profile checklist, plus The Voice of Becoming newsletter.", body, "newsletter.html", "", "newsletter.html")

def main():
    posts = load_posts()
    events = json.load(open(os.path.join(ROOT, "data", "events.json"), encoding="utf-8")).get("events", [])
    out = {"index.html": home(posts), "about.html": about(), "blog.html": blog_index(posts),
           "calendar.html": calendar(events), "freebies.html": freebies(), "newsletter.html": newsletter()}
    os.makedirs(os.path.join(SITE, "blog"), exist_ok=True)
    for old in glob.glob(os.path.join(SITE, "blog", "*.html")): os.remove(old)
    for p in posts: out["blog/%s.html" % p["slug"]] = article(p, posts)
    for name, h in out.items():
        open(os.path.join(SITE, name), "w", encoding="utf-8").write(h)
    urls = "".join("<url><loc>%s/%s</loc></url>" % (SITE_URL, n.replace("index.html", "")) for n in out)
    open(os.path.join(SITE, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>' % urls)
    open(os.path.join(SITE, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE_URL)
    print("built %d pages (%d articles, %d events)" % (len(out), len(posts), len(events)))

if __name__ == "__main__":
    main()

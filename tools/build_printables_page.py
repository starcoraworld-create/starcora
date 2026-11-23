#!/usr/bin/env python3
"""Build public/printables/index.html (starcora.world/printables/) from the BOOKS list below.

The page reuses the Grown-ups page's head, header and footer (paths moved one folder down),
so menu changes on grownups.html carry over the next time this runs.

To add a printable storybook:
  1. Shrink the A4 and US Letter PDFs with tools/shrink_pdf.py and put them in public/printables/pdf/
     with the file names the printables chat gave them. File names and addresses never change once live.
  2. Add one line to BOOKS (newest last), run:  python3 tools/build_printables_page.py  from the repo root.
  3. Add the PDFs' page to sitemap.xml if new, check the page, push when Courtney says.
"""
import os, re, json, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, 'public')
SITE = 'https://starcora.world'

BOOKS = [
    # n, title, file stem (before _printable_A4.pdf), pages, what's inside
    (0, 'Welcome to Starcora', 'Starcora_Welcome_to_Starcora', 17,
     'Count the sky, follow the arrows, match each friend to their badge, sort frozen from melted, hop along the number stones, find the missing jigsaw piece and read a treasure map. Cut out Planet Starcora to keep.'),
    (1, 'The Fallen Star', 'Starcora_The_Fallen_Star', 15,
     'Crack the secret code, find the hidden lanterns, trace the swirls, wind up Oro, solve three vine mazes and keep the fallen star safe. Cut out a star medal to keep.'),
    (2, 'The Star Rocket', 'Starcora_The_Star_Rocket', 19,
     'Find the rocket pieces, solve the root mazes, pick the piece that fits, build the rocket in order, match the gears, count down a dot-to-dot and colour the rainbow by numbers. Cut out the star rocket to keep.'),
    (3, 'The Rainbow Wisp', 'Starcora_The_Rainbow_Wisp', 19,
     'Rainbow sudoku, tangled ribbons, twin blooms, count the logs, mirror pictures, logic clues, odd one out and spot the difference. Cut out the rainbow wisp lantern to keep.'),
]

ACTIVITIES = [
    ('paper-rocket', 'Paper straw rocket', 'Colour it, roll it, blow it! Print a Star Rocket and send it zooming with one big puff through a straw.', 'paper-straw-rocket-craft-sola-oro-rose-700.webp'),
    ('star-and-moon-pumpkins', 'No-carve star and moon pumpkins', 'Paint a pumpkin purple and cover it in printable stars, moons and friends.', 'no-carve-star-and-moon-pumpkins-sola-oro-rose-700.webp'),
    ('moonmist-cloud-cups', 'Moonmist cloud cups', 'A no-bake yoghurt recipe with printable star toppers.', 'moonmist-cloud-cups-sola-oro-rose-700.webp'),
]

TITLE = 'Print & Play: free printable storybooks for kids 4 to 7, with puzzles on every page | Starcora'
DESC = 'Free printable storybooks for children aged 4 to 7, a screen-free way to enjoy Starcora. Read the story aloud and solve a pencil-and-paper puzzle on every page: codes, mazes, counting, patterns and cut-outs. A4 and US Letter PDFs.'
URL = SITE + '/printables/'

def mb(path):
    return '%.1f MB' % (os.path.getsize(path) / 1048576)

def relink(s):
    """Move a root-page fragment one folder down."""
    def fix(m):
        attr, v = m.group(1), m.group(2)
        if re.match(r'(https?:|mailto:|#|\.\./|data:|/)', v):
            return m.group(0)
        return '%s="../%s"' % (attr, v)
    return re.sub(r'\b(href|src)="([^"]*)"', fix, s)

def main():
    g = open(os.path.join(PUB, 'grownups.html'), encoding='utf8').read()
    header = g[g.index('<header class="site-header">'):g.index('</header>') + 9]
    footer = g[g.index('<footer class="site-footer">'):g.index('</footer>') + 9]
    header = relink(header).replace(' aria-current="page"', '')
    header = header.replace('<a href="../printables/index.html">', '<a href="index.html" aria-current="page">')
    footer = relink(footer).replace('<a href="../printables/index.html">', '<a href="index.html">')
    tail = g[g.index('</footer>') + 9:g.index('</body>')]
    tail = relink(tail)

    cards = []
    parts = []
    for n, title, stem, pages, inside in BOOKS:
        a4 = 'pdf/%s_printable_A4.pdf' % stem
        us = 'pdf/%s_printable_US_Letter.pdf' % stem
        for f in (a4, us):
            if not os.path.exists(os.path.join(PUB, 'printables', f)):
                raise SystemExit('Missing ' + f)
        cards.append('''    <article class="pbook">
      <a class="pcover" href="../books/book-{n}/index.html" aria-label="Read Book {n}: {t} online"><img src="../assets/book-{n}-300.webp" width="300" height="393" loading="lazy" alt="Book {n} cover: {t}, a Starcora printable storybook"></a>
      <div class="pinfo">
        <h3>Book {n}: {t}</h3>
        <p class="pmeta">{pages} pages to print</p>
        <p>{inside}</p>
        <div class="pdl"><a class="gbtn" href="{a4}" download>Download A4 <small>{a4mb}</small></a><a class="gbtn" href="{us}" download>Download US Letter <small>{usmb}</small></a></div>
        <a class="readon" href="../books/book-{n}/index.html">Read Book {n} online first</a>
      </div>
    </article>'''.format(n=n, t=html.escape(title), pages=pages, inside=html.escape(inside), a4=a4, us=us,
                         a4mb=mb(os.path.join(PUB, 'printables', a4)), usmb=mb(os.path.join(PUB, 'printables', us))))
        parts.append({"@type": "Book", "name": "Book %d: %s (printable storybook)" % (n, title),
                      "bookFormat": "https://schema.org/EBook", "inLanguage": "en-GB", "isAccessibleForFree": True,
                      "image": SITE + "/assets/book-%d.webp" % n, "numberOfPages": pages,
                      "typicalAgeRange": "4-7", "description": inside,
                      "encoding": [{"@type": "MediaObject", "encodingFormat": "application/pdf", "contentUrl": URL + a4, "name": "A4"},
                                   {"@type": "MediaObject", "encodingFormat": "application/pdf", "contentUrl": URL + us, "name": "US Letter"}]})

    acts = []
    for slug, t, d, img in ACTIVITIES:
        acts.append('      <a href="../activities/{s}/"><img src="../assets/activities/{img}" width="700" height="700" loading="lazy" alt=""><span><b>{t}</b><span>{d}</span></span></a>'.format(
            s=slug, img=img, t=html.escape(t), d=html.escape(d)))

    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Starcora printable storybooks", "url": URL,
           "description": DESC, "inLanguage": "en-GB", "isPartOf": {"@type": "WebSite", "name": "Starcora", "url": SITE + "/"},
           "hasPart": parts},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Starcora", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": "Print & Play", "item": URL}]}]

    head = '''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preload" as="image" href="../assets/logo-cream.webp" fetchpriority="high">
<link rel="preload" as="image" href="../assets/sky.webp" fetchpriority="high">
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="Starcora">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/assets/share.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#8E6BC4">
<link rel="icon" href="../assets/favicon-48.png" sizes="48x48" type="image/png">
<link rel="icon" href="../assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
<link rel="stylesheet" href="../stories.css">
<style>
.hero.short{{height:auto;min-height:0;padding:150px 16px 60px;text-align:center}}
.hero.short .titles{{position:relative;top:auto}}
.doc{{max-width:56rem;margin:0 auto;padding:clamp(40px,6vw,70px) 20px clamp(56px,8vw,90px)}}
.doc .lead{{max-width:42rem;margin:0 auto}}
.doc h2{{font-family:var(--display);font-weight:500;font-variation-settings:"SOFT" 100;font-size:28px;margin:6px 0 10px;text-align:center;color:var(--ink)}}
.doc p,.doc li{{color:#4A3550}}
.doc .big{{font-size:20px;color:var(--ink)}}
.doc a{{color:#5B3A7A}}
.pbooks{{display:grid;gap:26px;margin:26px 0 10px}}
.pbook{{display:grid;grid-template-columns:150px minmax(0,1fr);gap:24px;align-items:start;padding:22px 24px;border-radius:8px;
  background:linear-gradient(rgba(255,250,238,.66),rgba(255,250,238,.66)),var(--parch) url(../assets/parchment.webp) 0 0/933px auto;border:1.5px solid var(--gold-line);
  box-shadow:inset 0 0 0 4px rgba(255,250,238,.8),inset 0 0 0 5px rgba(201,150,58,.5),0 14px 26px -20px rgba(90,50,20,.55)}}
.pcover img{{display:block;width:100%;height:auto;transform:rotate(-3deg);filter:drop-shadow(0 10px 12px rgba(60,30,20,.35));transition:transform .35s cubic-bezier(.3,1.5,.5,1)}}
.pcover:hover img{{transform:rotate(0) translateY(-4px)}}
.pinfo h3{{font-family:var(--display);font-weight:500;font-variation-settings:"SOFT" 100;font-size:24px;margin:0;color:var(--ink);line-height:1.2}}
.pinfo .pmeta{{margin:4px 0 8px;font-weight:700;color:#7A5A2E;font-size:15px}}
.pinfo p{{margin:0 0 14px}}
.pdl{{display:flex;flex-wrap:wrap;gap:12px 14px;margin:4px 0 12px}}
.pdl .gbtn{{font-size:16px}}
.pdl .gbtn small{{font-weight:600;font-size:12px;opacity:.8;margin-left:4px}}
.readon{{font-weight:700;font-size:15px}}
.tips{{max-width:42rem;margin:0 auto}}
.tips li{{margin:0 0 8px}}
.acts3{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin:18px 0 0}}
.acts3 a{{display:block;text-decoration:none;color:var(--ink);border-radius:8px;overflow:hidden;border:1.5px solid var(--gold-line);background:#FBF1DC;
  box-shadow:inset 0 0 0 3px rgba(255,250,238,.8),0 12px 22px -18px rgba(90,50,20,.55);transition:transform .3s cubic-bezier(.3,1.5,.5,1)}}
.acts3 a:hover{{transform:translateY(-4px)}}
.acts3 img{{display:block;width:100%;height:auto;aspect-ratio:1}}
.acts3 a>span{{display:block;padding:12px 14px 14px}}
.acts3 b{{display:block;font-family:var(--display);font-weight:500;font-size:18px;line-height:1.2;margin-bottom:4px}}
.acts3 a>span>span{{display:block;font-size:14px;color:#5E4558;line-height:1.45}}
.acts3 b{{color:var(--ink)}}
@media (max-width:700px){{.pbook{{grid-template-columns:96px minmax(0,1fr);gap:16px;padding:18px 16px}}.acts3{{grid-template-columns:1fr}}.pdl{{flex-direction:column;align-items:stretch}}.pdl .gbtn{{font-size:15px;white-space:nowrap}}}}
</style>
<script type="application/ld+json">{ld0}</script>
<script type="application/ld+json">{ld1}</script>
</head>
<body class="parch">
'''.format(title=html.escape(TITLE), desc=html.escape(DESC), url=URL, site=SITE,
           ld0=json.dumps(ld[0], ensure_ascii=False), ld1=json.dumps(ld[1], ensure_ascii=False))

    main = '''<main class="no-ico">
<section class="hero short" aria-labelledby="t">
  <div class="sky"></div>
  <div class="titles"><h1 id="t">Print &amp; Play</h1><p>Printable storybooks to read and solve at the table</p></div>
</section>
<article class="doc">
  <div class="lead">
  <p class="big dropcap">Every Starcora storybook has a printable twin. It has the same story and pictures as the book on screen, with a pencil-and-paper puzzle facing every page: codes to crack, mazes, counting, patterns and a cut-out to keep. A grown-up or your child can read the story aloud, and your child solves the puzzles.</p>
  <p>It's a screen-free way to enjoy Starcora. The puzzles are different from the games online, so children who have already read the book on screen still get something new. Each book prints in colour on plain paper and comes in A4 and US Letter.</p>
  </div>

  <span class="startrail sm" role="presentation"></span>
  <h2>Printable storybooks</h2>
  <div class="pbooks">
{cards}
  </div>
  <p style="text-align:center">More printable storybooks are on the way.</p>

  <span class="startrail sm" role="presentation"></span>
  <h2>Printing tips</h2>
  <ul class="tips">
    <li>Print at actual size (100%), so the cut-outs fit their spaces.</li>
    <li>Choose A4 in the UK, Europe and Australia, and US Letter in the US and Canada.</li>
    <li>The last page has cut-outs to keep. A grown-up can help with the scissors.</li>
    <li>The cover and last page have a code to scan, which opens the same story on starcora.world.</li>
  </ul>

  <span class="startrail sm" role="presentation"></span>
  <h2>Printable activities</h2>
  <p style="text-align:center">Crafts and recipes with free printables, made with Sola, Oro and Rose.</p>
  <div class="acts3">
{acts}
  </div>
</article>
</main>
'''.format(cards='\n'.join(cards), acts='\n'.join(acts))

    out = head + header + '\n' + main + footer + tail + '</body>\n</html>\n'
    os.makedirs(os.path.join(PUB, 'printables'), exist_ok=True)
    open(os.path.join(PUB, 'printables', 'index.html'), 'w', encoding='utf8').write(out)
    print('Wrote public/printables/index.html with %d books' % len(BOOKS))

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Build one page per colouring page: public/art/<slug>/index.html (address starcora.world/art/<slug>/).

Source: the PAGES list in public/art.html. Each line has an id (used for the pin file assets/pins/colour-<id>.jpg),
a slug (the address; once pinned it NEVER changes; a second picture of the same subject gets a name for what's different, e.g. oro-rocket), name, tags, art, alt and added (go-live date, YYYY-MM-DD).
Pages dated in the future are not built and stay hidden on the Art page until their day.
Also rewrites the colouring-page lines in public/sitemap.xml.

Run from the repository root:  python3 tools/build_art_pages.py   (add --date YYYY-MM-DD to build as if it were that day)
To add a page: put the PNG in assets/colour, its thumb in assets/colour/thumbs, its pin in assets/pins/colour-<id>.jpg,
add one line to PAGES (and a line to ABOUT/TITLE below), run this, check, push.
"""
import re, sys, os, json, html, datetime, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PUB = os.path.join(ROOT, 'public')
BASE = 'https://starcora.world'
today = datetime.date.today().isoformat()
if '--date' in sys.argv: today = sys.argv[sys.argv.index('--date') + 1]

# Title words (for the <title>) and one or two short lines about each picture. New pages: add a line here.
TITLE = {'oro': 'Oro the Robot', 'rose': 'Rose the Deer', 'dotstool': 'Dotstool Mushroom', 'swirlbud': 'Swirlbud Flower',
         'lantern': 'Lantern-bloom Flower', 'daisy': 'Daisy Flower', 'tulip': 'Tulip Flower', 'chest': 'Cova Treasure Chest'}
ABOUT = {
 'sola': 'Sola is the sunny leader and inventor. Her sun-power brings light, warmth and a burst of energy.',
 'oro': 'Oro is the most enthusiastic little robot in the universe. His moon-power can cool, pull and make things still.',
 'rose': 'Rose is small and quiet, and always somehow right. Her flower-power makes things grow, mend and bloom.',
 'dotstool': 'A big spotty mushroom from the Moonmist forest, with flowers all around it.',
 'spiral': 'The twisty Spiral Tree from the Moonmist forest.',
 'swirlbud': 'Swirlbuds are lollipop swirl flowers that grow in the Moonmist.',
 'lantern': 'A lantern-bloom is a glowing flower that hangs like a little lamp in the Moonmist forest.',
 'daisy': 'A happy daisy with big, easy petals for little hands.',
 'tulip': 'A tall tulip with big, easy petals for little hands.',
 'sky': 'The sky over the Moonmist, with the moon, stars, a ringed planet, clouds and treetops.',
 'chest': 'The Cova Chest is where Sola, Oro and Rose keep their treasures. It has a planet carved on the front.',
}

src = open(os.path.join(PUB, 'art.html'), encoding='utf8').read()
block = re.search(r'const PAGES=\[(.*?)\n\];', src, re.S).group(1)
pages = []
for line in block.split('\n'):
    m = re.search(r"\{id:'([^']+)',slug:'([^']+)',name:'([^']+)',tags:\[([^\]]*)\],art:C\+'([^']+)',alt:'((?:[^'\\]|\\.)*)',added:'([\d-]+)'", line)
    if m: pages.append(dict(id=m[1], slug=m[2], name=m[3], tags=re.findall(r"'([^']+)'", m[4]), art=m[5], alt=m[6].replace("\\'", "'"), added=m[7]))
assert pages, 'no PAGES found'
for key in ('id', 'slug'):
    seen = [p[key] for p in pages]; dup = {x for x in seen if seen.count(x) > 1}
    assert not dup, f'Two colouring pages share the same {key}: {dup}. Give each its own (e.g. oro-rocket); a pinned address never changes.'
live = [p for p in pages if p['added'] <= today]
ART = os.path.join(PUB, 'art'); os.makedirs(ART, exist_ok=True)
keep = {p['slug'] for p in live}
for d in os.listdir(ART):  # remove pages no longer live (date moved later)
    if os.path.isdir(os.path.join(ART, d)) and d not in keep: shutil.rmtree(os.path.join(ART, d))
E = html.escape

def build(p):
    s = src
    url = f"{BASE}/art/{p['slug']}/"
    tname = TITLE.get(p['id'], p['name'])
    title = f"{tname} Colouring Page for Kids: Free Printable | Starcora"
    about = ABOUT.get(p['id'], '')
    desc = f"Free {p['name']} colouring page for kids aged 4 to 7. {about} Print it at home or colour it on screen."
    img = f"{BASE}/assets/colour/{p['art']}"
    ld = [{"@context": "https://schema.org", "@type": "VisualArtwork", "name": f"{p['name']} colouring page", "description": desc, "url": url,
           "image": img, "artform": "Colouring page", "isAccessibleForFree": True, "inLanguage": "en-GB",
           "audience": {"@type": "PeopleAudience", "suggestedMinAge": 4, "suggestedMaxAge": 7},
           "isPartOf": {"@type": "CollectionPage", "name": "Free colouring pages for kids", "url": BASE + "/art"},
           "creator": {"@type": "Organization", "name": "Starcora", "url": BASE + "/"}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
           {"@type": "ListItem", "position": 1, "name": "Starcora", "item": BASE + "/"},
           {"@type": "ListItem", "position": 2, "name": "Colouring pages", "item": BASE + "/art"},
           {"@type": "ListItem", "position": 3, "name": f"{p['name']} colouring page", "item": url}]}]
    seo = f'''<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="Starcora">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/pins/colour-{p['id']}.jpg">
<meta name="twitter:card" content="summary_large_image">
''' + ''.join(f'<script type="application/ld+json" data-seo>{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)
    s = s.replace('<head>\n', '<head>\n<base href="/">\n', 1)
    n0 = len(s)
    s = re.sub(r'<title>.*?</title>\n', '', s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description"[^>]*>\n', '', s, count=1)
    s = re.sub(r'<link rel="canonical"[^>]*>\n', '', s, count=1)
    s = re.sub(r'<meta (property="og:[^"]+"|name="twitter:[^"]+")[^>]*>\n', '', s)
    s = re.sub(r'<script type="application/ld\+json"[^>]*>.*?</script>\n', '', s, flags=re.S)
    s = s.replace('<base href="/">\n', '<base href="/">\n' + seo, 1)
    s = s.replace('<link rel="preload" as="image" href="assets/sky.webp" fetchpriority="high">\n', '', 1)
    s, k = re.subn(r'<div class="titles"><h1 id="t">.*?</h1><p>.*?</p></div>',
                   f'<div class="titles"><h1 id="t" class="no-ico">{E(p["name"])} colouring page</h1><p>Free to print or colour on screen</p></div>', s, count=1)
    assert k == 1
    others = [o for o in live if o['id'] != p['id']]
    same = [o for o in others if set(o['tags']) & set(p['tags'])]
    more = (same + [o for o in others if o not in same])[:4]
    cards = ''.join(f'''<div class="card"><a class="thumb" href="art/{o['slug']}/"><img src="assets/colour/thumbs/{o['art'].replace('.png', '.webp')}" width="420" height="420" loading="lazy" alt="{E(o['alt'])}, free to print"></a><p class="cname"><a href="art/{o['slug']}/">{E(o['name'])}</a></p></div>''' for o in more)
    pin = f'data-pin-media="{BASE}/assets/pins/colour-{p["id"]}.jpg" data-pin-url="{url}" data-pin-description="Free {E(p["name"])} colouring page for kids aged 4 to 7. Print it or colour it on screen at Starcora."'
    single = f'''<section class="gallery" id="gallery">
  <article class="one">
    <div class="big"><img src="assets/colour/{p['art']}" width="1000" height="1000" alt="{E(p['alt'])}, free colouring page to print" fetchpriority="high" {pin}></div>
    <div class="info">
      <span class="tag">Free colouring page</span>
      <h2>Colour {E(p['name'])}</h2>
      <p>{E(about)} Tap <b>Paint</b> to colour it on screen, or <b>Print</b> to colour it at the table.</p>
      <div class="btns"><button class="pill" data-paint="{p['id']}">Paint</button><button class="pill alt" data-print="{p['id']}">Print</button></div>
    </div>
  </article>
  <h2 class="shelf">More colouring pages</h2>
  <div class="grid">{cards}</div>
  <a class="allbtn" href="art">See all colouring pages</a>
</section>'''
    s, k = re.subn(r'<section class="gallery" id="gallery">.*?\n</section>', lambda m: single, s, count=1, flags=re.S); assert k == 1
    s = s.replace('<script>\nconst svgUrl', f'<script>window.SINGLE={json.dumps(p["id"])};</script>\n<script>\nconst svgUrl', 1)
    assert 'window.SINGLE' in s
    s, k = re.subn(r'<div id="pinimg" hidden><img data-src="[^"]+"([^>]*?)alt="[^"]*"([^>]*?)data-pin-description="[^"]*"',
                   lambda m: f'<div id="pinimg" hidden><img data-src="assets/pins/colour-{p["id"]}.jpg"{m[1]}alt="Free {E(p["name"])} colouring page for kids"{m[2]}data-pin-description="Free {E(p["name"])} colouring page for kids aged 4 to 7. Print it or colour it on screen at Starcora." data-pin-url="{url}"', s, count=1)
    assert k == 1
    d = os.path.join(ART, p['slug']); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf8').write(s)

for p in live: build(p)
sm_path = os.path.join(PUB, 'sitemap.xml'); sm = open(sm_path, encoding='utf8').read()
sm = re.sub(r'\s*<!-- colouring pages: built by tools/build_art_pages.py -->.*?<!-- /colouring pages -->', '', sm, flags=re.S)
entries = '\n'.join(f'''  <url><loc>{BASE}/art/{p['slug']}/</loc><lastmod>{p['added']}</lastmod><priority>0.7</priority><image:image><image:loc>{BASE}/assets/colour/{p['art']}</image:loc><image:title>{E(p['name'])} colouring page</image:title></image:image></url>''' for p in live)
sm = sm.replace('</urlset>', f'  <!-- colouring pages: built by tools/build_art_pages.py -->\n{entries}\n  <!-- /colouring pages -->\n</urlset>')
open(sm_path, 'w', encoding='utf8').write(sm)
print(f'{len(live)} live of {len(pages)} colouring pages (date {today}); waiting:', [p['slug'] + ' ' + p['added'] for p in pages if p not in live])

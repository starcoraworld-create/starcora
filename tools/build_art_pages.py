#!/usr/bin/env python3
"""Build one page per colouring page: public/art/<id>.html  (served at starcora.world/art/<id>).

Source of truth: the PAGES list in public/art.html. Each line can have:
  added:'YYYY-MM-DD'  = go-live date. Before that day the page is not built and is hidden in the gallery.
  book:N              = links the page to Book N (optional).
Also rebuilds the colouring-page lines in public/sitemap.xml.
Run from the repository root:  python3 tools/build_art_pages.py   (add --date YYYY-MM-DD to test a future day)
"""
import re,sys,os,json,html,datetime
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));PUB=os.path.join(ROOT,'public')
BASE='https://starcora.world'
BOOKS={0:'Welcome to Starcora',1:'The Fallen Star',2:'The Star Rocket'}
today=datetime.date.today().isoformat()
if '--date' in sys.argv: today=sys.argv[sys.argv.index('--date')+1]
src=open(os.path.join(PUB,'art.html'),encoding='utf8').read()
block=re.search(r'const PAGES=\[(.*?)\n\];',src,re.S).group(1)
pages=[]
for line in block.split('\n'):
    m=re.search(r"\{id:'([^']+)',name:'([^']+)',tags:\[([^\]]*)\],art:C\+'([^']+)',alt:'([^']*)',added:'([\d-]+)'(?:,book:(\d+))?",line)
    if m: pages.append(dict(id=m[1],name=m[2],tags=re.findall(r"'([^']+)'",m[3]),art=m[4],alt=m[5].replace("\\'","'"),added=m[6],book=int(m[7]) if m[7] else None))
live=[p for p in pages if p['added']<=today]
os.makedirs(os.path.join(PUB,'art'),exist_ok=True)
# remove pages that are no longer live (e.g. date moved later)
keep={p['id']+'.html' for p in live}
for f in os.listdir(os.path.join(PUB,'art')):
    if f.endswith('.html') and f not in keep: os.remove(os.path.join(PUB,'art',f))
E=html.escape
def head_seo(p):
    title=f"{p['name']} colouring page for kids: free to print or paint online | Starcora"
    desc=f"Free {p['name']} colouring page for kids aged 4 to 7. {p['alt']}. Print it for the table or paint it on screen with fill, brush and stickers."
    url=f"{BASE}/art/{p['id']}"
    img=f"{BASE}/assets/colour/{p['art']}"
    ld={"@context":"https://schema.org","@type":"VisualArtwork","name":f"{p['name']} colouring page","description":desc,"url":url,"image":img,
        "artform":"Colouring page","isAccessibleForFree":True,"inLanguage":"en-GB","audience":{"@type":"PeopleAudience","suggestedMinAge":4,"suggestedMaxAge":7},
        "isPartOf":{"@type":"CollectionPage","name":"Free colouring pages for kids","url":BASE+"/art"},"creator":{"@type":"Organization","name":"Starcora","url":BASE+"/"}}
    return title,desc,url,f'''<title>{E(title)}</title>
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
<script type="application/ld+json" data-seo>{json.dumps(ld,ensure_ascii=False)}</script>
'''
def blurb(p):
    a=p['alt']
    if ':' in a:
        t=a.split(':',1)[1].strip();return t[0].upper()+t[1:]+'.'
    return f"A {p['name']} picture from the Moonmist, ready to colour."
def build(p):
    s=src
    title,desc,url,seo=head_seo(p)
    # head: base, swap SEO block (title .. json-ld) for this page's
    s=s.replace('<head>\n','<head>\n<base href="/">\n',1)
    s=re.sub(r'<title>.*?</script>\n',lambda m:seo,s,count=1,flags=re.S)
    s=s.replace('<link rel="preload" as="image" href="assets/sky.webp" fetchpriority="high">\n','',1)
    # hero titles
    s=re.sub(r'<div class="titles"><h1 id="t">.*?</h1><p>.*?</p></div>',
             f'<div class="titles"><h1 id="t">{E(p["name"])} colouring page</h1><p>Free to print or paint on screen</p></div>',s,count=1)
    # gallery -> single page
    others=[o for o in live if o['id']!=p['id']]
    same=[o for o in others if set(o['tags'])&set(p['tags'])]; more=(same+[o for o in others if o not in same])[:4]
    cards=''.join(f'''<div class="card"><a class="thumb" href="art/{o['id']}"><img src="assets/colour/thumbs/{o['art'].replace('.png','.webp')}" width="420" height="420" loading="lazy" alt="{E(o['alt'])}, free to print"></a><p class="cname"><a href="art/{o['id']}">{E(o['name'])}</a></p></div>''' for o in more)
    bookline=''
    if p['book'] is not None:
        b=p['book'];bookline=f'<a class="bookline" href="books/book-{b}/"><img src="assets/book-{b}-sm.webp" alt="" width="44" height="58">From Book {b}: {E(BOOKS.get(b,""))}. Read the story</a>'
    pin=f'data-pin-media="{BASE}/assets/pins/colour-{p["id"]}.jpg" data-pin-url="{url}" data-pin-description="Free {E(p["name"])} colouring page for kids aged 4 to 7. Print it or paint it on screen at Starcora."'
    single=f'''<section class="gallery" id="gallery">
  <article class="one">
    <div class="big"><img src="assets/colour/{p['art']}" width="1000" height="1000" alt="{E(p['alt'])}, free colouring page to print" {pin}></div>
    <div class="info">
      <span class="tag">Free colouring page</span>
      <h2>Colour {E(p['name'])}</h2>
      <p>{E(blurb(p))} Tap <b>Paint</b> to colour it on screen, or <b>Print</b> to colour it at the table.</p>
      <div class="btns"><button class="pill" data-paint="{p['id']}">Paint</button><button class="pill alt" data-print="{p['id']}">Print</button></div>
      {bookline}
    </div>
  </article>
  <h2 class="shelf">More colouring pages</h2>
  <div class="grid">{cards}</div>
  <a class="allbtn" href="art">See all colouring pages</a>
</section>'''
    s=re.sub(r'<section class="gallery" id="gallery">.*?\n</section>',lambda m:single,s,count=1,flags=re.S)
    s=s.replace('<script>\nconst svgUrl',f'<script>window.SINGLE={json.dumps(p["id"])};</script>\n<script>\nconst svgUrl',1)
    # hidden pin picture for this page
    s=re.sub(r'<div id="pinimg" hidden><img data-src="assets/pins/[^"]+"',f'<div id="pinimg" hidden><img data-src="assets/pins/colour-{p["id"]}.jpg"',s,count=1)
    s=re.sub(r'(<div id="pinimg" hidden><img [^>]*?alt=")[^"]*(" data-pin-description=")[^"]*"',lambda m:m[1]+f'Free {E(p["name"])} colouring page for kids'+m[2]+f'Free {E(p["name"])} colouring page for kids aged 4 to 7. Print it or paint it on screen at Starcora."',s,count=1)
    s=s.replace('<a href="art.html" aria-current="page">','<a href="art.html" aria-current="page">',1)
    open(os.path.join(PUB,'art',p['id']+'.html'),'w',encoding='utf8').write(s)
for p in live: build(p)
# sitemap: replace the colouring-page block
sm_path=os.path.join(PUB,'sitemap.xml');sm=open(sm_path,encoding='utf8').read()
sm=re.sub(r'\s*<!-- colouring pages: built by tools/build_art_pages.py -->.*?<!-- /colouring pages -->','',sm,flags=re.S)
entries='\n'.join(f'''  <url>
    <loc>{BASE}/art/{p['id']}</loc>
    <lastmod>{p['added']}</lastmod>
    <image:image><image:loc>{BASE}/assets/colour/{p['art']}</image:loc><image:title>{E(p['name'])} colouring page</image:title></image:image>
  </url>''' for p in live)
sm=sm.replace('</urlset>',f'  <!-- colouring pages: built by tools/build_art_pages.py -->\n{entries}\n  <!-- /colouring pages -->\n</urlset>')
open(sm_path,'w',encoding='utf8').write(sm)
print(f'{len(live)} live of {len(pages)} colouring pages (date {today}); waiting:',[p["id"]+' '+p["added"] for p in pages if p not in live])

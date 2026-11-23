#!/usr/bin/env python3
"""One-off (23 Nov 2026): add Printables to every page's menu, menu panel and footer.
Menu order: left Home, Storybooks, Videos, Art | right Activities, Printables, Grown-ups."""
import re,os,sys
PUB=sys.argv[1] if len(sys.argv)>1 else 'public'
done=[]
for root,_,files in os.walk(PUB):
    if '/books/' in root+'/' : continue
    for f in files:
        if not f.endswith('.html'): continue
        p=os.path.join(root,f);s=open(p,encoding='utf8').read()
        if 'class="menu left"' not in s or 'printables/index.html' in s: continue
        m=re.search(r'<a href="([^"]*)activities/index\.html"( aria-current="page")?><img class="ni"( loading="lazy")? src="([^"]*)assets/nav/activities\.webp"',s)
        if not m: print('no activities link',p);continue
        pre,ipre=m.group(1),m.group(4)
        cur=' aria-current="page"' if os.path.normpath(p).endswith(os.path.normpath('printables/index.html')) else ''
        def link(lazy): return f'<a href="{pre}printables/index.html"{cur}><img class="ni"{lazy} src="{ipre}assets/nav/printables.webp" alt="" width="48" height="48">Printables</a>'
        # desktop menus: move Art to the end of the left menu, add Printables after Activities on the right
        L=re.search(r'<nav class="menu left"[^>]*>(.*?)</nav>',s,re.S);R=re.search(r'<nav class="menu right"[^>]*>(.*?)</nav>',s,re.S)
        art=re.search(r'<a href="[^"]*art\.html"[^>]*><img class="ni"[^>]*>Art</a>',R.group(1)).group(0)
        rnew=R.group(1).replace(art,'')
        rnew=re.sub(r'(<a href="[^"]*activities/index\.html"[^>]*><img class="ni"[^>]*>Activities</a>)',lambda x:x.group(1)+link(''),rnew,1)
        s=s[:R.start(1)]+rnew+s[R.end(1):]
        L=re.search(r'<nav class="menu left"[^>]*>(.*?)</nav>',s,re.S)
        s=s[:L.end(1)]+art+s[L.end(1):]
        # panel
        P=re.search(r'<nav class="menu-panel"[^>]*>(.*?)</nav>',s,re.S)
        pnew=re.sub(r'(<a href="[^"]*activities/index\.html"[^>]*><img class="ni"[^>]*>Activities</a>)',lambda x:x.group(1)+link(' loading="lazy"'),P.group(1),1)
        s=s[:P.start(1)]+pnew+s[P.end(1):]
        # footer
        s=re.sub(r'(<nav aria-label="Footer">.*?<a href="[^"]*activities/index\.html">Printable activities</a>)',lambda x:x.group(1)+f'<a href="{pre}printables/index.html">Printable storybooks</a>',s,1,flags=re.S)
        open(p,'w',encoding='utf8').write(s);done.append(p)
print(len(done),'pages updated')

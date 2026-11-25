#!/usr/bin/env python3
"""One-off (25 Nov 2026): add Games to every page's menu and menu panel (before Activities).
Menu order: left Home, Storybooks, Videos, Art | right Games, Activities, Print & Play, Grown-ups."""
import re,os,sys
PUB=sys.argv[1] if len(sys.argv)>1 else 'public'
n=0
for root,_,files in os.walk(PUB):
    if '/books/' in root+'/' or '/games/oros-check-up' in root: continue
    for f in files:
        if not f.endswith('.html'): continue
        p=os.path.join(root,f);s=open(p,encoding='utf8').read()
        if 'class="menu right"' not in s or 'assets/nav/games.webp' in s: continue
        m=re.search(r'<a href="([^"]*)activities/index\.html"( aria-current="page")?><img class="ni"( loading="lazy")? src="([^"]*)assets/nav/activities\.webp"',s)
        if not m: print('no activities link',p);continue
        pre,ipre=m.group(1),m.group(4)
        here=os.path.normpath(p).endswith(os.path.normpath('games/index.html'))
        cur=' aria-current="page"' if here else ''
        href=f'{pre}games/index.html' if not here else 'index.html'
        def link(lazy): return f'<a href="{href}"{cur}><img class="ni"{lazy} src="{ipre}assets/nav/games.webp" alt="" width="48" height="48">Games</a>'
        for nav,lazy in (('menu right',''),('menu-panel',' loading="lazy"')):
            N=re.search(r'<nav class="'+nav+r'"[^>]*>(.*?)</nav>',s,re.S)
            new=re.sub(r'(<a href="[^"]*activities/index\.html"[^>]*><img class="ni")',lambda x:link(lazy)+x.group(1),N.group(1),1)
            s=s[:N.start(1)]+new+s[N.end(1):]
        open(p,'w',encoding='utf8').write(s);n+=1
print(n,'pages updated')

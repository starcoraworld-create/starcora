#!/usr/bin/env python3
"""Make a colouring page pin (1000 x 1500) in the same style as the first 11 (colour-oro.jpg template).
Usage: make_colour_pin.py line_art.png "Name" out.jpg   (fonts from Drive 04 Website > Tools > pin fonts)"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
HERE=os.path.dirname(os.path.abspath(__file__)); PUB=os.path.join(os.path.dirname(HERE),'public')
FONTS=os.environ.get('PIN_FONTS','/home/claude/work/tools/pin fonts')
art, name, out = sys.argv[1], sys.argv[2], sys.argv[3]
bg=Image.open(os.path.join(PUB,'assets/pins/colour-oro.jpg')).convert('RGB')
d=ImageDraw.Draw(bg)
d.rounded_rectangle((120,240,879,974),radius=32,fill=(255,255,255))
d.rounded_rectangle((50,1008,950,1446),radius=34,fill=(58,37,56))
a=Image.open(art).convert('L'); bb=Image.eval(a,lambda v:255-v).getbbox(); a=a.crop(bb)
s=min(640/a.width,600/a.height); a=a.resize((round(a.width*s),round(a.height*s)),Image.LANCZOS)
bg.paste(a.convert('RGB'),(500-a.width//2,607-a.height//2))
F=lambda f,n: ImageFont.truetype(os.path.join(FONTS,f),n)
def wrap(text,font,maxw):
    words=text.split();lines=[''];
    for w in words:
        t=(lines[-1]+' '+w).strip()
        if d.textlength(t,font=font)<=maxw: lines[-1]=t
        else: lines.append(w)
    return lines
size=70
while True:
    tf=F('fraunces600.ttf',size); lines=wrap(name,tf,820)+['colouring page']
    if len(lines)<=3 and all(d.textlength(l,font=tf)<=820 for l in lines): break
    size-=4
sf=F('nunito-latin-600-normal.ttf',34); uf=F("nunito-latin-700-normal.ttf",34)
sub=['Free to print or paint on screen.','For kids aged 4 to 7.']
lh=round(size*1.1); block=len(lines)*lh+12+2*40+20+38
y=1008+(438-block)//2
for l in lines:
    d.text((500,y),l,font=tf,fill=(255,255,255),anchor='mt'); y+=lh
y+=12
for l in sub:
    d.text((500,y),l,font=sf,fill=(239,220,240),anchor='mt'); y+=40
y+=20
d.text((500,y),'starcora.world',font=uf,fill=(236,190,92),anchor='mt')
bg.save(out,quality=88,optimize=True,progressive=True)

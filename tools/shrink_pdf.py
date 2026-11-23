#!/usr/bin/env python3
"""Shrink a printable PDF without changing how it prints (23 Nov 2026).
1. Points every repeated copy of the same picture at one copy (the border icons repeat on every page).
2. Stores big pictures (over 150 KB) as quality-90 JPEGs at the same resolution; transparency masks are kept.
Usage: python3 tools/shrink_pdf.py in.pdf out.pdf   (needs: pip install pikepdf pillow)
Always compare pages before and after (render both with pdftoppm and look)."""
import sys, io, hashlib, pikepdf
src, dst = sys.argv[1], sys.argv[2]
pdf = pikepdf.open(src); canon = {}
def key(o):
    h = hashlib.sha1(o.read_raw_bytes())
    for k in ('/Width', '/Height', '/Filter', '/BitsPerComponent', '/DecodeParms'): h.update(repr(o.get(k)).encode())
    sm = o.get('/SMask')
    if sm is not None: h.update(hashlib.sha1(sm.read_raw_bytes()).digest())
    return h.hexdigest()
def walk(res):
    xo = res.get('/XObject')
    if xo is None: return
    for name in list(xo.keys()):
        o = xo[name]
        if o.get('/Subtype') == pikepdf.Name.Image:
            k = key(o)
            if k in canon:
                if canon[k].objgen != o.objgen: xo[name] = canon[k]
            else: canon[k] = o
        elif o.get('/Subtype') == pikepdf.Name.Form and '/Resources' in o: walk(o.Resources)
for p in pdf.pages: walk(p.Resources)
pdf.remove_unreferenced_resources()
from PIL import Image
for o in list(pdf.objects):
    if isinstance(o, pikepdf.Stream) and o.get('/Subtype') == pikepdf.Name.Image and o.get('/Filter') == pikepdf.Name.FlateDecode and int(o.get('/BitsPerComponent', 8)) == 8:
        raw = len(o.read_raw_bytes())
        if raw < 150000: continue
        try: im = pikepdf.PdfImage(o).as_pil_image()
        except Exception: continue
        if im.mode == 'RGBA': im = im.convert('RGB')
        if im.mode != 'RGB': continue
        b = io.BytesIO(); im.save(b, 'JPEG', quality=90, subsampling=0, optimize=True)
        if b.tell() > raw * 0.8: continue
        o.write(b.getvalue(), filter=pikepdf.Name.DCTDecode)
        if '/DecodeParms' in o: del o['/DecodeParms']
pdf.save(dst, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
print('done', dst)

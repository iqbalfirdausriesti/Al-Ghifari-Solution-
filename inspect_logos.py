import os, glob, re

for f in sorted(glob.glob("logos/*.svg")):
    with open(f, encoding="utf-8") as fp:
        c = fp.read()
    vb = re.search(r'viewBox=["\']([^"\']+)["\']', c)
    w = re.search(r'width=["\']([^"\']+)["\']', c)
    h = re.search(r'height=["\']([^"\']+)["\']', c)
    vb_str = vb.group(1) if vb else "None"
    w_str = w.group(1) if w else "None"
    h_str = h.group(1) if h else "None"
    print(f"{f:20} -> viewBox: {vb_str:25} w: {w_str:10} h: {h_str}")

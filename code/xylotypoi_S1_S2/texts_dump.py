import pymupdf, json, sys
pdf, out = sys.argv[1], sys.argv[2]
doc = pymupdf.open(pdf); p = doc[0]
txt = p.get_text("dict")
spans=[]
for b in txt["blocks"]:
    for l in b.get("lines",[]):
        d=l["dir"]
        for s in l["spans"]:
            x0,y0,x1,y1=s["bbox"]
            spans.append(dict(x0=x0,y0=y0,x1=x1,y1=y1,size=s["size"],font=s["font"],dir=(round(d[0],3),round(d[1],3)),text=s["text"],color=s["color"]))
horiz=[s for s in spans if s["dir"]==(1.0,0.0)]
vert=[s for s in spans if s["dir"]==(0.0,-1.0)]
other=[s for s in spans if s["dir"] not in ((1.0,0.0),(0.0,-1.0))]
def group(items, axis):
    if axis=='h': items=sorted(items,key=lambda s:(round(s["y1"]),s["x0"]))
    else: items=sorted(items,key=lambda s:(round(s["x0"]),-s["y1"]))
    out=[]
    for s in items:
        if out:
            g=out[-1]
            if axis=='h' and abs(g["y1"]-s["y1"])<3.5 and s["x0"]-g["x1"]<5 and s["x0"]-g["x1"]>-3:
                g["text"]+=s["text"]; g["x1"]=max(g["x1"],s["x1"]); g["y0"]=min(g["y0"],s["y0"]); g["fonts"].add(s["font"]); continue
            if axis=='v' and abs(g["x0"]-s["x0"])<3.5 and g["y0"]-s["y1"]<5 and g["y0"]-s["y1"]>-3:
                g["text"]+=s["text"]; g["y0"]=min(g["y0"],s["y0"]); g["x1"]=max(g["x1"],s["x1"]); g["fonts"].add(s["font"]); continue
        out.append(dict(x0=s["x0"],y0=s["y0"],x1=s["x1"],y1=s["y1"],text=s["text"],fonts={s["font"]},size=s["size"],color=s["color"],dir=s["dir"]))
    return out
allg=group(horiz,'h')+group(vert,'v')+[dict(x0=s["x0"],y0=s["y0"],x1=s["x1"],y1=s["y1"],text=s["text"],fonts={s["font"]},size=s["size"],color=s["color"],dir=s["dir"]) for s in other]
for g in allg: g["fonts"]=sorted(g["fonts"])
json.dump(allg, open(out,"w"), ensure_ascii=False, indent=0)
print(len(allg))


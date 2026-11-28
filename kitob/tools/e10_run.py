import pymupdf, numpy as np, sys
sys.path.insert(0,'tools')
R=pymupdf.Rect
SRC="Kimyo_1-qism_yakuniy_v3.pdf"
base=pymupdf.open(SRC)
W,H=base[0].rect.width,base[0].rect.height
TOP,BOT=74,780
GAPX=22
def runs_of(n):
    pm=base[n].get_pixmap(dpi=72,colorspace=pymupdf.csGRAY)
    a=np.frombuffer(pm.samples,np.uint8).reshape(pm.h,pm.w)
    ink=(a<240).sum(1)>0
    rs=[];s=None
    for y in range(52,783):
        if ink[y] and s is None:s=y
        if not ink[y] and s is not None:rs.append((s,y));s=None
    return rs
blocks=[]  # (pno,y0,y1,gap_before)
for n in range(81,91):
    rs=runs_of(n)
    for i,(a,b) in enumerate(rs):
        gap=(a-rs[i-1][1]) if i else None
        blocks.append([n,a,b,gap])
# layout
pages=[[] for _ in range(10)]
pi=0;y=TOP
for k,(n,a,b,g) in enumerate(blocks):
    h=b-a
    gap=0 if y==TOP else (g if g is not None else GAPX)
    if y!=TOP and y+gap+h>BOT:
        pi+=1;y=TOP;gap=0
    ny=y+gap
    pages[pi].append((n,a,b,ny))
    y=ny+h
    if pi>=10: raise SystemExit("overflow")
for i,p in enumerate(pages):
    print(82+i,[(x[0]+1,x[1],x[2],round(x[3],1)) for x in p], "end", round(max([x[3]+x[2]-x[1] for x in p] or [0]),1))
if len(sys.argv)>1 and sys.argv[1]=="dry":raise SystemExit
def strip(n,clip):
    t=pymupdf.open();t.insert_pdf(base,from_page=n,to_page=n)
    pg=t[0];c=R(clip)
    outs=[R(0,0,W,c.y0),R(0,c.y1,W,H)]
    for r in outs:
        if r.height>0.01: pg.add_redact_annot(r,fill=False)
    pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    return t
out=pymupdf.open()
out.insert_pdf(base,from_page=81,to_page=90)
for i,p in enumerate(pages):
    pg=out[i]
    pg.add_redact_annot(R(0,52,W,783),fill=False)
    pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_REMOVE,graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    for n,a,b,ny in p:
        clip=R(0,a-3,W,b+3)
        s=strip(n,clip)
        dy=ny-a
        pg.show_pdf_page(R(0,clip.y0+dy,W,clip.y1+dy),s,0,clip=clip)
out.save("parts_e/e10.pdf",garbage=3,deflate=True)

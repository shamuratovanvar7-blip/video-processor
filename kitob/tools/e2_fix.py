import pymupdf
R=pymupdf.Rect
SRC='Kimyo_1-qism_yakuniy_v3.pdf'
def strip(snap, clip, W, H):
    s=pymupdf.open('pdf',snap); pg=s[0]; c=R(clip)
    for r in [R(0,0,W,c.y0),R(0,c.y1,W,H),R(0,c.y0,c.x0,c.y1),R(c.x1,c.y0,W,c.y1)]:
        if r.width>.01 and r.height>.01: pg.add_redact_annot(r,fill=False)
    pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    return s
def snap(doc,n):
    t=pymupdf.open(); t.insert_pdf(doc,from_page=n,to_page=n); return t.tobytes()
def move(doc,n,rect,items,gfx=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED):
    p=doc[n]; W,H=p.rect.width,p.rect.height; sb=snap(doc,n)
    srcs=[(strip(sb,c,W,H),R(c),dy) for c,dy in items]
    p.add_redact_annot(R(rect),fill=False)
    p.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_REMOVE,graphics=gfx,text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    for s,c,dy in srcs:
        p.show_pdf_page(R(c.x0,c.y0+dy,c.x1,c.y1+dy),s,0,clip=c)
doc=pymupdf.open(SRC)
# p13: o'ng ustun elementlarini chap ustun balandligiga teng taqsimlash
cuts=[110,168,233,290,350,395,448]
items=[((306,cuts[i],548,cuts[i+1]),round(i*20.2,1)) for i in range(6)]
move(doc,12,(306,110,548,450),items)
# p16: 3-katak mazmunini vertikal markazlash
move(doc,15,(378,603,525,725),[((378,603,525,725),24)],gfx=pymupdf.PDF_REDACT_LINE_ART_NONE)
out=pymupdf.open(); out.insert_pdf(doc,from_page=9,to_page=17)
out.save('parts_e/e2.pdf',garbage=3,deflate=True)
for i in range(9):
    out[i].get_pixmap(dpi=110).save(f'render/e2_after_{10+i}.png')

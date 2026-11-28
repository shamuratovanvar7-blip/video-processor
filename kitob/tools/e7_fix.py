import sys, pymupdf
sys.path.insert(0, '/home/user/video-processor/kitob/tools')
import e5_fix as E
import e6_lib as L
R = pymupdf.Rect
SRC = 'Kimyo_1-qism_yakuniy_v3.pdf'


def grow_panel(doc, pno, panel, new_y1):
    x0, y0, x1, y1 = panel
    dy = new_y1 - y1
    clip = (x0 + 10, y0 + 1, x1 - 10, y1 - 1)
    E.move(doc, pno, (x0 - 1, y0 - 1, x1 + 1, y1 + 1), [(clip, dy / 2)],
           between=lambda: L.fill_rrect(doc[pno], (x0, y0, x1, new_y1), 9, L.PALE))


doc = pymupdf.open(SRC)
# 56: pastki-chap "Zarralar soni" kartasi o'ng qo'shnisi bilan bir xil pastki chegaraga
E.extend_card(doc, 55, (52.4, 567.7, 287.3, 686.3), 10.5, 7)
# 57: o'ng "Zarralar soni va hajm" kartasi chap qo'shnisi bilan bir xil pastki chegaraga
E.extend_card(doc, 56, (307.4, 84.7, 542.3, 203.3), 10.5, 7)
# 61, 62, 63: o'ng havorang panellar chap "Umumiy ko'rinishi" katagi pastigacha cho'ziladi
grow_panel(doc, 60, (283.5, 559.5, 541.5, 630.0), 640.2)
grow_panel(doc, 61, (269.2, 108.0, 527.2, 178.5), 202.2)
grow_panel(doc, 61, (269.2, 463.5, 527.2, 549.0), 558.4)
grow_panel(doc, 62, (283.5, 108.0, 541.5, 192.8), 202.2)
out = pymupdf.open(); out.insert_pdf(doc, from_page=54, to_page=62)
out.save('parts_e/e7.pdf', garbage=3, deflate=True)
base = pymupdf.open(SRC)
for i in range(9):
    base[54 + i].get_pixmap(dpi=110).save(f'render/e7_before_{55+i}.png')
    out[i].get_pixmap(dpi=110).save(f'render/e7_after_{55+i}.png')

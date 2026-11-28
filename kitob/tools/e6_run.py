import sys; sys.path.insert(0,'/home/user/video-processor/kitob/tools')
from e6_lib import *
import e6_p51
SRC="/home/user/video-processor/kitob/Kimyo_1-qism_yakuniy_v3.pdf"
def build():
    doc = pymupdf.open(SRC)
    # p48 (idx 47)
    equalize(doc, 47, (294.7, 354.0, 527.3, 531.0), 57.1, [383, 415.8, 449, 467], [0, 16, 16, 34, 50])
    equalize(doc, 47, (294.7, 126.0, 527.3, 339.8), 10.5, [], [0])
    # p50 (idx 49)
    equalize(doc, 49, (53.2, 519.8, 286.5, 637.5), 57.8, [549.3, 579.3, 596.7], [0, 18, 34, 48])
    # p51 formula row: third box -> same height as first two
    equalize(doc, 50, (389.2, 717.7, 541.5, 741.8), 13.5, [], [6.75], small=True)
    e6_p51.do51(doc, 50)
    # p52 (idx 51)
    equalize(doc, 51, (53.2, 90.0, 206.3, 114.0), 13.5, [], [6.75], small=True)
    equalize(doc, 51, (53.2, 246.7, 206.3, 335.3), 32.2, [274.5, 308.6], [0, 10, 22])
    equalize(doc, 51, (375.0, 246.7, 527.3, 366.8), 0.7, [], [0])
    equalize(doc, 51, (53.2, 658.6, 206.3, 726.1), 15.8, [], [7.9])
    equalize(doc, 51, (213.7, 658.6, 366.8, 726.1), 15.8, [], [7.9])
    return doc
if __name__ == "__main__":
    doc = build()
    for n in (48, 50, 51, 52):
        doc[n-1].get_pixmap(dpi=110).save(f"/tmp/w/a{n}.png")

import os
import sys

from PIL import Image
import numpy as np

# Functions to convert images <-> 24-bit arrays

def toimage(a):
    r = (a >> 16).astype(np.uint8)
    g = (a >>  8).astype(np.uint8)
    b = (a      ).astype(np.uint8)
    return Image.merge("RGB", [Image.fromarray(c) for c in (r, g, b)])

def toarray(im):
    (r,g,b) = [np.asarray(c, np.int).astype(np.int) for c in im.convert("RGB").split()]
    return (r << 16) + (g << 8) + b

if __name__ == '__main__':
    sources = sys.argv[1:]
    im = Image.open(sources[0])
    h = im.size[1] * 1024 / im.size[0]
    rows = (len(sources) + 3) / 4

    if not os.access("grade.png", os.R_OK):
        print "Making template grade.png"
        grade = Image.new("RGB", (4096, h * rows + 4096))

        ramps = np.arange(2 ** 24)
        ramps.resize((4096, 4096))
        grade.paste(toimage(ramps), (0, rows * h))

        for i,fn in enumerate(sources):
            print "%d/%d %s" % (i + 1, len(sources), fn)
            pic = Image.open(fn)
            pic.draft("RGB", (1024, 1024))
            pic = pic.resize((1024, h), Image.NEAREST)
            x = 1024 * (i % 4)
            y = h * (i / 4)
            grade.paste(pic, (x, y))
        grade.save("grade.png")
        print "Now edit grade.png then re-run multigrader.py"
    else:
        print "Applying grade.png to all images"
        grade = Image.open("grade.png")
        h = grade.size[1]
        clut = toarray(grade.crop((0, h - 4096, 4096, h))).flatten()
        for i,fn in enumerate(sources):
            print "%d/%d %s" % (i + 1, len(sources), fn)
            pic = toarray(Image.open(fn))
            toimage(clut[pic]).save(fn, quality = 99)
        os.rename("grade.png", "used-grade.png")

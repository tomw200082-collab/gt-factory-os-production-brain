from PIL import Image, ImageFilter, ImageChops
CUT='../dbx/cutouts'
TEAS = {'fresh':'0B7A5588','fresh_sf':'0B7A5671','detox':'0B7A5636','detox_sf':'0B7A5688',
        'energy':'0B7A5627','calm':'0B7A5610','consciousness':'0B7A5699','revive':'0B7A5645',
        'desertea':'0B7A5616','namastea':'0B7A5656'}

def cut(im):
    """Keep pixels that are dark OR colourful. The studio drop-shadow is light AND
    neutral, so it drops out; the cream sugar-free label is light but warm, so it stays."""
    rgb = im.convert('RGB')
    r,g,b = rgb.split()
    L = rgb.convert('L')
    mx = ImageChops.lighter(ImageChops.lighter(r,g),b)
    mn = ImageChops.darker(ImageChops.darker(r,g),b)
    sat = ImageChops.subtract(mx,mn)
    dark = L.point(lambda v: 255 if v < 205 else 0)
    col  = sat.point(lambda v: 255 if v > 14 else 0)
    m = ImageChops.lighter(dark, col).convert('L')
    m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))  # close holes
    m = m.filter(ImageFilter.GaussianBlur(0.6))
    out = rgb.convert('RGBA'); out.putalpha(m); return out

def trim(im, pad=4):
    bb = im.split()[-1].getbbox()
    if not bb: return im
    l,t,r,b = bb
    return im.crop((max(0,l-pad),max(0,t-pad),min(im.width,r+pad),min(im.height,b+pad)))

def square(im, size):
    im=im.copy(); im.thumbnail((size,size), Image.LANCZOS)
    c=Image.new('RGBA',(size,size),(0,0,0,0)); c.paste(im,((size-im.width)//2,(size-im.height)//2),im)
    return c

for name,f in TEAS.items():
    s = trim(cut(Image.open(f'{CUT}/{f}_cutout.png')))
    square(s,620).save(f'assets/{name}.png')
    cv = s.copy(); cv.thumbnail((900,1500), Image.LANCZOS); cv.save(f'assets/cv_{name}.png')

# proof: composite the cover bottles on the deep green to check for halos
strip = Image.new('RGB',(1900,720),(14,38,34))
x=30
for k in ['fresh','detox','energy','calm','consciousness','revive']:
    im=Image.open(f'assets/cv_{k}.png'); im.thumbnail((300,640), Image.LANCZOS)
    strip.paste(im,(x,720-im.height-30),im); x+=im.width+12
strip.save('halo_check.png'); print('ok')

# ── trim the residual shadow smear under each bottle ─────────────────────────
import numpy as np
for name in TEAS:
    for pre in ('', 'cv_'):
        f = f'assets/{pre}{name}.png'
        im = Image.open(f).convert('RGBA')
        a = np.array(im)[:, :, 3]
        rgb = np.array(im.convert('L'))
        solid = (a > 200) & (rgb < 200)              # real bottle body, not shadow
        rows = solid.sum(axis=1)
        thr = max(6, int(im.width * 0.10))
        keep = np.where(rows > thr)[0]
        if len(keep):
            base = keep[-1] + 2
            arr = np.array(im); arr[base:, :, 3] = 0
            im = Image.fromarray(arr)
            bb = im.split()[-1].getbbox()
            if bb: im = im.crop(bb)
        im.save(f)
    print('base-trim', name)

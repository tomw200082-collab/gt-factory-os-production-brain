from PIL import Image, ImageFilter, ImageChops
import numpy as np, glob, os

def cut_studio(im):
    """Drop a light, near-neutral studio background; keep dark or colourful content."""
    rgb = im.convert('RGB')
    r,g,b = rgb.split(); L = rgb.convert('L')
    mx = ImageChops.lighter(ImageChops.lighter(r,g),b)
    mn = ImageChops.darker(ImageChops.darker(r,g),b)
    sat = ImageChops.subtract(mx,mn)
    m = ImageChops.lighter(L.point(lambda v:255 if v<225 else 0),
                           sat.point(lambda v:255 if v>18 else 0)).convert('L')
    m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    m = m.filter(ImageFilter.GaussianBlur(0.6))
    out = rgb.convert('RGBA'); out.putalpha(m); return out

def content_crop(im, pad=6):
    a = np.array(im)[:,:,3]
    ys, xs = np.where(a > 40)
    if len(xs)==0: return im
    l,r,t,b = xs.min(), xs.max(), ys.min(), ys.max()
    return im.crop((max(0,l-pad), max(0,t-pad), min(im.width,r+pad+1), min(im.height,b+pad+1)))

def square(im, size=560):
    im=im.copy(); im.thumbnail((size,size), Image.LANCZOS)
    c=Image.new('RGBA',(size,size),(0,0,0,0)); c.paste(im,((size-im.width)//2,(size-im.height)//2),im)
    return c

for f in sorted(glob.glob('raw/*.png')):
    k = os.path.basename(f)[:-4]
    im = Image.open(f).convert('RGBA')
    corners = [im.getpixel(p)[:3] for p in [(2,2),(im.width-3,2),(2,im.height-3),(im.width-3,im.height-3)]]
    if all(min(c) >= 225 for c in corners):
        im = cut_studio(im)
        im = content_crop(im)
    else:
        im = content_crop(im, pad=0)
    square(im, 560).save(f'assets/{k}.png')
    print(k, im.size)

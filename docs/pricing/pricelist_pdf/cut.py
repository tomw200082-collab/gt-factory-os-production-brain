"""Cut every product out of its studio background onto transparency.

All 31 source photos are studio packshots on a flat, evenly-lit backdrop — grey
seamless for the bottles, warm cream for the powders, white for the ODK pouches
and the accessories. So the honest mask is not a luminance threshold (that eats
the cream FRESH label and keeps the grey shadow); it is DISTANCE FROM THE
BACKDROP COLOUR, sampled from the frame's own border.

  keep = ||px - median(border)|| > tau

Whatever the mask leaves floating is removed by flooding the background in from
the frame edge — whatever the flood cannot reach is the object. That is PIL's
C-level floodfill, so it stays fast.

Working size is 1400 px: a 24 mm tile at 300 dpi needs 284 px, so this is 5x
more resolution than the page can print.
"""
import os
import numpy as np
from PIL import Image, ImageDraw
from PIL.ImageFilter import MaxFilter, MinFilter, GaussianBlur

OUT = 'cut'
WORK = 1400
BG = 90
os.makedirs(OUT, exist_ok=True)


def _smooth(v, k):
    p = np.pad(v, ((k // 2, k // 2), (0, 0)), mode='edge')
    ker = np.ones(k) / k
    return np.stack([np.convolve(p[:, c], ker, 'valid') for c in range(3)], 1)


def backdrop(a, band=24, top=0.05, k=41):
    """A smooth 2-D model of the backdrop, built from the frame's own margins.

    A studio sweep is neither flat nor a simple ramp: it is brightest where the
    light hits, so a row of the bottle frames reads 132 · 177 · 122 across. Both
    a single median and a left-to-right ramp call that hot centre 'object'.

    It is, however, close to separable — one horizontal lighting profile scaled
    row by row. So take the profile from the object-free strip at the top of the
    frame, then scale it down the page using the left and right margins.
    """
    h, w, _ = a.shape
    prof = np.median(a[:max(8, int(h * top))], 0)                    # (w, 3)
    prof = _smooth(prof, 31)
    edge = np.r_[np.arange(band), np.arange(w - band, w)]
    prof = prof / np.maximum(prof[edge].mean(0), 1e-6)               # ~1 at margins

    side = np.concatenate([a[:, :band] / prof[None, :band],
                           a[:, -band:] / prof[None, -band:]], 1)
    scale = _smooth(np.median(side, 1), k)                           # (h, 3)
    return scale[:, None, :] * prof[None, :, :]


def raw_mask(im, mode, tau, dark, sat):
    """`flat` — distance from the modelled backdrop. For packshots on a plain
    sweep it separates a white bag from a cream wall, which no threshold can.

    `sweep` — dark OR colourful. The bottle frames carry a visible horizon where
    wall meets table, and a horizon is not separable, so the backdrop model
    misfires there. But a brown bottle on a grey sweep is trivially dark, and
    every label is saturated, so the old rule is the right tool for those 11.
    """
    if mode == 'sweep':
        a = np.array(im)
        L = np.array(im.convert('L')).astype(int)
        S = np.array(im.convert('HSV'))[..., 1].astype(int)
        return (L < dark) | (S > sat)
    a = np.array(im).astype(np.int16)
    d = np.sqrt(((a - backdrop(a)) ** 2).sum(2))
    return d > tau


def keep_blobs(m, frac=0.03, scale=4):
    """Drop specks: keep every component at least `frac` of the largest one.

    Not just the largest — the frother is sold with three loose whisk heads and
    the chasen sits beside its tube, so those photos are legitimately two or four
    separate objects. Components are found at 1/`scale` resolution, which is
    plenty to tell a whisk head from a dust mote.
    """
    a = np.array(m) > 127
    h, w = a.shape
    s = a[::scale, ::scale]
    lab = np.zeros(s.shape, np.int32)
    sizes, cur = {}, 0
    ys, xs = np.nonzero(s)
    for y, x in zip(ys, xs):
        if lab[y, x]:
            continue
        cur += 1
        r = np.zeros(s.shape, bool)
        r[y, x] = True
        while True:
            g = r.copy()
            g[1:] |= r[:-1]; g[:-1] |= r[1:]
            g[:, 1:] |= r[:, :-1]; g[:, :-1] |= r[:, 1:]
            g &= s
            if g.sum() == r.sum():
                break
            r = g
        lab[r] = cur
        sizes[cur] = int(r.sum())
    if not sizes:
        return m
    big = max(sizes.values())
    keep = {k for k, v in sizes.items() if v >= big * frac}
    small = np.isin(lab, list(keep))
    up = np.kron(small, np.ones((scale, scale), bool))[:h, :w]
    if up.shape != a.shape:                       # kron truncation guard
        pad = np.zeros(a.shape, bool)
        pad[:up.shape[0], :up.shape[1]] = up
        up = pad
    return Image.fromarray(((a & up) * 255).astype('uint8'))


def grow_until_stable(seed, allowed):
    r = seed & allowed
    while True:
        g = r.copy()
        g[1:] |= r[:-1]; g[:-1] |= r[1:]
        g[:, 1:] |= r[:, :-1]; g[:, :-1] |= r[:, 1:]
        g &= allowed
        if g.sum() == r.sum():
            return r
        r = g


def fill_holes(m, scale=4):
    """Close the Swiss cheese in a white product on a white backdrop.

    A white bag's own body sits the same distance from the cream sweep as the
    sweep does, so the threshold punches holes straight through the product. The
    fix is topological, not photometric: flood the background inward from the
    frame edge; any background the flood cannot reach is enclosed by the object,
    so it is a hole and belongs to the object.

    The flood runs at 1/`scale` resolution with a MAX-pooled background (a cell
    counts as background if any pixel in it does), which makes `reach` generous
    and therefore makes hole-filling conservative — it can only ever miss a hole,
    never eat real background.
    """
    a = np.array(m) > 127
    h, w = a.shape
    H, W = h // scale, w // scale
    bg = ~a[:H * scale, :W * scale].reshape(H, scale, W, scale).min(axis=(1, 3))
    seed = np.zeros((H, W), bool)
    seed[0], seed[-1], seed[:, 0], seed[:, -1] = True, True, True, True
    reach = grow_until_stable(seed, bg)
    holes = np.kron(bg & ~reach, np.ones((scale, scale), bool))
    out = a.copy()
    out[:holes.shape[0], :holes.shape[1]] |= holes
    return Image.fromarray((out * 255).astype('uint8'))


def object_mask(im, mode, tau, dark, sat, grow, erode):
    """Threshold · open (kill dust) · close (fill pinholes) · drop stray blobs ·
    pull the edge in by `erode` px so no rim of backdrop rides along.

    No flood-fill cleanup: `ImageDraw.floodfill` is a silent no-op on mode-L
    images in Pillow 12.3 and inverted every mask it touched.
    """
    m = Image.fromarray((raw_mask(im, mode, tau, dark, sat) * 255).astype('uint8'))
    m = m.filter(MinFilter(3)).filter(MaxFilter(3))
    m = m.filter(MaxFilter(grow)).filter(MinFilter(grow))
    m = keep_blobs(m)
    m = fill_holes(m)
    if erode:
        m = m.filter(MinFilter(erode))
    return m


def _body(a, mode):
    solid = a[..., 3] > 200
    if mode == 'sweep':
        return solid & (a[..., :3].mean(2) < 120)
    bg = backdrop(a[..., :3].astype(np.int16))
    d = np.sqrt(((a[..., :3].astype(np.int16) - bg) ** 2).sum(2))
    return solid & (d > 55)


def trim_base(im, mode='flat', floor=0.06):
    """Erase the shadow tail below the object's real footprint."""
    a = np.array(im)
    rows = _body(a, mode).sum(1)
    if rows.max() == 0:
        return im
    keep = np.where(rows > rows.max() * floor)[0]
    if len(keep):
        a[keep[-1] + 4:, :, 3] = 0
    return Image.fromarray(a)


def trim_sides(im, mode='flat', floor=0.02, pad=6):
    """Erase the cast shadow beside the object.

    A pale shadow on a pale sweep survives the threshold and is invisible on a
    cream page — but these cutouts also stand on the dark section bands, where a
    stray cream streak beside a bag is the first thing the eye finds. Columns
    that carry no real body are not part of the product."""
    a = np.array(im)
    cols = _body(a, mode).sum(0)
    if cols.max() == 0:
        return im
    keep = np.where(cols > cols.max() * floor)[0]
    if len(keep):
        a[:, :max(0, keep[0] - pad), 3] = 0
        a[:, keep[-1] + pad:, 3] = 0
    return Image.fromarray(a)


def cut(src, dst, mode='flat', tau=26, dark=105, sat=40, grow=5, erode=3, base=1, pad=8, feather=0.8):
    im = Image.open(src).convert('RGB')
    im.thumbnail((WORK, WORK), Image.LANCZOS)
    m = object_mask(im, mode, tau, dark, sat, grow, erode).filter(GaussianBlur(feather))
    out = im.convert('RGBA')
    out.putalpha(m)
    if base:
        out = trim_base(out, mode)
        out = trim_sides(out, mode)
    bb = out.getbbox()
    if bb:
        out = out.crop((max(0, bb[0] - pad), max(0, bb[1] - pad),
                        min(out.width, bb[2] + pad), min(out.height, bb[3] + pad)))
    out.save(os.path.join(OUT, dst))
    print(f'{dst:20s} {out.size}')
    return out


if __name__ == '__main__':
    import sys
    for spec in sys.argv[1:]:
        p = spec.split(':')
        kw = {}
        for kv in p[2:]:
            k, v = kv.split('=')
            kw[k] = float(v) if '.' in v else int(v)
        cut(p[0], p[1], **kw)

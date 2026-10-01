#!/usr/bin/env python3
"""GT Everyday — wholesale pricelist as a hosted static site.

Same page as `build_mobile.py` produces, delivered the way a website should be
rather than the way a forwarded file has to be:

  * Assets are linked, not inlined. The browser gets a ~30 KB HTML document it
    can paint immediately, and the photographs arrive in parallel and stay in
    the cache on the next visit — where the single-file edition re-downloads
    1 MB every time.
  * The four faces are subset to the glyphs this page actually sets. Rubik and
    Heebo ship Latin, Hebrew and Cyrillic; the pricelist uses a few hundred
    characters of that, so the type drops from ~244 KB to a fraction of it.
  * Everything under assets/ and fonts/ is content-stable, so `vercel.json`
    marks it immutable for a year. index.html is never cached, so a rebuild is
    live the moment it deploys.

The catalogue, prices, markup and stylesheet all come from `build_mobile.py`.
This file adds delivery only — it must never restate a figure.

Build:  python3 build_site.py   →  site/
"""
import pathlib
import shutil
import subprocess
import sys

import build_mobile as bm
import build_og

HERE = pathlib.Path(__file__).parent
SITE = HERE / 'site'

# The page sets Hebrew, Latin caps, digits and a short list of marks. Everything
# outside this set is dropped from the fonts, so anything added to the copy in
# build_mobile.py must be reflected here — the extraction below does that
# automatically by reading the rendered page rather than a hand-kept list.
EXTRA = '₪·–—’״׳%&()[]{}<>@/\\|+=*#"\'`~^_  ‎‏'


def page_text(html):
    """Every character the page can set, taken from the page itself."""
    out, depth = [], 0
    for ch in html:
        if ch == '<':
            depth += 1
        elif ch == '>':
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return ''.join(out)


def subset(src, dst, text):
    subprocess.run(
        [sys.executable, '-m', 'fontTools.subset', str(src),
         f'--text={text}', '--flavor=woff2', '--layout-features=*',
         '--no-hinting', '--desubroutinize', f'--output-file={dst}'],
        check=True, capture_output=True)


def build():
    bm.MODE, bm.FONT_EXT = 'site', 'woff2'
    html = bm.render()

    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / 'fonts').mkdir(parents=True)
    shutil.copytree(bm.ASSETS, SITE / 'assets')

    # &nbsp; and friends arrive as entities, so decode before collecting glyphs
    import html as htmlmod
    glyphs = ''.join(sorted(set(htmlmod.unescape(page_text(html))) | set(EXTRA)))

    before = after = 0
    for _, _, file in bm.FACES:
        src = bm.FONTS / file
        dst = SITE / 'fonts' / (file.rsplit('.', 1)[0] + '.woff2')
        subset(src, dst, glyphs)
        before += src.stat().st_size
        after += dst.stat().st_size

    (SITE / 'index.html').write_text(html, encoding='utf-8')
    (SITE / 'vercel.json').write_text("""{
  "headers": [
    {
      "source": "/(assets|fonts)/(.*)",
      "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
    },
    {
      "source": "/",
      "headers": [{ "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" }]
    }
  ]
}
""", encoding='utf-8')

    pdf = HERE / 'GT_pricelist_mobile.pdf'
    if pdf.exists():
        shutil.copy2(pdf, SITE / pdf.name)

    (SITE / 'robots.txt').write_text(
        'User-agent: *\nDisallow: /\n' if not bm.INDEXABLE
        else f'User-agent: *\nAllow: /\nSitemap: {bm.SITE_URL}/\n', encoding='utf-8')
    build_og.build()

    total = sum(f.stat().st_size for f in SITE.rglob('*') if f.is_file())
    print(f'site/  {len(glyphs)} glyphs  ·  fonts {before // 1024} KB → {after // 1024} KB'
          f'  ·  html {(SITE / "index.html").stat().st_size // 1024} KB'
          f'  ·  total {total / 1e6:.2f} MB')


if __name__ == '__main__':
    build()

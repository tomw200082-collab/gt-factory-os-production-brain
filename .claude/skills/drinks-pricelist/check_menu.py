"""Check one Canva menu design against the approved drink figures and against itself.

Input: a structured `read-design` result saved to a file (the JSON the Canva MCP returns when a
read opens a transaction; it is saved to a file when it is too large to return). Read all pages,
then cancel the transaction if you only wanted to check.

    python3 check_menu.py <saved-read.json> [--expect-drinks N]

Checks, per drink page (a page with a `... אופן הכנה:` header):
  - the header's name equals the page title (the heavy 60 px text);
  - cost, recommended price and margin equal the figures file's row for that title;
and for the whole design:
  - no footer catalog label (`gt Ice Matcha · 29` and the like) is left;
  - the list page (the text holding `.....`) names exactly the drink-page titles, with their prices;
  - every WhatsApp link goes to the lead line 972547588132;
  - the number of drink pages equals --expect-drinks, when given.
Exit 0 when clean; otherwise every finding is printed and the exit code is 1.

Titles that differ from the figures file's names by design are mapped in ALIAS.
"""
import json
import re
import sys
from pathlib import Path

FIGURES = Path(__file__).with_name('drinks_final_figures.json')
ALIAS = {"חליטת תה ירוק לואיזה וליים": "חליטת תה ירוק וליים"}
LEAD_LINE = 'https://wa.me/972547588132'
LABEL = re.compile(r'^gt [A-Za-z ]+ · \d+\s*$')


def norm(s: str) -> str:
    return re.sub(r'\s+', ' ', s.replace('׳', "'").replace('’', "'")).strip()


def load(path: str) -> list[tuple[int, dict]]:
    d = json.loads(Path(path).read_text(encoding='utf-8'))
    if isinstance(d, list):
        d = json.loads(d[0]['text'])
    content = d.get('design_content', d)
    numbers = content.get('page_metadata', {}).get('returned_page_indices') or range(1, len(content['pages']) + 1)
    return list(zip(numbers, content['pages']))


def texts(page: dict) -> list[tuple[str, dict]]:
    out = []
    for e in page.get('elements', []):
        for el in [e, *e.get('children', [])]:
            if el.get('type') == 'text':
                out.append((''.join(r['characters'] for r in el['textRegions']), el))
    return out


def main() -> int:
    args = sys.argv[1:]
    expect = int(args[args.index('--expect-drinks') + 1]) if '--expect-drinks' in args else None
    figures = {norm(v['name']): v for v in json.loads(FIGURES.read_text(encoding='utf-8'))['pages'].values()}
    pages = load(args[0])
    problems, drinks, lists = [], [], []
    for n, page in pages:
        tx = texts(page)
        for t, el in tx:
            if LABEL.match(t):
                problems.append(f'p{n}: catalog label left: {t!r}')
            for r in el['textRegions']:
                link = r['formatting'].get('link', '')
                if 'wa.me' in link and not link.startswith(LEAD_LINE):
                    problems.append(f'p{n}: WhatsApp link is not the lead line: {link[:40]}')
            if '.....' in t or re.search(r'\.{4,}\s*₪?\d', t):
                lists.append((n, t))
        header = next((t for t, _ in tx if t.strip().endswith('אופן הכנה:')), None)
        if header is None:
            continue
        title = next((t for t, el in tx if el['textRegions'][0]['formatting']['fontSize'] >= 55
                      and re.search('[֐-׿]', t) and '%' not in t), '')
        title, head = norm(title), norm(header.replace('אופן הכנה:', ''))
        cost = next((t for t, _ in tx if re.fullmatch(r'₪\d+\.\d\d\*?', t.strip())), None)
        price = next((t for t, _ in tx if re.fullmatch(r'₪\d+', t.strip())), None)
        marg = next((t for t, _ in tx if re.fullmatch(r'\d\d%', t.strip())), None)
        drinks.append((n, title, price))
        if head != title:
            problems.append(f'p{n}: header {head!r} != title {title!r}')
        row = figures.get(norm(ALIAS.get(title, title)))
        if row is None:
            problems.append(f'p{n}: no figures row for {title!r}')
            continue
        for label, got, want in (('cost', cost, row['cost']), ('price', price, row['price']), ('margin', marg, row['marg'])):
            if (got or '').strip().rstrip('*') != want.rstrip('*'):
                problems.append(f'p{n} {title}: {label} {got!r} != figures {want!r}')
    if expect is not None and len(drinks) != expect:
        problems.append(f'{len(drinks)} drink pages, expected {expect}')
    listed = []
    for n, t in lists:
        for line in t.split('\n'):
            m = re.match(r'^(.*?)\s*\.{4,}\s*₪?\s*(\d+)\s*$', line.strip())
            if m:
                listed.append((norm(m.group(1)), '₪' + m.group(2), n))
    if not lists:
        problems.append('no list page found')
    want = [(t, p) for _, t, p in drinks]
    got = [(t, p) for t, p, _ in listed]
    for item in want:
        if item not in got:
            problems.append(f'list page lacks {item[0]!r} {item[1]}')
    for item in got:
        if item not in want:
            problems.append(f'list page names {item[0]!r} {item[1]}, which no drink page shows')
    print(f'{len(pages)} pages read · {len(drinks)} drink pages · {len(listed)} list lines')
    for p in problems:
        print('  FAIL', p)
    print('clean' if not problems else f'{len(problems)} finding(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())

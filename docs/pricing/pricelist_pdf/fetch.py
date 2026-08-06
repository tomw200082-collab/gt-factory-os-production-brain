import urllib.request, os, io
from PIL import Image

SHOP = {
 'matcha500':'https://cdn.shopify.com/s/files/1/0484/4319/5552/files/12.png?width=900',
 'matcha22':'https://cdn.shopify.com/s/files/1/0484/4319/5552/files/images_e92d22fb-bf6e-4fbc-b76f-ffe505961033.jpg?width=900',
 'ube1kg':'https://cdn.shopify.com/s/files/1/0484/4319/5552/files/poudre-dube-100-pure-et-naturelle-des-philippines-3436852.webp?width=900',
 'odk_man':'https://cdn.shopify.com/s/files/1/0484/4319/5552/files/UntitledProject_37.webp?width=900',
 'odk_str':'https://cdn.shopify.com/s/files/1/0484/4319/5552/files/14845_strawberry-pouches.webp?width=900',
 'odk_pea':'https://cdn.shopify.com/s/files/1/0484/4319/5552/files/images_11ae1ef7-b1af-4d7a-929c-e46dc676cdd0.jpg?width=900',
 'whisk':'https://cdn.shopify.com/s/files/1/0484/4319/5552/files/images.jpg?width=900',
 'scoop':'https://cdn.shopify.com/s/files/1/0484/4319/5552/files/bamboo-matcha-scoop100000023662-500010.webp?width=900',
 'stand':'https://cdn.shopify.com/s/files/1/0484/4319/5552/files/whiskstand_chasentate_-1_1024x1024_5c915a51-c081-499d-b7eb-fdc39e2e1fde.webp?width=900',
 'bowl':'https://cdn.shopify.com/s/files/1/0484/4319/5552/files/matcha-bowl-cream-spout-1.webp?width=900',
 'glasspot':'https://cdn.shopify.com/s/files/1/0484/4319/5552/files/beautylabthestore-ulika-ximeiou-potiri-zeseos-glass-600ml_2.jpg?width=900',
}
os.makedirs('raw', exist_ok=True)
for k,u in SHOP.items():
    try:
        req=urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0'})
        d=urllib.request.urlopen(req, timeout=45).read()
        Image.open(io.BytesIO(d)).convert('RGBA').save(f'raw/{k}.png')
        print('ok', k)
    except Exception as e:
        print('FAIL', k, e)

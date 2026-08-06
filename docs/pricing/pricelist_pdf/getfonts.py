import urllib.request, re, os
UA='Mozilla/5.0 (Windows NT 6.1; rv:27.0) Gecko/20100101 Firefox/27.0'
os.makedirs('fonts', exist_ok=True)
def grab(fam, weights, out):
    url=f'https://fonts.googleapis.com/css2?family={fam}:wght@{";".join(weights)}&display=swap'
    css=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=40).read().decode()
    blocks=re.findall(r'font-weight:\s*(\d+);.*?src:\s*url\((https://[^)]+)\)', css, re.S)
    for w,u in blocks:
        d=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=40).read()
        p=f'fonts/{out}-{w}.woff'; open(p,'wb').write(d); print(p, len(d))
grab('Heebo',['400','500','700','900'],'heebo')
grab('Frank+Ruhl+Libre',['400','500','700'],'frank')

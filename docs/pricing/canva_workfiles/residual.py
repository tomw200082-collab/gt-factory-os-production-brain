# -*- coding: utf-8 -*-
import json
R=json.load(open("recipes.json"))
# ---- GT price list to the café, EX-VAT (Shopify list / Tom) -----------------
GT={
 "50 מ״ל תרכיז GT":50*0.065, "50 מ״ל מסאלה GT":50*0.065,
 "40 מ״ל תרכיז GT":40*0.065, "40 מ״ל תמצית מסאלה GT":40*0.065,
 "50 מ״ל מאצ'ה (1.8 גר')":1.8*(590/500),
 "50 מ״ל אובה (2 גר')":2*(340/1000),
 "40 מ״ל מחית אפרסק":40*0.060, "40 מ״ל מחית תות":40*0.060, "40 מ״ל מנגו":40*0.060,
}
out=[]
for x in R:
    gt=sum(GT.get(c,0) for c in x["chips"])
    rest=[c for c in x["chips"] if c not in GT]
    out.append(dict(pg=x["pg"],fam=x["fam"],heb=x["heb"],cost=x["cost"],price=x["price"],
                    gt=round(gt,2),resid=round(x["cost"]-gt,2),rest=rest))
json.dump(out,open("residual.json","w"),ensure_ascii=False)

print(f"{'#':>3} {'משקה':<28} {'עלות':>6} {'GT':>6} {'שארית':>7}  מה בשארית")
for z in sorted(out,key=lambda z:-z["resid"]):
    print(f"{z['pg']:3d} {z['heb'][:27]:<28} {z['cost']:6.2f} {z['gt']:6.2f} {z['resid']:+7.2f}  {' · '.join(z['rest'])}")
import statistics as st
rs=[z["resid"] for z in out]
print()
print("שארית: חציון %.2f  ממוצע %.2f  מינימום %.2f  מקסימום %.2f"%(
      st.median(rs),st.mean(rs),min(rs),max(rs)))
print("שאריות שליליות (GT לבדו כבר עובר את העלות המוצהרת): %d"%sum(1 for v in rs if v<0))

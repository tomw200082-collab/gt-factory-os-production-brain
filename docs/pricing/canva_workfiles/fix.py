# -*- coding: utf-8 -*-
import json, statistics as st
R=json.load(open("residual.json"))
# --- non-GT ingredients, Israeli food-service wholesale, EX-VAT -------------
M={
 "קרח":0.06, "⅔ כוס חלב":160*0.0069, "70 מ״ל קצף חלב":70*0.0069,
 "70 מ״ל קצף קר חלבי":70*0.0069, "⅔ כוס מים":0.01,
 "~150 מ״ל סודה":150*0.0025, "~150 מ״ל טוניק":150*0.007,
 "~150 מ״ל טוניק ורדים":150*0.008, "~250 מ״ל לימונדה":250*0.0035,
 "~150 מ״ל מיץ תפוזים":150*0.012, "40 מ״ל מיץ תפוחים":40*0.006,
 "40 מ״ל מי ליצ'י":40*0.012, "~150 מ״ל מי קוקוס":150*0.010,
 "70 מ״ל קרם קוקוס":70*0.014, "15 מ״ל סירופ אגבה":15*0.045,
 "מנת אספרסו":0.75, "סלייס לימון":0.25, "עשבי קישוט":0.20,
 "גרניש":0.35, "גרניש לפי טעם":0.35, "פיסטוק גרוס":0.55,
 "שומשום שחור":0.15, "קינמון":0.10, "מקל וניל":2.20,
 "תמצית וניל":0.15, "תפוז יבש":0.40, "2 ליצ'י":1.00, "מחית בננה":0.60,
}
out=[]
for z in R:
    true_rest=sum(M[c] for c in z["rest"])
    new=z["gt"]+true_rest
    out.append(dict(**z, rest_true=round(true_rest,2), new=round(new,2),
                    gap=round(z["cost"]-new,2),
                    pct=round(100*(z["cost"]-new)/new)))
json.dump(out,open("proposed.json","w"),ensure_ascii=False)
out.sort(key=lambda z:-z["gap"])
print(f"{'#':>3} {'משקה':<27} {'GT':>5} {'שארית':>6} {'שארית':>6} {'עלות':>6} {'מוצע':>6} {'פער':>6} {'%':>5}")
print(f"{'':>3} {'':<27} {'':>5} {'מוצהר':>6} {'אמת':>6} {'היום':>6} {'':>6} {'':>6} {'':>5}")
for z in out:
    print(f"{z['pg']:3d} {z['heb'][:26]:<27} {z['gt']:5.2f} {z['resid']:6.2f} {z['rest_true']:6.2f} {z['cost']:6.2f} {z['new']:6.2f} {z['gap']:+6.2f} {z['pct']:+4d}%")
g=[z["gap"] for z in out]
print()
print("פער: חציון ₪%.2f  ממוצע ₪%.2f  |  מנופחים מעל ₪1: %d/48  |  מתחת לאמת: %d/48"%(
      st.median(g), st.mean(g), sum(1 for v in g if v>1), sum(1 for v in g if v<0)))
mg_old=[100*(z["price"]-z["cost"])/z["price"] for z in out]
mg_new=[100*(z["price"]-z["new"])/z["price"] for z in out]
print("שוליים היום %.0f%%-%.0f%%  ->  לאחר תיקון %.0f%%-%.0f%%"%(
      min(mg_old),max(mg_old),min(mg_new),max(mg_new)))

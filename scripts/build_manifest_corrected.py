"""Update manifest with 6 new tasks added to Maksim's 2026-05-14 route."""
import json
import os

route_dir = r'C:\Users\tomw2\GTeveryday Dropbox\Data Center\Tom\AI Agents & Projects\Code Agents\PRODUCTION\.lionwheel-prints\2026-05-14-maksim'

GI_BASE = "https://www.greeninvoice.co.il/api/v1/documents/download?d="

new_tasks = [
    {
        "task_id": "24683822",
        "route_order": 1,
        "recipient_name": "זוזוברה - איסוף צ'קים",
        "destination_address": "יוחנן הסנדלר 6, כפר סבא",
        "driver_note": "",
        "green_invoice_urls": [],
        "notes": "לאסוף מהמשרדים",
        "destination_notes": None,
        "is_self_pickup": False,
        "order_items_count": 0,
        "packages_quantity": 0,
        "wp_order_id": None
    },
    {
        "task_id": "24683759",
        "route_order": 2,
        "recipient_name": 'בבקה הרצליה (בבקה בייקרי בע"מ)',
        "destination_address": "נתן אלתרמן 27, Herzliya",
        "driver_note": GI_BASE + "XjBEA5ylflOqwjJNQXj8DhKvkC77mNSphmsU20Cs0N8aE2A7oT4UauN83f9SnHeZ3AfT0msAMu8qepypd%2BIzjldx94J5JsibUtJhtzH7R3tuLvtg5LWrsWYy9z3Tj77bqvG0PFzdQQSscR%2FECI0YxiMHrl3fGb13TGw%2B89J937%2Fv2zzzRHeMNqWdYxV7eAQr5SR4mtG%2BAJj2NTCXGJm16P6SrdNqniBmJuEEFrUMNEotuuZHysikKfn8Kb09eVXcyzwSZhy2zVR3I7a2",
        "green_invoice_urls": [GI_BASE + "XjBEA5ylflOqwjJNQXj8DhKvkC77mNSphmsU20Cs0N8aE2A7oT4UauN83f9SnHeZ3AfT0msAMu8qepypd%2BIzjldx94J5JsibUtJhtzH7R3tuLvtg5LWrsWYy9z3Tj77bqvG0PFzdQQSscR%2FECI0YxiMHrl3fGb13TGw%2B89J937%2Fv2zzzRHeMNqWdYxV7eAQr5SR4mtG%2BAJj2NTCXGJm16P6SrdNqniBmJuEEFrUMNEotuuZHysikKfn8Kb09eVXcyzwSZhy2zVR3I7a2"],
        "notes": None,
        "destination_notes": None,
        "is_self_pickup": False,
        "order_items_count": 4,
        "packages_quantity": 1,
        "wp_order_id": "#GT12874"
    },
    {
        "task_id": "24683595",
        "route_order": 3,
        "recipient_name": "אליאס פוד טראקס (סאנשיין בפארק)",
        "destination_address": "הפארק 1, Rishon LeZion",
        "driver_note": GI_BASE + "p7omFng5EsZcjHDTg3B8mT8mV0oHbCSJ6J7kSHL2VOZX8A55FqRt1nFvxw%2BFBcT2Ju3TVCQMi0sLviKjUgnsMJeB%2Bh6exu3doAl0Po9Dwb6YO3cJrYbqFOh8H0GtP7N1v7Z1t5jO9wHAOh1zRiTSKpqBghkpcVP8d6uy0wNlgZ02ePZyzdc9ewINVP1s1oI2VQ030ZM6RmZPCILfdXEYZlKJFjVu7A%2BVhN8xmnkpQU%2BR%2BLFp7j37QCa9zStvZSWnW4r5vBPtUX4SrErc",
        "green_invoice_urls": [GI_BASE + "p7omFng5EsZcjHDTg3B8mT8mV0oHbCSJ6J7kSHL2VOZX8A55FqRt1nFvxw%2BFBcT2Ju3TVCQMi0sLviKjUgnsMJeB%2Bh6exu3doAl0Po9Dwb6YO3cJrYbqFOh8H0GtP7N1v7Z1t5jO9wHAOh1zRiTSKpqBghkpcVP8d6uy0wNlgZ02ePZyzdc9ewINVP1s1oI2VQ030ZM6RmZPCILfdXEYZlKJFjVu7A%2BVhN8xmnkpQU%2BR%2BLFp7j37QCa9zStvZSWnW4r5vBPtUX4SrErc"],
        "notes": None,
        "destination_notes": None,
        "is_self_pickup": False,
        "order_items_count": 12,
        "packages_quantity": 1,
        "wp_order_id": "#GT12873"
    },
    {
        "task_id": "24682608",
        "route_order": 4,
        "recipient_name": 'אורן יקיר יזמות ופרוייקטים בע"מ (קפה נדנדה)',
        "destination_address": "המרגנית 10, רמת גן",
        "driver_note": GI_BASE + "Vy5lanjPeI5pw%2FmHZGdTbTVx3P6XN96YWZBfpS5U1bNyaLCdPla5W8m6%2FlVzu07elYna5CPjHAr9ONEfgCjbxWsxjqayuKM7yfqUfQM3scacsVs0OPSdOfNJPrK7f%2Bgl5V8zRKISSpI6USdrWJTINUgIowBhHpvaAJg9n90MPAPMIRWGtrxnIdfafdTSN3lHWvex4TSJJCG2hfNK%2FD2Lt21r%2B%2FCpvi8O0DYAb8cEegXsJy0LgpWTb8o3GXEcIvtVbxu4JUz1VR54IOMR",
        "green_invoice_urls": [GI_BASE + "Vy5lanjPeI5pw%2FmHZGdTbTVx3P6XN96YWZBfpS5U1bNyaLCdPla5W8m6%2FlVzu07elYna5CPjHAr9ONEfgCjbxWsxjqayuKM7yfqUfQM3scacsVs0OPSdOfNJPrK7f%2Bgl5V8zRKISSpI6USdrWJTINUgIowBhHpvaAJg9n90MPAPMIRWGtrxnIdfafdTSN3lHWvex4TSJJCG2hfNK%2FD2Lt21r%2B%2FCpvi8O0DYAb8cEegXsJy0LgpWTb8o3GXEcIvtVbxu4JUz1VR54IOMR"],
        "notes": None,
        "destination_notes": None,
        "is_self_pickup": False,
        "order_items_count": 4,
        "packages_quantity": 1,
        "wp_order_id": "#GT12872"
    },
    {
        "task_id": "24682556",
        "route_order": 5,
        "recipient_name": 'קפה גן סיפור חולון בע"מ',
        "destination_address": "מוטה גור 15, Holon",
        "driver_note": GI_BASE + "sFDZ1bWEix2rkumRRHj1aKNOGQCZyOjAZ83T4biwq9zGvt1QvZd5d8Zyu%2BDDfSSMUrR4rhyjaElTLXyiX36kmGZ%2BD9WBWnpLaJjBmhSysZgDpNugBs9a%2BcdJ5EmovQKdm%2BSIMZHRmAzZzJvjvVtsvWS%2BoSAVL5b353oLGWjow0shqsjhsoVprT02tAxJrwK9rdZ4zUfkp7lZ5cR0LXcGu8uK251ZnortA1b72B9kg4fDaJWGbHc7KRm7U6lStHoowdQTX%2FzfQO9R1SHi",
        "green_invoice_urls": [GI_BASE + "sFDZ1bWEix2rkumRRHj1aKNOGQCZyOjAZ83T4biwq9zGvt1QvZd5d8Zyu%2BDDfSSMUrR4rhyjaElTLXyiX36kmGZ%2BD9WBWnpLaJjBmhSysZgDpNugBs9a%2BcdJ5EmovQKdm%2BSIMZHRmAzZzJvjvVtsvWS%2BoSAVL5b353oLGWjow0shqsjhsoVprT02tAxJrwK9rdZ4zUfkp7lZ5cR0LXcGu8uK251ZnortA1b72B9kg4fDaJWGbHc7KRm7U6lStHoowdQTX%2FzfQO9R1SHi"],
        "notes": None,
        "destination_notes": None,
        "is_self_pickup": False,
        "order_items_count": 4,
        "packages_quantity": 1,
        "wp_order_id": "#GT12871"
    },
    {
        "task_id": "24682503",
        "route_order": 6,
        "recipient_name": "פסיליטי",
        "destination_address": "דיזנגוף 245, Tel Aviv-Yafo",
        "driver_note": GI_BASE + "VuiEp%2BTTW1v2dc9%2FnQ6wftQ5%2FYeTXb0073jd51fBfVi5wg%2BtCog3Q3s5RphExycndswUIiKF0cDwXdJdwNNRVOU7ctLBdmhgRL7JIhG341ZGZgxYFWnXozLdshmrRP3acDfhPnLoOY2Q%2B9enuw8MgYdWTE3iVYemS%2Ft4djAZUNBpIaNG%2FarF1qisOrP3EsyjcD8GD8EFDBAgZ86o1s3%2BQXP3avNCxAF1QBhcdpqsowB57%2B68GSx09soA8Lebn8YthprPhLkAdfiCRJv0",
        "green_invoice_urls": [GI_BASE + "VuiEp%2BTTW1v2dc9%2FnQ6wftQ5%2FYeTXb0073jd51fBfVi5wg%2BtCog3Q3s5RphExycndswUIiKF0cDwXdJdwNNRVOU7ctLBdmhgRL7JIhG341ZGZgxYFWnXozLdshmrRP3acDfhPnLoOY2Q%2B9enuw8MgYdWTE3iVYemS%2Ft4djAZUNBpIaNG%2FarF1qisOrP3EsyjcD8GD8EFDBAgZ86o1s3%2BQXP3avNCxAF1QBhcdpqsowB57%2B68GSx09soA8Lebn8YthprPhLkAdfiCRJv0"],
        "notes": None,
        "destination_notes": None,
        "is_self_pickup": False,
        "order_items_count": 10,
        "packages_quantity": 1,
        "wp_order_id": "#GT12870"
    },
]

with open(os.path.join(route_dir, "manifest.json"), "r", encoding="utf-8") as f:
    existing = json.load(f)

for i, t in enumerate(existing["tasks"]):
    t["route_order"] = i + 7

all_tasks = new_tasks + existing["tasks"]

manifest = {
    "schema_version": 1,
    "driver_id": 28174,
    "driver_name": "מקסים",
    "delivery_date": "2026-05-14",
    "extracted_at": "2026-05-13T13:10:00+03:00",
    "source_url_filter": "/tasks?driver_id=28174&time_by=pickup_at&date=range&from=14/05/2026&to=14/05/2026",
    "tasks": all_tasks,
    "tasks_without_invoice": [
        {"task_id": "24683822", "reason": "no_url_in_driver_note"},
        {"task_id": "24680299", "reason": "no_url_in_driver_note"},
        {"task_id": "24669394", "reason": "no_url_in_driver_note"},
        {"task_id": "24649855", "reason": "no_url_in_driver_note"}
    ],
    "excluded_not_assigned_to_driver": [
        {"task_id": "24613558", "current_id": "", "driver_name": "(unassigned)"}
    ]
}

with_invoice = sum(1 for t in all_tasks if t["green_invoice_urls"])
print(f"Total tasks: {len(all_tasks)}")
print(f"With GI URL: {with_invoice}")
print(f"Without invoice: {len(manifest['tasks_without_invoice'])}")

with open(os.path.join(route_dir, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print("manifest.json written OK")

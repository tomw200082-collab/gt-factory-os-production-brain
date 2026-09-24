"""Offline checks for sweep.py — cases taken from the 2026-06-15..09-22
backtest (real task titles/notes). No network, no database.

    python3 -m unittest test_sweep.py -v
"""
import unittest

import sweep


def stub_master():
    m = object.__new__(sweep.Master)
    names = {
        "FG-DES-1L": "DESERTEA 1L", "FG-FRE-1L": "FRESH 1L", "FG-DET-1L": "DETOX 1L",
        "FG-DET-500ML": "DETOX 0.5L", "FG-NAM-500ML": "NAMASTEA 0.5L", "FG-DET-500ML-NS": "DETOX 0.5L NO SUGAR",
        "FG-NM-1L": "NONOMIMI SANGRIA 1L", "FG-NM-3850ML": "NONOMIMI SANGRIA 3.85L",
        "FG-MAT-500G": "MATCHA 0.5KG", "FG-MAT-18G": "MATCHA 18G",
    }
    m.items = {i: {"item_id": i, "item_name": n, "uom": "BOTTLE", "case_pack": 6, "barcode": None}
               for i, n in names.items()}
    m.names = sweep.name_index(m.items)
    m.suppliers = [{"supplier_id": "SUP-012", "name": "ריסטרטו"}, {"supplier_id": "SUP-017", "name": "צבר אריזות"}]
    return m


def row(n_lines=0, status="COMPLETED"):
    return {"lw_status": status, "n_lines": n_lines}


class Classify(unittest.TestCase):
    def setUp(self):
        self.m = stub_master()

    def cls(self, title, notes="", **kw):
        return sweep.classify(row(**kw), title, notes, self.m)

    def test_cheques_are_skipped_and_nothing_else_is(self):
        self.assertEqual(self.cls("תל יצחק - איסוף צ'קים מרעות"), "cheque")
        self.assertEqual(self.cls("בבקה כיכר הבימה ת\"א - איסוף צק"), "cheque")
        self.assertNotEqual(self.cls("יצחק מאפייה - השלמת סחורה"), "cheque")

    def test_canceled_produces_nothing(self):
        self.assertEqual(self.cls("דניאל שור (קפה פיורי) - השלמת סחורה", status="CANCELED"), "not_completed")

    def test_supplier_pickup_beats_return_wording(self):
        self.assertEqual(self.cls("ריסטרטו- איסוף סחורה עד 15:00", "מיידן לאסוף ולהחזיר למפעל - תודה:)"), "supplier")
        self.assertEqual(self.cls("צבר אריזות- איסוף סחורה - 1"), "supplier")

    def test_pick_up_and_hand_over_is_a_transfer(self):
        self.assertEqual(self.cls("אליטה אופק בע\"מ - איסוף סחורה",
                                  "לאסוף 2 ארגזים של דיטוקס 0.5 ליטר ולספק לנונומימי"), "transfer")
        self.assertEqual(self.cls("מימי ואזה חנויות - איסוף ארגזים ממימי ואזה ומסירה למפעל"), "return")

    def test_subcontract_before_supplement(self):
        self.assertEqual(self.cls("עמיתה- איסוף והשלמת מאצ'ה"), "subcontract")

    def test_delivery_hours_are_not_a_goods_receipt(self):
        self.assertEqual(self.cls("אלי אברהמי שווק בע\"מ", "קבלת סחורה בין 7:00-12:00"), "unclear")

    def test_a_task_with_order_lines_needs_a_signal(self):
        self.assertEqual(self.cls("נורדוי הבימה בע״מ (נורדיניו) - השלמת סחורה", n_lines=4), "order")
        self.assertEqual(self.cls("סברה קפה בע״מ", "FRESH Sugar-Free 500ml - 3 יח להוסיף ללא חיוב", n_lines=6),
                         "free_goods")

    def test_named_document_without_keyword_is_a_delivery(self):
        self.assertEqual(self.cls("נאבי יונה 63062"), "delivery")


class Documents(unittest.TestCase):
    def test_type_follows_the_word_then_the_number(self):
        self.assertEqual(sweep.doc_refs("אליטה אופק - השלמת סחורה - תעודת משלוח מספר 20286"),
                         [("20286", [sweep.GI_DELIVERY_NOTE])])
        self.assertEqual(sweep.doc_refs("אליטה אופק - השלמת סחורה חשבונית 63753"), [("63753", [sweep.GI_TAX_INVOICE])])
        self.assertEqual(sweep.doc_refs("אלי אברהמי שיווק - תעודת תשלוח 20269"), [("20269", [sweep.GI_DELIVERY_NOTE])])
        self.assertEqual(sweep.doc_refs("נאבי יונה 63062")[0][1][0], sweep.GI_TAX_INVOICE)

    def test_order_ids_and_phone_numbers_are_not_documents(self):
        self.assertEqual(sweep.doc_refs("#GT24589 טלפון 0544920296 רחוב 420286864"), [])


class Parse(unittest.TestCase):
    def setUp(self):
        self.m = stub_master()

    def lines(self, text):
        got, unparsed = sweep.note_lines(text, self.m, "out", "goods_out")
        return [(l["item_id"], l["quantity"]) for l in got], unparsed

    def test_sizes(self):
        for text, size in (("1L", "1000ML"), ("0.5 ליטר", "500ML"), ("חצי ליטר", "500ML"), ("1000ml", "1000ML"),
                           ("18 גרם", "18G"), ("Matcha Bag (500g)", "500G"), ("MATCHA 0.5KG", "500G"),
                           ("3.85L", "3850ML"), ("לואיזה נענע", None)):
            self.assertEqual(sweep.size_of(text), size, text)

    def test_explicit_lines(self):
        self.assertEqual(self.lines("5×1L חליטה מדברית, 6×1L היביסקוס, 4×1L לואיזה נענע")[0],
                         [("FG-DES-1L", 5), ("FG-FRE-1L", 6), ("FG-DET-1L", 4)])
        self.assertEqual(self.lines("לספק 2 יח DESERT ליטר - השלמה")[0], [("FG-DES-1L", 2)])
        self.assertEqual(self.lines("3 BOTTLE FRESH LITER")[0], [("FG-FRE-1L", 3)])
        self.assertEqual(self.lines("לאסוף 2 ארגזים של דיטוקס 0.5 ליטר")[0], [("FG-DET-500ML", 12)])
        self.assertEqual(self.lines("12 תמצית צ'אי מסאלה 0.5 ליטר")[0], [("FG-NAM-500ML", 12)])
        self.assertEqual(self.lines("60 יח' GT Nonomimi Sangria Cocktail 1000ml")[0], [("FG-NM-1L", 60)])

    def test_sentences_split_and_a_singular_noun_is_one(self):
        got, unparsed = self.lines("3 יח  FRESH ליטר. DETOX SF 1 יחידה.")
        self.assertEqual(got, [("FG-FRE-1L", 3)])
        self.assertEqual(unparsed, ["DETOX SF 1 יחידה"])
        got, _ = sweep.note_lines("להוסיף להזמנה ללא חיוב: בקבוק דיטוקס 0.5 ליטר", self.m, "out", "goods_out")
        self.assertEqual([(l["item_id"], l["quantity"], l["confidence"]) for l in got], [("FG-DET-500ML", 1, "low")])
        self.assertEqual(self.lines("בקבוקי דיטוקס 0.5 ליטר")[0], [])

    def test_missing_size_or_quantity_is_a_question(self):
        for text in ("12 Energy", "1 ארגזים של ג'זמין", "2 ארגזים דיטוקס ללא סוכר",
                     "3 ארגזים מכל סוג 0.5L"):
            got, unparsed = self.lines(text)
            self.assertEqual(got, [], text)
            self.assertTrue(unparsed, text)

    def test_two_products_in_one_breath_are_not_guessed(self):
        got, _ = self.lines("לספק ללקוחה 1 קופסא של מאצה 22*18 גרם שהזמינה ולאסוף ממנה 1 שקית מאצה חצי קילו")
        self.assertEqual(got, [])


class Customers(unittest.TestCase):
    def test_branch_matters(self):
        self.assertFalse(sweep.same_customer("קפה גן סיפור אשדוד בע״מ - השלמת סחורה", "קפה גן סיפור רעננה"))
        self.assertTrue(sweep.same_customer("אליטה אופק - השלמת סחורה - מרגריטות", "אליטה אופק בע\"מ"))


class Rationale(unittest.TestCase):
    """The first live proposal (2026-09-24, task 28069095) read "…שגשר הליקוט רואה סוג: …"."""
    def text(self, n_lines):
        r = {"lw_task_id": 28069095, "at": "2026-09-22 12:47:00+00", "n_lines": n_lines}
        p = {"proposed_lines": [], "credit_task_ids": []}
        return sweep.rationale(r, "עמיתה- איסוף מאצ'ה", "subcontract", p)

    def test_every_sentence_ends_before_the_next_begins(self):
        self.assertIn("שגשר הליקוט רואה. סוג: קבלנות משנה (עמיתה).", self.text(0))
        self.assertIn("שכבר לוקטו. סוג:", self.text(2))


if __name__ == "__main__":
    unittest.main()

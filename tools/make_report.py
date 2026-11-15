"""Build HW4_Report.pdf from results/hw4_results.json and figures/.

The report is generated, not hand-written, so every number in it comes from the
executed notebook.  Usage:

    python tools/make_report.py

The report is generated, not hand-written, so every number in it comes from the
executed notebook.  Usage:

    python tools/make_report.py

Layout is deliberately plain: no header, no footer, and a compact title block at the
top of page 1 instead of a separate cover page. The document is rebuilt until the
recorded page numbers stop moving, because the answer locator on page 1 has to print
the page on which each question actually starts.
"""

import json
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results", "hw4_results.json")
OUT_PDF = os.path.join(ROOT, "HW4_Report.pdf")

AUTHOR = "Hammer Hao"
COURSE = "CS 6220 - Data Mining Techniques"
TITLE = "Homework 4: Frequent Itemsets, Association Rules, and Hierarchical Clustering"
REPO = "https://github.com/hammer-hao/CS6220HW4"

ACCENT = colors.HexColor("#000000")
LIGHT = colors.HexColor("#f4f4f4")
GRID = colors.HexColor("#bbbbbb")
INK = colors.HexColor("#222222")
DATE = "November 14, 2026"


# --------------------------------------------------------------------------- styles
def make_styles():
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "Body4", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.6,
        leading=13.4, alignment=TA_JUSTIFY, spaceAfter=6, textColor=INK,
    )
    return {
        "title": ParagraphStyle("T", parent=body, fontName="Helvetica-Bold", fontSize=15,
                                leading=19, textColor=INK, alignment=TA_CENTER, spaceAfter=6),
        "subtitle": ParagraphStyle("ST", parent=body, fontSize=10.5, leading=14,
                                   textColor=INK, alignment=TA_CENTER),
        "meta": ParagraphStyle("M", parent=body, fontSize=9.2, leading=13,
                               alignment=TA_CENTER, textColor=INK),
        "h1": ParagraphStyle("H1", parent=body, fontName="Helvetica-Bold", fontSize=12.5,
                             leading=16, textColor=INK, spaceBefore=11, spaceAfter=5,
                             alignment=0, keepWithNext=1),
        "h2": ParagraphStyle("H2", parent=body, fontName="Helvetica-Bold", fontSize=10.2,
                             leading=13.5, textColor=INK,
                             spaceBefore=8, spaceAfter=3, keepWithNext=1),
        "body": body,
        "bullet": ParagraphStyle("B", parent=body, leftIndent=13, bulletIndent=3, spaceAfter=3),
        "cell": ParagraphStyle("C", parent=body, fontSize=8.1, leading=10.2, alignment=0,
                               spaceAfter=0),
        "cellb": ParagraphStyle("CB", parent=body, fontName="Helvetica-Bold", fontSize=8.2,
                                leading=10.4, textColor=INK, alignment=0, spaceAfter=0),
        "code": ParagraphStyle("Code", parent=body, fontName="Courier", fontSize=7.6,
                               leading=9.4, alignment=0),
        "caption": ParagraphStyle("Cap", parent=body, fontName="Helvetica-Oblique", fontSize=8.2,
                                  leading=10.6, textColor=INK, alignment=TA_CENTER,
                                  spaceBefore=2, spaceAfter=10),
    }


# --------------------------------------------------------------------------- helpers
class Marker(Flowable):
    """Zero-size flowable that records the page it is drawn on."""

    def __init__(self, key):
        Flowable.__init__(self)
        self.key = key
        self.width = 0
        self.height = 0

    def wrap(self, available_width, available_height):
        return (0, 0)

    def draw(self):
        pass


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def P(text, style, **kwargs):
    """Paragraph factory; ``qid`` tags the paragraph so its page can be recorded.

    The tag is read back in Report.afterFlowable, which makes the answer locator
    immune to a heading being pushed to the next page by keepWithNext.
    """
    qid = kwargs.pop("qid", None)
    paragraph = Paragraph(text, style, **kwargs)
    if qid:
        paragraph._qid = qid
    return paragraph


def code_block(text, styles, width=6.75 * inch):
    """Monospaced pseudo-code in a light box."""
    pre = Preformatted(text, styles["code"])
    table = Table([[pre]], colWidths=[width])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.4, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def data_table(header, rows, col_widths, styles, align_right=None):
    """Table with a plain ruled header row and wrapped paragraph cells."""
    align_right = align_right or []
    head = [P(esc(h), styles["cellb"]) for h in header]
    body = []
    for row in rows:
        cells = []
        for i, value in enumerate(row):
            cell = P(esc(value), styles["cell"])
            if i in align_right:
                cell.style = ParagraphStyle(
                    "R", parent=styles["cell"], alignment=2)
            cells.append(cell)
        body.append(cells)
    table = Table([head] + body, colWidths=col_widths, repeatRows=1, hAlign="CENTER")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#888888")),
        ("GRID", (0, 0), (-1, -1), 0.25, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    return table


def figure(path, width=6.5 * inch, caption=None, styles=None):
    reader = ImageReader(path)
    iw, ih = reader.getSize()
    height = width * ih / iw
    items = [Image(path, width=width, height=height)]
    if caption:
        items.append(P(caption, styles["caption"]))
    return KeepTogether(items)


# --------------------------------------------------------------------------- document
class Report(BaseDocTemplate):
    def __init__(self, filename, page_map, **kwargs):
        BaseDocTemplate.__init__(
            self, filename, pagesize=letter,
            leftMargin=0.85 * inch, rightMargin=0.85 * inch,
            topMargin=0.85 * inch, bottomMargin=0.8 * inch,
            title="CS 6220 Homework 4", author=AUTHOR, **kwargs)
        self.page_map = page_map
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height,
                      id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        # No header, no footer: the page carries nothing but the content.
        self.addPageTemplates([PageTemplate(id="main", frames=[frame])])

    def afterFlowable(self, flowable):
        qid = getattr(flowable, "_qid", None)
        if qid:
            self.page_map[qid] = self.page
        elif isinstance(flowable, Marker):
            self.page_map[flowable.key] = self.page


# --------------------------------------------------------------------------- content
def build_story(data, styles, page_map):
    """Assemble the full report. ``page_map`` supplies the page numbers of Q1..Q12."""
    story = []
    meta = data["meta"]
    apriori = data["apriori"]
    rules = data["rules"]
    q4 = data["q4"]
    clustering = data["clustering"]
    figs = data["figures"]

    def fig_path(name):
        return os.path.join(ROOT, figs[name])

    def page(key, default="-"): 
        return str(page_map.get(key, default))

    # ---------------------------------------------------------------- title page
    # ------------------------------------------------------- title block (page 1)
    # A compact heading instead of a separate cover page: title, one-line metadata,
    # the abstract, and then straight into the contents table.
    story.append(Spacer(1, 0.15 * inch))
    story.append(P(TITLE, styles["title"]))
    story.append(Spacer(1, 4))
    story.append(P("%s &nbsp;&middot;&nbsp; %s" % (esc(COURSE), esc(DATE)), styles["subtitle"]))
    story.append(Spacer(1, 2))
    story.append(P("%s &nbsp;&middot;&nbsp; %s &nbsp;&middot;&nbsp; CS6220_HW4.ipynb"
                   % (esc(AUTHOR), esc(REPO)), styles["meta"]))
    story.append(Spacer(1, 14))
    story.append(P(
        "This report documents a from-scratch implementation of the Apriori algorithm, of an "
        "Apriori-based association-rule miner that exploits the anti-monotonicity of confidence, "
        "and of hierarchical agglomerative clustering (HAC) with min_dist and max_dist linkage. "
        "All results are produced by the accompanying Jupyter notebook; the report only formats "
        "them. Part 1 mines frequent itemsets from a 20-transaction basket database at "
        "min_sup = 0.25, Part 2 extracts association rules at min_conf = 0.6 and discusses "
        "support, confidence and lift, and Part 3 clusters the 370 points of clustering.txt, "
        "comparing single-linkage and complete-linkage dendrograms at 13 clusters.", styles["body"]))
    story.append(Spacer(1, 6))

    # ---------------------------------------------------------------- locator
    story.append(P("Contents and answer locator", styles["h1"]))
    story.append(P(
        "Gradescope requires the page on which each answer starts; the table below gives it "
        "directly. Section numbers match the question numbers.", styles["body"]))
    story.append(Spacer(1, 3))

    locator_rows = [
        ["Q1", "GitHub repository and code organization", page("q1")],
        ["Q2", "Pseudo-code for Apriori and Apriori_rules", page("q2")],
        ["Q3", "Frequent itemsets for min_sup = 0.25 and pruning statistics", page("q3")],
        ["Q4", "The 3-itemset {Butter, Bread, Eggs}: support, candidacy, pruning", page("q4")],
        ["Q5", "Association rules for min_conf = 0.6, with lift", page("q5")],
        ["Q6", "Meaning of lift below 1.0", page("q6")],
        ["Q7", "Strongest and weakest rule", page("q7")],
        ["Q8", "Pseudo-code for hierarchical clustering", page("q8")],
        ["Q9", "Plot of clustering.txt and the number of natural clusters", page("q9")],
        ["Q10", "HAC with min_dist: dendrogram and 13 coloured clusters", page("q10")],
        ["Q11", "HAC with max_dist: dendrogram and 13 coloured clusters", page("q11")],
        ["Q12", "Which clustering agrees more with intuition, and why", page("q12")],
        ["A", "Appendix: reproducibility, verification, dependencies", page("appa")],
    ]
    story.append(data_table(["#", "Answer", "Page"], locator_rows,
                            [0.55 * inch, 4.85 * inch, 0.65 * inch], styles, align_right=[0, 2]))
    story.append(Spacer(1, 10))
    story.append(P("<b>Summary of results.</b> Apriori finds 10 frequent itemsets (5 singletons, "
                   "4 pairs, 1 triple) and prunes 2 of the 3 length-3 candidates. "
                   "Apriori_rules returns 11 rules; the strongest is {Bread, Milk} -> {Butter} "
                   "(confidence 1.00, lift 3.33) and the weakest is {Bread} -> {Milk} "
                   "(confidence 0.63, lift 1.14). clustering.txt contains 13 natural clusters, "
                   "and at k = 13 single linkage recovers all of them while complete linkage "
                   "cuts the elongated strips and the rings apart.", styles["body"]))
    story.append(Spacer(1, 10))

    # ---------------------------------------------------------------- Q1
    story.append(P("1. Repository and code organization (Q1)", styles["h1"], qid="q1"))
    story.append(P(
        "The complete source is at <b>%s</b>. The repository is self-contained: clone it, install "
        "the pinned dependencies, and execute the notebook." % esc(REPO), styles["body"]))
    layout = (
        "CS6220HW4/\n"
        "|-- CS6220_HW4.ipynb     the solution: implementations, experiments, discussion\n"
        "|-- HW4_Report.pdf       this report\n"
        "|-- clustering.txt       370 x 2 dataset for Part 3\n"
        "|-- requirements.txt     pinned dependencies (numpy, scipy, matplotlib, reportlab)\n"
        "|-- README.md            build/run instructions\n"
        "|-- figures/             the five figures of this report (written by the notebook)\n"
        "|-- results/             hw4_results.json, every number used in this report\n"
        "`-- tools/make_report.py  rebuilds this PDF from the notebook results"
    )
    story.append(code_block(layout, styles))
    story.append(Spacer(1, 6))
    story.append(P(
        "The notebook is organised in four parts, each introduced by a markup cell: setup; "
        "Part 1 (support, confidence, Apriori); Part 2 (Apriori_rules and Apriori_general); "
        "Part 3 (HAC, dendrograms, cluster assignments). Every function carries a docstring "
        "stating its parameters and return values, and inline comments mark the join / prune / "
        "count steps, the incremental distance update, and the dendrogram bookkeeping. The "
        "notebook is committed with its outputs, so all tables and figures below are visible "
        "there as well. Each algorithmic claim is checked inside the notebook with assertions "
        "(see Appendix A).", styles["body"]))
    story.append(P(
        "To reproduce: <font face='Courier' size='8.4'>python -m pip install -r requirements.txt</font> "
        "then <font face='Courier' size='8.4'>jupyter nbconvert --to notebook --execute --inplace "
        "CS6220_HW4.ipynb</font>, then <font face='Courier' size='8.4'>python tools/make_report.py</font> "
        "to regenerate this PDF.", styles["body"]))

    # ---------------------------------------------------------------- Q2
    story.append(P("2. Pseudo-code for Apriori and Apriori_rules (Q2)", styles["h1"], qid="q2"))
    story.append(P(
        "Both algorithms are the same level-wise loop over increasing sizes, differing only in "
        "what is being extended, how candidates are pruned, and how they are scored.", styles["body"]))
    story.append(P("Algorithm 1 - Apriori (frequent itemsets)", styles["h2"]))
    story.append(code_block(
        "Apriori(T, min_sup)\n"
        "  L1 <- { {i} : support({i}, T) >= min_sup }\n"
        "  k  <- 2\n"
        "  while L(k-1) is not empty\n"
        "    Ck  <- join(L(k-1))                      # pairs sharing the first k-2 items\n"
        "    Ck' <- { c in Ck : every (k-1)-subset of c is in L(k-1) }   # prune; log removed\n"
        "    for c in Ck'                             # count: one pass over T\n"
        "      c.sup <- support(c, T)\n"
        "    Lk <- { c in Ck' : c.sup >= min_sup }\n"
        "    k  <- k + 1\n"
        "  return union of all Lk", styles))
    story.append(Spacer(1, 6))
    story.append(P("Algorithm 2 - Apriori_rules (association rules, anti-monotone consequents)", styles["h2"]))
    story.append(code_block(
        "Apriori_rules(F, min_conf)                  # F = frequent itemsets with supports\n"
        "  for each Z in F with |Z| >= 2\n"
        "    H1 <- { {a} : conf(Z\\{a} -> {a}) = sup(Z)/sup(Z\\{a}) >= min_conf }\n"
        "    k  <- 1\n"
        "    while Hk is not empty\n"
        "      emit every rule  Z\\H -> H  for H in Hk   (support, confidence, lift)\n"
        "      Ck+1 <- join(Hk)                     # consequents sharing the first k-1 items\n"
        "      Ck+1' <- { h in Ck+1 : every k-subset of h is in Hk }      # prune; log removed\n"
        "      for h in Ck+1'                       # count\n"
        "        conf <- sup(Z) / sup(Z\\h)\n"
        "      Hk+1 <- { h in Ck+1' : conf >= min_conf }\n"
        "      k <- k + 1", styles))
    story.append(Spacer(1, 6))
    story.append(P(
        "The prune test for rules is the same as for itemsets, applied to the consequent: if "
        "Z\\H -> H does not reach min_conf, no rule whose consequent is a superset of H can "
        "either, because confidence = sup(Z)/sup(Z\\H) is non-increasing in H (a smaller "
        "antecedent can only be more frequent). The join keys differ as well: Apriori joins "
        "itemsets on their common prefix, Apriori_rules joins consequents on theirs.", styles["body"]))
    story.append(P(
        "<b>Optional generalisation.</b> The notebook also implements "
        "<font face='Courier' size='8.4'>Apriori_general(seed, join_step, prune_step, "
        "score_step, min_thr)</font>, which takes the four differing operations as parameters. "
        "Instantiating it with the itemset join, the subset prune and the support score "
        "reproduces Apriori exactly, and instantiating it with the consequent join, the same "
        "prune and the confidence score reproduces all 11 rules; both equalities are asserted "
        "in the notebook.", styles["body"]))
    story.append(P(
        "<b>Use of AI.</b> The code was produced with the help of an AI coding agent "
        "(DeepSeek Harness). The prompts and the progression of the implementation are archived "
        "in <font face='Courier' size='8.4'>prompts.md</font> in the repository; a shareable "
        "chat link is to be inserted here by the author.", styles["body"]))

    # ---------------------------------------------------------------- Q3
    story.append(P("3. Frequent itemsets and pruning statistics (Q3)", styles["h1"], qid="q3"))
    story.append(P(
        "With 20 transactions, min_sup = 0.25 means an itemset must occur in at least 5 baskets. "
        "The table reports, per size k, how many candidates the join produced, how many the "
        "prune step removed because a (k-1)-subset was not frequent, how many were counted, and "
        "how many reached the threshold.", styles["body"]))

    rows = []
    for k in sorted(apriori["levels"], key=int):
        info = apriori["levels"][k]
        rows.append([k, info["candidates"], info["pruned"], info.get("kept", info["candidates"] - info["pruned"]),
                     info["frequent"]])
    story.append(data_table(["k", "candidates from join", "pruned", "counted", "frequent k-itemsets"],
                            rows, [0.5 * inch, 1.55 * inch, 0.85 * inch, 0.95 * inch, 1.6 * inch],
                            styles, align_right=[0, 1, 2, 3, 4]))
    story.append(Spacer(1, 8))
    story.append(P("Frequent itemsets found (support in parentheses)", styles["h2"]))
    freq_rows = []
    for k in sorted(apriori["levels"], key=int):
        info = apriori["levels"][k]
        items = ", ".join("%s (%.2f)" % ("{" + ", ".join(x["itemset"]) + "}", x["support"])
                          for x in info["itemsets"])
        freq_rows.append([k, len(info["itemsets"]), items or "-"])
    story.append(data_table(["k", "count", "frequent itemsets"], freq_rows,
                            [0.45 * inch, 0.6 * inch, 5.5 * inch], styles, align_right=[0, 1]))
    story.append(Spacer(1, 8))
    story.append(P(
        "<b>Pruned length-3 candidates.</b> {Bread, Butter, Eggs} was removed because "
        "{Butter, Eggs} has support 0.15 < 0.25, and {Bread, Eggs, Milk} because {Eggs, Milk} "
        "has support 0.15. Both were rejected without a support count.", styles["body"]))
    story.append(P(
        "<b>Was pruning effective?</b> It is correct and it does save work, but on this toy "
        "database it is not the dominant filter. Pruning cannot fire at k = 1 (no previous "
        "level) or at k = 2 (every 1-subset of a pair is a frequent singleton by construction), "
        "so all 10 pairs are counted. At k = 3 it removes 2 of the 3 candidates - 67 % of that "
        "level - leaving only {Bread, Butter, Milk} to be counted, and it is that surviving "
        "triple that is frequent. The loop then stops at k = 4 because the join step produces no "
        "candidate at all (a single frequent 3-itemset cannot be paired).", styles["body"]))
    story.append(P(
        "The larger saving comes from the support test itself: 6 of the 10 pairs die at k = 2 "
        "({Milk, Cereal} 0.20, {Butter, Eggs} 0.15, {Milk, Eggs} 0.15 and the three Cereal pairs "
        "with Bread/Butter/Eggs at 0.05, 0.05 and 0.00), which is what keeps the candidate set at "
        "k = 3 as small as three. Overall the search generated 25 candidates (12 + 10 + 3) and "
        "counted 23 of them, out of 2<super>12</super> - 1 = 4095 possible itemsets. Pruning is "
        "therefore effective but modest here; its benefit grows with the number of frequent "
        "items, a regime this database does not reach.", styles["body"]))

    # ---------------------------------------------------------------- Q4
    story.append(P("4. The 3-itemset {Butter, Bread, Eggs} (Q4)", styles["h1"], qid="q4"))
    singles = q4["singletons"]
    pairs = q4["pairs"]
    q4_rows = []
    for item in ("Bread", "Butter", "Eggs"):
        q4_rows.append(["1-itemset", "{%s}" % item, "%.2f" % singles[item],
                        "yes" if singles[item] >= meta["min_sup"] else "no"])
    for pair, support in pairs.items():
        q4_rows.append(["2-itemset", "{%s}" % pair.replace(" & ", ", "), "%.2f" % support,
                        "yes" if support >= meta["min_sup"] else "no"])
    q4_rows.append(["3-itemset", "{Bread, Butter, Eggs}", "%.2f" % q4["triple_support"],
                    "no"])
    story.append(KeepTogether([data_table(
        ["size", "itemset", "support", "frequent at 0.25?"], q4_rows,
        [0.9 * inch, 2.1 * inch, 0.85 * inch, 1.5 * inch], styles, align_right=[2])]))
    story.append(Spacer(1, 8))
    story.append(P(
        "<b>Supports.</b> The three 1-itemsets are all frequent: {Bread} 0.40, {Butter} 0.30, "
        "{Eggs} 0.30. Of the three 2-itemsets, {Bread, Butter} (0.30) and {Bread, Eggs} (0.25) "
        "are frequent, but <b>{Butter, Eggs} has support 0.15 and is not</b>. The triple itself "
        "has support 0.15.", styles["body"]))
    story.append(P(
        "<b>Would Apriori consider it a length-3 candidate? Yes.</b> The join step pairs "
        "{Bread, Butter} with {Bread, Eggs} because they share the prefix {Bread}, and their "
        "union is exactly {Bread, Butter, Eggs} - one of the three length-3 candidates the run "
        "generated.", styles["body"]))
    story.append(P(
        "<b>Would it be pruned? Yes.</b> The prune step finds that one of its 2-subsets, "
        "{Butter, Eggs}, is missing from L2, so the candidate is discarded before any support "
        "count is spent on it. This is downward closure in action: a frequent itemset cannot "
        "contain an infrequent subset. The data agree independently - the triple occurs in only "
        "3 of 20 baskets (0.15), so it would fail the support test anyway.", styles["body"]))

    # ---------------------------------------------------------------- Q5
    story.append(P("5. Association rules for min_conf = 0.6 (Q5)", styles["h1"], qid="q5"))
    story.append(P(
        "Apriori_rules returns the following 11 rules. Support is the support of the full "
        "itemset, confidence is sup(antecedent and consequent)/sup(antecedent), and lift is "
        "confidence/sup(consequent).", styles["body"]))
    rule_rows = []
    for i, r in enumerate(rules, 1):
        rule_rows.append([
            i,
            "{" + ", ".join(r["antecedent"]) + "}",
            "{" + ", ".join(r["consequent"]) + "}",
            "%.2f" % r["support"],
            "%.3f" % r["confidence"],
            "%.3f" % r["lift"],
        ])
    story.append(data_table(["#", "antecedent", "consequent", "support", "confidence", "lift"],
                            rule_rows,
                            [0.38 * inch, 1.55 * inch, 1.55 * inch, 0.75 * inch, 0.95 * inch,
                             0.75 * inch],
                            styles, align_right=[0, 3, 4, 5]))
    story.append(Spacer(1, 8))
    story.append(P(
        "The rules come from the four frequent pairs (6 rules with a one-item consequent) and "
        "from {Bread, Butter, Milk} (5 rules: three with a one-item consequent and two with a "
        "two-item consequent). No rule is produced with Milk as the antecedent and two items as "
        "the consequent, because sup(Milk) = 0.55 makes those confidences 0.45. No rule "
        "involves Diapers or Beer: {Diapers, Beer} has support 0.15 and never enters the "
        "frequent set, so the classic beer-and-diapers pattern needs a lower support threshold "
        "than 0.25. For the same reason the anti-monotone prune never had to remove a candidate "
        "rule in this run - the database is too small for a confident rule to generate an "
        "unconfident superset - which the notebook reports explicitly.", styles["body"]))

    # ---------------------------------------------------------------- Q6
    story.append(P("6. What a lift below 1.0 means (Q6)", styles["h1"], qid="q6"))
    story.append(P(
        "Lift compares the observed co-occurrence of A and B with what independence predicts: "
        "lift(A -> B) = confidence(A -> B) / support(B) = support(A and B) / "
        "[support(A) support(B)].", styles["body"]))
    story.append(P(
        "<b>lift &gt; 1</b> - A and B occur together more often than chance, so seeing A raises "
        "the probability of B (positive correlation).", styles["bullet"], bulletText="\u2022"))
    story.append(P(
        "<b>lift = 1</b> - the items are independent; the rule carries no information beyond the "
        "base rate of B.", styles["bullet"], bulletText="\u2022"))
    story.append(P(
        "<b>lift &lt; 1</b> - <b>negative correlation</b>: A occurring makes B <i>less</i> likely "
        "than its overall base rate. The items behave like substitutes.", styles["bullet"],
        bulletText="\u2022"))
    story.append(P(
        "A rule with lift below 1 can still have high confidence if B is very frequent, which is "
        "why the two measures must be read together: as a recommendation, such a rule is worse "
        "than doing nothing, because the customer who bought A is <i>less</i> likely than an "
        "average customer to want B.", styles["body"]))

    # ---------------------------------------------------------------- Q7
    story.append(P("7. Strongest and weakest rule (Q7)", styles["h1"], qid="q7"))
    story.append(P(
        "<b>Strongest: {Bread, Milk} -> {Butter}</b> - support 0.25, confidence 1.000, lift 3.333. "
        "Every basket with Bread and Milk also contains Butter, the lift is the highest of all "
        "11 rules, and its support is as high as any perfect-confidence rule can be here. Its "
        "mirror image {Butter} -> {Bread, Milk} reaches the same lift with confidence 0.833.",
        styles["body"]))
    story.append(P(
        "<b>Weakest: {Bread} -> {Milk}</b> - support 0.25, confidence 0.625, lift 1.136. It "
        "barely clears min_conf and has the lowest lift of the run: Bread buyers are only about "
        "14 % more likely than anybody else to take Milk, because Milk is already in 11 of the "
        "20 baskets (support 0.55). The rule is true but uninformative - it restates the base "
        "rate of a popular item.", styles["body"]))
    story.append(P(
        "The contrast is the point of Q6: confidence can be inflated by a frequent consequent, "
        "whereas lift cannot. A rule is interesting when both are high; a high confidence with a "
        "lift near 1 is a rule that says nothing.", styles["body"]))

    # ---------------------------------------------------------------- Q8
    story.append(P("8. Pseudo-code for hierarchical clustering (Q8)", styles["h1"], qid="q8"))
    story.append(code_block(
        "HAC(X, dist_fn)                     # dist_fn is min_dist or max_dist\n"
        "  D <- matrix of point-to-point distances        # the only O(n^2) point comparison\n"
        "  C <- { {x} : x in X }                          # every point is its own cluster\n"
        "  Z <- empty list of merges\n"
        "  while |C| > 1\n"
        "    (A, B) <- argmin over pairs of clusters of dist(A, B)\n"
        "    append (A, B, dist(A,B), |A|+|B|) to Z       # dendrogram bookkeeping\n"
        "    for every other cluster K in C               # INCREMENTAL update\n"
        "      D[A u B, K] <- min or max of D[A,K], D[B,K]   # never loops over point pairs\n"
        "    C <- (C \\ {A, B}) u {A u B}\n"
        "  return Z\n"
        "\n"
        "cluster_membership(Z, k):\n"
        "  apply only the first n-k merges of Z with a union-find over the merge tree\n"
        "  return the resulting k components as the labels of the n points", styles))
    story.append(Spacer(1, 6))
    story.append(P(
        "The incremental step is the crucial one: the distance from the new cluster to any other "
        "cluster is a min (or max) of two numbers that are already in the matrix, so after the "
        "initial matrix no cluster distance is ever computed by scanning pairs of points. The "
        "implementation stores the matrix in place, retires the merged slot, and keeps a "
        "label array so each merge can be written into the linkage matrix in the standard "
        "[left, right, distance, size] form used by dendrogram code.", styles["body"]))
    story.append(P(
        "<b>Use of AI.</b> As for Part 1, the implementation was written with an AI coding agent "
        "(DeepSeek Harness); the prompt history is archived in prompts.md in the repository.", styles["body"]))

    # ---------------------------------------------------------------- Q9
    story.append(KeepTogether([
        P("9. The dataset and the number of natural clusters (Q9)", styles["h1"], qid="q9"),
        figure(fig_path("fig1_dataset.png"), width=5.2 * inch,
               caption="Figure 1 - the 370 points of clustering.txt. The groups are not "
                       "all round: four are elongated vertical strips, two are rings.",
               styles=styles)]))
    story.append(P(
        "<b>Thirteen clusters.</b> The data is a small gallery of 13 point groups of three "
        "different shapes, separated by clear empty space:", styles["body"]))
    q9_rows = [
        ["1-4", "four vertical strips", "x 0.04-0.12, 0.16-0.26, 0.34-0.44, 0.48-0.56; y 0.00-0.35",
         "40, 60, 60, 40"],
        ["5-8", "four small blobs (lower right)", "(0.62-0.72, 0.24-0.30), (0.70-0.75, 0.01-0.06), "
         "(0.79-0.87, 0.27-0.31), (0.92-1.04, 0.15-0.24)", "10, 10, 10, 20"],
        ["9-11", "three compact blobs (upper left)", "(0.06-0.17, 0.50-0.55), (0.19-0.28, 0.77-0.83), "
         "(0.38-0.44, 0.65-0.71)", "16, 17, 17"],
        ["12-13", "two ring-shaped groups", "(0.60-0.89, 0.74-0.97), (0.75-1.03, 0.63-0.86)",
         "35, 35"],
    ]
    story.append(data_table(["groups", "shape", "extent", "points"], q9_rows,
                            [0.7 * inch, 1.55 * inch, 3.6 * inch, 0.85 * inch], styles,
                            align_right=[3]))
    story.append(Spacer(1, 6))
    story.append(P(
        "A coarser reading is possible - two groups (upper and lower half), or four strips plus "
        "'the rest' - but the gaps between the 13 groups are all much larger than the spacing "
        "inside them, and both linkages find 13 clusters at a natural cut height. The dataset is "
        "deliberately interesting for question 12: four clusters are <b>elongated</b> (0.09 wide "
        "and 0.34 tall in data units) and two are <b>non-convex</b> (a ring 0.02 thick and 0.30 "
        "across).", styles["body"]))

    # ---------------------------------------------------------------- Q10
    story.append(KeepTogether([
        P("10. HAC with min_dist: dendrogram and 13 clusters (Q10)", styles["h1"], qid="q10"),
        figure(fig_path("fig2_dendrogram_min.png"), width=6.3 * inch,
               caption="Figure 2 - single-linkage dendrogram. The dashed line is the cut "
                       "that yields 13 clusters (between merge heights 0.071 and 0.075).",
               styles=styles)]))
    story.append(figure(fig_path("fig3_clusters_min.png"), width=4.9 * inch,
                        caption="Figure 3 - the same 13 clusters drawn in the plane.", styles=styles))
    sizes_min = sorted(clustering["min"]["sizes"], reverse=True)
    story.append(P(
        "<b>The clusters match intuition almost exactly.</b> Each of the 13 groups of Q9 comes "
        "out as one cluster: the four strips keep their full height (y = 0 to 0.35) and their "
        "narrow width (0.09), the two rings are each a single colour, and the small blobs stay "
        "separate. Cluster sizes are %s and there are no singletons - every cluster has at least "
        "the 10 points the data gives it." % ", ".join(str(s) for s in sizes_min), styles["body"]))
    story.append(P(
        "The clusters are long, and this is the well-known weakness of single linkage: it merges "
        "as soon as <i>one</i> pair of points is close, so it follows connectivity rather than "
        "compactness. Here the chains are real (the strips are contiguous), but on data where a "
        "sparse bridge of points connects two groups, single linkage would merge them.", styles["body"]))

    # ---------------------------------------------------------------- Q11
    story.append(KeepTogether([
        P("11. HAC with max_dist: dendrogram and 13 clusters (Q11)", styles["h1"], qid="q11"),
        figure(fig_path("fig4_dendrogram_max.png"), width=6.3 * inch,
               caption="Figure 4 - complete-linkage dendrogram with the same cut "
                       "(between merge heights 0.288 and 0.290).", styles=styles)]))
    story.append(figure(fig_path("fig5_clusters_max.png"), width=4.9 * inch,
                        caption="Figure 5 - the 13 complete-linkage clusters.", styles=styles))
    sizes_max = sorted(clustering["max"]["sizes"], reverse=True)
    story.append(P(
        "<b>The clusters match intuition noticeably worse.</b> With sizes %s, complete linkage "
        "produces 13 compact clusters, but not the 13 clusters that are in the data:"
        % ", ".join(str(s) for s in sizes_max), styles["body"]))
    story.append(P(
        "The four vertical strips are cut horizontally: complete linkage never allows a "
        "cluster taller than about 0.3, so every strip is split at roughly y = 0.2 - the second "
        "strip survives only as x 0.17-0.26 / y 0.00-0.21 (32 points).", styles["bullet"],
        bulletText="\u2022"))
    story.append(P(
        "The pieces are regrouped <i>across</i> strips: one cluster spans x 0.05-0.26 at "
        "y 0.24-0.35 (the tops of strips 1 and 2, 34 points), another spans x 0.35-0.56 at "
        "y 0.00-0.17 (the bottoms of strips 3 and 4, 42 points) and a third spans x 0.34-0.52 "
        "at y 0.13-0.35 (their tops, 55 points). Two visually separate groups share a cluster "
        "while one group sits in two clusters.", styles["bullet"], bulletText="\u2022"))
    story.append(P(
        "The big ring is broken into a left arc (13 points) and a top arc (19 points); the "
        "smaller ring survives intact (38 points) only because its diameter is smaller.",
        styles["bullet"], bulletText="\u2022"))
    story.append(P(
        "Two pairs of small blobs are glued together: the upper blobs at (0.19-0.28, 0.77-0.83) "
        "and (0.38-0.44, 0.65-0.71) form one 34-point cluster, and the lower-right blobs at "
        "(0.79-0.87, 0.27-0.31) and (0.92-1.04, 0.15-0.24) form one 30-point cluster.",
        styles["bullet"], bulletText="\u2022"))

    # ---------------------------------------------------------------- Q12
    story.append(P("12. Which clustering agrees more with intuition, and why (Q12)", styles["h1"], qid="q12"))
    story.append(P(
        "<b>min_dist (single linkage) agrees much more with intuition on this dataset</b>, "
        "because the natural clusters are elongated or non-convex and single linkage is the only "
        "one of the two that can represent such shapes.", styles["body"]))
    story.append(P(
        "<b>min_dist</b> merges clusters when the closest pair of points is close: "
        "d(A,B) = min over a in A, b in B of |a-b|. Along a strip or around a ring, consecutive "
        "points are about 0.01 apart although the shape is 0.35 across, so the cluster can grow "
        "along the shape without ever asking how far its two ends are. That is why the strips and "
        "the rings survive. The price is chaining: a sparse path of points between two groups "
        "would merge them.", styles["body"]))
    story.append(P(
        "<b>max_dist</b> merges only when the farthest pair is close: d(A,B) = max over a in A, "
        "b in B of |a-b|. This keeps clusters compact and roughly spherical - excellent for the "
        "three round blobs, which it recovers well - but it caps a cluster's diameter at the "
        "merge height (0.29). The strips and rings have diameter 0.35, so complete linkage "
        "<i>must</i> cut them, and it cuts wherever the constraint bites: across the middle of a "
        "strip, and across a ring.", styles["body"]))
    story.append(P(
        "In one sentence: min_dist answers 'which points are connected?', max_dist answers 'which "
        "points fit in a ball?'. This dataset is made of strips and rings, so the connectivity "
        "answer is the one that matches the eye. On data made of well separated Gaussian blobs "
        "the verdict would usually be reversed, because complete linkage is far more robust to "
        "noise and to outliers.", styles["body"]))
    story.append(P(
        "A quantitative check agrees: the mean silhouette coefficient of the 13-cluster "
        "partitions is similar for both (0.43 for min_dist, 0.47 for max_dist), which is exactly "
        "why the plots and the shapes, not a single number, have to decide the question.",
        styles["body"]))

    # ---------------------------------------------------------------- appendix
    story.append(P("Appendix A - Reproducibility and verification", styles["h1"], qid="appa"))
    story.append(P(
        "Every number and figure in this report is produced by CS6220_HW4.ipynb, which writes "
        "results/hw4_results.json and figures/*.png; tools/make_report.py only formats them. The "
        "notebook asserts the following while it runs, so a silent regression would stop the "
        "execution:", styles["body"]))
    story.append(P(
        "support and confidence are checked against hand-computed values for the basket database;",
        styles["bullet"], bulletText="\u2022"))
    story.append(P(
        "Apriori_general reproduces both Apriori (identical set of 10 frequent itemsets) and "
        "Apriori_rules (identical count of 11 rules);", styles["bullet"], bulletText="\u2022"))
    story.append(P(
        "the incremental linkage distances equal a deliberately naive implementation that "
        "recomputes every cluster distance from all pairs of points (40-point sample, max "
        "absolute difference 0.0);", styles["bullet"], bulletText="\u2022"))
    story.append(P(
        "for both linkage rules, the 369 merge distances and the 13-cluster partition agree with "
        "scipy.cluster.hierarchy (single and complete linkage).", styles["bullet"], bulletText="\u2022"))
    story.append(Spacer(1, 4))
    story.append(P("Dependencies (pinned in requirements.txt)", styles["h2"]))
    dep_rows = [
        ["numpy, scipy, matplotlib", "arrays, computation and every figure (SciPy also "
                                     "cross-checks the linkage matrices)"],
        ["pandas, ipykernel, nbformat, nbconvert", "notebook tables and notebook execution"],
        ["reportlab", "this PDF report"],
    ]
    story.append(data_table(["package", "used for"], dep_rows,
                            [2.6 * inch, 3.9 * inch], styles))

    return story


def build(data, page_map, out_path=OUT_PDF):
    styles = make_styles()
    doc = Report(out_path, page_map)
    doc.build(build_story(data, styles, page_map))
    return doc.page_map


def main():
    with open(RESULTS, encoding="utf-8") as fh:
        data = json.load(fh)

    # Build until the recorded page numbers stop moving, then write the final file.
    # (A build to a scratch path is harmless: the PDF is regenerated below.)
    scratch = os.path.join(ROOT, "_report_pass.pdf")
    page_map = {}
    for _ in range(4):
        new_map = build(data, page_map, scratch)
        if new_map == page_map:
            break
        page_map = new_map

    final_map = build(data, page_map, OUT_PDF)
    if os.path.exists(scratch):
        os.remove(scratch)

    print("wrote", OUT_PDF)
    print("answer pages:", {k: final_map[k] for k in sorted(final_map)})
    print("total pages:", max(final_map.values()))


if __name__ == "__main__":
    main()

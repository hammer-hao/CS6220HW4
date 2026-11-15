# CS 6220 — Homework 4

Frequent itemsets with Apriori, association rules with an anti-monotone
`Apriori_rules`, and hierarchical agglomerative clustering (single and complete
linkage) on a 2-D dataset.

**Report:** [`HW4_Report.pdf`](HW4_Report.pdf) — answers Q1–Q12, with a page locator on page 2.
**Notebook:** [`CS6220_HW4.ipynb`](CS6220_HW4.ipynb) — the complete solution, committed with all
outputs.

---

## What is implemented

| Part | Item | Where |
|---|---|---|
| 1 | `support(itemset, transactions)`, `confidence(antecedent, consequent, transactions)` | notebook, §1.2 |
| 1 | `apriori(transactions, min_sup)` with explicit join / prune / count steps and a per-`k` pruning log | notebook, §1.3 |
| 2 | `apriori_rules(frequent, transactions, min_conf)` — level-wise search over consequents | notebook, §2.1 |
| 2 | `apriori_general(...)` — the optional generalisation; reproduces both of the above | notebook, §2.6 |
| 3 | `hac(X, dist_fn)` with incremental cluster-distance updates, `cut_tree`, `plot_dendrogram` | notebook, §3.2–3.4 |

## Requirements

Python 3.10+ and the packages in [`requirements.txt`](requirements.txt). The versions
below are the ones the results were produced with:

```bash
python -m pip install -r requirements.txt
```

## Run the notebook

```bash
jupyter nbconvert --to notebook --execute --inplace CS6220_HW4.ipynb
```

or open it interactively with `jupyter lab CS6220_HW4.ipynb` and *Run All*. Executing the
notebook

* prints every support / pruning / rule table,
* writes the five figures to `figures/`, and
* writes every number used in the report to `results/hw4_results.json`.

Run it from the repository root: the notebook reads `clustering.txt` with a relative path.

## Rebuild the report

```bash
python tools/make_report.py
```

This reads `results/hw4_results.json` and `figures/*.png` and rewrites `HW4_Report.pdf`.
It builds the document twice so the answer locator can list the real page numbers.

## Repository layout

```
CS6220_HW4.ipynb     solution notebook (all cells executed)
HW4_Report.pdf       written report, answers Q1-Q12
clustering.txt       370 x 2 dataset for Part 3
requirements.txt     pinned dependencies
figures/             fig1_dataset, fig2/4 dendrograms, fig3/5 cluster plots
results/             hw4_results.json - every number in the report
tools/make_report.py report generator (reportlab)
prompts.md           record of the AI-assisted development
```

## Results at a glance

* **Apriori**, `min_sup = 0.25`: 10 frequent itemsets (5 singletons, 4 pairs, 1 triple);
  2 of the 3 length-3 candidates are pruned; the search stops at `k = 4`.
* **Apriori_rules**, `min_conf = 0.6`: 11 rules; strongest `{Bread, Milk} -> {Butter}`
  (support 0.25, confidence 1.00, lift 3.33), weakest `{Bread} -> {Milk}`
  (confidence 0.63, lift 1.14).
* **HAC**, 13 clusters: `min_dist` (single linkage) recovers all 13 natural groups
  (four elongated strips, four small blobs, three round blobs, two rings), while `max_dist`
  (complete linkage) cuts the strips and the rings into pieces.

## Verification performed by the notebook

* `support` / `confidence` checked against hand-computed values;
* `Apriori_general` asserted to reproduce `Apriori` (identical 10 itemsets) and
  `Apriori_rules` (identical 11 rules);
* the incremental linkage distances asserted equal to a naive reimplementation that
  recomputes cluster distances from all pairs of points (40-point sample, difference 0.0);
* both dendrograms and both 13-cluster partitions asserted equal to
  `scipy.cluster.hierarchy.linkage` / `fcluster`.

# Development record and AI assistance

Per the assignment, this file documents how the solution was developed and what part of it
was produced with the help of AI.

## Tools used

* **AI coding agent:** DeepSeek Harness (deepseek-flash model), used as an assistant for
  drafting the implementations, the notebook prose and the report generator.
* **Verification (not AI):** every algorithmic claim is checked inside the notebook —
  against hand-computed supports and confidences, against a naive O(n^3) reimplementation of
  the linkage update, and against `scipy.cluster.hierarchy` for both linkage rules.

> **Shareable chat link:** _to be filled in by the author_ — paste the shared conversation
> URL here before submitting.

## Main prompts, in the order they were used

Each prompt corresponds to one step of the pseudo-code in the report.

### 1. Reading the assignment and the data

> Read `HW4.pdf` and `clustering.txt`. List every deliverable and every question
> (Q1–Q12) with its point value, and describe the structure of the clustering data.

### 2. Part 1 — support, confidence, Apriori

> Implement `support(itemset, transactions)` as a fraction of transactions containing all
> items, and `confidence(A, B)` as support(A ∪ B)/support(A). Then implement Apriori with the
> three explicit steps: *join* (pairs of frequent (k−1)-itemsets sharing their first k−2
> items), *prune* (drop a candidate when one of its (k−1)-subsets is not frequent, logging
> each pruned candidate and the offending subset), and *count* (one pass over the
> transactions). Expose a per-k log with the number of candidates, pruned candidates and
> frequent itemsets. Use `min_sup = 0.25` on the 20-transaction example.

### 3. Part 2 — Apriori_rules

> Implement `apriori_rules` that, for each frequent itemset Z, grows the consequent H
> level-wise and prunes using the anti-monotonicity of confidence (if conf(Z\H → H) < min_conf
> then no superset consequent can be confident). Report support, confidence and lift
> (lift = confidence / support(consequent)) for `min_conf = 0.6`. Do not enumerate all splits
> of Z.

### 4. Bonus — Apriori_general

> Abstract the common loop of Apriori and Apriori_rules into
> `apriori_general(seed, join_step, prune_step, score_step, min_thr)` and assert that it
> reproduces both earlier results exactly.

### 5. Part 3 — HAC

> Implement agglomerative clustering with the cluster-distance function as a parameter,
> supporting `min_dist` and `max_dist`. Update the distance matrix incrementally: after a
> merge, the new distances are the elementwise min/max of the two existing rows, never a scan
> over pairs of points. Record each merge (children, distance, size) so a dendrogram can be
> drawn and cluster membership for a target k can be recovered by cutting the merge record.

### 6. Analysis, figures and report

> Run the experiments, discuss the pruning statistics, the {Butter, Bread, Eggs} question,
> the strongest/weakest rules, and the 13-cluster comparison of the two linkages. Produce the
> notebook with all cells executed and a PDF report with a page locator for Gradescope.

## What was reviewed by hand

* Every support and confidence value in the report tables was re-derived by hand from the
  transaction list (e.g. support(Bread) = 8/20, confidence(Bread → Butter) = 6/8).
* The 13 clusters were checked against the scatter plot and against the bounding boxes of the
  clusters (each cluster's extent was inspected to confirm that the four strips and the two
  rings really are single, contiguous groups).
* The two linkage results were cross-checked against SciPy on the full dataset.

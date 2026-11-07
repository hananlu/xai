# Update: focused priorities completed

The common-case table and learned-layer parameter control described below are now completed and independently audited in ../xai_replication_32/conference_checks/. The main paper is eight pages including references and shows the bounded results; the notebook/deck are updated. Original source/data/model freezes remain unchanged. The control is post-hoc, conditional on comparable nonflat records and does not validate causal demand attribution. Broader network/replacement validation remains a scope limitation, not an experiment added to this conference version.

The text below is the historical pre-extension review.

---

# Submission readiness review — 7 November 2026

Scope: review of the current manuscript and delivered project artifacts, not a new systematic literature search or a new experiment. The current study is a reproducible empirical draft; publication readiness still depends on a sharper evidence-to-claim argument and venue fit.

## Highest priority: make attribution usefulness visible

The main paper emphasizes target-minus-source differences. A difference near zero can also occur when both source and target rankings are unhelpful. Report absolute Q and a compact comparison of Shapley, IG, occlusion and recency, with each method's effective denominator. Existing quality CSV files already contain these methods. No model retraining is required to construct the comparison.

Use common cases and complete neural-seed sets. IG has a smaller accepted subset; comparing accepted IG against all-case Shapley can confound method with case selection. A main full-budget Shapley/occlusion/recency panel and a separate common-accepted-IG panel would be clearer. Label any newly constructed analysis as exploratory; preserve both frozen primary endpoints and existing inference rules.

## Additional validation requiring an actual new test

The arithmetic calibrations, Shapley efficiency/permutation checks, checkpoint re-queries and IG tolerances validate implementation consistency. They do not by themselves show that an attribution depends on learned model parameters. A parameter-randomization sanity control is a useful next experiment, with rules defined before running it. Test whether the explanation responds to changes in model parameters; do not assume its operator-normalized Q must decrease, since the response game also changes with the model.

## Sharpen the empirical contribution

The study already states a bounded deployment/measurement gap, but the reader should quickly see how its evaluation differs from the closest cited network-XAI and explanation-generalization work. A concise comparison of deployment unit, frozen source fitting, reference semantics, numerical screening, timestamp pairing and informative-case exclusions would make the contribution easier to assess. It would not establish a first-in-field claim.

The robust narrative is that neither cohort establishes systematic degradation or equivalence, while reference-specific secondary evidence does not recur and low-volume forecast/denominator failures limit apparent complete-case reliability. Keep that evidence visible, rather than treating lack of a significant transfer penalty as proof that XAI transfers safely.

## Important scope limits, not all immediate blockers

All institutions share one ISP, source anchors and trained models overlap, and the two history replacements are controlled stress tests. There is no independently validated conditional traffic replacement mechanism or external-network replication. These constrain broader claims; they need not all be resolved to submit a carefully scoped empirical paper. Additional specialized explainer/model baselines depend on the target venue and exact comparative claim.

The method does not validate causal traffic demand attribution, a universal explainer ranking, equivalence or cross-ISP reliability. Existing complete-case exclusions and nominal uncertainty are disclosed and should remain so.

## Layout correction

Two-column LaTeX figure floats were deferred beyond their source position and reached a page containing references. The previous layout review missed that ordering problem. The current source moves the local example earlier and places a float barrier before the bibliography. The main paper remains seven pages including all 18 references, with six figures and two tables. The reference page has no figures. Scientific results and frozen code/model/data inputs are unchanged.

Suggested next sequence: (1) existing-output method-comparison table, (2) prespecified parameter-randomization control, (3) tighten the contribution comparison and finalize the venue-specific format. No additional experiment is claimed in this review.

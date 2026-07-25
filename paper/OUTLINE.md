# BioHackrXiv report — drafting plan

**Working title:** *Measure before you rewrite: ablation-driven redesign of LLM-facing RDF
schema documentation in TogoMCP*

**Short title:** *Togothon: ablation-driven MIE redesign*

**Framing (per your choice):** the **measure-then-redesign method** is the subject. The v3
format is the payoff and the equivalence run is the receipt — neither is the headline. The
report's thesis in one sentence: *we did not know which parts of our LLM-facing documentation
earned their tokens, so we measured it by ablation; the measurement said the value was real
but heavily redundant and concentrated in query-construction content; we rebuilt the format
around that finding and proved equivalence at 15% fewer input tokens.*

**Evidence scope:** everything — the nulls, the super-additive redundancy arc, and the full
set of methodological traps. The traps section is written to be the most reusable part of the
paper for anyone else running an eval like this.

**Target length:** ~4,500–5,500 words + 3 figures + 7 tables. That is long for BioHackrXiv but
justified by the evidence volume; §5 (traps) and §8 (discussion) are the compressible parts if
we need to cut.

---

## 1. Front matter (YAML)

| field | value | status |
|---|---|---|
| `title` | *Measure before you rewrite: ablation-driven redesign of LLM-facing RDF schema documentation in TogoMCP* | draft |
| `title_short` | `Togothon: ablation-driven MIE redesign` | draft |
| `tags` | knowledge graphs; SPARQL; RDF Portal; Model Context Protocol; LLM agents; benchmarking; ablation study | draft |
| `authors` / `affiliations` | **NEEDED** — names, ORCIDs, RORs, CRediT roles | ❗ |
| `date` | 24 July 2026 (or the Togothon date) | draft |
| `event` / `biohackathon_name` / `_url` / `_location` / `group` | **BLOCKER — see below** | ❗ |
| `git_url` | must point at *your* `mie-redesign` repo, not the template | ❗ |
| `cito-bibliography` | `paper.bib` | ok |
| LICENSE | template ships a placeholder; BioHackrXiv wants **CC-BY** | ❗ |

### The Togothon metadata blocker

Togothon is DBCLS's monthly knowledge-graph meeting (the former SPARQLthon); **Togothon166 ran
23–24 July 2026 at CRIK Shinanomachi**, i.e. this week. But Togothon is **not** in the
BioHackrXiv meetings index — the registered Japanese meetings are `BH25JP` (DBCLS BioHackathon
2025, Mie), `BH24JP`, `BH23JP`, `BH22JP`, etc. Three ways out, in order of preference:

1. Ask DBCLS to register Togothon as a BioHackrXiv meeting (it is a recurring, organized event;
   this is the clean fix and helps every future Togothon report).
2. File under `BH25JP` and mention Togothon in the text as where the work was carried out.
3. Submit with custom `biohackathon_*` fields and let the editors sort it out — the PDF will
   build, but the meeting page won't link it.

I've left this as a marked TODO in the draft either way.

---

## 2. Section plan

### §1 Introduction (~500 words)

- RDF Portal exposes ~36 life-science SPARQL endpoints; TogoMCP wraps them as an MCP server so
  an LLM agent can query them in natural language. Published: *Database* 2026,
  doi:10.1093/database/baag042 — **that paper is built on MIE v2** and establishes that MIE
  files help in aggregate.
- The gap this report addresses: an MIE file is documentation *written for a model*. Ours had
  grown to 11 hand-authored sections per database across 36 databases, by intuition. Nobody
  knew which sections earned their tokens — and every token is re-read on every turn of every
  session, so the cost is recurring and the question is not academic.
- Stated as a general problem: **what belongs in a "schema card" for an LLM agent, and how
  would you know?** Anyone building an MCP server over a structured resource faces it.
- Contributions: (a) a reusable ablation harness + statistical protocol for LLM-facing
  documentation; (b) the finding — value real, heavily redundant, concentrated in
  query-construction content; (c) MIE v3, a format derived from that evidence; (d) a
  pre-registered equivalence release showing −15% input tokens / −15% cost / −6% latency at no
  measured quality cost, with factoid accuracy up.
- One paragraph on what we did *not* find, flagged early so the nulls read as a result rather
  than a failure.

### §2 Background: TogoMCP and MIE files (~450 words)

- TogoMCP architecture in three sentences (root FastMCP + mounted sub-servers; `run_sparql`,
  `get_MIE_file`, REST wrappers, TogoID/NCBI/TogoVar).
- **Table 1** — the v2.3 MIE: 11 sections, one line each on what each was *supposed* to do, and
  the three functional groups we later ablated together, with byte share:

  | group | sections | share of MIE bytes |
  |---|---|---|
  | query | `schema_info`, `shape_expressions`, `sparql_query_examples`, `cross_references`, `cross_database_queries` | 53% |
  | guardrails | `critical_warnings`, `common_errors`, `anti_patterns` | 25% |
  | orientation | `architectural_notes`, `data_statistics`, `sample_rdf_entries` | 22% |

- The benchmark we measure against: 100 biologically grounded questions, 5 types × 20
  (`yes_no`, `factoid`, `list`, `summary`, `choice`), 34 databases, ≥60% multi-database, all
  screened by a PubMed test so the answer is not recoverable from literature. Scoring:
  LLM-as-judge on four criteria (recall, precision, non-redundancy, readability), 1–5 each,
  **4–20 total**; plus a binary exact-answer grader on the gradable subset.
- **Key point to make explicitly:** the observation that the redundancy was *orthogonal* — the
  same predicate-level fact restated up to three ways (ShEx shape / sample triple / worked
  query, with the xref list a loose fourth). This is the hypothesis the ablations test.

### §3 Method: an ablation harness for documentation (~600 words)

- Mechanism: `ablate_mie.py` generates a stripped corpus variant; a local TogoMCP instance
  serves it via `TOGOMCP_MIE_DIR`; `run_ablation.py` runs each condition against the benchmark
  in isolated sessions. Answering `claude-sonnet-4-5`, judge `claude-opus-4-8`, both through
  the Anthropic API.
- **Four ablation families** — present them as a designed escalation, because that's the
  argument:
  1. **leave-one-section-out** (11 conditions) — marginal necessity
  2. **leave-one-group-out** (3 conditions) — necessity with redundancy suppressed
  3. **whole-MIE removal** (`no_mie`, tool-level block on `get_MIE_file`) — total value
  4. **leave-one-in / keep-one-group** (3 conditions) — sufficiency
- Statistics: every reported effect is a **paired per-question** difference with a 95% CI;
  ceiling/floor trimming (`--exclude-ceiling 20 --exclude-floor 12`) reported alongside
  untrimmed; multiple-comparison thresholds stated per family (|z|>2.84 at k=11, >2.39 at k=3,
  >1.96 for the single planned `no_mie` comparison).
- Scale, so readers can budget their own: 40-question pilot × 3 replicates per condition;
  section sweep ~$845 / ~72 h, group sweep ~$265 / ~27.5 h, plus keep-one-in and `no_mie`.
- **Design decision worth a paragraph:** we escalated only because the cheap test was null.
  Leave-one-out is cheap and answers "necessary?"; it cannot distinguish "worthless" from
  "redundant". That distinction needs whole-removal *and* leave-one-in, and those are the
  expensive runs. Recommend this ordering to others.

### §4 Results I — the redundancy arc (~700 words)

- **Table 2** — the 11 leave-one-out contributions with CIs and z (verbatim from FINDINGS).
  Headline: **0 of 11** have a CI excluding 0, on any of three axes (judge score, exact-answer
  correctness, query effort). Baseline 17.13/20. Best is `common_errors` +0.65 ± 0.65 (z=1.94)
  — nominally p≈0.052, fails Bonferroni, and one near-miss out of 11 is what chance produces.
  Report the power calculation (n≈73 needed) so the null is bounded, not just asserted.
- Group ablation: also null. Removing the **entire `query` group — 53% of the MIE — costs
  +0.20 ± 0.40**. The pre-registered Σ-of-sections prediction (guardrails leads) failed
  outright: guardrails came last.
- `no_mie`: **the first non-null.** +0.88–0.93 ± 0.68, z≈2.6, p≈0.007–0.02, stable across 1- and
  5-judge treatments.
- **Table 3 / Figure 2 — the arc.** This is the paper's central result and should be a figure:

  | removed | contribution | significant |
  |---|---:|---|
  | one section (×11) | ≤ +0.65 | no |
  | one group (×3) | ≤ +0.20 | no |
  | Σ of the 3 groups | +0.34 | — |
  | **whole MIE** | **+0.88–0.93** | **yes** |

  The whole is **~2.7× the sum of its parts** — super-additivity is the signature of strong
  redundancy, and it is what disambiguates the group nulls from worthlessness. Note honestly
  that mid-investigation the group null *looked* like a refutation of the redundancy
  hypothesis, and `no_mie` reversed that reading.
- **Table 4 — leave-one-in (sufficiency).** `keep_query` alone recovers **+0.92 ± 0.54 (z=3.32)
  = 99%** of the whole-MIE effect; its complement (baseline − keep_query) is **+0.01**, i.e.
  dropping guardrails+orientation from the full MIE costs nothing measurable.
  `keep_orientation` 44% (NS), `keep_guardrails` 13% (NS).
- Two secondary findings worth their space:
  - **The one robust behavioral effect is not about quality:** removing `guardrails`
    significantly *cuts* SPARQL calls (−0.92 ± 0.92). The warnings provoke defensive querying.
  - **Variance is answer-limited, not judge-limited:** decomposing 3 answers × 5 judges gives
    judge-jitter SD 0.41 vs between-answer SD 1.20 — **98% of the per-question mean variance is
    agent stochasticity.** This reverses a standing assumption in our own notes and changes the
    power lever from "more judges" to "more answer replicates / more questions." Directly
    useful to anyone designing an LLM-as-judge eval.

### §5 Results II — traps that faked or destroyed signal (~800 words) ← *the reusable section*

Present as eight numbered lessons, each with the concrete incident and the rule it produced.
Consider boxing this or giving it a summary table (**Table 7**).

1. **Never bank a baseline across batches.** Our first analysis showed *every* section
   contribution slightly negative — removing anything apparently helped. Cause: the baseline
   had been reused from a run 1–2 days earlier. All 11 contributions subtract the same
   baseline, so they are **one event, not eleven** — a baseline sitting ~0.4 low drags them all
   negative together. Fresh in-batch baseline: 16.72 → 17.13, and the pattern dissolved into a
   healthy 7-positive/4-negative spread. *Rule: baseline and ablated rows must come from the
   same batch, and beware resume logic that silently reuses a prior condition.*
2. **An aggregate difference is not a per-question effect.** `sparql_query_examples` looked like
   a clear winner: removing it drove SPARQL calls 466 → 585 (+25%). Paired, the per-question
   delta was +0.87 ± 1.07 — CI includes 0. Per-question counts vary enormously (paired SD ≈
   3.2); the ratio was reading a sum as an effect.
3. **Check for hidden coupling — an ablation can be a dual ablation.** Stripping `schema_info`
   also broke the `find_databases` discovery tool, which builds its catalog from that block. Its
   near-zero contribution is therefore a robustness result, not evidence the text is worthless.
   The tell is in the logs: fallback `list_databases` calls jump 1–2 → 38. Two knock-ons —
   the `query` group inherits the confound, and, by luck of where `schema_info` sits, the
   `keep_query` headline is measured entirely *between working-discovery conditions*, so the
   confound cancels exactly where it would have mattered most.
4. **Your benchmark may leak through the tool schema.** The full 36-database roster is in the
   `database` parameter's enum on `run_sparql`/`get_MIE_file`, and tool schemas are not
   stripped by any corpus ablation. So every condition sees every database name; the benchmark
   is *name-free but domain-transparent*. Worth stating because it bounds what any
   discovery-side ablation can measure.
5. **Gate on evidence the condition actually ran.** A relative `--results-dir` resolved against
   the wrong working directory, so config paths silently failed, the runner fell back to
   production defaults, and **every group sweep for nine days served identical full MIEs** —
   zero ablation signal, no error. Tell-tale: 0 `CallToolRequest`s in the condition's server log
   vs ~1500 in a valid one. *Rule: assert non-zero tool calls per condition before trusting any
   number.*
6. **Subscription auth cannot sustain a batch this size.** Rate-limited runs produced
   `"Not logged in · Please run /login"` answer stubs that the runner recorded as
   `success=True`, scoring 4/20 — whole conditions of 40/40 login errors. Fixed by forcing API
   auth plus an abort-after-3-consecutive-failures guard on the judge.
7. **Token accounting must include the prompt-cache buckets.** We recorded only `input_tokens`
   and dropped `cache_creation_input_tokens` / `cache_read_input_tokens` — which is exactly
   where a large MIE read is billed. A single-turn probe: `input_tokens: 10` vs
   `cache_creation_input_tokens: 20,366`. **The redesign's own target metric was structurally
   unmeasurable** until this was fixed. The same fix removed a latent double-count.
8. **Spurious content-policy refusals contaminate agent benchmarks.** ~5% of cells returned a
   near-identical ~420-character refusal on benign microbiology questions; 4 questions were
   refused by *both* arms on every run and measure nothing. Refusals floor a cell at 4/20, so an
   imbalanced split flips a delta: batch 1's raw +1.31 was **+0.58 once refusals were excluded**
   — the difference was refusal luck, not capability. *Rule: detect refusals by signature,
   report raw and clean, and trust the clean number.*

Plus a short closing paragraph on **ceiling effects**: baseline 16.7–17.1/20 means the judge
score cannot resolve sub-0.4-point effects at this n, which caps every null above.

### §6 The v3 redesign (~600 words)

- The design rule the evidence implies: value is concentrated in query-construction content, so
  reorganize *around* it, collapse the 3× restatement, drop the prose-only sections.
- **The core move:** the **verified, executable worked example becomes the atomic unit** — one
  example *is* the shape, the sample triple, and the annotated warning it would otherwise be
  written as, three times.
- **Table 5 / Figure 1** — the v2→v3 mapping (11 author-function sections → 5 need-based parts:
  `discovery`, header, `examples`, `schema_delta`, `id_join_map`).
- Authoring rules, each with the reason it exists:
  - §4.1 **everything countable is verified and dated** → the file becomes machine-testable; a
    re-run that disagrees is a drift signal, not silent rot. (Include the YAML `on:`-parses-as-
    boolean footgun — it's a nice detail and a real trap.)
  - §4.2 one fact, one place.
  - §4.3 carry only the non-recoverable (with the "example scaffolding rides for free" carve-out).
  - §4.4 **a positive route is not a caveat** — see §7, this rule was *bought* by a regression.
  - §4.6 **no test leakage** — an example's subject must not be a benchmark entity.
  - §4.5 progressive disclosure as a forward-looking hook.
- Outcome: 36 databases, 302 examples, **29–65% smaller** per file. Authored two hand-written
  pilots + 34 agent-delegated, every enumeration route independently live-re-verified. Note in
  passing that live verification **caught real errors in the v2 corpus** (chebi role-IRI
  mislabel, rhea dropped cross-join, pdb EC-prefix over-match, clinvar gene-bnode split, …) —
  evidence that "verified and dated" is doing work beyond the token budget.

### §7 Validation: smoke → canary → full equivalence (~700 words)

- **Pre-registration matters here and should be stated up front:** this was declared an
  *equivalence* test, not "did the score go up." Three criteria, fixed before the run: bytes
  down (deterministic, no statistics), judge score flat within a **±0.5/20** margin, factoid
  correctness up-or-flat.
- **Smoke (2 databases, 25 questions).** Flat on average (−0.44 ± 0.82, uniprot −0.13) but with
  a *systematic* localized regression: q066, where v3 found 14 LIM-domain proteins vs the true
  71, wrong on all 3 runs. Root cause: v2 documented UniProt keyword classification as a
  first-class enumeration route in ~5 places; the v3 draft collapsed all of it into a single
  *negative caveat* ("`up:classifiedWith` also carries keywords, filter them out"), so the agent
  read the route as noise to exclude. **This is the origin of spec rule §4.4.** Then the honest
  epilogue: the first fix used q066's exact subject (LIM domain, count 71) — leakage — so it was
  de-overfit to a neutral subject (SH3 domain) and **transfer-tested**: the agent generalized the
  idiom to LIM domain and scored 18 on all 3 runs with no LIM entity anywhere in the corpus.
  The de-overfit version was *better* than the overfit one.
- **Canary (10 risk-first questions).** Caught q022, a subtler failure: the GlyCosmos endpoint
  embeds its **own partial GO snapshot**, whose `subClassOf*` closure yields 14 terms → 44 genes.
  v3 was self-consistent — it trusted a deficient local hierarchy. The correct route expands on
  the authoritative `go` database (33 terms) and VALUES-joins back (208, gold-exact). Fix: a
  first-class two-database enumeration example. Δ went **−5.7 → +1.0**, and v3 became *more*
  stable than v2, which had reached 208 only via an external ontology service and collapsed on
  one run. *Lesson worth stating generally: a co-hosted ontology snapshot is not the ontology.*
- **Full equivalence run, n=100 × 3 replicates × 2 corpora,** in five gated batches.
  - **Figure 3 / Table 6 — the CI ladder:** n=50 +0.34 [−0.14, +0.82] → 75 +0.29 [−0.11, +0.70]
    → 85 +0.30 [−0.09, +0.69] → **100 +0.293 [−0.09, +0.68]** (96 usable questions). Monotonically
    tightening, estimate stable. Draw the −0.5 non-regression margin on the figure.
  - **Read it correctly, and say so:** the CI straddles 0, so this is genuine *equivalence*, not
    a proven gain. The mild positive tilt must not be over-claimed. What the data does support:
    the lower bound (−0.09) sits well inside the −0.5 margin ⇒ v3 demonstrably does not regress.
  - By question type: **factoid +1.01** (the largest gain, and exactly the aggregation /
    query-construction axis v3 targets), yes_no +0.54, list +0.18, choice +0.16, **summary −0.42**
    (the one soft type — v3's terseness gives less scaffolding for open-ended prose synthesis).
    Recall sub-score +0.16 corroborates.
  - **Table 7 — the deterministic win, measured at runtime:** input tokens −15.4% (73,059 →
    61,790 per question), cache-read −17.0%, cost −14.8% ($0.52 → $0.44/question), latency −5.9%.
    Explain why a 29–65% file shrink lands as 15% fewer total input tokens: the MIE is a large
    but partial share of per-question context.
- Data-quality caveat stated plainly: ~5% refusal contamination, 4 questions unmeasurable,
  excluded from the clean verdict.

### §8 Discussion (~600 words)

Five points, in order of how transferable they are:

1. **Redundancy is invisible to leave-one-out, and that is a general trap in ablation studies of
   documentation.** "Not individually necessary given everything else" is not "worthless." If
   your ablation is null, you have not shown the content is dead weight — you need whole-removal
   (total value) and leave-one-in (sufficiency) to tell those apart. Our arc — section-null +
   group-null + whole-significant + one-group-sufficient — is one coherent story only when read
   as a set.
2. **The example is the right atomic unit for LLM-facing schema documentation.** A verified
   executable query carries the shape, an instance, and the trap simultaneously, and — unlike
   prose — it is machine-checkable. This is the design claim we'd defend beyond TogoMCP.
3. **Compression preferentially destroys positive routes.** The q066 failure is the general
   shape: a mechanism that is both "*the* way to do X" and "watch out for X when doing Y" gets
   compressed to the caveat, which reads to the agent as *avoid this* — the opposite of intent.
   Relevant to anyone summarizing documentation, by hand or with an LLM.
4. **Documentation as a testable artifact.** Verified-and-dated values turn drift into a signal
   and let CI execute every example. This changes the maintenance economics of a 36-database
   corpus more than the token saving does.
5. **Agent-authored documentation needs a leakage rule.** When the docs and the eval are both
   produced with model assistance, an example can quietly contain the test answer. §4.6 plus a
   grep against the question set is a cheap, general guard.

**Limitations,** stated without hedging: single answering model (Sonnet 4.5) and single judge
family; one benchmark, whose ceiling (16.7–17.1/20) caps resolvable effect size; 40-question
pilot for the ablations (n≈73–88 needed for a `common_errors`-sized effect); LLM-as-judge; ~5%
refusal contamination; the equivalence result is equivalence, not superiority.

### §9 Future work (~250 words)

- **Progressive disclosure**: `get_MIE_file(database, level=header|+examples|full)` — the v3
  header was authored to stand alone precisely so this is possible.
- **CI that executes every example's `verified:` block** against the live endpoint; drift as a
  build failure.
- **Per-query outcome logging** (syntax error / empty / rows) — a far sharper effort metric than
  tool-call counts, and the direct test of whether query-guidance content does what it claims.
- **Power**: make exact-answer correctness the primary endpoint at n≥150, and buy precision with
  answer replicates rather than judge replicates (per the variance decomposition).
- Cross-model replication; migration of the authoring tooling to v3 (done post-release);
  applying the same measure-then-redesign loop to the Usage Guide.

### §10 Availability, Acknowledgements, References

- Code: TogoMCP repo, release **v2.0.0** (the MAJOR that flipped the served corpus to v3 and
  retired the discovery trio); the `benchmark/` tree with the ablation harness, the 100-question
  set, and the durable `FINDINGS.md` records. Server: https://togomcp.rdfportal.org/
- Suggest a **Zenodo DOI** for the release + benchmark snapshot so the report has something
  citable and archival. (Decision needed.)
- CiTO annotations: `citesAsAuthority:` the *Database* TogoMCP paper (this work extends it —
  `extends:` is arguably the right term), `citesAsDataSource:` RDF Portal, MCP spec.

---

## 3. Figures and tables to produce

| # | Type | Content | Source | Effort |
|---|---|---|---|---|
| Fig 1 | diagram | v2 (11 sections, grouped) → v3 (5 parts) mapping | MIE_v3_spec §1.3 | low (Mermaid/SVG) |
| **Fig 2** | forest plot | **The redundancy arc** — 11 section effects, 3 group effects, Σ groups, whole-MIE, 3 keep-one-in, all with 95% CI, zero line marked | ablation FINDINGS tables | medium (matplotlib) |
| Fig 3 | line + band | CI ladder: Δ vs n (50/75/85/100) with −0.5 margin | release FINDINGS | low |
| Table 1 | — | v2 sections × functional groups × byte share | ablation FINDINGS | trivial |
| Table 2 | — | 11 leave-one-out contributions (CI, z, Δ effort) | ablation FINDINGS | trivial |
| Table 3 | — | Redundancy arc summary | ablation FINDINGS | trivial |
| Table 4 | — | Leave-one-in sufficiency (%gap, complement) | ablation FINDINGS | trivial |
| Table 5 | — | v2→v3 section mapping | MIE_v3_spec §1.3 | trivial |
| Table 6 | — | Equivalence by question type | release FINDINGS | trivial |
| Table 7 | — | Runtime tokens/cost/time | release FINDINGS | trivial |

Fig 2 is the one that carries the argument visually — worth the effort. All numbers exist in the
committed `FINDINGS.md` files, so no result CSVs are needed (they're gitignored anyway).

---

## 4. Open questions — I need your input on these

1. **Authors, ORCIDs, affiliations, CRediT roles.** Who's on it? (BioHackrXiv wants ≥2 authors.)
2. **The Togothon/meeting metadata** — register Togothon with BioHackrXiv, file under `BH25JP`,
   or submit with custom fields? Which Togothon number and date should the report name?
3. **Is the `mie-redesign` repo the public home of the paper?** `git_url` must point there, and
   the LICENSE needs swapping to CC-BY.
4. **How much of the design rationale can be public?** The full rationale doc
   (`internal_docs/mie-redesign-from-scratch-2026-07-20.md`) is gitignored. I'll write §6 from
   the shipped spec only unless you want to publish the rationale too.
5. **Zenodo DOI** for the TogoMCP v2.0.0 release + benchmark snapshot — worth minting for the
   Availability section?
6. **Should the report name the models?** Naming `claude-sonnet-4-5` / `claude-opus-4-8` is
   reproducibility-correct but dates the paper. My recommendation: name them.
7. **How prominent should the `summary −0.42` soft spot be?** I plan to report it plainly in §7
   and again in Limitations. Say if you'd rather it be one mention.
8. **Word budget** — is ~5,000 words acceptable, or should I target the shorter ~3,000?

## 5. Suggested next steps

1. You answer the open questions above (at minimum #1 and #2 — the rest can be TODOs).
2. I generate Figures 1–3 and drop them in `paper/`.
3. I draft `paper/paper.md` end-to-end and `paper/paper.bib`, committed into your local
   `mie-redesign` checkout.
4. A verification pass: every statistic in the draft re-checked against the source `FINDINGS.md`
   files, CI arithmetic re-derived, and the PDF built through the BioHackrXiv preview service.

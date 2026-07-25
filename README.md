# Measure before you rewrite

A BioHackrXiv report on the ablation-driven redesign of **MIE files** — the per-database schema
documents that [TogoMCP](https://togomcp.rdfportal.org/) delivers to an LLM agent at query time so
it can compose SPARQL against the DBCLS [RDF Portal](https://rdfportal.org/).

The MIE format had grown to eleven hand-authored sections across 36 databases, each section added
because someone believed it would help. Nobody had checked whether it did. This report is about
finding out, and about what the answer implied for the format.

**The finding.** Removing any single section is null. Removing any whole functional group is null.
Removing *everything* costs +0.9/20 — the whole is worth ~2.7× the sum of its parts, the signature
of heavy redundancy. And one group alone, the query-construction content, recovers 99% of the
total. The value was real, distributed, and concentrated somewhere specific.

**The consequence.** MIE v3 reorganizes around that evidence, with the verified executable example
as the atomic unit — one example *is* the shape, the sample triple, and the annotated trap. At
n=100 benchmark questions it is statistically indistinguishable from v2 in answer quality while
using **15% fewer input tokens**, costing **15% less**, and running **6% faster**, with the
factoid-question score up a full point.

The report also documents eight measurement traps that faked or destroyed signal along the way —
a banked baseline that made eleven independent-looking results out of one, a harness bug that
silently voided nine days of sweeps, token accounting that omitted the prompt-cache buckets where
the whole effect was billed — and a correction to our own method: we spent the most money on the
least informative experiment, and say why we would not do that again.

## Contents

| Path | |
| --- | --- |
| [`paper/paper.md`](paper/paper.md) | The report (source of record) |
| [`paper/paper.pdf`](paper/paper.pdf) | Built automatically from `paper.md` on push to `main` |
| [`paper/paper.bib`](paper/paper.bib) | Bibliography |
| [`paper/figs.py`](paper/figs.py) | Regenerates all three figures |
| [`paper/OUTLINE.md`](paper/OUTLINE.md) | Drafting plan and open questions |

## Figures

All figure data is transcribed from the durable `FINDINGS.md` records in the TogoMCP repository;
no result CSVs are needed.

```bash
pip install matplotlib
python paper/figs.py        # writes the three PNGs into paper/
```

## Building the PDF

`.github/workflows/gen_pdf.yaml` renders `paper/paper.md` through the BioHackrXiv service on every
push to `main` and commits the result back. To preview a draft by hand, point the
[BioHackrXiv Preview Service](http://preview.biohackrxiv.org/) at this repository.

## Underlying work

- **TogoMCP** — <https://togomcp.rdfportal.org/> · source at <https://github.com/dbcls/togomcp>.
  The ablation harness, the 100-question benchmark, the MIE v3 corpus and specification, and the
  `FINDINGS.md` records behind every number in this report all live there.
- **Archived snapshot** (release v2.0.0, the version everything was measured against) —
  [doi:10.5281/zenodo.21543297](https://doi.org/10.5281/zenodo.21543297)
- **The system paper**, which describes TogoMCP and is based on MIE v2 —
  Kinjo *et al.*, *Database* **2026**:baag042,
  [doi:10.1093/database/baag042](https://doi.org/10.1093/database/baag042)

## Citation

Until the preprint is posted, cite the archived software snapshot above. The report's own DOI will
be added here on publication.

## License

[CC BY 4.0](LICENSE).

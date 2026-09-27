# Bibliography audit - 2026-09-27

Audited on 2026-09-27. Scope: all 36 original entries in `neurips/references.bib`, including uncited entries, plus the requested `KarimireddyEtAl2019` and `BakryGentilLedoux2014` additions, for **38 verified works**. The corrections documented here have now been applied to `references.bib`. All 36 original keys were preserved. This report addresses bibliographic identity, metadata, and attribution. Mathematical revisions are documented separately in `../modifications.md`.

Original 36-entry bibliography SHA-256: `b93a53d896e7bfb928afa9b57ba0d9fc75e0b5b7fef760fd9a5a2aa54deb0427`.

Final 38-entry bibliography SHA-256: `6ead7e862fd44b986ea877c9b0ff528d7e2a675416799519ee261737862b27c6`. Subsequent edits may change the file.

## Summary

- All 38 entries correspond to identifiable real works. No wholly fabricated or wholly unverifiable entry was found.
- Added verified entries for `KarimireddyEtAl2019` and `BakryGentilLedoux2014`. Sion (1958) was already present and remains under `sion1958general`; no duplicate was added.
- Applied one definite pagination correction: `ChizatBach2018`.
- Updated author metadata for `BinkowskiSutherlandArbelGretton2018` and `DragutinovicRanganath2026`; the latter now explicitly cites arXiv v2 with its three authors.
- Normalized current JMLR numbering, article-number presentation, and the source-exact name Alexander Smola. Protected proper names in BibTeX titles without changing title wording.
- Every entry now has a verified source URL; 23 entries have verified DOI fields. An absent DOI is not an assertion that no DOI exists.
- The original exact WFR-action attribution to Chizat--Bach was unverified as worded. The manuscript now removes that attribution and directly cited the existing WFR sources; the final context check confirms the concern is addressed.

Verification used original publisher/proceedings records, publisher issue indexes, arXiv records and manuscripts, and the original author-provided blog citation. For inaccessible publisher pages, primary published PDFs archived by public repositories or publisher-provided indexes were used. Secondary bibliographies were not treated as decisive evidence.

## Applied corrections

Bibliography line numbers in this section refer to the original snapshot, before added fields shifted them.

### 1. `ChizatBach2018`: correct the page range

Location: `neurips/references.bib:194`.

Changed `pages = {3040--3050}` to `pages = {3036--3046}`. Authors, title, year 2018, venue and volume 31 are correct.

The [official NeurIPS metadata JSON](https://proceedings.neurips.cc/paper_files/paper/2018/file/a1afc58c6ca9540d057299ec3016d726-Metadata.json) explicitly gives `page_first: 3036` and `page_last: 3046`. The [Curran/publisher table of contents](https://www.proceedings.com/content/048/048413webtoc.pdf), PDF page 18, independently places this paper at 3036 and the next paper at 3047. Although 3040--3050 circulates in citations, it does not match these two primary records. The [current official BibTeX export](https://proceedings.neurips.cc/paper_files/paper/2018/file/a1afc58c6ca9540d057299ec3016d726-Bibtex.bib) leaves pages empty, so omitting the field is also source-consistent.

### 2. `DragutinovicRanganath2026`: align authors with the arXiv version

Location: `neurips/references.bib:306`.

Applied the current v2 author list and pinned the cited version:

```bibtex
author = {Sara Dragutinovi{\'c} and Yedi Zhang and Rajesh Ranganath},
eprint = {2603.00742v2},
note = {arXiv:2603.00742v2},
url = {https://arxiv.org/abs/2603.00742v2},
```

The [current arXiv record, v2](https://arxiv.org/abs/2603.00742v2), revised 29 June 2026, lists these three authors in that order. The title, year, identifier and primary class in the bibliography are correct.

Important qualification: the original two-author list is authentic for [v1](https://arxiv.org/abs/2603.00742v1), submitted 28 February 2026. This was version drift, not a hallucinated author list. The existing key was preserved despite the additional author. The added arXiv-issued DOI identifies the preprint across versions; the URL, eprint and note select v2. This key remains uncited in the manuscript snapshot inspected.

### 3. `BinkowskiSutherlandArbelGretton2018`: use the updated author name

Location: `neurips/references.bib:345`.

Applied this author list, matching the current primary record:

```bibtex
author = {Miko{\l}aj Bi{\'n}kowski and Danica J. Sutherland and Michael Arbel and Arthur Gretton},
```

The [arXiv record](https://arxiv.org/abs/1801.01401) lists Danica J. Sutherland and explicitly identifies the work as published at ICLR 2018. The [conference PDF indexed by OpenReview](https://openreview.net/pdf/5308a4739abf6c4d149c09c21a4c52e29538f914.pdf) also carries that name. Keep the title, ICLR venue and 2018 publication year; the arXiv metadata revision in 2021 does not change the conference year. This is an author-name update, not evidence of a fictitious work or different coauthor.

### 4. `CuturiAvis2014`: normalize the JMLR citation number

Location: `neurips/references.bib:96`.

The [official JMLR record](https://jmlr.org/papers/v15/cuturi14a.html) gives **15(17):533--564, 2014**, whereas the bibliography had `number = {1}`. Applied `number = {17}` to follow current JMLR metadata. The title, both authors, volume, pages and year match. This is a journal citation-number normalization, not a fabricated work: annual-volume/issue-1 conventions also circulate for JMLR.

## Requested addition: `KarimireddyEtAl2019`

The [official PMLR proceedings record](https://proceedings.mlr.press/v97/karimireddy19a.html) verifies the title, four authors in order, ICML 2019, volume 97 and pages 3252--3261. Added entry:

```bibtex
@inproceedings{KarimireddyEtAl2019,
  author    = {Sai Praneeth Karimireddy and Quentin Rebjock and Sebastian U. Stich and Martin Jaggi},
  title     = {Error Feedback Fixes {SignSGD} and other Gradient Compression Schemes},
  booktitle = {Proceedings of the 36th International Conference on Machine Learning},
  series    = {Proceedings of Machine Learning Research},
  volume    = {97},
  pages     = {3252--3261},
  year      = {2019},
  publisher = {PMLR},
  url       = {https://proceedings.mlr.press/v97/karimireddy19a.html}
}
```

The [published paper's first page](https://proceedings.mlr.press/v97/karimireddy19a/karimireddy19a.pdf) includes the middle initial in **Sebastian U. Stich**; the landing-page BibTeX abbreviates this to Sebastian Stich. Both identify the same author; the corrected entry follows the paper itself.

**Attribution check:** Section 3, Counterexamples 1--3 and Theorem I, supplies signSGD nonconvergence examples, including failure despite unbiased stochastic gradients. This supports the revised manuscript's limited claim that nonlinear sign normalization can obstruct convergence. It does not establish failure for every stochastic Muon variant. The wording inspected near `paper.tex:2101` makes that limitation explicit and is consistent with the source. The distinction between dual convex dissipation and a fixed metric is established in the manuscript itself.

**Sion already covered:** `sion1958general` is present at `references.bib:41` and cited near `paper.tex:1582`. Its [original publisher PDF](https://msp.org/pjm/1958/8-1/pjm-v8-n1-p14-p.pdf) verifies Maurice Sion, *On General Minimax Theorems*, Pacific Journal of Mathematics 8(1):171--176 (1958). Reuse that key; do not add a duplicate `Sion1958` entry.

## Requested addition: `BakryGentilLedoux2014`

The [official Springer book record](https://link.springer.com/book/10.1007/978-3-319-00227-9) verifies all three authors, title, series volume 348, first edition, Springer Cham, and copyright/publication year 2014. The November 2013 release dates shown for the hardcover and eBook do not require replacing the standard 2014 citation year. Added entry:

```bibtex
@book{BakryGentilLedoux2014,
  author    = {Dominique Bakry and Ivan Gentil and Michel Ledoux},
  title     = {Analysis and Geometry of {Markov} Diffusion Operators},
  series    = {Grundlehren der mathematischen Wissenschaften},
  volume    = {348},
  publisher = {Springer},
  address   = {Cham},
  year      = {2014},
  doi       = {10.1007/978-3-319-00227-9},
  isbn      = {978-3-319-00226-2},
  url       = {https://link.springer.com/book/10.1007/978-3-319-00227-9}
}
```

**Attribution check and useful pinpoints:** [Chapter 4, Poincare Inequalities, pp. 177--233](https://link.springer.com/chapter/10.1007/978-3-319-00227-9_4), covers spectral gaps, exponential convergence and curvature-based inequalities. [Chapter 5, Logarithmic Sobolev Inequalities, pp. 235--275](https://link.springer.com/chapter/10.1007/978-3-319-00227-9_5), covers entropy decay and curvature criteria. These are appropriate classical references for the KL/log-Sobolev and Poincare background near `paper.tex:4335` onward. Cite the book with chapter pinpoints where useful; separate bibliography entries for those chapters are unnecessary. This verifies the classical attribution, not the manuscript's new spectral-geometry extensions or every normalization constant. Only the publisher's book/chapter records and abstracts were needed for this scope; full chapter access is subscription-restricted.

## Presentation and minor normalization

Applied the following presentation improvements: replaced `pages = {7}` and `pages = {203}` with explicit article-number notes; removed Smola's extra middle initial; added JMLR number 25. The rationale distinguishes these improvements from false metadata.

- `BurgerErbarHoffmannMatthesSchlichting2023`: **7 is an article number**, not a one-page extent. The [publisher record](https://link.springer.com/article/10.1007/s00205-024-02065-w) and [issue contents](https://link.springer.com/journal/205/volumes-and-issues/249-1) verify volume 249, issue 1, article 7, **2025**. With the manuscript's `plainnat` style, an explicit `note = {Article 7}` in place of `pages = {7}` is clearer. An `eid` field is appropriate only if the chosen bibliography style actually renders it. Do not change the year to 2023 or 2024: 2023 is the preprint year and 3 December 2024 is online publication, while the issue year is 2025. The key's suffix need not match the publication year.
- `BackhoffBeiglbockPammer2019`: **203 is an article number**, not a page. The [publisher record](https://link.springer.com/article/10.1007/s00526-019-1624-y) and [issue contents](https://link.springer.com/journal/526/volumes-and-issues/58-6) verify 58(6), article 203 (2019). Use an explicit article-number note if improving `plainnat` presentation. The underlying locator is correct.
- `GrettonBorgwardtRaschSchoelkopfSmola2012`: the [JMLR record](https://jmlr.org/papers/v13/gretton12a.html) and [published first page](https://jmlr.org/papers/volume13/gretton12a/gretton12a.pdf) use **Alexander Smola**, without the extra middle initial in the bibliography. Removing `J.` gives source-exact authorship; this is a minor name-form difference, not a different-person attribution. The current JMLR citation number **25** may also be added, yielding 13(25):723--773. Omitting that number is not an error.
- Missing DOI/URL fields are generally completeness issues, not hallucinations. Verified source URLs for every key are supplied below. Preserve useful capitalization in BibTeX titles where `plainnat` would lowercase proper names, but ordinary title-case differences are not metadata falsifications.

## Context checks

These checks are confined to citation attribution. Line numbers describe the manuscript snapshot read during the audit and may shift in later revisions.

1. **Muon blog authorship is correct.** The seven names in `KellerJordan2024` exactly match the original post's own [Citation block](https://kellerjordan.github.io/posts/muon/#citation). Do not reduce the author list to Keller Jordan merely because the post is on his blog. Its date is 8 December 2024. The references at `paper.tex:97` and `paper.tex:1870` to practical Muon and Newton--Schulz are consistent with the source.
2. **Muon scaling authorship is correct.** All 28 authors, in order, match [arXiv:2502.16982](https://arxiv.org/abs/2502.16982). Its abstract supports the paper's broad large-scale-training attribution. No publication venue should be invented for this `@misc` entry.
3. **Paty--Cuturi is the relevant antecedent.** The [official abstract](https://proceedings.mlr.press/v97/paty19a.html) explicitly describes minimizing the sum of the largest displacement-moment eigenvalues, which supports the citation at `paper.tex:102` concerning the Ky Fan special case. This checks the identity and attribution, not every theorem in the manuscript.
4. **The transport references are real but describe distinct constructions.** [Burger et al.](https://link.springer.com/article/10.1007/s00205-024-02065-w) modulate dynamic transport by the current distribution's covariance; [Chen et al.](https://arxiv.org/abs/1610.03041) transport matrix-valued densities; [Backhoff et al.](https://link.springer.com/article/10.1007/s00526-019-1624-y) consider costs on conditional probability laws. The manuscript's `paper.tex:100` describes these as related work, not identical models, which is a defensible attribution.
5. **The 2024 Sebbouh publication is correct despite the 2023 key.** [PMLR](https://proceedings.mlr.press/v238/sebbouh24a.html) confirms AISTATS 2024, volume 238, pages 586--594. Its abstract explicitly links cost-regularized minimization to Gromov--Wasserstein structure, supporting the direction of the comparison at `paper.tex:104`.
6. **Chizat--Bach's exact WFR-action attribution needs qualification.** At `paper.tex:4693`, the manuscript says the displayed action is exactly the classical WFR action used by `ChizatBach2018`. The [full primary manuscript](https://arxiv.org/pdf/1805.09545), including the appendix, develops lifted Wasserstein flows, homogeneous projections onto the sphere (Appendix A.2), and radial/tangential dynamics (Appendix C.2, notably Lemma C.3). It does not explicitly formulate that action as a WFR variational metric. The mathematical correspondence may be valid, but I could not verify the stronger historical attribution as worded. `ChizatPeyreSchmitzerVialard2018` and `LieroMielkeSavare2018`, already present and verified, are direct sources for WFR/HK dynamic and static formulations. This is an attribution caveat, not a claim that Chizat--Bach is irrelevant or that the displayed identity is false.
7. **Do not confuse weight normalization with update normalization.** [Morwani--Ramaswamy](https://proceedings.mlr.press/v167/morwani22a.html) studies standard/exponential weight-normalized homogeneous networks; it is not a Muon paper. Its metadata is correct, and it is currently uncited, so no actual misattribution was found.

**Final follow-up on item 6:** At the final context check, `paper.tex:4995` onward no longer attributes the exact action to Chizat--Bach. It explicitly records the reaction normalization `alpha^2/4` and directly cites `ChizatPeyreSchmitzerVialard2018` and `LieroMielkeSavare2018`. The historical-attribution concern is resolved. This does not constitute an independent proof of the manuscript's action identity.

## Identifier provenance

The bibliography now contains 38 URL fields and 23 DOI fields. Publisher DOIs were copied from the linked publisher records or published articles, not generated from citation keys. The only arXiv-issued DOI fields added are for the two entries actually cited as arXiv preprints: [Liu et al.](https://arxiv.org/abs/2502.16982) and [Dragutinovic et al.](https://arxiv.org/abs/2603.00742v2). Conference entries retain their proceedings URLs instead of borrowing the DOI of a preprint version.

Additional DOI provenance where the main table uses another access route:

- `BhatiaJainLim2019`: [Elsevier's indexed record](https://www.sciencedirect.com/science/article/pii/S0723086918300021) gives `10.1016/j.exmath.2018.01.002`.
- `fan1951maximum` and `MeiMontanariNguyen2018`: the NAS-provided published articles in PMC explicitly give `10.1073/pnas.37.11.760` and `10.1073/pnas.1806579115`, respectively.
- `NingGeorgiouTannenbaum2015`: the [NIH record](https://pubmed.ncbi.nlm.nih.gov/26997667/) gives `10.1109/TAC.2014.2350171`; the publication coordinates were independently checked in IEEE's own index.
- `ChenGeorgiouTannenbaum2018`: the [published IEEE PDF](https://par.nsf.gov/servlets/purl/10114182), first page, explicitly gives `10.1109/TAC.2017.2767707`.
- `BackhoffPammer2022`: search-indexed text of the [original IMS issue PDF](https://www.imstat.org/publications/bej/bej_28_1/bej_28_1.pdf) gives `10.3150/21-BEJ1346`.
- `MurraySwensonKar2019`: the [authors' university publication record](https://pure.psu.edu/en/publications/revisiting-normalized-gradient-descent-fast-evasion-of-saddle-poi/) gives `10.1109/TAC.2019.2914998`; IEEE's own index and issue digest independently verify the article and pagination. The live IEEE article page was challenge-blocked.
- `SejdinovicSriperumbudurGrettonFukumizu2013`: the [author-submitted arXiv record](https://arxiv.org/abs/1207.6076) explicitly lists the published-paper DOI `10.1214/13-AOS1140`.

`sion1958general` has a verified primary-publisher PDF URL but no DOI field was added: secondary records list a DOI, while the publisher XHTML record and DOI redirect could not be read to the required primary-source standard. This is a narrowly unresolved identifier check, not an unverifiable entry. No DOI was guessed for Takatsu, JMLR, PMLR, NeurIPS, ICLR, or the blog.

## Compact per-key verified-source table

"OK" means the title, author identities/order and publication coordinates agree with the primary source, allowing ordinary capitalization, expanded first names and equivalent venue names. The table records both initially correct entries and the corrections applied. Every key in the final file appears exactly once across the original-entry and added-entry tables.

| Key | Result / verified publication coordinates | Primary verified source |
| --- | --- | --- |
| `Gelbrich1990` | OK; Math. Nachr. 147(1):185--203 (1990) | [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1002/mana.19901470121) |
| `Takatsu2011` | OK; Osaka J. Math. 48(4):1005--1026 (2011) | [Publishing university, version of record](https://ir.library.osaka-u.ac.jp/repo/ouka/all/4973/) |
| `BhatiaJainLim2019` | OK; Expositiones Math. 37(2):165--191 (2019) | [Elsevier](https://www.sciencedirect.com/science/article/pii/S0723086918300021) |
| `fan1951maximum` | OK; PNAS 37(11):760--766 (1951) | [NAS-provided published article in PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC1063464/) |
| `sion1958general` | Work/metadata OK; Pacific J. Math. 8(1):171--176 (1958); DOI withheld pending primary verification | [Publisher PDF](https://msp.org/pjm/1958/8-1/pjm-v8-n1-p14-p.pdf) |
| `BurgerErbarHoffmannMatthesSchlichting2023` | Article-number display normalized; ARMA 249(1), article 7 (2025) | [Springer](https://link.springer.com/article/10.1007/s00205-024-02065-w) |
| `NingGeorgiouTannenbaum2015` | OK; IEEE TAC 60(2):373--382 (2015) | [IEEE publisher author index, PDF p. 8](https://ieeecss.org/sites/ieeecss/files/2019-10/Index_2015.pdf), [NIH bibliographic record](https://pubmed.ncbi.nlm.nih.gov/26997667/) |
| `PatyCuturi2019` | OK; ICML, PMLR 97:5072--5081 (2019) | [PMLR](https://proceedings.mlr.press/v97/paty19a.html) |
| `FlamaryCuturiCourtyRakotomamonjy2018` | OK; Machine Learning 107(12):1923--1945 (2018) | [Springer](https://link.springer.com/article/10.1007/s10994-018-5717-1) |
| `CuturiAvis2014` | JMLR number corrected to 17; 15(17):533--564 (2014) | [JMLR](https://jmlr.org/papers/v15/cuturi14a.html) |
| `CarlierJimenezSantambrogio2008` | OK; SIAM J. Control Optim. 47(3):1330--1350 (2008) | [SIAM](https://epubs.siam.org/doi/10.1137/060672832) |
| `ChenGeorgiouTannenbaum2018` | OK; IEEE TAC 63(8):2612--2619 (2018) | [Published IEEE PDF archived by NSF](https://par.nsf.gov/servlets/purl/10114182), [arXiv](https://arxiv.org/abs/1610.03041) |
| `Villani2009` | OK; Springer, Grundlehren vol. 338 (2009 copyright year) | [Springer book record](https://link.springer.com/book/10.1007/978-3-540-71050-9) |
| `Brenier1991` | OK; CPAM 44(4):375--417 (1991) | [Wiley](https://onlinelibrary.wiley.com/doi/10.1002/cpa.3160440402) |
| `BenamouBrenier2000` | OK; Numer. Math. 84(3):375--393 (2000) | [Springer](https://link.springer.com/article/10.1007/s002110050002) |
| `GozlanRobertoSamsonTetali2017` | OK; JFA 273(11):3327--3405 (2017) | [Elsevier](https://www.sciencedirect.com/science/article/am/pii/S0022123617303294), [arXiv authors](https://arxiv.org/abs/1412.7480) |
| `BackhoffBeiglbockPammer2019` | Article-number display normalized; Calc. Var. PDE 58(6), article 203 (2019) | [Springer](https://link.springer.com/article/10.1007/s00526-019-1624-y) |
| `BackhoffPammer2022` | OK; Bernoulli 28(1):370--394 (2022) | [IMS issue PDF, indexed primary text](https://www.imstat.org/publications/bej/bej_28_1/bej_28_1.pdf), [arXiv authors/title](https://arxiv.org/abs/2003.05338) |
| `AmbrosioGigliSavare2008` | OK; Birkhauser Basel, 2nd ed., Lectures in Mathematics ETH Zurich (2008) | [Springer/Birkhauser book record](https://link.springer.com/book/10.1007/978-3-7643-8722-8) |
| `ChizatBach2018` | Pages corrected to 3036--3046; NeurIPS vol. 31 (2018) | [NeurIPS metadata](https://proceedings.neurips.cc/paper_files/paper/2018/file/a1afc58c6ca9540d057299ec3016d726-Metadata.json), [publisher TOC](https://www.proceedings.com/content/048/048413webtoc.pdf) |
| `ChizatPeyreSchmitzerVialard2018` | OK; JFA 274(11):3090--3123 (2018) | [Elsevier](https://www.sciencedirect.com/science/article/pii/S0022123618301058) |
| `LieroMielkeSavare2018` | OK; Invent. Math. 211(3):969--1117 (2018) | [Springer](https://link.springer.com/article/10.1007/s00222-017-0759-8) |
| `PethickXieAntonakopoulosEtAl2025` | OK, all six authors; ICML, PMLR 267:49069--49104 (2025) | [PMLR](https://proceedings.mlr.press/v267/pethick25a.html) |
| `GuptaKorenSinger2018` | OK; ICML, PMLR 80:1842--1850 (2018) | [PMLR](https://proceedings.mlr.press/v80/gupta18a.html) |
| `CutkoskyMehta2020` | OK; ICML, PMLR 119:2260--2268 (2020) | [PMLR](https://proceedings.mlr.press/v119/cutkosky20b.html) |
| `MorwaniRamaswamy2022` | OK; ALT, PMLR 167:827--880 (2022) | [PMLR](https://proceedings.mlr.press/v167/morwani22a.html) |
| `MurraySwensonKar2019` | OK; IEEE TAC 64(11):4818--4824 (2019) | [IEEE publisher author index, PDF p. 11](https://ieeecss.org/sites/ieeecss/files/2020-08/Index_2019.pdf), [arXiv](https://arxiv.org/abs/1711.05224) |
| `SebbouhCuturiPeyre2023` | OK; AISTATS, PMLR 238:586--594 (2024), despite key suffix | [PMLR](https://proceedings.mlr.press/v238/sebbouh24a.html) |
| `MeiMontanariNguyen2018` | OK; PNAS 115(33):E7665--E7671 (2018) | [Published article in PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6099898/) |
| `LiuSuYaoEtAl2025` | OK, all 28 authors; arXiv:2502.16982, cs.LG (2025) | [arXiv](https://arxiv.org/abs/2502.16982) |
| `KellerJordan2024` | OK, all seven authors; original blog post, 8 Dec 2024 | [Original post and citation block](https://kellerjordan.github.io/posts/muon/) |
| `DragutinovicRanganath2026` | Added Yedi Zhang; three-author v2 explicitly pinned (2026); old two-author list authentic for v1 | [arXiv v1](https://arxiv.org/abs/2603.00742v1), [arXiv v2](https://arxiv.org/abs/2603.00742v2) |
| `GrettonBorgwardtRaschSchoelkopfSmola2012` | Source-exact Alexander Smola; JMLR number added; 13(25):723--773 (2012) | [JMLR](https://jmlr.org/papers/v13/gretton12a.html) |
| `SejdinovicSriperumbudurGrettonFukumizu2013` | OK; Ann. Statist. 41(5):2263--2291 (2013) | [arXiv with publisher journal reference and DOI](https://arxiv.org/abs/1207.6076) |
| `LiSwerskyZemel2015` | OK; ICML, PMLR 37:1718--1727 (2015) | [PMLR](https://proceedings.mlr.press/v37/li15.html) |
| `BinkowskiSutherlandArbelGretton2018` | Updated Sutherland's given name to Danica J.; ICLR 2018 | [arXiv, with ICLR publication statement](https://arxiv.org/abs/1801.01401) |

Additional works requested after the original 36-entry audit:

| Added key | Result / verified publication coordinates | Primary verified source |
| --- | --- | --- |
| `KarimireddyEtAl2019` | Added; ICML, PMLR 97:3252--3261 (2019), four authors | [PMLR](https://proceedings.mlr.press/v97/karimireddy19a.html), [published PDF](https://proceedings.mlr.press/v97/karimireddy19a/karimireddy19a.pdf) |
| `BakryGentilLedoux2014` | Added; Springer Cham, Grundlehren vol. 348 (2014), three authors | [Springer book](https://link.springer.com/book/10.1007/978-3-319-00227-9), [Poincare chapter](https://link.springer.com/chapter/10.1007/978-3-319-00227-9_4), [log-Sobolev chapter](https://link.springer.com/chapter/10.1007/978-3-319-00227-9_5) |

## Unverifiable items and access limits

**Wholly unverifiable bibliography entries: none.** No unresolved work-identity, title, venue or year mismatch remains after the corrections and version qualifications above.

Some live landing pages were not readable: IEEE Xplore and OpenReview returned browser challenges; Project Euclid returned an iframe shell; several DOI redirects failed. These failures are not evidence of hallucination. IEEE's own indexes, published PDFs in public archives, arXiv and publisher-indexed text supplied the necessary evidence. In particular, Bernoulli's 2022 coordinates were checked against search-indexed text of the original IMS issue PDF; a fresh direct fetch of that PDF failed. The report does not claim fresh full-text access to every paywalled article.

The original exact WFR-action attribution discussed above was not verified as worded; the final manuscript removes it. Both requested additional references are verified, bringing the total number of checked works to 38. The only specifically identified optional identifier left unverified to the primary-source standard is Sion's DOI, which was not inserted. Subscription restrictions prevented full-chapter inspection of Bakry--Gentil--Ledoux; its metadata and the relevance of Chapters 4--5 are verified from Springer records and abstracts. This report does not certify all constants or new mathematical claims in the manuscript.

## Final validation

- All 36 original citation keys preserved; exactly two requested keys added, for 38 entries.
- Exactly 38 source URLs and 23 DOI fields.
- BibTeX processed all entries using the manuscript's `plainnat` style in an isolated temporary directory: exit code 0, no warnings. No manuscript build or generated manuscript files were touched.
- A final scan of citation commands in `neurips/*.tex` found 33 cited keys and no missing bibliography key.
- Five entries were uncited in that final snapshot but fully audited: `Gelbrich1990`, `Takatsu2011`, `Brenier1991`, `MorwaniRamaswamy2022`, and `DragutinovicRanganath2026`. Uncited status is not a bibliography defect and can change in later manuscript versions.
- The audit table covers all 38 keys exactly once.

The applied bibliography corrections are in `references.bib`; the complete manuscript revision log is in `../modifications.md`.

# Consistency of the companion application, code, and results

Updated on 22 September 2026 after transferring the collective-threshold application into the [README](README.md#collective-threshold-correlations).

## Current location and source

The numerical application, its decay theorem and proof, and the truncation bounds now live in the README. They were transferred from Section 6 of the supplied `v2FWCII_arxiv-FINAL.pdf`, *Fractional Wiener chaos: Part 2. Interface Spectral Chaos*, by Elena Boguslavskaya and Elina Shishkina. The actual source filename uses underscores and a hyphen as shown here. The source has 32 pages: Section 6 starts on page 25 and ends on page 29, which contains the figure and the start of the conclusion.

The forthcoming arXiv manuscript is being revised separately to omit this application and amend its abstract, introduction, and conclusion. References in this repository therefore point to the README application, not to a Section 6 in that revised manuscript. No revised manuscript PDF was prepared or substituted by this GitHub update.

Source PDF SHA-256: `1f609535af9a4091693ff4abb1eab8494161053b8275c3b6f00dc5e05264c761`.

The matching local LaTeX source was used to preserve the mathematics accurately, and the rendered PDF pages were checked against it. The transfer preserves all four subsections, the theorem and complete proof, the formula for the product Caputo equation, both covariance sums, the large-time limits, and both truncation estimates. The background definitions have been repeated, references have been converted to stable links, and the Gaussian benchmark and diagnostics cited as S.1/S.2 are included in the README.

## Reference mapping

The equation numbers in this table refer **only to the 22 September source snapshot before Section 6 was removed**. They are provenance information, not references to the numbering of the forthcoming arXiv revision.

| Source location or label | Current location |
| --- | --- |
| Section 6, pages 25-29 | [Computing the decay of collective threshold correlations](README.md#collective-threshold-correlations) |
| Section 6.1 | [The observation and its spectral coefficients](README.md#observation) |
| Section 6.2 | [Evolution in the product chaos](README.md#product-chaos-evolution) |
| Section 6.3 | [Truncating the collective expansion](README.md#truncating-expansion) |
| Section 6.4 | [Numerical evaluation](README.md#numerical-evaluation) |
| Main construction: equations (19), (25), (26) and the product-basis theorem | [Ground state (B1)](README.md#ground-state), [product basis (B2)](README.md#product-basis), and [spectral background](README.md#spectral-background) |
| Threshold coefficient identity (31) | [Boundary-flux identity (B3)](README.md#threshold-coefficients) |
| Covariance definitions (33) | [Covariances (C1)](README.md#covariances) |
| Product-evolution display (unnumbered) | [Product evolutions (C2)](README.md#product-evolutions) |
| Product Caputo equation (34) | [Product Caputo equation (C3)](README.md#product-caputo) |
| Covariance series (35) | [Covariance series (C4)](README.md#covariance-series) |
| Theorem 6.1 and long-time limits (36) | [Decay theorem](README.md#decay-theorem) and [long-time limits (C5)](README.md#long-time-limits) |
| Mittag-Leffler asymptotics (37) | [Mittag-Leffler asymptotics (C6)](README.md#mittag-leffler-asymptotics) |
| Truncation bounds (38) | [Truncation bounds (C7)](README.md#truncation-bounds) |
| Figure 1 | [Figure C1](README.md#collective-figure), with tracked PNG and vector PDF in `reference/` |
| Repository citations to Section S.1 | [Gaussian coefficients and independent benchmark](README.md#gaussian-benchmark) |
| Repository citations to Section S.2 | [Numerical procedure, truncation table, and diagnostics](README.md#numerical-diagnostics) |
| Source references to Beghin et al., Bingham et al., Meerschaert and Straka, and SciPy | [README bibliography](README.md#references) |

The main manuscript remains the source for the interface operator, its domains, and the product spectral construction. The README names those constructions and repeats the definitions needed for the companion; it does not claim to reproduce all proofs from Sections 2-5.

## Input and output consistency

**No numerical inconsistency was found in the checked application.** Its printed inputs and four rounded error/bound values agree with the stored reference and the numerical reproduction. The parameter and formula conventions are:

| Quantity | Implementation and reference | Finding |
| --- | --- | --- |
| Two-coordinate, half-stable numerical example | `parameters.m = 2`, `parameters.tau = 0.5` | Matches the transferred numerical evaluation |
| Gaussian and deformed figure panels | First two spectra: `mu = 1` and `mu = 1/2` | Matches Figure C1 |
| Retained modes | 32 positive-mode weights; 34 raw eigenvalues include the ground state and first omitted mode | Matches the supplied reference calculation |
| Extra nodal diagnostic | `mu = 3/7`, `alpha = 3`, `beta = 1` | Diagnostic only; not a third figure panel |
| Coefficient identity | `w1(0) = 1/sqrt(2*pi)`, gaps `lambda_k = alpha_k - alpha_0` | Matches (B3) |
| Clock argument | `erfcx(lambda*sqrt(t)/2)`; sum of gaps for the shared clock | Matches (C2) and (C4) |
| Centering | Positive-mode coefficients unchanged by subtracting `p_mu`; ground-mode coefficient absent from covariance sums | Matches the observation definition |
| Correlation normalization | Divide both covariances and their bands by `[p_mu*(1-p_mu)]^2` | Matches Figure C1 |
| Long-time scaling | `sqrt(t)*C_shared`, `t*C_independent`; amplitude factor `2/sqrt(pi)` | Matches (C5) for `m = 2`, `tau = 1/2` |
| Omitted mode and mass | `gaps[N]` gives the first omitted gap; coefficient residual is `p_mu*(1-p_mu) - sum(weights)` | Matches (C7) |

The supplied experiment uses cutoff 24, a cutoff-18 comparison at `mu = 1/2`, a 12,001-point root scan for deformed parameters, and large-time diagnostics through `t = 1,000,000`. These are implementation and supplementary details; they are now documented directly in [S.2](README.md#numerical-diagnostics).

### Four printed numerical values

At `mu = 1`, `t = 1`, and `N = 32`, the values preserved from the source's numerical evaluation are **unnormalized covariance** errors and bounds:

| Quantity | README/source value | Stored reference | Reproduction checked on 12 September | Finding |
| --- | --- | --- | --- | --- |
| Shared-clock error | `1.17e-4` | `1.16518845363619e-4` | `1.16518845363617e-4` | Same at displayed precision |
| Independent-clock error | `5.94e-5` | `5.93548887269611e-5` | `5.93548887269472e-5` | Same at displayed precision |
| Shared-clock bound | `3.56e-4` | `3.56009263264683e-4` | `3.56009263264683e-4` | Same at displayed precision |
| Independent-clock bound | `2.36e-4` | `2.36452142849036e-4` | `2.36452142849036e-4` | Same at displayed precision |

Both errors are positive and less than their bounds. The complete truncation table decreases with `N = 4, 8, 16, 32` and is now included in [S.2](README.md#truncation-table). Moving the application changes the documentation location, not the numerical model or stored reference values.

### Covariances versus correlations

At `mu = 1`, `p_mu = 1/2`, so the figure's normalization multiplies a covariance by 16. The finite 32-mode curves and the independent Gaussian quadrature markers are intentionally different:

| Quantity at t = 1 | Shared clock | Independent clocks |
| --- | --- | --- |
| Gaussian quadrature covariance | `0.0150734676645318` | `0.0125986424003652` |
| 32-mode covariance | `0.0149569488191681` | `0.0125392875116382` |
| Normalized quadrature marker | `0.241175482633` | `0.201578278406` |
| Normalized 32-mode curve | `0.239311181107` | `0.200628600186` |

For `mu = 1/2`, the normalization divisor is approximately `0.0446862244726752`, giving `t = 1` curve values approximately `0.174136402231` and `0.130458951540`. The transferred figure was visually compared with the source PDF. Its vector plot was not independently digitized into a separate numerical data series.

## Reference comparison and repeatability

The original 12 September audit compared all 499 numeric fields outside version metadata, with relative tolerance `1e-8` and absolute tolerance `1e-11`. All passed; the largest absolute difference was about `9.84e-13`, in `spectral[1].coefficients[20]`. Structure and the three nonnumeric leaf values outside version metadata matched exactly. Both runs recorded zero quadrature warnings.

The reference used Python 3.12.13; the audit used Python 3.12.14 with the same NumPy 2.3.5, SciPy 1.17.0, and Matplotlib 3.10.8. No printed application value is affected by those small numerical differences. At `t = 1,000,000`, scaled shared and independent covariances approach their finite-sum amplitudes to within about `4.02e-7` and `3.71e-6` relatively, respectively. These finite-time differences are consistent with (C5).

The eleven-test suite was rerun for the 22 September documentation migration. `test_documented_numerical_evaluation` checks the parameters and four rounded values now stated in the README; `test_full_reference_consistency` compares the complete reference and newly calculated JSON. No PDF parser is required to run these tests.

```sh
python reproduce.py
python -m unittest -v test_reproduce
```

The bounds account for spectral truncation using floating-point inputs, not root completeness or all special-function and quadrature uncertainty. This audit does not independently certify the analytical theorems.

## Historical manuscript archive

The previously published [12 September PDF](archive/fractional_wiener_chaos_II_2026-09-12.pdf) is retained only for provenance. Its title was *Fractional Wiener chaos: Part 2. Interface spectral chaos and decay of collective correlations*; it has 23 pages, with Section 6 on pages 17-20 and Figure 1 on page 21. It is **not the revised arXiv manuscript**. Its SHA-256 is `4b8768a25ce65acc92dae04fe9b577c1151bbe7ef576cfac1c3d564b7a2ef9aa`.

In that historical version, the covariance series, long-time limits, and truncation bounds were numbered (21), (22), and (24). Current readers should use README labels (C4), (C5), and (C7) instead. If a future manuscript version changes its inputs or results, review this correspondence explicitly rather than reusing obsolete section or page numbers.

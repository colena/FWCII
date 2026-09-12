# Collective threshold relaxation

Reproduce the numerical comparison of collective threshold covariances under a shared inverse half-stable clock and independent clocks. This standalone research code computes interface spectra, covariance sums, truncation estimates, Gaussian benchmarks, long-time amplitudes, and a two-panel figure.

The calculation uses two coordinates (`m = 2`), clock order `tau = 1/2`, deformation parameters `mu = 1, 1/2, 3/7`, and 32 retained positive modes per coordinate. The numerical methods use floating-point arithmetic; they are not interval-certified calculations.

## Associated paper and reference

This code accompanies the paper by **Elena Boguslavskaya and Elina Shishkina**:

> *Fractional Wiener chaos: Part 2. Interface spectral chaos and decay of collective correlations.* Manuscript supplied with this repository; PDF snapshot compiled on 12 September 2026. [Read the paper](fractional_wiener_chaos_II_FINAL.pdf).

The paper constructs an interface spectral basis and uses it to compare how a centred product of threshold observations retains correlation with its initial value under shared and independent inverse stable clocks. This repository implements that numerical example: **Section 6, especially Section 6.4 (page 20), and Figure 1 (page 21)**. 

The boundary-flux coefficients implement equation (18); the shared and independent covariance sums implement equation (21); `amplitudes()` implements the `m = 2`, `tau = 1/2` case of equation (22); and the truncation estimates implement equation (24). The figure uses `mu = 1` and `mu = 1/2`. The additional `mu = 3/7` calculation checks a nodal interface mode and is not a third plotted case. The code reproduces this numerical application, rather than every analytical construction or parameter range studied in the paper.

When referring to these numerical results, cite the paper using the authors and title above and identify the version of this repository used. 

**Paper/results consistency:** the input parameters, covariance normalization, decay powers, and all four printed error/bound values in Section 6.4 agree with `reference/results.json` and a fresh run. The paper rounds these four numbers to three significant figures. The figure displays normalized correlations, while the benchmark errors and bounds are unnormalized covariances. See [PAPER_CONSISTENCY.md](PAPER_CONSISTENCY.md) for the comparison and its scope.

## Quick start

Download or clone this repository, then open a terminal in its root directory. Use **Python 3.12** for the tested environment.

On macOS or Linux:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python reproduce.py
```

On Windows, using PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe reproduce.py
```

The script prints a summary and creates `outputs/` inside the repository. Open `outputs/figures/collective_clocks.png` to view the figure, or `outputs/numerical_report.md` for the numerical report.

Only Python, NumPy, SciPy, and Matplotlib are required. No manuscript files, LaTeX installation, external dataset, account, or network connection is needed after installing dependencies. Matplotlib uses the headless `Agg` backend, so a graphical desktop is not required.

## Outputs

Every run overwrites these generated files, all relative to the repository root:

| File | Contents |
| --- | --- |
| `outputs/results.json` | Parameters, versions, spectra, coefficients, diagnostics, benchmarks, amplitudes, and figure metadata |
| `outputs/results.txt` | Concise numerical summary |
| `outputs/numerical_report.md` | Standalone report with benchmark and diagnostic tables and a linked figure |
| `outputs/figures/collective_clocks.pdf` | Vector figure |
| `outputs/figures/collective_clocks.png` | Raster figure |

Output paths are resolved relative to `reproduce.py`, so the script can also be launched from another working directory using its full path. The repository must be writable. Generated outputs are ignored by Git; the original numerical reference in `reference/results.json` is kept separately and is never overwritten by the script.

## Tests

With the virtual environment activated, run:

```sh
python -m unittest -v test_reproduce
```

On Windows without activation:

```powershell
.venv\Scripts\python.exe -m unittest -v test_reproduce
```

The suite runs the complete reproduction in a temporary directory, from a different working directory, and checks:

- Generation of the report, numerical files, and both figure formats inside the standalone folder.
- Gaussian probabilities, spectra, coefficient formulas, and covariance reference values.
- Decreasing truncation errors for `N = 4, 8, 16, 32`, within the estimated remainder bounds.
- Ordered spectra, positive gaps, coefficient mass, interface matching, Gram matrices, and direct coefficient quadrature.
- Cutoff sensitivity and the nodal case `mu = 3/7`.
- Long-time amplitudes and scaled covariance convergence through `t = 1,000,000`.
- Small Gaussian spectra for `N = 1` through `8`, and deformed spectra for `N = 1, 4, 6, 7, 8`.
- Agreement with the input parameters and four rounded numerical values in the paper's Section 6.4, and a recursive comparison of fresh results with the full stored reference.

Tests preserve both `reference/` and any existing `outputs/`. Temporary outputs are deleted after testing. The numerical tolerances are regression checks rather than certified error bounds.

Validated on 12 September 2026 with Python 3.12.14 on macOS (Apple silicon) and the pinned dependencies: all eleven tests passed, including the paper consistency checks and full numerical reproduction, with zero recorded quadrature warnings. Windows and Linux instructions are provided but were not tested in this environment.

## Expected numerical results

For the Gaussian case (`mu = 1`) at `t = 1`:

| Quantity | Shared clock | Independent clocks |
| --- | --- | --- |
| Independent quadrature benchmark | 0.0150734676645 | 0.0125986424004 |
| Absolute error with 32 modes | 1.16519e-4 | 5.93549e-5 |
| Estimated truncation bound | 3.56009e-4 | 2.36452e-4 |

The expected threshold probabilities are approximately `0.5`, `0.696491311248`, and `0.734484032950` for `mu = 1, 1/2, 3/7`, respectively. Successful reference runs record zero quadrature warnings. Small changes in the last digits of numerical diagnostics can occur across platforms.

`reference/results.json` contains the original numerical reference produced with Python 3.12.13, NumPy 2.3.5, SciPy 1.17.0, and Matplotlib 3.10.8. `requirements.txt` pins those three direct numerical dependencies; pip resolves their transitive dependencies. Each fresh run records its actual versions in `outputs/results.json`.

## Repository contents

```text
collective-threshold-relaxation/
├── README.md
├── PAPER_CONSISTENCY.md
├── fractional_wiener_chaos_II_FINAL.pdf
├── LICENSE
├── requirements.txt
├── reproduce.py
├── interface_modes.py
├── test_reproduce.py
├── .gitignore
└── reference/
    └── results.json
```

`reproduce.py` implements the spectral data, covariance sums, Gaussian benchmark, asymptotic coefficients, figure, and report. `interface_modes.py` supplies the reciprocal-Gamma characteristic equation, root scan, interface matching, and half-line mode normalisation. `test_reproduce.py` uses Python's standard `unittest` library, so no additional test framework is required.

## Numerical procedure

1. At `mu = 1`, use the exact integer spectrum. For the deformed parameters, scan the characteristic determinant on 12,001 points and refine sign changes with Brent iteration. Include the ground mode, 32 positive modes, and the first omitted mode. The nodal interface case is retained.
2. Evaluate parabolic-cylinder functions by recurrence from nonpositive orders. Normalise modes with half-line quadrature to cutoff 24, and check the first nine-mode Gram matrix, matching residuals, and direct versus boundary-flux threshold coefficients. Repeat at cutoff 18 for `mu = 1/2`.
3. Evaluate the half-stable clock multiplier as `erfcx(lambda * sqrt(t) / 2)`. Use sums of product energies for the shared clock and multiply one-coordinate responses for independent clocks.
4. Compare Gaussian covariances against operational-time integration of the exact arcsine threshold covariance and inverse half-stable density. This benchmark does not use the cylinder functions or root scan.
5. Plot normalised covariances over `1 <= t <= 100000` for `mu = 1` and `mu = 1/2`. Record scaled long-time checks through `t = 1000000` for all three parameters.

Both plotted covariances are divided by `[p_mu * (1 - p_mu)]^2`. Shared-clock covariances decay as `t^(-1/2)`; independent-clock covariances decay as `t^(-1)`. The exact Gaussian independent-clock amplitude is `(log(2))^2 / (4*pi)`.

The shaded bands account for omitted spectral contributions using approximate numerical inputs. They do not enclose errors in roots, special functions, or quadrature. Root completeness is not certified. The code supports numerical reproduction of the research calculation, not a replacement for its analytical proofs.

## Using the functions

Run this example from the repository root in the activated environment:

```python
from reproduce import spectral_data, covariances, amplitudes

N = 4
spectrum = spectral_data(mu=1.0, N=N)
shared, independent, shared_bound, independent_bound = covariances(
    spectrum, t=[1.0, 100.0, 10000.0], N=N
)
long_time = amplitudes(spectrum, N=N)
```

Pass the same `N` to the consuming functions: their defaults are 32. `N` represents a positive integer count of retained modes. The Gram diagnostic checks up to the first nine available modes, including the ground and first omitted modes; it also works when fewer than nine modes are available.

The complete reproduction has fixed parameters in `main()` and no command-line options. Its benchmark, report, and figure are written for the supplied `m = 2`, `tau = 1/2` experiment.

To rebuild only the Markdown report from the original reference, without recomputing spectra or figures:

```sh
python -c 'import json; from pathlib import Path; from reproduce import write_reports; write_reports(json.loads(Path("reference/results.json").read_text()))'
```

This creates `outputs/numerical_report.md`; its figure link becomes available after a full reproduction run.

## Troubleshooting

- **Missing Python package:** use the same virtual-environment interpreter for installation and execution. `python -m pip check` checks installed dependency compatibility.
- **Output permission error:** move the repository to a writable directory, since outputs are stored beside the script under `outputs/`.
- **Unwritable Matplotlib cache:** set `MPLCONFIGDIR` to a writable directory. For example, on macOS/Linux, run `MPLCONFIGDIR=.matplotlib python reproduce.py`.
- **Numerical differences:** compare the benchmark errors with their bounds and run the tests. Exact byte-for-byte agreement of floating-point results or figure files across platforms is not expected.

## License

MIT License. See [LICENSE](LICENSE).

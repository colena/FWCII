# Fractional Wiener Chaos II: numerical reproduction

This directory reproduces the reciprocal-Gamma eigenvalues, stochastic Galerkin benchmark, Table 1 diagnostics, and Figure 1 for the manuscript **Fractional Wiener Chaos II: Fixed-µ Interface Spectral Chaos and Ground-State Fractional Calculus**.

## Method

The code uses the Schrödinger representation

\[
u_k(x)=w_1(x)^{1/2}e_k^{(\mu)}(x).
\]

so Gaussian inner products of the interface eigenfunctions become ordinary Lebesgue integrals. The characteristic roots are found by bracketing zeros of \(\Delta_\mu\). The matching coefficients are obtained from the numerical nullspace of the two-by-two transmission matrix. All half-line integrals use adaptive Gauss-Kronrod quadrature. The default computation uses tolerance `5e-13` and cutoff `24`; the test suite repeats the calculation at different tolerances and cutoffs.

## Reproduce the outputs

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python reproduce.py --output-dir reference
pytest -q
```

For the exact environment used to generate the archived reference output, install
`requirements-lock.txt` instead.  A GitHub Actions workflow runs the tests on
Python 3.11 and 3.13.

Generated files:

- `reference/galerkin_errors.csv`
- `reference/reference_output.json`
- `reference/Fig1.pdf`
- `reference/Fig1.png`

The code was tested with Python 3.13, NumPy 2.3, SciPy 1.17, Matplotlib 3.10, and pytest 9.0.

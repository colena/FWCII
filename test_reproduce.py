"""Run the complete reproduction in isolation and check numerical invariants.

Run with: python -m unittest -v test_reproduce
The repository outputs and reference data are never overwritten.
"""
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np


class SmallSpectrumTests(unittest.TestCase):
    def test_gaussian_small_mode_counts(self):
        from reproduce import spectral_data, gaussian_weights, covariances, gaussian_benchmark
        shared_reference = gaussian_benchmark(1.0, 2)
        independent_reference = gaussian_benchmark(1.0, 1) ** 2
        for N in range(1, 9):
            with self.subTest(N=N):
                data = spectral_data(1.0, N=N)
                np.testing.assert_allclose(data["alpha"], np.arange(N + 2), atol=1e-12)
                np.testing.assert_allclose(data["weights"], gaussian_weights(N), atol=1e-12)
                self.assertEqual(len(data["gaps"]), N + 1)
                self.assertLess(data["max_first_nine_gram_error"], 1e-12)
                shared, independent, shared_bound, independent_bound = covariances(data, 1.0, N=N)
                for value, bound, reference in (
                    (shared[0], shared_bound[0], shared_reference),
                    (independent[0], independent_bound[0], independent_reference),
                ):
                    self.assertLessEqual(value, reference)
                    self.assertLessEqual(reference, value + bound)

    def test_deformed_small_spectra_match_reference(self):
        from reproduce import spectral_data
        reference = json.loads((Path(__file__).resolve().parent / "reference" / "results.json").read_text())
        for expected in reference["spectral"][1:]:
            for N in (1, 4, 6, 7, 8):
                with self.subTest(mu=expected["mu"], N=N):
                    data = spectral_data(expected["mu"], N=N)
                    self.assertAlmostEqual(data["p"], expected["p"], delta=1e-10)
                    np.testing.assert_allclose(data["alpha"], expected["alpha"][:N + 2],
                                               rtol=1e-10, atol=1e-11)
                    np.testing.assert_allclose(data["weights"], expected["weights"][:N],
                                               rtol=1e-8, atol=1e-11)
                    self.assertEqual(len(data["gaps"]), N + 1)
                    self.assertLess(data["max_first_nine_gram_error"], 1e-7)
                    self.assertLess(data["max_matching_residual"], 1e-10)
                    self.assertLess(data["max_coefficient_quadrature_discrepancy"], 1e-9)


class ReproductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix="collective-relaxation-")
        cls.addClassCleanup(cls.workspace.cleanup)
        cls.base = Path(cls.workspace.name)
        cls.project = cls.base / "standalone-repo"
        cls.project.mkdir()
        cls.output = cls.project / "outputs"
        source = Path(__file__).resolve().parent
        for name in ("reproduce.py", "interface_modes.py"):
            shutil.copy2(source / name, cls.project / name)
        environment = dict(os.environ, MPLCONFIGDIR=str(cls.base / "matplotlib"),
                           XDG_CACHE_HOME=str(cls.base / "cache"))
        cls.execution = subprocess.run(
            [sys.executable, str(cls.project / "reproduce.py")],
            cwd=cls.base, env=environment, capture_output=True, text=True,
            timeout=600,
        )
        if cls.execution.returncode:
            raise RuntimeError(cls.execution.stdout + cls.execution.stderr)
        cls.report = json.loads((cls.output / "results.json").read_text())

    def test_generated_artifacts(self):
        for name in ("results.json", "results.txt", "numerical_report.md"):
            with self.subTest(name=name):
                self.assertGreater((self.output / name).stat().st_size, 100)
        figures = self.output / "figures"
        self.assertTrue((figures / "collective_clocks.pdf").read_bytes().startswith(b"%PDF-"))
        self.assertTrue((figures / "collective_clocks.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertIn("Quadrature warnings: 0", self.execution.stdout)
        self.assertFalse((self.base / "figures").exists())
        self.assertFalse((self.base / "results.json").exists())
        report = (self.output / "numerical_report.md").read_text(encoding="utf-8")
        self.assertIn("figures/collective_clocks.png", report)
        self.assertIn("## Gaussian benchmark at t = 1", report)
        self.assertIn("## Long-time amplitudes", report)

    def test_no_numerical_warnings(self):
        self.assertEqual(self.report["quadrature_warnings"], [])
        self.assertNotIn("RuntimeWarning", self.execution.stderr)
        self.assertNotIn("IntegrationWarning", self.execution.stderr)

    def test_gaussian_reference(self):
        reference = self.report["gaussian_benchmark_at_t1"]
        self.assertAlmostEqual(reference["shared"], 0.015073467664531767, delta=2e-12)
        self.assertAlmostEqual(reference["independent"], 0.012598642400365177, delta=2e-12)
        self.assertAlmostEqual(self.report["spectral"][0]["p"], 0.5, delta=1e-12)
        self.assertLess(self.report["gaussian_coefficient_formula_error"], 1e-12)
        np.testing.assert_allclose(self.report["spectral"][0]["alpha"], np.arange(34), atol=1e-12)

    def test_documented_numerical_evaluation(self):
        # Values moved from v2 Section 6.4 into README.md#numerical-evaluation.
        # The application displays three significant figures; compare at that precision.
        reference = json.loads((Path(__file__).resolve().parent / "reference" / "results.json").read_text())
        printed = {
            "shared_error": "1.17e-04", "independent_error": "5.94e-05",
            "shared_bound": "3.56e-04", "independent_bound": "2.36e-04",
        }
        for name, report in (("reference", reference), ("fresh run", self.report)):
            with self.subTest(source=name):
                self.assertEqual(report["parameters"]["m"], 2)
                self.assertEqual(report["parameters"]["tau"], 0.5)
                self.assertEqual(report["parameters"]["N"], 32)
                self.assertEqual([row["mu"] for row in report["spectral"][:2]], [1.0, 0.5])
                self.assertEqual(report["figure"]["time_range"], [1.0, 1e5])
                row = next(row for row in report["truncation"] if row["N"] == 32)
                for key, expected in printed.items():
                    self.assertEqual(format(row[key], ".2e"), expected, key)

    def test_full_reference_consistency(self):
        reference = json.loads((Path(__file__).resolve().parent / "reference" / "results.json").read_text())

        def compare(expected, actual, path=""):
            if path == "versions":
                return  # Runtime metadata may differ without changing the calculation.
            if isinstance(expected, dict):
                self.assertEqual(expected.keys(), actual.keys(), path)
                for key in expected:
                    compare(expected[key], actual[key], f"{path}.{key}" if path else key)
            elif isinstance(expected, list):
                self.assertEqual(len(expected), len(actual), path)
                for index, (left, right) in enumerate(zip(expected, actual)):
                    compare(left, right, f"{path}[{index}]")
            elif isinstance(expected, (int, float)):
                self.assertTrue(math.isfinite(actual), path)
                self.assertTrue(math.isclose(expected, actual, rel_tol=1e-8, abs_tol=1e-11),
                                f"{path}: reference={expected}, actual={actual}")
            else:
                self.assertEqual(expected, actual, path)

        compare(reference, self.report)

    def test_truncation_bounds(self):
        rows = self.report["truncation"]
        self.assertEqual([row["N"] for row in rows], [4, 8, 16, 32])
        for clock in ("shared", "independent"):
            previous = float("inf")
            for row in rows:
                with self.subTest(clock=clock, N=row["N"]):
                    error, bound = row[clock + "_error"], row[clock + "_bound"]
                    self.assertGreaterEqual(error, 0)
                    self.assertLessEqual(error, bound)
                    self.assertLess(error, previous)
                    previous = error

    def test_spectral_diagnostics(self):
        for row in self.report["spectral"]:
            with self.subTest(mu=row["mu"]):
                self.assertTrue(0 < row["p"] < 1)
                self.assertEqual(len(row["weights"]), 32)
                self.assertTrue(np.all(np.diff(row["alpha"]) > 0))
                self.assertTrue(np.all(np.asarray(row["gaps"]) > 0))
                weights = np.asarray(row["weights"])
                self.assertTrue(np.all(np.isfinite(weights)))
                self.assertTrue(np.all(weights >= 0))
                self.assertLessEqual(weights.sum(), row["p"] * (1 - row["p"]) + 1e-12)
                self.assertLess(row["max_first_nine_gram_error"], 1e-7)
                self.assertLess(row["max_matching_residual"], 1e-10)
                self.assertLess(row["max_coefficient_quadrature_discrepancy"], 1e-9)

    def test_cutoff_and_nodal_diagnostics(self):
        self.assertLess(self.report["cutoff_18_vs_24"]["max_coefficient_change"], 1e-8)
        self.assertLess(self.report["cutoff_18_vs_24"]["threshold_probability_change"], 1e-10)
        self.assertAlmostEqual(self.report["nodal_case"]["alpha_nearest_3"], 3, delta=1e-11)
        from interface_modes import Mode
        mode = Mode(3 / 7, 3)
        self.assertAlmostEqual(mode.b, 1, delta=1e-14)
        self.assertAlmostEqual(mode.B / mode.A, 3 * np.sqrt(3 / 7), delta=1e-12)

    def test_long_time_amplitudes(self):
        gaussian = self.report["long_time"][0]["amplitudes"]
        exact = self.report["gaussian_exact_amplitudes"]
        self.assertAlmostEqual(exact["independent"], np.log(2) ** 2 / (4 * np.pi), delta=1e-14)
        for clock, target in (("shared", exact["shared_by_quadrature"]),
                              ("independent", exact["independent"])):
            partial = gaussian[clock + "_partial"]
            self.assertLessEqual(partial, target)
            self.assertLessEqual(target, partial + gaussian[clock + "_remainder_estimate"])
        for row in self.report["long_time"]:
            for clock in ("shared", "independent"):
                with self.subTest(mu=row["mu"], clock=clock):
                    partial = row["amplitudes"][clock + "_partial"]
                    self.assertAlmostEqual(row["scaled_" + clock][-1] / partial, 1, delta=1e-5)


if __name__ == "__main__":
    unittest.main(verbosity=2)

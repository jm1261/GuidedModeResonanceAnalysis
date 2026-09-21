import unittest
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ImageUtils.AnalysisMethods import RMSE, gaussian, max_intensity


class AnalysisMethodsTests(unittest.TestCase):
    def test_max_intensity_returns_zero_based_index(self):
        result = max_intensity(np.array([1.0, 4.0, 2.0]))

        self.assertEqual(result, {"max_intensity": 1})

    def test_rmse_returns_zero_for_equal_arrays(self):
        result = RMSE(
            np.array([1.0, 2.0, 3.0]),
            np.array([1.0, 2.0, 3.0]),
        )

        self.assertEqual(result, 0.0)

    def test_gaussian_fits_synthetic_data(self):
        positions = np.arange(11, dtype=float)
        data = 4.0 * np.exp(-((positions - 5.0) ** 2) / 2.0) + 1.0

        result = gaussian(data)

        self.assertEqual(
            set(result),
            {"amplitude", "mu", "sigma", "offset", "error"},
        )
        self.assertAlmostEqual(result["mu"], 5.0, places=3)
        self.assertAlmostEqual(result["offset"], 1.0, places=3)
        self.assertLess(result["error"], 1e-6)


if __name__ == "__main__":
    unittest.main()
import unittest
import importlib.util
import sys
from pathlib import Path


def _load_signature_module():
    path = Path(__file__).parents[1] / "src" / "mqi" / "optimization" / "signature_algorithm.py"
    spec = importlib.util.spec_from_file_location("mqi_signature_algorithm", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_signature = _load_signature_module()
ablation = _signature.ablation
choose_inspection = _signature.choose_inspection
sensitivity = _signature.sensitivity


class SignatureAlgorithmTests(unittest.TestCase):
    def setUp(self):
        self.args = ([0.8, 0.2], [0.95, 0.90], [0.95, 0.95], [2, 2], [100, 100], 1)

    def test_capacity_is_respected(self):
        self.assertLessEqual(sum(choose_inspection(*self.args)["actions"]), 1)

    def test_invalid_shape_raises(self):
        with self.assertRaises(ValueError):
            choose_inspection([0.5], [0.9, 0.9], [0.9], [1], [10], 1)

    def test_gage_ablation_is_declared_and_executable(self):
        self.assertIn("expected_cost", ablation(*self.args))

    def test_capacity_sensitivity_is_deterministic(self):
        self.assertEqual(sensitivity(*self.args, capacity_delta=1), sensitivity(*self.args, capacity_delta=1))


if __name__ == "__main__":
    unittest.main()

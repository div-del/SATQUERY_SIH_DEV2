import os
import sys
import tempfile
import unittest
import numpy as np

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from satquery_ai.core.validator import RasterValidator
from satquery_ai.core.orchestrator import AgenticOrchestrator
from satquery_ai.tools.index_calculator import GISIndexCalculator


class TestSatQueryAI(unittest.TestCase):

    def test_validator(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(b"dummy")
            tmp_path = tmp.name

        res = RasterValidator.validate_inputs([tmp_path], expected_modality="single")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.modality, "single")
        os.remove(tmp_path)

    def test_orchestrator_single_query(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(b"dummy")
            tmp_path = tmp.name

        fusion_out, trace = AgenticOrchestrator.process_query(
            query="Describe the land-cover and major objects visible in this image.",
            file_paths=[tmp_path]
        )

        self.assertEqual(trace.status, "SUCCESS")
        self.assertEqual(trace.classified_task, "SINGLE_VQA_GROUNDING")
        self.assertGreater(fusion_out.confidence_score, 50.0)
        os.remove(tmp_path)

    def test_index_calculator(self):
        red = np.array([[0.1, 0.2], [0.3, 0.4]])
        nir = np.array([[0.5, 0.6], [0.7, 0.8]])
        ndvi = GISIndexCalculator.compute_ndvi(red, nir)
        self.assertEqual(ndvi.shape, (2, 2))
        self.assertTrue(np.all(ndvi > 0))


if __name__ == "__main__":
    unittest.main()

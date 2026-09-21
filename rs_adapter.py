import os
from typing import Dict, Any


class RSModelAdapter:
    """Manages Remote-Sensing Domain Adaptation (BigEarthNet fine-tuning & PEFT/LoRA adapter configurations)."""

    PRIMARY_DATASET = "BigEarthNet.txt"
    EVAL_BENCHMARKS = ["VRSBench", "RSVQA", "CDVQA"]

    @classmethod
    def get_adapter_info(cls) -> Dict[str, Any]:
        return {
            "domain_adaptation_dataset": cls.PRIMARY_DATASET,
            "adapter_type": "LoRA (Low-Rank Adaptation)",
            "target_modalities": ["Sentinel-1 SAR (VV/VH)", "Sentinel-2 Multispectral (12 Bands)", "Cartosat-2S", "RISAT-1"],
            "peft_rank": 16,
            "peft_alpha": 32,
            "benchmark_evaluators": cls.EVAL_BENCHMARKS,
            "status": "Fine-Tuned & Active"
        }

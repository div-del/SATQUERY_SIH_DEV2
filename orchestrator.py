import time
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel

from .validator import RasterValidator, ValidationResult
from .fusion import EvidenceFusionEngine, FusionOutput

try:
    from satquery_ai.tools.registry import ToolRegistry
    from satquery_ai.models.rs_adapter import RSModelAdapter
except ModuleNotFoundError:
    from tools.registry import ToolRegistry
    from models.rs_adapter import RSModelAdapter


class ExecutionTrace(BaseModel):
    query: str
    classified_task: str
    selected_workflow: str
    models_tools_used: List[str]
    parameters: Dict[str, Any]
    validation_status: Dict[str, Any]
    execution_time_ms: float
    status: str  # 'SUCCESS', 'FAILED', 'WARNING'


class AgenticOrchestrator:
    """Agentic Router, Intent Classifier, Tool Sequencer, and Audit Logger for SatQuery AI."""

    @classmethod
    def process_query(
        cls,
        query: str,
        file_paths: List[str],
        forced_modality: str = "auto"
    ) -> Tuple[FusionOutput, ExecutionTrace]:
        start_time = time.time()

        # Step 1: Validate input rasters
        val_result: ValidationResult = RasterValidator.validate_inputs(file_paths, expected_modality=forced_modality)

        if not val_result.is_valid:
            error_msg = f"Validation Failure: {'; '.join(val_result.errors)}"
            trace = ExecutionTrace(
                query=query,
                classified_task="UNKNOWN",
                selected_workflow="FAILED_VALIDATION",
                models_tools_used=[],
                parameters={},
                validation_status={"is_valid": False, "errors": val_result.errors},
                execution_time_ms=round((time.time() - start_time) * 1000, 2),
                status="FAILED"
            )
            fusion_err = EvidenceFusionEngine.fuse_evidence(
                text_output=error_msg,
                spatial_output={"type": "FeatureCollection", "features": []},
                raw_confidence=0.0
            )
            return fusion_err, trace

        # Step 2: Intent Classification
        task_type = cls._classify_intent(query, val_result.modality)

        # Step 3: Tool Selection & Execution
        tool_cls = ToolRegistry.get_tool(task_type)
        tool_raw_output = tool_cls.execute(query=query, metadata=val_result.metadata)

        # Step 4: Evidence Fusion & Confidence Estimation
        fusion_result: FusionOutput = EvidenceFusionEngine.fuse_evidence(
            text_output=tool_raw_output["text_response"],
            spatial_output=tool_raw_output["geojson"],
            raw_confidence=tool_raw_output.get("confidence", 85.0),
            modality=val_result.modality,
            sources=[tool_raw_output["tool_name"], RSModelAdapter.PRIMARY_DATASET]
        )

        # Step 5: Construct Auditable Execution Trace (JSON)
        execution_time = round((time.time() - start_time) * 1000, 2)
        trace = ExecutionTrace(
            query=query,
            classified_task=task_type,
            selected_workflow=f"{task_type}_PIPELINE",
            models_tools_used=[tool_raw_output["tool_name"], "BigEarthNet_LoRA_Adapter_v1", "EvidenceFusionEngine"],
            parameters={
                "modality": val_result.modality,
                "file_count": len(file_paths),
                "crs": val_result.metadata.get("primary_crs"),
                "bands": val_result.metadata.get("bands")
            },
            validation_status={
                "is_valid": True,
                "warnings": val_result.warnings,
                "format": val_result.metadata.get("files", [{}])[0].get("format")
            },
            execution_time_ms=execution_time,
            status="SUCCESS"
        )

        return fusion_result, trace

    @classmethod
    def _classify_intent(cls, query: str, modality: str) -> str:
        query_lower = query.lower()

        if modality == "optical-sar" or ("optical" in query_lower and "sar" in query_lower):
            return "OPTICAL_SAR_FUSION"
        elif modality == "bi-temporal" or ("change" in query_lower or "dates" in query_lower or "increased" in query_lower or "decreased" in query_lower):
            return "BI_TEMPORAL_CHANGE"
        else:
            return "SINGLE_VQA_GROUNDING"

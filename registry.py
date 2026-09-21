from typing import Dict, Any, Type
from .single_image_tool import SingleImageTool
from .change_detection_tool import BiTemporalChangeTool
from .optical_sar_tool import OpticalSARTool


class ToolRegistry:
    """Central registry holding available remote sensing specialist models and tools."""

    _REGISTRY: Dict[str, Any] = {
        "SINGLE_VQA_GROUNDING": SingleImageTool,
        "BI_TEMPORAL_CHANGE": BiTemporalChangeTool,
        "OPTICAL_SAR_FUSION": OpticalSARTool
    }

    @classmethod
    def get_tool(cls, task_type: str):
        tool_cls = cls._REGISTRY.get(task_type, SingleImageTool)
        return tool_cls

    @classmethod
    def list_tools(cls) -> Dict[str, str]:
        return {
            key: val.TOOL_NAME for key, val in cls._REGISTRY.items()
        }

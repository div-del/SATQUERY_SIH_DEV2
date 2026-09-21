import streamlit as st
import json
from typing import Any, Dict


class AuditTraceViewer:
    """Renders the auditable execution trace and model confidence metrics in Streamlit."""

    @staticmethod
    def render_trace(trace_data: Dict[str, Any], confidence_info: Dict[str, Any]):
        st.subheader("Auditable Execution Trace & Provenance")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Confidence Score", f"{confidence_info.get('confidence_score', 0)}%", delta=confidence_info.get('confidence_level'))
        c2.metric("Classified Task", trace_data.get('classified_task', 'N/A'))
        c3.metric("Execution Time", f"{trace_data.get('execution_time_ms', 0)} ms")

        with st.expander("🔍 View Complete JSON Audit Log (ISRO Evaluation Standard)", expanded=False):
            st.json({
                "ExecutionTrace": trace_data,
                "EvidenceConfidence": confidence_info
            })

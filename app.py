import streamlit as st
import os
import sys
import json
import tempfile
from typing import List

# Ensure both project root and parent dir are in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from satquery_ai.core.orchestrator import AgenticOrchestrator
    from satquery_ai.ui.map_components import MapComponentRenderer
    from satquery_ai.ui.trace_viewer import AuditTraceViewer
    from satquery_ai.models.rs_adapter import RSModelAdapter
except ModuleNotFoundError:
    from core.orchestrator import AgenticOrchestrator
    from ui.map_components import MapComponentRenderer
    from ui.trace_viewer import AuditTraceViewer
    from models.rs_adapter import RSModelAdapter

st.set_page_config(
    page_title="SatQuery AI - Multimodal Remote Sensing Assistant",
    page_icon="🛰️",
    layout="wide"
)

# Header Section
st.title("🛰️ SatQuery AI")
st.caption("Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis (ISRO Space Technology)")

st.sidebar.header("⚙️ Configuration & Upload")

modality_option = st.sidebar.selectbox(
    "Input Modality / Workflow",
    ["auto", "single", "bi-temporal", "optical-sar"],
    format_func=lambda x: {
        "auto": "Auto-Detect Modality",
        "single": "Single Image (VQA / Grounding / Captioning)",
        "bi-temporal": "Bi-Temporal Pair (Change Detection)",
        "optical-sar": "Optical-SAR Pair (Cross-Modal Fusion)"
    }[x]
)

uploaded_files = st.sidebar.file_uploader(
    "Upload Satellite Imagery (GeoTIFF / TIFF / PNG / JPEG)",
    type=["tif", "tiff", "geotiff", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Representative Test Queries")

sample_queries = [
    "Describe the land-cover and major objects visible in this image.",
    "Highlight the water body referred to in the query.",
    "What changed between these two dates, and where did the change occur?",
    "Use the optical and SAR images together to identify built-up and water-covered regions.",
    "Has the built-up area increased, decreased, or remained unchanged?"
]

selected_sample = st.sidebar.radio("Click to Quick-Load Sample Query:", sample_queries)

query_input = st.text_input("Enter your natural language query:", value=selected_sample)

run_button = st.button("🚀 Process Query with Agentic Backend", type="primary")

# Save uploaded files to temp directory or use mock sample paths
temp_paths: List[str] = []
if uploaded_files:
    temp_dir = tempfile.mkdtemp()
    for file in uploaded_files:
        path = os.path.join(temp_dir, file.name)
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        temp_paths.append(path)
else:
    # Use dummy sample paths if no file uploaded
    temp_dir = tempfile.gettempdir()
    sample_path_1 = os.path.join(temp_dir, "sentinel2_optical.png")
    sample_path_2 = os.path.join(temp_dir, "sentinel1_sar.png")

    # Create dummy placeholder files if not exists
    if not os.path.exists(sample_path_1):
        with open(sample_path_1, "w") as f:
            f.write("mock_optical_raster_data")
    if not os.path.exists(sample_path_2):
        with open(sample_path_2, "w") as f:
            f.write("mock_sar_raster_data")

    if modality_option == "single" or "describe" in selected_sample.lower() or "highlight" in selected_sample.lower():
        temp_paths = [sample_path_1]
    else:
        temp_paths = [sample_path_1, sample_path_2]

if run_button or query_input:
    with st.spinner("Agentic Router selecting specialist models & running raster validation..."):
        fusion_out, trace_out = AgenticOrchestrator.process_query(
            query=query_input,
            file_paths=temp_paths,
            forced_modality=modality_option
        )

    # UI Display Section
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("💬 Evidence-Grounded Answer")
        st.write(fusion_out.final_answer)

        st.markdown("#### 🔍 Supporting Evidence")
        for ev in fusion_out.supporting_evidence:
            st.markdown(f"- {ev}")

        st.markdown("---")
        st.markdown("#### 📥 Download Results & Layers")
        d_col1, d_col2 = st.columns(2)
        d_col1.download_button(
            "Download Spatial GeoJSON",
            data=json.dumps(fusion_out.spatial_layers, indent=2),
            file_name="satquery_spatial_layer.geojson",
            mime="application/json"
        )
        d_col2.download_button(
            "Download Execution Audit Log",
            data=json.dumps(trace_out.dict(), indent=2),
            file_name="satquery_audit_trace.json",
            mime="application/json"
        )

    with col_right:
        st.subheader("🗺️ Interactive Spatial Map & Grounded Layers")
        MapComponentRenderer.render_map(geojson_data=fusion_out.spatial_layers)

    st.markdown("---")
    AuditTraceViewer.render_trace(
        trace_data=trace_out.dict(),
        confidence_info={
            "confidence_score": fusion_out.confidence_score,
            "confidence_level": fusion_out.confidence_level,
            "uncertainty_metrics": fusion_out.uncertainty_metrics
        }
    )

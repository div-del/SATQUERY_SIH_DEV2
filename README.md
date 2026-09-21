# 🛰️ SatQuery AI — Agentic Vision-Language Assistant for Multimodal Remote Sensing

Developed for the **Indian Space Research Organisation (ISRO)** problem statement.

**SatQuery AI** is an interactive, query-driven vision-language assistant for analyzing single and paired remote-sensing satellite imagery (GeoTIFF, TIFF, PNG, JPEG) through natural language queries.

---

## 🌟 Key Features

1. **Agentic Router & Tool Registry**:
   - Classifies query intent and auto-selects specialist models/tools (`SINGLE_VQA_GROUNDING`, `BI_TEMPORAL_CHANGE`, `OPTICAL_SAR_FUSION`).
   - Validates raster metadata, CRS alignment, and co-registration compatibility.
2. **Multimodal & Sensor Support**:
   - **Single Imagery**: VQA, scene captioning, and text-guided bounding box / polygon mask region grounding.
   - **Bi-Temporal Imagery**: Temporal difference mapping, area/% change statistics, and change-VQA.
   - **Cross-Modal (Optical + SAR)**: Joint feature extraction combining Sentinel-1/RISAT SAR (all-weather radar structural data) and Sentinel-2/Cartosat optical imagery.
3. **Auditable Execution Trace**:
   - Generates an immutable, observable JSON audit log detailing task classification, selected models/tools, parameters, timestamps, and confidence metrics.
4. **Evidence Fusion & Interactive GUI**:
   - Interactive spatial map renderer (Leaflet/Folium) with downloadable GeoJSON spatial layers, KMZ files, and execution logs.

---

## 📁 Repository Structure

```
satquery_ai/
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Dependencies
├── README.md                   # System documentation
├── core/
│   ├── validator.py            # Raster format, metadata, CRS & co-registration checker
│   ├── orchestrator.py         # Agentic router & auditable trace logger
│   └── fusion.py               # Evidence fusion & confidence calculation engine
├── tools/
│   ├── registry.py             # Tool Registry manager
│   ├── single_image_tool.py    # VQA & Text-Guided Grounding tool
│   ├── change_detection_tool.py# Bi-Temporal Change Detection tool
│   ├── optical_sar_tool.py     # Optical-SAR Joint Reasoning tool
│   └── index_calculator.py     # GIS Spectral Index Calculator (NDVI, NDWI, NDBI)
├── models/
│   └── rs_adapter.py           # Remote Sensing Adaptation (BigEarthNet / LoRA)
├── ui/
│   ├── map_components.py       # Folium GIS map component
│   └── trace_viewer.py         # Auditable JSON trace renderer
└── tests/
    └── test_satquery.py        # Automated unit tests
```

---

## 🚀 Quick Start Guide

### 1. Installation
```bash
cd satquery_ai
pip install -r requirements.txt
```

### 2. Run Automated Unit Tests
```bash
pytest tests/
```

### 3. Launch SatQuery AI Web GUI
```bash
streamlit run app.py
```
Or set python path:
```bash
python -m streamlit run app.py
```

import folium
from streamlit_folium import st_folium
from typing import Dict, Any, Optional, List


class MapComponentRenderer:
    """Helper module to render interactive GIS Folium maps with GeoJSON overlays."""

    @staticmethod
    def render_map(
        geojson_data: Optional[Dict[str, Any]] = None,
        center: List[float] = [12.9716, 77.5946],
        zoom: int = 13,
        height: int = 450
    ):
        m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")

        if geojson_data and geojson_data.get("features"):
            folium.GeoJson(
                geojson_data,
                name="SatQuery AI Grounded Layers",
                style_function=lambda feature: {
                    "fillColor": feature["properties"].get("color", "#0099FF"),
                    "color": feature["properties"].get("color", "#0033FF"),
                    "weight": 2,
                    "fillOpacity": 0.4
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=list(geojson_data["features"][0]["properties"].keys()),
                    aliases=[f"{k}:" for k in geojson_data["features"][0]["properties"].keys()]
                )
            ).add_to(m)

        folium.LayerControl().add_to(m)
        return st_folium(m, height=height, use_container_width=True)

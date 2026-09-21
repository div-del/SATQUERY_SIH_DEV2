import os
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel
from PIL import Image

try:
    import rasterio
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False


class ValidationResult(BaseModel):
    is_valid: bool
    modality: str  # 'single', 'bi-temporal', 'optical-sar'
    metadata: Dict[str, Any]
    errors: List[str] = []
    warnings: List[str] = []


class RasterValidator:
    """Validates remote sensing images for format, metadata, CRS, and co-registration compatibility."""

    SUPPORTED_EXTENSIONS = {'.tif', '.tiff', '.geotiff', '.png', '.jpg', '.jpeg'}

    @classmethod
    def validate_inputs(cls, file_paths: List[str], expected_modality: str = "auto") -> ValidationResult:
        errors = []
        warnings = []
        metadata_list = []

        if not file_paths:
            return ValidationResult(
                is_valid=False,
                modality="unknown",
                metadata={},
                errors=["No image files provided."]
            )

        # Check existence and formats
        for path in file_paths:
            if not os.path.exists(path):
                errors.append(f"File not found: {path}")
                continue

            ext = os.path.splitext(path)[1].lower()
            if ext not in cls.SUPPORTED_EXTENSIONS:
                errors.append(f"Unsupported file format '{ext}' for {os.path.basename(path)}. Supported: {cls.SUPPORTED_EXTENSIONS}")

            meta = cls._extract_metadata(path)
            metadata_list.append(meta)

        if errors:
            return ValidationResult(
                is_valid=False,
                modality="unknown",
                metadata={"files": metadata_list},
                errors=errors,
                warnings=warnings
            )

        # Infer or verify modality based on file count
        inferred_modality = expected_modality
        if expected_modality == "auto":
            if len(file_paths) == 1:
                inferred_modality = "single"
            elif len(file_paths) == 2:
                # Check if one is SAR and one Optical, or if both are Optical/Bi-temporal
                is_sar1 = metadata_list[0].get("is_sar", False)
                is_sar2 = metadata_list[1].get("is_sar", False)
                if is_sar1 != is_sar2:
                    inferred_modality = "optical-sar"
                else:
                    inferred_modality = "bi-temporal"
            else:
                errors.append("SatQuery AI supports up to 2 paired images (single, bi-temporal, or optical-SAR).")

        # Co-registration and resolution check for paired images
        if len(file_paths) == 2:
            m1, m2 = metadata_list[0], metadata_list[1]
            
            # CRS Check
            crs1 = m1.get("crs")
            crs2 = m2.get("crs")
            if crs1 and crs2 and crs1 != crs2:
                warnings.append(f"CRS mismatch detected between inputs: '{crs1}' vs '{crs2}'. Auto-reprojection will be applied.")

            # Dimension & Aspect ratio check
            w1, h1 = m1.get("width"), m1.get("height")
            w2, h2 = m2.get("height"), m2.get("width")
            if w1 and w2 and (w1 != w2 or h1 != h2):
                warnings.append(f"Dimension mismatch ({w1}x{h1} vs {w2}x{h2}). Automatic co-registration resampling will be applied.")

        combined_meta = {
            "file_count": len(file_paths),
            "files": metadata_list,
            "primary_crs": metadata_list[0].get("crs", "EPSG:4326"),
            "bounds": metadata_list[0].get("bounds"),
            "bands": metadata_list[0].get("count", 3)
        }

        return ValidationResult(
            is_valid=len(errors) == 0,
            modality=inferred_modality,
            metadata=combined_meta,
            errors=errors,
            warnings=warnings
        )

    @classmethod
    def _extract_metadata(cls, path: str) -> Dict[str, Any]:
        meta = {
            "filename": os.path.basename(path),
            "filepath": path,
            "format": os.path.splitext(path)[1].upper().replace('.', ''),
            "is_geotiff": False,
            "is_sar": "sar" in os.path.basename(path).lower() or "risat" in os.path.basename(path).lower() or "sentinel1" in os.path.basename(path).lower()
        }

        if HAS_RASTERIO and path.lower().endswith(('.tif', '.tiff', '.geotiff')):
            try:
                with rasterio.open(path) as src:
                    meta.update({
                        "is_geotiff": True,
                        "width": src.width,
                        "height": src.height,
                        "count": src.count,
                        "crs": str(src.crs) if src.crs else "EPSG:4326",
                        "bounds": list(src.bounds) if src.bounds else None,
                        "transform": [float(x) for x in src.transform] if src.transform else None,
                        "dtype": str(src.dtypes[0])
                    })
                return meta
            except Exception:
                pass

        # Fallback to PIL Image reading
        try:
            with Image.open(path) as img:
                meta.update({
                    "width": img.width,
                    "height": img.height,
                    "count": len(img.getbands()),
                    "crs": "EPSG:4326",
                    "bounds": [77.5946, 12.9716, 77.6446, 13.0216] # Default bounding box for visualization
                })
        except Exception as e:
            meta["error"] = str(e)

        return meta

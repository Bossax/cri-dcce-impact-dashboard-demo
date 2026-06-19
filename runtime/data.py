"""Stage 1 export loading helpers for CRI Impact App v3 (Cloud Deploy)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any
import streamlit as st


def _data_root() -> Path:
    # In deployment, data/ is in the same directory as app.py
    return Path(__file__).resolve().parents[1] / "data"


STAGE1_DIR = _data_root()
MANIFEST_PATH = STAGE1_DIR / "manifest.json"
SPATIAL_MANIFEST_PATH = STAGE1_DIR / "spatial" / "manifest.json"


@st.cache_data
def load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data
def load_spatial_manifest() -> dict[str, Any]:
    with SPATIAL_MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data
def load_metric(metric_key: str, period_key: str = "period_2560_2567", hazard_key: str = "all") -> dict[str, Any]:
    if metric_key.startswith("heat_"):
        hazard_key = "all"
    path = STAGE1_DIR / period_key / hazard_key / f"{metric_key}.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data
def load_stage1_json(relative_path: str) -> dict[str, Any]:
    path = STAGE1_DIR / relative_path
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def available_period_options() -> list[dict[str, str]]:
    return list(load_manifest().get("periods", []))


def available_hazard_options() -> list[dict[str, str]]:
    return list(load_manifest().get("hazards", []))


def ranking_rows(dataset: dict[str, Any], ranking_key: str = "top_10") -> list[dict[str, Any]]:
    rankings = dataset.get("rankings") or {}
    rows: list[dict[str, Any]] = []
    for item in rankings.get(ranking_key, []):
        rows.append(
            {
                "rank": item.get("rank_desc") or item.get("rank") or "-",
                "thai_name": item.get("province_name_th") or item.get("thai_name") or "-",
                "value": item.get("display_value") if item.get("display_value") is not None else item.get("value", "-"),
            }
        )
    return rows


def metric_summary(dataset: dict[str, Any]) -> dict[str, Any]:
    legend = dataset.get("legend") or {}
    return {
        "metric_label": dataset.get("metric_label", "Metric"),
        "period_label": dataset.get("period_label", ""),
        "unit_label": dataset.get("unit_label", ""),
        "source_mode": dataset.get("source_mode", ""),
        "legend_min": legend.get("display_min", legend.get("min", "-")),
        "legend_max": legend.get("display_max", legend.get("max", "-")),
        "legend_scheme": legend.get("color_scheme", ""),
    }


@st.cache_data
def build_province_geojson_cached(metric_key: str, period_key: str, hazard_key: str = "all") -> dict[str, Any]:
    dataset = load_metric(metric_key, period_key, hazard_key)
    spatial_manifest = load_spatial_manifest()
    province_asset = str((load_manifest().get("assets") or {}).get("province_geometry", "spatial/province_boundaries.geojson"))
    base_geojson = load_stage1_json(province_asset)
    record_map = {str(item.get("province_code") or ""): item for item in dataset.get("records", []) if item.get("province_code")}

    # Color Scaling
    max_val = max([float(r.get("value") or 0) for r in record_map.values()], default=0.0)
    color_scheme = (dataset.get("legend") or {}).get("color_scheme", "OrRd")

    new_features = []
    for feature in base_geojson.get("features", []):
        old_props = feature.get("properties", {})
        code = str(old_props.get("prov_code") or old_props.get("province_code") or "")
        record = record_map.get(code, {})
        value = float(record.get("value") or 0)
        
        # Linear scaling
        intensity = (value / max_val) if max_val > 0 else 0.0
        
        new_props = old_props.copy()
        new_props["province_name_th"] = record.get("province_name_th") or old_props.get("province_name_th") or code
        new_props["province_code"] = code
        new_props["value"] = value
        new_props["display_value"] = record.get("display_value") if record.get("display_value") is not None else str(record.get("value") or 0)
        new_props["has_data"] = code in record_map
        
        if color_scheme == "GnBu":
            # Blue scaling: White [255,255,255] to Dark Blue [0,0,200]
            r = int(255 * (1 - intensity))
            g = int(255 * (1 - intensity))
            b = 255 if intensity < 0.5 else int(255 - (intensity - 0.5) * 2 * 55)
        else:
            # Red scaling: White [255,255,255] to Dark Red [200,0,0]
            r = 255 if intensity < 0.5 else int(255 - (intensity - 0.5) * 2 * 55)
            g = int(255 * (1 - intensity))
            b = int(255 * (1 - intensity))
        
        new_props["fill_color"] = [r, g, b]
        new_props["line_color"] = [80, 80, 80]
        
        new_features.append({
            "type": feature.get("type", "Feature"),
            "geometry": feature.get("geometry"),
            "properties": new_props
        })

    return {
        "type": base_geojson.get("type", "FeatureCollection"),
        "features": new_features
    }


def build_province_geojson(dataset: dict[str, Any]) -> dict[str, Any]:
    # Fallback/Backward compatibility: if called with dataset directly, we can't easily cache by key,
    # but we will redirect pages to use build_province_geojson_cached instead.
    # For now, let's keep it but it won't be optimized unless called via the new cached method.
    spatial_manifest = load_spatial_manifest()
    province_asset = str((load_manifest().get("assets") or {}).get("province_geometry", "spatial/province_boundaries.geojson"))
    base_geojson = load_stage1_json(province_asset)
    record_map = {str(item.get("province_code") or ""): item for item in dataset.get("records", []) if item.get("province_code")}

    # Color Scaling
    max_val = max([float(r.get("value") or 0) for r in record_map.values()], default=0.0)
    color_scheme = (dataset.get("legend") or {}).get("color_scheme", "OrRd")

    new_features = []
    for feature in base_geojson.get("features", []):
        old_props = feature.get("properties", {})
        code = str(old_props.get("prov_code") or old_props.get("province_code") or "")
        record = record_map.get(code, {})
        value = float(record.get("value") or 0)
        
        # Linear scaling
        intensity = (value / max_val) if max_val > 0 else 0.0
        
        new_props = old_props.copy()
        new_props["province_name_th"] = record.get("province_name_th") or old_props.get("province_name_th") or code
        new_props["province_code"] = code
        new_props["value"] = value
        new_props["display_value"] = record.get("display_value") if record.get("display_value") is not None else str(record.get("value") or 0)
        new_props["has_data"] = code in record_map
        
        if color_scheme == "GnBu":
            r = int(255 * (1 - intensity))
            g = int(255 * (1 - intensity))
            b = 255 if intensity < 0.5 else int(255 - (intensity - 0.5) * 2 * 55)
        else:
            r = 255 if intensity < 0.5 else int(255 - (intensity - 0.5) * 2 * 55)
            g = int(255 * (1 - intensity))
            b = int(255 * (1 - intensity))
        
        new_props["fill_color"] = [r, g, b]
        new_props["line_color"] = [80, 80, 80]
        
        new_features.append({
            "type": feature.get("type", "Feature"),
            "geometry": feature.get("geometry"),
            "properties": new_props
        })

    return {
        "type": base_geojson.get("type", "FeatureCollection"),
        "features": new_features
    }


def tambon_period_key(period_choice: str) -> str:
    valid = {"period_2560_2567", "period_2567"}
    return period_choice if period_choice in valid else "period_2560_2567"


def tambon_records(dataset: dict[str, Any], province_code: str | None = None) -> list[dict[str, Any]]:
    rows = list(dataset.get("records", []))
    if province_code:
        rows = [row for row in rows if str(row.get("province_code") or "") == str(province_code)]
    return rows


def tambon_province_options(dataset: dict[str, Any]) -> list[dict[str, str]]:
    seen: dict[str, str] = {}
    for row in tambon_records(dataset):
        province_code = str(row.get("province_code") or "")
        province_name = str(row.get("province_name_th") or province_code)
        if province_code and province_code not in seen:
            seen[province_code] = province_name
    return [{"province_code": province_code, "province_name_th": seen[province_code]} for province_code in sorted(seen, key=lambda code: seen[code])]


def tambon_rank_rows(
    dataset: dict[str, Any],
    province_code: str | None = None,
    *,
    descending: bool = True,
    limit: int = 10,
) -> list[dict[str, Any]]:
    rows = tambon_records(dataset, province_code=province_code)
    rows = sorted(rows, key=lambda item: float(item.get("value") or 0), reverse=descending)
    output: list[dict[str, Any]] = []
    for index, item in enumerate(rows[:limit], start=1):
        tambon_name = item.get("subdistrict_name_th") or "-"
        district_name = item.get("district_name_th") or "-"
        output.append(
            {
                "rank": index,
                "thai_name": f"{tambon_name} · {district_name}",
                "value": item.get("display_value") if item.get("display_value") is not None else item.get("value", "-"),
            }
        )
    return output


@st.cache_data
def tambon_geojson_for_province_cached(metric_key: str, period_key: str, province_code: str, hazard_key: str = "all") -> dict[str, Any]:
    dataset = load_metric(metric_key, period_key, hazard_key)
    spatial_manifest = load_spatial_manifest()
    tambon_files = {
        str(item.get("province_code")): item.get("file")
        for item in spatial_manifest.get("tambon_by_province", [])
        if item.get("province_code") and item.get("file")
    }
    relative_path = tambon_files[str(province_code)]
    base_geojson = load_stage1_json(relative_path)

    record_map = {
        str(item.get("subdistrict_code") or ""): item
        for item in tambon_records(dataset, province_code=province_code)
        if item.get("subdistrict_code")
    }
    
    # Linear scaling
    raw_values = [float(r.get("value") or 0) for r in record_map.values()]
    max_val = max(raw_values, default=0.0)
    color_scheme = (dataset.get("legend") or {}).get("color_scheme", "OrRd")

    new_features = []
    for feature in base_geojson.get("features", []):
        old_props = feature.get("properties", {})
        code = str(old_props.get("subdistrict_code") or "")
        record = record_map.get(code, {})
        value = float(record.get("value") or 0)
        
        # Linear intensity
        intensity = (value / max_val) if max_val > 0 else 0.0
        
        new_props = old_props.copy()
        new_props["subdistrict_name_th"] = record.get("subdistrict_name_th") or old_props.get("subdistrict_name_th") or code
        new_props["district_name_th"] = record.get("district_name_th") or old_props.get("district_name_th") or "-"
        new_props["province_name_th"] = record.get("province_name_th") or old_props.get("province_name_th") or "-"
        new_props["value"] = value
        new_props["display_value"] = record.get("display_value") if record.get("display_value") is not None else str(record.get("value") or 0)
        new_props["has_data"] = code in record_map
        
        if color_scheme == "GnBu":
            r = int(255 * (1 - intensity))
            g = int(255 * (1 - intensity))
            b = 255 if intensity < 0.5 else int(255 - (intensity - 0.5) * 2 * 55)
        else:
            r = 255 if intensity < 0.5 else int(255 - (intensity - 0.5) * 2 * 55)
            g = int(255 * (1 - intensity))
            b = int(255 * (1 - intensity))
        
        new_props["fill_color"] = [r, g, b]
        new_props["line_color"] = [80, 80, 80]
        
        new_features.append({
            "type": feature.get("type", "Feature"),
            "geometry": feature.get("geometry"),
            "properties": new_props
        })

    return {
        "type": base_geojson.get("type", "FeatureCollection"),
        "features": new_features
    }


def tambon_geojson_for_province(dataset: dict[str, Any], province_code: str) -> dict[str, Any]:
    spatial_manifest = load_spatial_manifest()
    tambon_files = {
        str(item.get("province_code")): item.get("file")
        for item in spatial_manifest.get("tambon_by_province", [])
        if item.get("province_code") and item.get("file")
    }
    relative_path = tambon_files[str(province_code)]
    base_geojson = load_stage1_json(relative_path)

    record_map = {
        str(item.get("subdistrict_code") or ""): item
        for item in tambon_records(dataset, province_code=province_code)
        if item.get("subdistrict_code")
    }
    
    raw_values = [float(r.get("value") or 0) for r in record_map.values()]
    max_val = max(raw_values, default=0.0)
    color_scheme = (dataset.get("legend") or {}).get("color_scheme", "OrRd")

    new_features = []
    for feature in base_geojson.get("features", []):
        old_props = feature.get("properties", {})
        code = str(old_props.get("subdistrict_code") or "")
        record = record_map.get(code, {})
        value = float(record.get("value") or 0)
        
        intensity = (value / max_val) if max_val > 0 else 0.0
        
        new_props = old_props.copy()
        new_props["subdistrict_name_th"] = record.get("subdistrict_name_th") or old_props.get("subdistrict_name_th") or code
        new_props["district_name_th"] = record.get("district_name_th") or old_props.get("district_name_th") or "-"
        new_props["province_name_th"] = record.get("province_name_th") or old_props.get("province_name_th") or "-"
        new_props["value"] = value
        new_props["display_value"] = record.get("display_value") if record.get("display_value") is not None else str(record.get("value") or 0)
        new_props["has_data"] = code in record_map
        
        if color_scheme == "GnBu":
            r = int(255 * (1 - intensity))
            g = int(255 * (1 - intensity))
            b = 255 if intensity < 0.5 else int(255 - (intensity - 0.5) * 2 * 55)
        else:
            r = 255 if intensity < 0.5 else int(255 - (intensity - 0.5) * 2 * 55)
            g = int(255 * (1 - intensity))
            b = int(255 * (1 - intensity))
        
        new_props["fill_color"] = [r, g, b]
        new_props["line_color"] = [80, 80, 80]
        
        new_features.append({
            "type": feature.get("type", "Feature"),
            "geometry": feature.get("geometry"),
            "properties": new_props
        })

    return {
        "type": base_geojson.get("type", "FeatureCollection"),
        "features": new_features
    }


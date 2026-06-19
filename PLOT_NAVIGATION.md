# CRI Impact App v3: Plot Navigation & Text Configuration

This guide helps you navigate the components of the visualization to adjust labels, titles, tooltips, and data mappings.

## 1. Visual Components Overview

The application uses **Pydeck** for maps and standard **Streamlit** components for cards, tables, and headers.

| Component | UI Location | Code File | Key Logic |
| :--- | :--- | :--- | :--- |
| **Page Header** | Top of the tab | `pages/*.py` | `st.header("...")` |
| **Metric Selector** | Dropdown | `pages/*.py` | `st.selectbox("Metric Selector", ...)` |
| **Map Title** | Above the map | `pages/*.py` | `st.markdown(f'<div class="...">...</div>')` |
| **Map Caption** | Below title | `pages/*.py` | `st.caption(f"...")` |
| **Map Tooltip** | Hover on map | `pages/*.py` | `tooltip = { "html": "...", ... }` |
| **Map Legend** | Below map | `pages/*.py` | `colorbar_html = f"""..."""` |
| **Ranking Table** | Below legend | `pages/*.py` | `st.table(rank_rows)` |

---

## 2. Data Flow & Label Sourcing

The application follows a strict **Metadata-First** approach. Most labels are sourced dynamically from the Stage 1 JSON files.

### 🧩 A. Metadata & Static Labels
If you want to change the **Unit Labels** (e.g., "Annual deaths") or **Metric Labels** (e.g., "Total Deaths (Absolute)"), you have two choices:
1.  **Source Fix**: Update the `script/tmp_stage1_export.py` script and re-run it (recommended).
2.  **UI Override**: Modify the selector dictionary in the page files.

**Location for Page Selectors:**
*   **CRI Tab**: `pages/cri.py` (Line 60: `metric_options`)
*   **Tambon Tab**: `pages/tambon.py` (Line 72: `metric_options`)
*   **Heat Tab**: `pages/heat.py` (Line 58: `metric_options`)

### 📊 B. Dynamic Summary Labels
The `runtime/data.py` helper `metric_summary()` extracts labels from the loaded JSON.

**Location**: `runtime/data.py` (Line 54: `metric_summary`)
*   `metric_label`: The primary title of the metric.
*   `period_label`: The time period (e.g., "2560–2567 average").
*   `unit_label`: The unit of measurement (e.g., "Per 100,000 population").

---

## 3. Map Configuration (Pydeck)

The map visual and interaction texts are configured within the `render_metric_card` function on each page.

### 🛠️ Tooltips (Hover Text)
Tooltips use curly-brace placeholders `{}` that reference keys in the GeoJSON `properties` object.

**Location**: `pages/cri.py` (Line 38)
```python
tooltip = {
    "html": "<b>{province_name_th}</b><br/>Value: {display_value}",
    "style": {"backgroundColor": "steelblue", "color": "white"}
}
```
*   `{province_name_th}`: Drawn from GeoJSON properties.
*   `{display_value}`: Pre-formatted string value from Stage 1 JSON.

### 🎨 Legend / Colorbar
The legend is manually constructed using HTML/CSS to ensure it fits the "Single-View" design.

**Location**: `pages/cri.py` (Line 44: `colorbar_html`)
*   It uses `summary['legend_min']`, `summary['unit_label']`, and `summary['legend_max']`.

---

## 4. Property Mapping (GeoJSON)

If you need to change **which keys** are available to the Tooltips or Tables, look at the GeoJSON builders in the runtime.

**Locations**:
*   **Province Level**: `runtime/data.py` (Line 66: `build_province_geojson`)
*   **Tambon Level**: `runtime/data.py` (Line 144: `tambon_geojson_for_province`)

**Key Property Keys**:
*   `province_name_th` / `subdistrict_name_th`: Localized names.
*   `display_value`: The value formatted as a string (handling decimals).
*   `value`: The raw numerical value (used for color scaling).

---

## 5. Navigation Checklist for "Fixing Texts"

1.  **Metric Name in Dropdown?** -> Check `pages/*.py` in `metric_options`.
2.  **Chart Title/Caption?** -> Check `pages/*.py` inside `render_metric_card`.
3.  **Tooltip Content?** -> Check `pages/*.py` in `tooltip` variable.
4.  **Table Headers?** -> Check `runtime/data.py` in `ranking_rows` or `tambon_rank_rows`.
5.  **Units in Legend?** -> Check `pages/*.py` in `colorbar_html`.

# CRI Impact Dashboard V4.3

This is the standalone production deployment repository for the Climate Resilience Index (CRI) Impact Dashboard, serving pre-computed Stage 1 analytical data to visualize climate risks, economic loss, and health impacts across Thailand.

---

## 🚀 Release V4.3 Summary: Core Pipeline & Exporter Fixes

Release **v4.3** implements the core architectural fixes and feature specifications defined in the [v4.3 Requirements Specification Document](file:///C:/Users/sitth/OracleWorkspace/Arun_Creagy/ψ/incubate/DCCE/CRI/data_system/artifacts/analysis/2026-07-30_v4.3-cri-pipeline-and-exporter-requirements.md):

* **REQ-1: Full Medallion Rebuild & Comma String Sanitization**:
  Fixed a silent data loss bug in numeric parsing where formatted comma strings (e.g. `"1,422"`) were coerced to `NaN` 0.0. Rebuilt all Silver & Gold DDPM impact facts using `parse_clean_numeric()`, recovering **1,100,814 affected households** nationwide (including restoring 123,849 flood households in Nakhon Si Thammarat).

* **REQ-2: Canonical Multi-Year Baseline Window Standard (`2561–2567`)**:
  Officially deprecated legacy 8-year export folders (`period_2560_2567`) and locked **`period_2561_2567`** (7-year baseline window) as the sole canonical multi-year window alongside single-year **`period_2567`**.

* **REQ-3: Unified Export Payload Contract**:
  Standardized JSON export payloads across all UI metric cards to include explicit `raw_value`, `normalized_score`, `display_value`, `rank_desc`, and `unit_metadata`.

* **REQ-4: Standalone Heatwave Casualty Score & DOH Attribution**:
  Added a standalone equal-weighted MinMax score ($50\%\text{ Deaths} + 50\%\text{ Injuries}$) under **Department of Health (DOH / กรมอนามัย)** attribution. Standardized UI tab title to **"Heat Casualties"** and selector metric to **"Heat Casualty Score"**.

---

## 📜 Version History & Cumulative Changelog

### V4.2 Data & UI Upgrade
1. **Household-data normalization**: Annual population and household registrations are consolidated to unique subdistrict-year records before impact data joins.
2. **Exporter join guardrail**: Household values are pre-aggregated by subdistrict and year, preventing accidental join fan-out.
3. **Normalized CRI components**: The six province component metrics display min-max normalized values on the `Score [0-1]` scale.
4. **Tambon population rates**: Tambon views include deaths and affected-people rates per 100,000 population.

### V4.1 Refinements: Cold Spell Exclusion & Metadata Cleanups
1. **Cold Spell Exclusion**: Excluded Cold Spell (ภัยหนาว) from the hazard disaggregation options and all cumulative climate calculations, updating overall averages (`ALL` hazard) to represent the sum of Flood, Drought, Windstorm, and Landslide.
2. **Data Owner Registry**: Corrected Department of Health (DOH) attribution for heatwave statistics and MOF CGD/DDPM for government advance payment relief.

### V4.0 Feature Additions: Hazard Disaggregation
1. **Hazard Selector Dimension**: Added interactive selector dropdowns across CRI province metrics and Tambon-level human impact pages, supporting Flood (อุทกภัย), Drought (ภัยแล้ง), Windstorm (วาตภัย), Landslide (ดินโคลนถล่ม), and All Climate Hazards (รวมทุกภัย).
2. **Disaggregated Spatial Caching**: Custom `hazard_key` support across `load_metric` caching layers.
3. **Adoption of Nested Data Structure**: Swapped old flat JSON outputs with nested hazard-specific subdirectories under `period_2561_2567/` and `period_2567/`.

### V3.1 Optimizations
1. **Payload Reduction**: Heavy geospatial boundaries downsampled by ~90% (from 32MB to 2.5MB) to eliminate websocket serialization latency.
2. **Aggressive Caching**: Native `st.cache_data` implemented across data loading and geometry-building pipelines.
3. **Standalone Architecture**: Relies entirely on static pre-exported JSON assets located in the `data/` directory.

---

## 🏃 Running Locally

Ensure you have Python 3.9+ installed.

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Launch Streamlit:
   ```bash
   streamlit run app.py
   ```

---

## ☁️ Deployment

This repository is pre-configured for instant deployment on Streamlit Cloud. Connect the repository and set the main file path to `app.py`.

---

## 📁 Data Assets Structure
All app assets are self-contained inside `data/`:
* `/data/manifest.json`: Root metadata, period, and hazard definitions.
* `/data/spatial/`: Geospatial boundary overlays.
* `/data/period_2561_2567/[hazard_key]/`: Pre-calculated metrics for the 7-year baseline window (2561–2567).
* `/data/period_2567/[hazard_key]/`: Pre-calculated metrics for the single-year 2567 scope.

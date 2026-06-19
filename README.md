# CRI Impact Dashboard V4.0

This is the standalone deployment bundle for the Climate Resilience Index (CRI) Impact Dashboard. It serves pre-computed Stage 1 analytical data to visualize climate risks, economic loss, and health impacts across Thailand.

## V4.0 Feature Additions: Hazard Disaggregation
This version expands dashboard capability to support hazard-specific views:

1. **Hazard Selector Dimension**: Added interactive selector dropdowns across the CRI province metrics and Tambon-level human impact pages, supporting Flood (อุทกภัย), Drought (ภัยแล้ง), Windstorm (วาตภัย), Cold Spell (ภัยหนาว), Landslide (ดินโคลนถล่ม), and All Climate Hazards (รวมทุกภัย).
2. **Disaggregated Spatial Caching**: Custom `hazard_key` support across `load_metric` caching layers.
3. **Adoption of Nested Data Structure**: Swapped old flat JSON outputs with nested hazard-specific subdirectories under `period_2560_2567/` and `period_2567/`.

## V3.1 Optimizations
This version introduces a hardened, high-performance architecture optimized for serverless cloud deployment (e.g., Streamlit Cloud):

1. **Payload Reduction**: Heavy geospatial boundaries have been aggressively downsampled, reducing the national map payload by ~90% (from 32MB to 2.5MB) to eliminate websocket serialization latency.
2. **Aggressive Caching**: Native `st.cache_data` is implemented across the data loading and geometry-building pipeline. Maps are pre-computed in memory, enabling near-instant metric switching.
3. **Standalone Architecture**: All runtime geospatial dependencies (`geopandas`, `fiona`, `GDAL`) have been stripped out. The app relies entirely on static, pre-exported JSON assets located in the `data/` directory.

## Running Locally

Ensure you have Python 3.9+ installed.

1. Install the lightweight requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## Deployment
This repository is pre-configured for instant deployment on Streamlit Cloud. Simply connect the repository and point the main file path to `app.py`. No additional APT packages or heavy spatial libraries are required.

## Data Structure
The `data/` directory is self-contained:
* `/data/manifest.json`: Root metadata, period, and hazard definitions.
* `/data/spatial/`: Contains the optimized `_simple.geojson` boundary files.
* `/data/period_*/[hazard_key]/`: Contains the pre-calculated metrics for each temporal slice and selected hazard.

"""Heat Mortality page."""
from __future__ import annotations

import streamlit as st
import pydeck as pdk

from components.period_controls import PeriodOption, render_period_choice
from runtime import data


def render() -> None:
    st.header("Heat-Related Mortality & Impact")
    
    # 1. Setup Columns
    col_ctrl, col_map = st.columns([1, 2])

    with col_ctrl:
        # Time Period
        period_options = [
            PeriodOption("period_2560_2567", "2560-2567 Average"),
            PeriodOption("period_2567", "2567 Only"),
        ]
        period_key = render_period_choice(control_key="heat", options=period_options, default_key="period_2560_2567")

        # Metric Selector
        metric_options = {
            "Heat-Related Deaths": "heat_deaths",
            "Heat-Related Injuries": "heat_injured",
        }
        selected_label = st.selectbox("Metric Selector", options=list(metric_options.keys()), key="heat_metric_selector")
        selected_metric = metric_options[selected_label]

        # Load Data for Ranking
        dataset = data.load_metric(selected_metric, period_key)
        rank_rows = data.ranking_rows(dataset)
        summary = data.metric_summary(dataset)

        st.markdown(f"**Ranking: {summary['metric_label']}**")
        st.caption(f"{summary['unit_label']}")
        st.table(rank_rows)

        # Download button for all 77 provinces
        records = dataset.get("records", [])
        import pandas as pd
        df_all = pd.DataFrame(records)
        if not df_all.empty:
            cols_to_keep = []
            rename_map = {}
            if "rank_desc" in df_all.columns:
                cols_to_keep.append("rank_desc")
                rename_map["rank_desc"] = "Rank"
            if "province_code" in df_all.columns:
                cols_to_keep.append("province_code")
                rename_map["province_code"] = "Province Code"
            if "province_name_th" in df_all.columns:
                cols_to_keep.append("province_name_th")
                rename_map["province_name_th"] = "Province Name (Thai)"
            if "province_name_en" in df_all.columns:
                cols_to_keep.append("province_name_en")
                rename_map["province_name_en"] = "Province Name (English)"
            if "display_value" in df_all.columns:
                cols_to_keep.append("display_value")
                rename_map["display_value"] = "Value"
            elif "value" in df_all.columns:
                cols_to_keep.append("value")
                rename_map["value"] = "Value"
                
            df_export = df_all[cols_to_keep].rename(columns=rename_map)
            df_export = df_export.sort_values(by="Rank").reset_index(drop=True)
            csv_data = df_export.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="Download All 77 Provinces CSV",
                data=csv_data,
                file_name=f"all_provinces_heat_{selected_metric}_{period_key}.csv",
                mime="text/csv",
                key="heat_download_button",
            )

    with col_map:
        # Map and Vertical Colorbar
        dataset = data.load_metric(selected_metric, period_key)
        summary = data.metric_summary(dataset)
        geojson = data.build_province_geojson(dataset)

        st.markdown(f'<div class="cri-section-title" style="margin-bottom:0px;">{summary["metric_label"]}</div>', unsafe_allow_html=True)
        st.caption(f"{summary['period_label']}")

        # Nested columns for Map + Vertical Legend
        col_map_inner, col_legend = st.columns([0.92, 0.08])

        with col_map_inner:
            view_state = pdk.ViewState(latitude=13.7367, longitude=100.5231, zoom=5, pitch=0)
            layer = pdk.Layer(
                "GeoJsonLayer",
                geojson,
                pickable=True,
                opacity=1.0,
                stroked=True,
                filled=True,
                get_fill_color="properties.fill_color",
                get_line_color="properties.line_color",
                line_width_min_pixels=1,
            )
            tooltip = {
                "html": "<b>{province_name_th}</b><br/>Value: {display_value}",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }
            st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip, map_style="light"))

        with col_legend:
            # Vertical Colorbar
            gradient = "linear-gradient(to bottom, rgba(200,0,0,1.0), rgba(255,255,255,1.0))"
            st.markdown(
                f"""
                <div style="display: flex; flex-direction: column; align-items: center; height: 400px; padding-top: 40px;">
                    <div style="font-size: 0.7rem; margin-bottom: 4px;">{summary['legend_max']}</div>
                    <div style="flex-grow: 1; width: 12px; background: {gradient}; border-radius: 6px; border: 1px solid #ddd;"></div>
                    <div style="font-size: 0.7rem; margin-top: 4px;">{summary['legend_min']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

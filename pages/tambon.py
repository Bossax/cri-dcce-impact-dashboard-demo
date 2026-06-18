"""Tambon-Level Human Impact page."""
from __future__ import annotations

import streamlit as st
import pydeck as pdk

from components.period_controls import PeriodOption, render_period_choice
from runtime import data


def render() -> None:
    st.header("Tambon-Level Human Impact")
    
    # 1. Setup Columns
    col_ctrl, col_map = st.columns([1, 2])

    with col_ctrl:
        # Time Period
        period_options = [
            PeriodOption("period_2560_2567", "2560-2567 Average"),
            PeriodOption("period_2567", "2567 Only"),
        ]
        period_key = render_period_choice(control_key="tambon", options=period_options, default_key="period_2560_2567")

        # Metric Selector
        metric_options = {
            "Tambon Deaths": "tambon_deaths",
            "Tambon Affected Households": "tambon_affected_households",
        }
        selected_metric_label = st.selectbox("Metric Selector", options=list(metric_options.keys()), key="tambon_metric_selector")
        selected_metric = metric_options[selected_metric_label]

        # Province Selector
        base_dataset = data.load_metric(selected_metric, period_key)
        province_options = data.tambon_province_options(base_dataset)
        selected_province = st.selectbox(
            "Select Province to Zoom",
            options=province_options,
            format_func=lambda x: x["province_name_th"],
            key="tambon_province_selector"
        )

        if not selected_province:
            st.info("Please select a province to view tambon-level data.")
            return

        province_code = selected_province["province_code"]

        # Load Data for Ranking
        dataset = data.load_metric(selected_metric, period_key)
        summary = data.metric_summary(dataset)
        rank_rows = data.tambon_rank_rows(dataset, province_code)

        st.markdown(f"**Ranking: {summary['metric_label']}**")
        st.caption(f"{selected_province['province_name_th']} | {summary['unit_label']}")
        st.table(rank_rows)

    with col_map:
        # Map and Vertical Colorbar
        geojson = data.tambon_geojson_for_province_cached(selected_metric, period_key, province_code)
        
        # Calculate Local Maximum for the selected province
        local_max = 0.0
        for row in rank_rows:
            try:
                val = float(row.get("value", 0))
                if val > local_max:
                    local_max = val
            except (ValueError, TypeError):
                pass
        
        display_max = f"{local_max:,.1f}" if local_max % 1 != 0 else f"{int(local_max):,}"
        if local_max == 0:
             display_max = "0"

        st.markdown(f'<div class="cri-section-title" style="margin-bottom:0px;">{summary["metric_label"]}</div>', unsafe_allow_html=True)
        st.caption(f"{summary['period_label']}")

        # Nested columns for Map + Vertical Legend
        col_map_inner, col_legend = st.columns([0.92, 0.08])

        with col_map_inner:
            view_state = pdk.ViewState(latitude=13.7367, longitude=100.5231, zoom=7, pitch=0)
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
                "html": "<b>{subdistrict_name_th}</b><br/>{district_name_th}, {province_name_th}<br/>Value: {display_value}",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }
            st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip, map_style="light"))

        with col_legend:
            # Vertical Colorbar
            st.markdown(
                f"""
                <div style="display: flex; flex-direction: column; align-items: center; height: 400px; padding-top: 40px;">
                    <div style="font-size: 0.7rem; margin-bottom: 4px;">{display_max}</div>
                    <div style="flex-grow: 1; width: 12px; background: linear-gradient(to bottom, rgba(200,0,0,1.0), rgba(255,255,255,1.0)); border-radius: 6px; border: 1px solid #ddd;"></div>
                    <div style="font-size: 0.7rem; margin-top: 4px;">0</div>
                </div>
                """,
                unsafe_allow_html=True
            )

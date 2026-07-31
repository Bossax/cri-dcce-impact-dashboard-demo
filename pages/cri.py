"""CRI Province-level page."""
from __future__ import annotations

import streamlit as st
import pydeck as pdk

from components.period_controls import PeriodOption, render_period_choice
from runtime import data


def render() -> None:
    st.header("ผลกระทบระดับจังหวัด (CRI Impact Index)")
    
    # 1. Setup Columns
    col_ctrl, col_map = st.columns([1, 2])

    with col_ctrl:
        # Time Period
        period_options = [
            PeriodOption("period_2561_2567", "ค่าเฉลี่ยปี 2561–2567"),
            PeriodOption("period_2567", "เฉพาะปี 2567"),
        ]
        period_key = render_period_choice(control_key="cri", options=period_options, default_key="period_2561_2567")

        # Hazard Selector
        hazard_options = data.available_hazard_options()
        selected_hazard = st.selectbox(
            "เลือกประเภทภัยพิบัติ",
            options=hazard_options,
            format_func=lambda x: x["hazard_label"],
            key="cri_hazard_selector"
        )
        hazard_key = selected_hazard["hazard_key"]

        # Metric Selector (Filtered dynamically by hazard capability)
        metric_options = {}
        # Only complete hazards have CRI score
        if hazard_key not in ["landslide", "wildfire", "cold_spell"]:
            metric_options["คะแนน CRI ภาพรวม"] = "cri_score"
            
        metric_options.update({
            "จำนวนผู้เสียชีวิต (คะแนน)": "deaths_abs",
            "อัตราการเสียชีวิต (คะแนน)": "deaths_rate",
            "จำนวนผู้ได้รับผลกระทบ (คะแนน)": "affected_ppl_abs",
            "อัตราส่วนผู้ได้รับผลกระทบ (คะแนน)": "affected_ppl_rate",
            "มูลค่าเงินเยียวยา (คะแนน)": "loss_abs",
            "มูลค่าเงินเยียวยาต่อ GPP (คะแนน)": "loss_per_gpp",
        })
        
        selected_label = st.selectbox("เลือกตัวชี้วัด", options=list(metric_options.keys()), key="cri_metric_selector")
        selected_metric = metric_options[selected_label]

        # Check constraints
        data_available = True
        warning_msg = ""
        warning_type = ""
        
        if hazard_key == "wildfire" and period_key == "period_2561_2567":
            data_available = False
            warning_msg = "ไม่มีข้อมูลค่าเฉลี่ยสะสมระยะยาวสำหรับไฟป่า กรุณาเลือก 'เฉพาะปี 2567'"
            warning_type = "warning"
        elif (hazard_key in ["landslide", "wildfire", "cold_spell"]) and (selected_metric in ["loss_abs", "loss_per_gpp"]):
            data_available = False
            warning_msg = f"ไม่มีการลงบันทึกข้อมูลความเสียหายทางเศรษฐกิจสำหรับภัย{selected_hazard['hazard_label']}"
            warning_type = "info"

        if data_available:
            # Load Data for Ranking
            dataset = data.load_metric(selected_metric, period_key, hazard_key)
            rank_rows = data.ranking_rows(dataset, use_score=True)
            summary = data.metric_summary(dataset, use_score=True)

            st.markdown(f"**การจัดอันดับ: {summary['metric_label']}**")
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
                    label="ดาวน์โหลดข้อมูล 77 จังหวัด (CSV)",
                    data=csv_data,
                    file_name=f"all_provinces_{selected_metric}_{period_key}_{hazard_key}.csv",
                    mime="text/csv",
                    key="cri_download_button",
                )
        else:
            if warning_type == "warning":
                st.warning(warning_msg)
            else:
                st.info(warning_msg)

    with col_map:
        if data_available:
            # Map and Vertical Colorbar
            summary = data.metric_summary(dataset, use_score=True)
            geojson = data.build_province_geojson_cached(selected_metric, period_key, hazard_key, use_score=True)

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
                scheme = summary.get("legend_scheme", "OrRd")
                if scheme == "GnBu":
                    gradient = "linear-gradient(to bottom, rgba(0,0,200,1.0), rgba(255,255,255,1.0))"
                else:
                    gradient = "linear-gradient(to bottom, rgba(200,0,0,1.0), rgba(255,255,255,1.0))"
                    
                st.markdown(
                    f"""
                    <div style="display: flex; flex-direction: column; align-items: center; height: 450px; padding-top: 20px;">
                        <div style="writing-mode: vertical-rl; text-orientation: mixed; font-size: 0.75rem; font-weight: 600; color: #555; margin-bottom: 10px; transform: rotate(180deg);">{summary['unit_label']}</div>
                        <div style="font-size: 0.7rem; margin-bottom: 4px; font-weight: bold;">{summary['legend_max']}</div>
                        <div style="flex-grow: 1; width: 14px; background: {gradient}; border-radius: 7px; border: 1px solid #ddd; box-shadow: inset 0 0 4px rgba(0,0,0,0.1);"></div>
                        <div style="font-size: 0.7rem; margin-top: 4px; font-weight: bold;">{summary['legend_min']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No map data available for the selected configuration.")

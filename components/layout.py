"""Layout primitives for the v3 app."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import pydeck as pdk
import streamlit as st


@dataclass(frozen=True)
class MapPanel:
    title: str
    body: str
    deck: pdk.Deck


def render_panel(panel: MapPanel) -> None:
    st.markdown(
        f"""
        <div class="cri-card">
          <div class="cri-section-title">{panel.title}</div>
          <div class="cri-muted">{panel.body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.pydeck_chart(panel.deck, use_container_width=True)


def render_map_row(panels: Sequence[MapPanel]) -> None:
    if not panels:
        return
    if len(panels) == 1:
        left, right = st.columns([1, 1], gap="large")
        with left:
            render_panel(panels[0])
        with right:
            st.empty()
        return
    left, right = st.columns(2, gap="large")
    with left:
        render_panel(panels[0])
    with right:
        render_panel(panels[1])


def make_deck(geojson: dict[str, object], *, center_lat: float = 13.5, center_lon: float = 101.0, zoom: float = 5.2) -> pdk.Deck:
    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson,
        stroked=True,
        filled=True,
        pickable=True,
        opacity=0.75,
        get_fill_color="properties.fill_color",
        get_line_color="properties.line_color",
        line_width_min_pixels=1,
    )
    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=zoom, pitch=0)
    return pdk.Deck(layers=[layer], initial_view_state=view_state, map_style=None, tooltip={"text": "{province_name_th}\n{display_value}"})


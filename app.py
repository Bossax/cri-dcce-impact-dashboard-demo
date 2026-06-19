"""CRI Impact App v3."""
from __future__ import annotations

import streamlit as st

from pages import cri, heat, methodology, tambon


def _apply_global_style() -> None:
    st.markdown(
        """
        <style>
          .block-container { padding-top: 1.25rem; padding-bottom: 2rem; }
          .cri-card {
            border: 1px solid rgba(49, 51, 63, 0.14);
            border-radius: 16px;
            padding: 1rem 1rem 0.75rem 1rem;
            background: rgba(255, 255, 255, 0.65);
          }
          .cri-section-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0 0 0.35rem 0;
          }
          .cri-muted {
            color: rgba(49, 51, 63, 0.76);
          }
          /* Hide Sidebar completely */
          [data-testid="collapsedControl"] { display: none; }
          section[data-testid="stSidebar"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="CRI Impact Index", page_icon="🌏", layout="wide", initial_sidebar_state="collapsed")
    _apply_global_style()

    st.title("CRI Impact Index")
    st.caption("v4.0 | Explore climate-impact patterns across provinces and tambons.")

    tabs = st.tabs([
        "Methodology",
        "CRI",
        "Tambon-Level Human Impact",
        "Heat Mortality",
    ])

    with tabs[0]:
        methodology.render()
    with tabs[1]:
        cri.render()
    with tabs[2]:
        tambon.render()
    with tabs[3]:
        heat.render()


if __name__ == "__main__":
    main()


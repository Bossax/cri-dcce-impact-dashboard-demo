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
          [data-testid="collapsedControl"] { display: none !important; }
          section[data-testid="stSidebar"] { display: none !important; width: 0px !important; }
          div[data-testid="stSidebarUserContent"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="ดัชนีผลกระทบจากความเสี่ยงจากภูมิอากาศ (CRI Impact Index)", page_icon="🌏", layout="wide", initial_sidebar_state="collapsed")
    _apply_global_style()

    st.title("Thailand Climate Risk Index (CRI)")
    st.caption("v4.4 | 31 July 2026")

    tabs = st.tabs([
        "ระเบียบวิธี (Methodology)",
        "ดัชนี CRI ระดับจังหวัด (Province-Level CRI)",
        "ผลกระทบต่อมนุษย์ระดับตำบล (Tambon Human Impact)",
        "ผลกระทบจากความร้อน (Heat Casualties)",
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


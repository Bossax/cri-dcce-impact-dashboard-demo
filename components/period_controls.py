"""Period controls bound to Stage 1 export keys."""
from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class PeriodOption:
    key: str
    label: str


def render_period_choice(*, control_key: str, options: list[PeriodOption], default_key: str) -> str:
    labels = [item.label for item in options]
    keys = [item.key for item in options]
    index = keys.index(default_key) if default_key in keys else 0
    selected_label = st.radio(
        "Time period",
        labels,
        index=index,
        horizontal=True,
        key=f"period_{control_key}",
    )
    return keys[labels.index(selected_label)]


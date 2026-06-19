"""Methodology page."""
from __future__ import annotations

import streamlit as st


def render() -> None:
    st.header("Methodology & Data Guidance")
    
    tab1, tab2 = st.tabs(["Overview", "Calculation Framework"])

    with tab1:
        st.markdown(
            """
            ### 1. What the CRI Impact Index is
            The Climate Resilience Index (CRI) Impact Index is a spatial composite indicator designed to measure the direct human and economic impacts of climate-related disasters across Thailand. Unlike traditional hazard maps, this index focuses on the *realized* consequences—lives lost, households affected, and economic disruptions—anchoring abstract climate risks in empirical evidence.

            ### 2. What the indicators measure
            - **Human Impact**: Realized mortality (absolute and per capita) and household displacement due to extreme weather events.
            - **Economic Impact**: Direct financial losses compared to the Gross Provincial Product (GPP), representing the local economy's sensitivity to shocks.
            - **Heat Impact**: Heat-related injuries and fatalities recorded by public health systems.

            ### 3. What data sources are used
            The system integrates several high-fidelity datasets:
            - **Disaster Impact**: Standardized village-level reports from the Department of Disaster Prevention and Mitigation (**DDPM**).
            - **Demographics**: Official registration statistics for Population and Households from the Department of Provincial Administration (**DOPA**). 
            - **Economic Metrics**: Gross Provincial Product (GPP) from the **NESDC** and disaster-related financial relief from **Government Advance Payments**.
            - **Public Health**: Heat-related mortality and injury data from the **Ministry of Public Health**.

            ### 4. Why "Affected Households" instead of "Affected People"?
            In the DDPM reporting system, headcount data (Affected People) is often under-reported or left as zero. Our analysis shows that **Affected Households** has **2.5x more data points** than headcount metrics, as it is the primary unit used for disaster compensation and official government relief. Using households provides a more robust and consistent proxy for social disruption across all provinces.

            ### 5. What the time-period selector means
            - **2560-2567 Average**: Represents the 8-year cumulative average, highlighting persistent "hotspots" where impacts are chronic.
            - **2567 Only**: Focuses on the most recent full calendar year to illustrate current trends and immediate shifts in impact patterns.

            ### 6. Known limitations
            - **Affected Rate Interpretation**: The "Affected Rate" represents *incidents per 100 households*. Because a single household can be hit by multiple independent disasters in one year, this rate can mathematically exceed 100%.
            - **Economic Metrics**: The primary economic proxy is **Government Advance Payment** (เงินทดรองราชการ) for relief, measured in **THB**. This represents the direct fiscal cost of recovery. **Loss per GPP** is calculated as a **Percentage Point (%)** of the Gross Provincial Product (GPP), where GPP is denominated in **Million THB**. It is important to note that these figures represent government advance payments accounted for by DDPM from various sources of advance payment made by line agencies to recover and relief disaster in provinces.
            - **Government Relief Caps**: These emergency funds may hit administrative ceilings (e.g., 20M THB/event), potentially understating absolute total damage but providing a reliable indicator of provincial fiscal stress.

            ### 7. Data Lineage & Metadata
            | Dataset | Source Agency | Detail |
            | :--- | :--- | :--- |
            | **Human Impact** | DDPM | Standardized village reports |
            | **Population** | DOPA | Annual registration statistics|
            | **Households** | DOPA | Annual registration statistics|
            | **GPP** | NESDC | Current market prices (Million THB)|
            | **Economic Relief**| DDPM | Government advance payments (THB) |
            | **Heat Impact** | MOPH | Clinical cases of heat-related injuries/deaths |
            """
        )

    with tab2:
        st.markdown("### Calculation Methodology")
        st.markdown(
            """
            The CRI score utilizes **Min-Max Normalization** to scale data between 0 and 1. The province with the highest impact receives a score of 1.0, and the province with the lowest impact receives 0. The final CRI Score is the sum of 6 weighted indicators.
            """
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### A. Human Impact (50% Weight)")
            st.latex(r"S_1 = \text{Norm}(\text{Deaths}) \times 0.075")
            st.latex(r"S_2 = \text{Norm}(\text{DeathRate}) \times 0.225")
            st.latex(r"S_3 = \text{Norm}(\text{AffHH}) \times 0.050")
            st.latex(r"S_4 = \text{Norm}(\text{AffRate}) \times 0.150")

        with col2:
            st.markdown("#### B. Economic Impact (50% Weight)")
            st.latex(r"S_5 = \text{Norm}(\text{Relief}) \times 0.125")
            st.latex(r"S_6 = \text{Norm}(\text{Relief\_GPP\_Ratio}) \times 0.375")

        st.markdown("#### Total CRI Score")
        st.latex(r"CRI = \sum_{i=1}^{6} S_i")

        st.markdown("---")
        st.markdown("#### Indicators and Weighting Table")
        st.markdown(
            """
            | Component | Indicator | Variable Code | Weight | Unit |
            | :--- | :--- | :--- | :--- | :--- |
            | **Human Impact** | Total Deaths | `deaths_abs` | 7.5% | Annual deaths |
            | (50%) | Death Rate | `deaths_rate` | 22.5% | Per 100k pop |
            | | Total Affected HH | `affected_hh_abs` | 5.0% | Annual households |
            | | Affected Rate | `affected_rate` | 15.0% | Per 100 HH |
            | **Economic Impact** | Govt Advance Payment | `loss_abs` | 12.5% | THB |
            | (50%) | Relief per Unit GPP | `loss_per_gpp` | 37.5% | Percentage Points (%) |
            """
        )


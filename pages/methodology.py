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

            ### 4. Conversion of Affected Households to Affected People
            In the raw DDPM reporting system, headcount data (Affected People) is often missing or under-reported. However, Affected Households data is robustly recorded as it is the primary administrative unit for disaster relief and compensation. 
            
            To estimate the number of **Affected People**, we calculate the average population per household ratio for each subdistrict (Tambon) using DOPA registry data. We then multiply the affected households by this ratio:
            - **Tambon Multiplier**: Calculated dynamically for each subdistrict and year.
            - **Province Fallback**: If subdistrict population or household statistics are missing, we fall back to the province's average household size.
            - **National Fallback**: If both are unavailable, we fall back to a default national average of 3.0 people per household.
            
            *Note on potential artifacts*: Because household sizes vary across different regions and years, applying this multiplier may introduce slight discrepancies compared to direct census counts. However, it ensures uniform human-scale comparison across different hazards.

            ### 5. Hazard Completeness and CRI Score Exclusion
            The composite Climate Resilience Index (CRI) score requires a complete set of 6 metrics (representing human and economic dimensions). 
            - **Complete Hazards**: *Flood, Drought, and Windstorm* are fully documented and integrated into the composite all-hazard CRI Score.
            - **Incomplete Hazards**: *Landslide, Wildfire, and Cold Spell* lack financial relief data. To prevent calculation skew, they do not have hazard-specific CRI Scores, and their values are omitted from the overall composite CRI calculation.

            ### 6. What the time-period selector means
            - **2560-2567 Average**: Represents the 8-year cumulative average, highlighting persistent "hotspots" where impacts are chronic.
            - **2567 Only**: Focuses on the most recent full calendar year to illustrate current trends and immediate shifts in impact patterns.
            
            ### 7. Known limitations
            - **Affected Rate Interpretation**: The "Affected Rate" represents *estimated affected people per 100,000 population*.
            - **Economic Metrics**: The primary economic proxy is **Government Advance Payment** (เงินทดรองราชการ) for relief, measured in **THB**. This represents the direct fiscal cost of recovery. **Loss per GPP** is calculated as a **Percentage Point (%)** of the Gross Provincial Product (GPP), where GPP is denominated in **Million THB**. It is important to note that these figures represent government advance payments accounted for by DDPM from various sources of advance payment made by line agencies to recover and relief disaster in provinces.
            - **Government Relief Caps**: These emergency funds may hit administrative ceilings (e.g., 20M THB/event), potentially understating absolute total damage but providing a reliable indicator of provincial fiscal stress.
 
            ### 8. Data Lineage & Metadata
            | Dataset | Source Agency | Detail |
            | :--- | :--- | :--- |
            | **Human Impact** | DDPM | Standardized village reports (Bronze: Open Data) |
            | **Population** | DOPA | Annual registration statistics (Silver: Annual) |
            | **Households** | DOPA | Annual registration statistics (Silver: Annual) |
            | **GPP** | NESDC | Current market prices (Million THB) (Silver: Annual) |
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
            st.latex(r"S_3 = \text{Norm}(\text{AffPpl}) \times 0.050")
            st.latex(r"S_4 = \text{Norm}(\text{AffPplRate}) \times 0.150")

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
            | | Total Affected People | `affected_ppl_abs` | 5.0% | Annual people (estimated) |
            | | Affected People Rate | `affected_ppl_rate` | 15.0% | Per 100k pop |
            | **Economic Impact** | Govt Advance Payment | `loss_abs` | 12.5% | THB |
            | (50%) | Relief per Unit GPP | `loss_per_gpp` | 37.5% | Percentage Points (%) |
            """
        )

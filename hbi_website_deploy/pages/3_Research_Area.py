"""Research Area — Members with a specific research area."""

import pandas as pd
import streamlit as st
from urllib.parse import unquote

from utils.data_loader import (
    load_members,
    load_positions,
    load_research_areas,
    build_directory_data,
)
from utils.components import (
    inject_custom_css,
    render_card_html,
    render_card_grid,
    render_list_row_html,
    render_list_view,
    UCALGARY_RED,
)

st.set_page_config(
    page_title="Research Area – HBI",
    page_icon="🧠",
    layout="wide",
)
inject_custom_css()

# ── Get area from query params ───────────────────────────────────────────────
area_param = st.query_params.get("area", "")
area = unquote(area_param) if area_param else ""

if not area:
    st.warning("No research area specified.")
    if st.button("← Back to Directory"):
        st.switch_page("Home.py")
    st.stop()

# ── Load data ────────────────────────────────────────────────────────────────
research_areas = load_research_areas()
directory = build_directory_data()

# Find members with this area (exact match)
matching_ids = set(
    research_areas[research_areas["area"] == area]["member_id"]
)
# Fallback: case-insensitive partial match
if not matching_ids:
    matching_ids = set(
        research_areas[
            research_areas["area"].str.lower().str.contains(area.lower(), na=False)
        ]["member_id"]
    )

filtered = (
    directory[directory["member_id"].isin(matching_ids)]
    .sort_values("name")
    .reset_index(drop=True)
)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="hbi-banner">'
    f'<h1>🔬 Research Area</h1>'
    f'<p style="font-size:1.4rem;font-weight:700;text-transform:capitalize;">{area}</p>'
    f'</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("← Back to Directory"):
        st.switch_page("Home.py")

st.markdown(f'<p style="font-size:1.15rem;">{len(filtered)} members with this research area</p>', unsafe_allow_html=True)

# ── View toggle ──────────────────────────────────────────────────────────────
view_mode = st.radio("View", ["Grid", "List"], horizontal=True, label_visibility="collapsed")

# ── Render members ───────────────────────────────────────────────────────────
if filtered.empty:
    st.info("No members found for this research area.")
else:
    if view_mode == "Grid":
        cards = []
        for _, row in filtered.iterrows():
            mid = row["member_id"]
            name = str(row["name"]) if pd.notna(row["name"]) else "Unknown"
            title = str(row["title"]) if pd.notna(row.get("title")) else ""
            dept = str(row["department"]) if pd.notna(row.get("department")) else ""
            areas = row.get("research_areas_list", [])
            if not isinstance(areas, list):
                areas = []
            cards.append(render_card_html(name, title, dept, areas, member_id=mid))
        st.markdown(render_card_grid(cards), unsafe_allow_html=True)
    else:
        rows = []
        for _, row in filtered.iterrows():
            mid = row["member_id"]
            name = str(row["name"]) if pd.notna(row["name"]) else "Unknown"
            title = str(row["title"]) if pd.notna(row.get("title")) else ""
            dept = str(row["department"]) if pd.notna(row.get("department")) else ""
            areas = row.get("research_areas_list", [])
            if not isinstance(areas, list):
                areas = []
            rows.append(render_list_row_html(name, title, dept, areas, member_id=mid))
        st.markdown(render_list_view(rows), unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Data sourced from UCalgary Profiles · Hotchkiss Brain Institute")

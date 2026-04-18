"""HBI Members Directory — Home / Directory Page."""

import streamlit as st
import pandas as pd

from utils.data_loader import (
    load_members,
    load_positions,
    load_research_areas,
    load_education,
    build_directory_data,
)
from utils.components import (
    inject_custom_css, render_card_html, render_card_grid,
    render_list_row_html, render_list_view,
)

# ── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="HBI Members Directory",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_custom_css()

# ── Cached data ──────────────────────────────────────────────────────────────
directory = build_directory_data()
members = load_members()
positions = load_positions()
research_areas = load_research_areas()
education = load_education()

# ── Header banner ────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hbi-banner">
        <h1>🧠 HBI Members Directory</h1>
        <p>Hotchkiss Brain Institute · University of Calgary</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar filters ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 HBI")
    st.markdown("---")

    search_query = st.text_input(
        "🔍 Search",
        placeholder="Name, keyword, research area…",
    )

    st.markdown("#### Filters")
    st.caption("ℹ️ Filters accept manual text input only at this time.")

    # HBI membership status filter
    hbi_statuses = sorted(directory["hbi_membership"].replace("", pd.NA).dropna().unique().tolist())
    sel_membership = st.selectbox(
        "HBI Membership Status",
        ["All"] + hbi_statuses,
        index=0,
    )

    filter_area = st.text_input("Research Area", placeholder="e.g. neuroscience")

    filter_dept = st.text_input("Department", placeholder="e.g. Pediatrics")

    filter_faculty = st.text_input("Faculty", placeholder="e.g. Cumming School")

    edu_years = education["year"].dropna()
    year_range = None
    if not edu_years.empty:
        yr_min_full, yr_max_full = int(edu_years.min()), int(edu_years.max())
        if yr_min_full < yr_max_full:
            year_range = st.slider(
                "Highest Degree Earned (Year)",
                yr_min_full,
                yr_max_full,
                (yr_min_full, yr_max_full),
            )

    st.markdown("---")
    if st.button("🔄 Reset All Filters", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ── Apply filters (AND across groups, OR within group) ───────────────────────
ids = set(members["member_id"])

if search_query:
    q = search_query.lower()
    name_hit = set(
        members[members["name"].str.lower().str.contains(q, na=False)]["member_id"]
    )
    area_hit = set(
        research_areas[
            research_areas["area"].str.lower().str.contains(q, na=False)
        ]["member_id"]
    )
    pos_hit = set(
        positions[
            positions["title"].str.lower().str.contains(q, na=False)
            | positions["department"].str.lower().str.contains(q, na=False)
        ]["member_id"]
    )
    ids &= name_hit | area_hit | pos_hit

if filter_area:
    fa = filter_area.lower()
    ids &= set(
        research_areas[
            research_areas["area"].str.lower().str.contains(fa, na=False)
        ]["member_id"]
    )

if sel_membership != "All":
    ids &= set(directory[directory["hbi_membership"] == sel_membership]["member_id"])

if filter_dept:
    fd = filter_dept.lower()
    ids &= set(
        positions[
            positions["department"].str.lower().str.contains(fd, na=False)
        ]["member_id"]
    )

if filter_faculty:
    ff = filter_faculty.lower()
    ids &= set(
        positions[
            positions["faculty"].str.lower().str.contains(ff, na=False)
        ]["member_id"]
    )

if year_range:
    yr_lo, yr_hi = year_range
    if (yr_lo, yr_hi) != (yr_min_full, yr_max_full):
        # Rank degrees: highest level per member only
        _DEGREE_RANK = {
            "phd": 5, "ph.d": 5, "doctor of philosophy": 5, "d.phil": 5,
            "md": 4, "m.d": 4, "d.v.m": 4,
            "msc": 3, "m.sc": 3, "master of science": 3,
            "ma": 3, "m.a": 3, "master of arts": 3, "meng": 3,
            "bsc": 2, "b.sc": 2, "b.sc.": 2, "bsc.": 2,
            "bachelor of science": 2,
            "ba": 2, "b.a": 2, "bachelor of arts": 2,
            "beng": 2, "b.eng": 2,
        }
        _edu = education.dropna(subset=["year"]).copy()
        _edu["_rank"] = _edu["degree"].str.lower().str.strip().map(_DEGREE_RANK).fillna(0)
        _top = _edu.sort_values("_rank", ascending=False).drop_duplicates("member_id", keep="first")
        ids &= set(
            _top[(_top["year"] >= yr_lo) & (_top["year"] <= yr_hi)]["member_id"]
        )

filtered = (
    directory[directory["member_id"].isin(ids)]
    .sort_values("name")
    .reset_index(drop=True)
)

# ── Results count + view toggle + per-page selector ─────────────────────────
rcount_col, toggle_col, perpage_col = st.columns([3, 1, 1])
with rcount_col:
    st.markdown(f"Showing **{len(filtered)}** of **{len(members)}** members")
with toggle_col:
    st.markdown("**View mode**")
    view_mode = st.selectbox(
        "View mode", ["Grid", "List"], index=0, label_visibility="collapsed"
    )
with perpage_col:
    st.markdown("**Profiles per Page**")
    per_page_options = ["25", "50", "100", "All"]
    per_page_choice = st.selectbox("Profiles per Page", per_page_options, index=0, label_visibility="collapsed")

# ── Export button (sidebar, after filters applied) ───────────────────────────
with st.sidebar:
    if not filtered.empty:
        export = filtered[["name", "title", "department", "faculty", "profile_url"]].copy()
        export.columns = ["Name", "Primary Position", "Department", "Faculty", "Profile URL"]
        export["Research Areas"] = filtered["research_areas_list"].apply(
            lambda x: "; ".join(str(a) for a in x) if isinstance(x, list) else ""
        )
        st.download_button(
            "📥 Download Filtered Results",
            export.to_csv(index=False),
            "hbi_members_filtered.csv",
            "text/csv",
            use_container_width=True,
        )

# ── Pagination setup ────────────────────────────────────────────────────────
PER_PAGE = len(filtered) if per_page_choice == "All" else int(per_page_choice)
total_pages = max(1, -(-len(filtered) // PER_PAGE)) if PER_PAGE > 0 else 1

# Auto-reset page when filter state changes
_fhash = hash(
    (
        search_query,
        filter_area,
        sel_membership,
        filter_dept,
        filter_faculty,
        str(year_range),
        per_page_choice,
    )
)
if st.session_state.get("_fh") != _fhash:
    st.session_state["dir_page"] = 0
    st.session_state["_fh"] = _fhash

page = max(0, min(st.session_state.get("dir_page", 0), total_pages - 1))
start_idx = page * PER_PAGE
page_data = filtered.iloc[start_idx : start_idx + PER_PAGE]

# ── Member card grid / list ───────────────────────────────────────────────────
if page_data.empty:
    st.info("No members match your current filters. Try broadening your search.")
else:
    if view_mode == "Grid":
        cards = []
        for _, row in page_data.iterrows():
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
        for _, row in page_data.iterrows():
            mid = row["member_id"]
            name = str(row["name"]) if pd.notna(row["name"]) else "Unknown"
            title = str(row["title"]) if pd.notna(row.get("title")) else ""
            dept = str(row["department"]) if pd.notna(row.get("department")) else ""
            areas = row.get("research_areas_list", [])
            if not isinstance(areas, list):
                areas = []
            rows.append(render_list_row_html(name, title, dept, areas, member_id=mid))
        st.markdown(render_list_view(rows), unsafe_allow_html=True)

    # ── Pagination controls ──────────────────────────────────────────────────
    st.markdown("")
    c1, c2, c3, c4, c5 = st.columns([1, 1, 2, 1, 1])
    with c1:
        if st.button("⏮ First", disabled=page == 0, key="pg_first"):
            st.session_state["dir_page"] = 0
            st.rerun()
    with c2:
        if st.button("◀ Prev", disabled=page == 0, key="pg_prev"):
            st.session_state["dir_page"] = page - 1
            st.rerun()
    with c3:
        st.markdown(
            f"<div style='text-align:center;padding:8px 0;'>"
            f"Page <b>{page + 1}</b> of <b>{total_pages}</b></div>",
            unsafe_allow_html=True,
        )
    with c4:
        if st.button("Next ▶", disabled=page >= total_pages - 1, key="pg_next"):
            st.session_state["dir_page"] = page + 1
            st.rerun()
    with c5:
        if st.button("Last ⏭", disabled=page >= total_pages - 1, key="pg_last"):
            st.session_state["dir_page"] = total_pages - 1
            st.rerun()

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Data sourced from UCalgary Profiles · Hotchkiss Brain Institute")

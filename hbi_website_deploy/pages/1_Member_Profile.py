"""HBI Member Profile — Individual profile view."""

import html as html_mod

import pandas as pd
import streamlit as st

from utils.data_loader import (
    load_members,
    load_positions,
    load_research_areas,
    load_education,
    load_publications,
    load_activities,
    load_contact_info,
    load_news,
)
from utils.components import (
    inject_custom_css,
    render_avatar_html,
    render_research_tags,
    section_header,
    UCALGARY_RED,
)

_esc = lambda s: html_mod.escape(str(s)) if s else ""

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Member Profile – HBI", page_icon="🧠", layout="wide")
inject_custom_css()

# ── Resolve member ID ────────────────────────────────────────────────────────
member_id = st.session_state.get("selected_member") or st.query_params.get("id")

if not member_id:
    st.warning("No member selected.")
    if st.button("← Back to Directory"):
        st.switch_page("Home.py")
    st.stop()

# Keep URL bookmarkable
st.query_params["id"] = member_id

# ── Load member ──────────────────────────────────────────────────────────────
members = load_members()
member = members[members["member_id"] == member_id]

if member.empty:
    st.error(f"Member not found: {member_id}")
    if st.button("← Back to Directory"):
        st.switch_page("Home.py")
    st.stop()

m = member.iloc[0]
name = str(m["name"]) if pd.notna(m["name"]) else "Unknown"
profile_url = str(m["profile_url"]) if pd.notna(m.get("profile_url")) else None
honorific = str(m["honorific"]) if pd.notna(m.get("honorific")) else ""
biography = str(m["biography"]) if pd.notna(m.get("biography")) else ""

# ── Related data ─────────────────────────────────────────────────────────────
mem_positions = (
    load_positions()
    .query("member_id == @member_id")
    .sort_values("sort_order")
)
mem_areas = (
    load_research_areas()
    .query("member_id == @member_id")
    .sort_values("sort_order")
)
mem_edu = (
    load_education()
    .query("member_id == @member_id")
    .sort_values("sort_order")
)
mem_pubs = (
    load_publications()
    .query("member_id == @member_id")
    .sort_values("sort_order")
)
mem_acts = (
    load_activities()
    .query("member_id == @member_id")
    .sort_values("sort_order")
)
mem_contact = load_contact_info().query("member_id == @member_id")
mem_news = (
    load_news()
    .query("member_id == @member_id")
    .sort_values("sort_order")
)

# ── Credential string from education ─────────────────────────────────────────
degrees = mem_edu["degree"].dropna().tolist()
credential_str = ", ".join(str(d) for d in degrees[:3]) if degrees else ""

# ── Profile banner + avatar ──────────────────────────────────────────────────
display_name = f"{honorific} {name}".strip() if honorific else name
avatar = render_avatar_html(name, 110)

cred_html = (
    f'<div style="color:#555;margin-top:4px;font-size:0.95rem;">{_esc(credential_str)}</div>'
    if credential_str else ""
)

banner_html = (
    f'<div style="background:linear-gradient(135deg,{UCALGARY_RED} 0%,#8B0015 100%);'
    f'height:180px;border-radius:10px;"></div>'
    f'<div style="margin-top:-60px;padding-left:2rem;display:flex;'
    f'align-items:flex-end;gap:1.5rem;margin-bottom:1.2rem;">'
    f'<div style="border:4px solid #fff;border-radius:50%;'
    f'box-shadow:0 2px 10px rgba(0,0,0,0.15);line-height:0;">{avatar}</div>'
    f'<div style="padding-bottom:8px;">'
    f'<div style="font-size:1.8rem;font-weight:700;color:#1A1A1A;'
    f'margin:0;line-height:1.3;">{_esc(display_name)}</div>'
    f'{cred_html}'
    f'</div></div>'
)

st.markdown(banner_html, unsafe_allow_html=True)

# ── Navigation row ───────────────────────────────────────────────────────────
nav1, nav2, _ = st.columns([1, 1, 2])
with nav1:
    if st.button("← Back to Directory"):
        st.switch_page("Home.py")
with nav2:
    if profile_url:
        st.link_button("View on UCalgary ↗", profile_url)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# ── Positions ────────────────────────────────────────────────────────────────
if not mem_positions.empty:
    section_header("Positions")
    for _, pos in mem_positions.iterrows():
        ptitle = str(pos["title"]) if pd.notna(pos["title"]) else ""
        pdept = str(pos["department"]) if pd.notna(pos["department"]) else ""
        pfac = str(pos["faculty"]) if pd.notna(pos["faculty"]) else ""
        sub = " · ".join(p for p in [pdept, pfac] if p)
        if ptitle:
            st.markdown(f"**{_esc(ptitle)}**")
        if sub:
            st.caption(sub)

# ── Contact Information ──────────────────────────────────────────────────────
if not mem_contact.empty:
    section_header("Contact Information")
    for _, c in mem_contact.iterrows():
        ctype = str(c["contact_type"]) if pd.notna(c["contact_type"]) else ""
        label = str(c["label"]) if pd.notna(c["label"]) else ctype.title()
        value = str(c["value"]) if pd.notna(c["value"]) else ""
        url = str(c["url"]) if pd.notna(c["url"]) else ""

        if ctype == "email" and value:
            st.markdown(f"**{_esc(label)}:** [{_esc(value)}](mailto:{value})")
        elif url:
            display = value if value else url
            st.markdown(f"**{_esc(label)}:** [{_esc(display)}]({url})")
        elif value:
            st.markdown(f"**{_esc(label)}:** {_esc(value)}")

# ── Background (Biography + Education) ──────────────────────────────────────
if biography or not mem_edu.empty:
    section_header("Background")

    if biography:
        st.markdown(biography)
        st.markdown("")

    if not mem_edu.empty:
        st.markdown("##### Educational Background")
        for _, ed in mem_edu.iterrows():
            degree = str(ed["degree"]) if pd.notna(ed["degree"]) else ""
            inst = str(ed["institution"]) if pd.notna(ed["institution"]) else ""
            year = str(int(ed["year"])) if pd.notna(ed["year"]) else ""
            parts = [p for p in [degree, inst, year] if p]
            if parts:
                st.markdown(f"- {', '.join(parts)}")

# ── Research Areas ───────────────────────────────────────────────────────────
if not mem_areas.empty:
    section_header("Research")
    st.markdown("##### Areas of Research")
    areas_list = mem_areas["area"].dropna().tolist()
    st.markdown(
        render_research_tags(areas_list, max_show=50),
        unsafe_allow_html=True,
    )

# ── Publications ─────────────────────────────────────────────────────────────
if not mem_pubs.empty:
    section_header("Publications")
    for _, pub in mem_pubs.iterrows():
        ptitle = str(pub["title"]) if pd.notna(pub["title"]) else ""
        purl = str(pub["url"]) if pd.notna(pub["url"]) else ""
        raw = str(pub["raw_text"]) if pd.notna(pub["raw_text"]) else ""
        display = ptitle or raw
        if purl and display:
            st.markdown(f"- [{_esc(display)}]({purl})")
        elif display:
            st.markdown(f"- {_esc(display)}")
        elif purl:
            st.markdown(f"- [{purl}]({purl})")

# ── Activities ───────────────────────────────────────────────────────────────
if not mem_acts.empty:
    section_header("Activities")
    for cat in mem_acts["category"].dropna().unique():
        cat_rows = mem_acts[mem_acts["category"] == cat]
        st.markdown(f"**{str(cat).title()}**")
        items, seen = [], set()
        for _, act in cat_rows.iterrows():
            text = str(act["title"]) if pd.notna(act["title"]) else ""
            key = text[:80]
            if not text or key in seen:
                continue
            seen.add(key)
            items.append(text[:200] + ("…" if len(text) > 200 else ""))
        for item in items[:5]:
            st.markdown(f"- {item}")
        if len(items) > 5:
            with st.expander(f"Show all {len(items)} items"):
                for item in items[5:]:
                    st.markdown(f"- {item}")

# ── News ─────────────────────────────────────────────────────────────────────
if not mem_news.empty:
    section_header("News")
    for _, n in mem_news.iterrows():
        headline = str(n["headline"]) if pd.notna(n["headline"]) else ""
        source = str(n["source"]) if pd.notna(n["source"]) else ""
        date = str(int(n["date"])) if pd.notna(n["date"]) else ""
        nurl = str(n["url"]) if pd.notna(n["url"]) else ""
        if headline:
            if nurl:
                st.markdown(f"📰 [{_esc(headline)}]({nurl})")
            else:
                st.markdown(f"📰 {_esc(headline)}")
            meta = " · ".join(p for p in [source, date] if p)
            if meta:
                st.caption(meta)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Data sourced from UCalgary Profiles · Hotchkiss Brain Institute")

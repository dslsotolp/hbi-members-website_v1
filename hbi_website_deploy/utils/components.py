"""Shared UI components for the HBI Members website."""

import hashlib
import html as html_mod
from urllib.parse import quote

import streamlit as st

UCALGARY_RED = "#CF0722"
UCALGARY_DARK = "#8B0015"
UCALGARY_GOLD = "#FFCD00"

AVATAR_COLORS = [
    "#CF0722", "#2D6A4F", "#264653", "#2A6F97", "#014F86",
    "#6A040F", "#7B2CBF", "#5A189A", "#3C096C", "#D4A373",
    "#1B4332", "#A30519", "#9D0208", "#370617", "#10002B",
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    return html_mod.escape(str(text)) if text else ""


def get_initials(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    if parts:
        return parts[0][0].upper()
    return "?"


def get_avatar_color(name: str) -> str:
    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(AVATAR_COLORS)
    return AVATAR_COLORS[idx]


# ── Avatar ───────────────────────────────────────────────────────────────────

def render_avatar_html(name: str, size: int = 60) -> str:
    initials = _esc(get_initials(name))
    color = get_avatar_color(name)
    fs = size // 2
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
        f'background:{color};color:#fff;display:inline-flex;align-items:center;'
        f'justify-content:center;font-size:{fs}px;font-weight:700;'
        f'flex-shrink:0;line-height:1;">{initials}</div>'
    )


# ── Research tags ────────────────────────────────────────────────────────────

def render_research_tags(areas: list, max_show: int = 6, clickable: bool = True) -> str:
    if not areas:
        return ""
    tags = ""
    for area in areas[:max_show]:
        href = f'/Research_Area?area={quote(str(area))}' if clickable else '#'
        tags += (
            f'<a class="hbi-tag" href="{href}">{_esc(area)}</a>'
        )
    if len(areas) > max_show:
        tags += (
            f'<span style="display:inline-block;padding:3px 10px;margin:2px;'
            f'border-radius:12px;background:{UCALGARY_RED};font-size:0.74rem;'
            f'color:#fff;font-weight:600;">+{len(areas) - max_show} more</span>'
        )
    return f'<div style="margin-top:6px;line-height:1.9;">{tags}</div>'


# ── Noise filtering ──────────────────────────────────────────────────────────

_NOISE_VALUES = frozenset({
    "fulltime", "faculty", "adjuncts", "emeriti", "specialization",
    "clinical", "calgary campus", "member", "clinical research",
})


def _clean_field(text: str | None) -> str:
    """Return the text if meaningful, otherwise empty string."""
    if not text:
        return ""
    if text.strip().lower() in _NOISE_VALUES:
        return ""
    return text.strip()


# ── Member card (directory) ──────────────────────────────────────────────────

def render_card_html(name: str, title: str, department: str, areas: list,
                     member_id: str = "") -> str:
    avatar = render_avatar_html(name, 48)
    safe_name = _esc(name)
    safe_title = _esc(_clean_field(title))
    safe_dept = _esc(_clean_field(department))
    if not safe_title and not safe_dept:
        safe_title = "HBI Member"
    tags = render_research_tags(areas)
    href = f"/Member_Profile?id={_esc(member_id)}" if member_id else "#"
    # Use &nbsp; placeholders to keep consistent height for empty lines
    title_html = safe_title if safe_title else "&nbsp;"
    dept_html = safe_dept if safe_dept else "&nbsp;"
    return (
        f'<div class="hbi-card" onclick="window.location.href=\'{href}\'" style="cursor:pointer;">'
        f'  <div class="hbi-card-body">'
        f'    <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:2px;">'
        f'      {avatar}'
        f'      <div style="min-width:0;">'
        f'        <div style="font-weight:600;font-size:1rem;color:#1A1A1A;line-height:1.3;">{safe_name}</div>'
        f'        <div style="font-size:0.85rem;color:#555;margin-top:2px;min-height:1.2em;">{title_html}</div>'
        f'        <div style="font-size:0.8rem;color:#888;min-height:1.1em;">{dept_html}</div>'
        f'      </div>'
        f'    </div>'
        f'    {tags}'
        f'  </div>'
        f'  <a class="hbi-card-btn" href="{href}" onclick="event.stopPropagation();">View Profile →</a>'
        f'</div>'
    )


def render_card_grid(cards_html: list[str]) -> str:
    """Wrap a list of card HTML strings in a CSS Grid container."""
    return '<div class="hbi-grid">' + '\n'.join(cards_html) + '</div>'


# ── List row (directory list view) ───────────────────────────────────────────

def render_list_row_html(name: str, title: str, department: str, areas: list,
                         member_id: str = "") -> str:
    avatar = render_avatar_html(name, 40)
    safe_name = _esc(name)
    safe_title = _esc(_clean_field(title))
    safe_dept = _esc(_clean_field(department))
    if not safe_title and not safe_dept:
        safe_title = "HBI Member"
    tags = render_research_tags(areas, max_show=6)
    href = f"/Member_Profile?id={_esc(member_id)}" if member_id else "#"
    subtitle = " · ".join(p for p in [safe_title, safe_dept] if p)
    return (
        f'<div class="hbi-list-row" onclick="window.location.href=\'{href}\'" style="cursor:pointer;">'
        f'  <div class="hbi-list-left">'
        f'    {avatar}'
        f'    <div style="min-width:0;">'
        f'      <div style="font-weight:600;font-size:0.95rem;color:#1A1A1A;">{safe_name}</div>'
        f'      <div style="font-size:0.82rem;color:#666;margin-top:2px;">{subtitle}</div>'
        f'    </div>'
        f'  </div>'
        f'  <div class="hbi-list-tags">{tags}</div>'
        f'  <a class="hbi-list-action" href="{href}" onclick="event.stopPropagation();">View →</a>'
        f'</div>'
    )


def render_list_view(rows_html: list[str]) -> str:
    """Wrap list row HTML strings in a list container."""
    return '<div class="hbi-list">' + '\n'.join(rows_html) + '</div>'


# ── Section header (profile page) ───────────────────────────────────────────

def section_header(title: str):
    st.markdown(
        f'<div style="border-bottom:3px solid {UCALGARY_RED};padding-bottom:6px;'
        f'margin:2rem 0 1rem 0;">'
        f'<h3 style="margin:0;font-size:1.05rem;text-transform:uppercase;'
        f'letter-spacing:0.5px;color:#1A1A1A;">{_esc(title)}</h3></div>',
        unsafe_allow_html=True,
    )


# ── Global CSS injection ────────────────────────────────────────────────────

def inject_custom_css():
    st.markdown(
        """
    <style>
    /* ── Banner ── */
    .hbi-banner {
        background: linear-gradient(135deg, #CF0722 0%, #8B0015 100%);
        color: white;
        padding: 2rem 2.5rem;
        border-radius: 10px;
        margin-bottom: 1.2rem;
    }
    .hbi-banner h1 { margin:0; font-size:2rem; font-weight:700; color:white !important; }
    .hbi-banner p  { margin:0.3rem 0 0 0; font-size:1rem; opacity:0.9; color: white !important; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] .stMarkdown h2 { color: #CF0722; }
    section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p {
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    /* ── Card action buttons ── */
    div[data-testid="stVerticalBlock"] .stButton > button[kind="primary"] {
        background-color: #CF0722;
        border: none;
        font-size: 0.82rem;
    }

    /* ── Card grid ── */
    .hbi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .hbi-card {
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 1rem;
        max-width: 480px;
        display: flex;
        flex-direction: column;
        transition: box-shadow 0.15s, border-color 0.15s;
        cursor: pointer;
    }
    .hbi-card:hover {
        border-color: #CF0722;
        box-shadow: 0 4px 16px rgba(207,7,34,0.12);
    }
    .hbi-card-body {
        flex: 1;
    }
    .hbi-card-btn {
        display: block;
        margin-top: auto;
        padding: 8px 0;
        text-align: center;
        background: #CF0722;
        color: #fff !important;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        text-decoration: none !important;
    }
    .hbi-card a {
        position: relative;
        z-index: 1;
    }
    .hbi-card-btn:hover {
        background: #A50519;
    }

    /* ── List view ── */
    .hbi-list {
        display: flex;
        flex-direction: column;
        gap: 0;
    }
    .hbi-list-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #E8E8E8;
        transition: background 0.12s;
        cursor: pointer;
    }
    .hbi-list-row:first-child {
        border-top: 1px solid #E8E8E8;
    }
    .hbi-list-row:hover {
        background: #FEF0F1;
    }
    .hbi-list-left {
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: 260px;
        flex-shrink: 0;
    }
    .hbi-list-tags {
        flex: 1;
        min-width: 0;
        overflow: hidden;
    }
    .hbi-list-action {
        flex-shrink: 0;
        color: #CF0722;
        font-weight: 600;
        font-size: 0.85rem;
        white-space: nowrap;
        text-decoration: none !important;
    }

    /* ── Research tags ── */
    .hbi-tag {
        display: inline-block;
        padding: 3px 10px;
        margin: 2px;
        border-radius: 12px;
        background: #F0F2F5;
        font-size: 0.74rem;
        color: #1A1A1A;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        text-decoration: none !important;
        border: 1px solid transparent;
        transition: border-color 0.15s;
    }
    .hbi-tag:hover {
        border-color: #CF0722;
        color: #1A1A1A;
        text-decoration: none;
    }
    .hbi-tag:active {
        border-color: #8B0015;
    }

    /* ── Hide Streamlit chrome ── */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    </style>
    """,
        unsafe_allow_html=True,
    )

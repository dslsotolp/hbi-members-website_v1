"""HBI Community (Alumni) — Placeholder page."""

import streamlit as st
from utils.components import inject_custom_css

st.set_page_config(
    page_title="HBI Community – Coming Soon",
    page_icon="🧠",
    layout="wide",
)
inject_custom_css()

st.markdown(
    """
    <div class="hbi-banner">
        <h1>🤝 HBI Community</h1>
        <p>Alumni Directory · Hotchkiss Brain Institute</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("")
st.markdown("### Coming Soon")
st.markdown(
    """
The HBI Community directory will allow past trainees and alumni to:

- 🔍 **Search** by name, job title, industry, and location
- 👤 **View profiles** with career details and LinkedIn connections
- 🌍 **Filter** by geographical region, country, and city
- 🤝 **Connect** through the Community Mentorship program
- ✏️ **Claim or update** their own profiles

---

*This feature is currently under development. Stay tuned!*
"""
)

if st.button("← Back to Directory"):
    st.switch_page("Home.py")

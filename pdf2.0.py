# app.py – PDF Comparison Tool (Improved: UI/UX + Performance + Robust PDF Reading)

import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import os
import hashlib
from difflib import SequenceMatcher
from io import BytesIO

st.set_page_config(
    page_title="PDF Diff",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

.stApp { background: #0c0e14; color: #dde3f0; }

/* Banner */
.banner {
    background: linear-gradient(160deg, #111520 0%, #0c0e14 50%, #0f1a2e 100%);
    border: 1px solid #1e2740;
    border-radius: 14px;
    padding: 2rem 2.5rem 1.6rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.banner::after {
    content: 'PDF';
    position: absolute;
    right: 2rem; top: 50%;
    transform: translateY(-50%);
    font-size: 6rem;
    font-weight: 800;
    color: rgba(99,130,255,0.05);
    letter-spacing: -4px;
    pointer-events: none;
    font-family: 'Syne', sans-serif;
}
.banner .tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #6382ff;
    display: block;
    margin-bottom: 0.5rem;
}
.banner h1 {
    font-size: 1.9rem;
    font-weight: 800;
    color: #eef2ff;
    margin: 0 0 0.4rem;
    letter-spacing: -0.5px;
}
.banner p { color: #7888a8; font-size: 0.88rem; margin: 0; font-weight: 400; }

/* Step label */
.step-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #6382ff;
    font-weight: 600;
    margin: 1.8rem 0 0.7rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.step-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1e2740;
}

/* Pair card */
.pair-card {
    background: #111520;
    border: 1px solid #1e2740;
    border-radius: 10px;
    padding: 0.85rem 1.2rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.83rem;
}
.pair-card .fname {
    font-family: 'JetBrains Mono', monospace;
    color: #8899bb;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.pair-card .arrow { color: #6382ff; font-size: 1rem; flex-shrink: 0; }
.pair-card .score {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #3b82f6;
    background: #0f1e38;
    border: 1px solid #1e3560;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    flex-shrink: 0;
}

/* Similarity badge */
.sim-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 0.35rem 0.85rem;
    border-radius: 6px;
    margin-bottom: 1rem;
}
.sim-badge.high   { background: #1a3a1a; color: #4ade80; border: 1px solid #166534; }
.sim-badge.medium { background: #2a2a10; color: #facc15; border: 1px solid #713f12; }
.sim-badge.low    { background: #2a1010; color: #f87171; border: 1px solid #7f1d1d; }

/* Comparison header */
.compare-header {
    background: #111520;
    border: 1px solid #1e2740;
    border-left: 3px solid #6382ff;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.4rem;
    margin: 1.5rem 0 0.75rem;
}
.compare-header .title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    color: #c8d4ee;
    font-weight: 600;
    margin-bottom: 0.25rem;
}
.compare-header .sub { color: #4a5878; font-size: 0.78rem; }

/* PDF label */
.pdf-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #6382ff;
    background: #0f1630;
    border: 1px solid #1e2d54;
    padding: 0.3rem 0.75rem;
    border-radius: 5px;
    margin-bottom: 0.5rem;
    display: inline-block;
}

/* Warn / info boxes */
.warn-box {
    background: #1a1207;
    border: 1px solid #78350f;
    border-radius: 8px;
    padding: 0.75rem 1.1rem;
    color: #fcd34d;
    font-size: 0.84rem;
    margin-bottom: 0.6rem;
}
.info-box {
    background: #0e1e35;
    border: 1px solid #1e3a60;
    border-radius: 8px;
    padding: 0.75rem 1.1rem;
    color: #93c5fd;
    font-size: 0.84rem;
    margin-bottom: 0.6rem;
}
.success-box {
    background: #052e16;
    border: 1px solid #166534;
    border-radius: 8px;
    padding: 0.75rem 1.1rem;
    color: #86efac;
    font-size: 0.84rem;
    margin-bottom: 0.6rem;
}
.error-box {
    background: #1f0909;
    border: 1px solid #7f1d1d;
    border-radius: 8px;
    padding: 0.75rem 1.1rem;
    color: #fca5a5;
    font-size: 0.84rem;
    margin-bottom: 0.6rem;
}

/* Metric row */
.metric-row {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin: 0.75rem 0 1.25rem;
}
.metric-pill {
    background: #111520;
    border: 1px solid #1e2740;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-size: 0.82rem;
    color: #8899bb;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.metric-pill .val {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-size: 1rem;
    color: #c8d4ee;
}

/* Streamlit overrides */
div[data-testid="stFileUploader"] {
    background: #111520;
    border: 1px dashed #1e2d54;
    border-radius: 10px;
    padding: 0.4rem;
}
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: #111520 !important;
    border: 1px solid #1e2740 !important;
    color: #dde3f0 !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important;
}
.stButton > button {
    background: #3b5bdb;
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 0.6rem 2rem;
    font-size: 0.88rem;
    transition: background 0.2s;
}
.stButton > button:hover { background: #2f4cc4; }
.stSlider > div { padding: 0.1rem 0; }
label[data-testid="stWidgetLabel"] { color: #7888a8 !important; font-size: 0.83rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div class="banner">
  <span class="tag">Document Comparison Tool</span>
  <h1>PDF Diff</h1>
  <p>Upload two sets of PDFs — matched by filename similarity — and compare their content side by side.</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PDF TEXT EXTRACTION  (robust multi-library fallback)
# ─────────────────────────────────────────────

def _try_pypdf(data: bytes) -> str | None:
    """Primary extractor: pypdf (modern successor to PyPDF2)."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(data))
        pages = []
        for page in reader.pages:
            try:
                t = page.extract_text()
                if t:
                    pages.append(t)
            except Exception:
                pass
        return "\n".join(pages) if pages else None
    except Exception:
        return None


def _try_pdfplumber(data: bytes) -> str | None:
    """Fallback extractor: pdfplumber — better on complex layouts."""
    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(BytesIO(data)) as pdf:
            for page in pdf.pages:
                try:
                    t = page.extract_text()
                    if t:
                        pages.append(t)
                except Exception:
                    pass
        return "\n".join(pages) if pages else None
    except Exception:
        return None


def _try_pymupdf(data: bytes) -> str | None:
    """Second fallback: PyMuPDF (fitz) — handles many edge cases."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=data, filetype="pdf")
        pages = []
        for page in doc:
            try:
                t = page.get_text()
                if t:
                    pages.append(t)
            except Exception:
                pass
        return "\n".join(pages) if pages else None
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def extract_text(file_data: bytes, filename: str) -> tuple[str, str]:
    """
    Try multiple PDF extractors in order of reliability.
    Returns (text, method_used).
    Cached by file content hash so repeated reruns are instant.
    """
    for extractor, label in [
        (_try_pypdf,     "pypdf"),
        (_try_pdfplumber,"pdfplumber"),
        (_try_pymupdf,   "PyMuPDF"),
    ]:
        result = extractor(file_data)
        if result and result.strip():
            return result.strip(), label

    return "", "failed"


# ─────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────

def base_name(filename: str) -> str:
    return os.path.splitext(filename)[0]


def calc_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def similarity_class(score: float) -> str:
    if score >= 0.75: return "high"
    if score >= 0.40: return "medium"
    return "low"


def similarity_emoji(score: float) -> str:
    if score >= 0.75: return "🟢"
    if score >= 0.40: return "🟡"
    return "🔴"


# ─────────────────────────────────────────────
# STEP 1 — UPLOAD
# ─────────────────────────────────────────────
st.markdown('<div class="step-label">Step 1 — Upload</div>', unsafe_allow_html=True)
col_u1, col_u2 = st.columns(2)
with col_u1:
    files1 = st.file_uploader("Set 1 (Old / Reference)", type="pdf",
                               accept_multiple_files=True)
with col_u2:
    files2 = st.file_uploader("Set 2 (New / Comparison)", type="pdf",
                               accept_multiple_files=True)

# ─────────────────────────────────────────────
# STEP 2 — CONFIGURE
# ─────────────────────────────────────────────
st.markdown('<div class="step-label">Step 2 — Configure</div>', unsafe_allow_html=True)
cfg1, cfg2, cfg3 = st.columns(3)
with cfg1:
    match_threshold = st.slider(
        "Filename match threshold", 0.1, 1.0, 0.5, 0.05,
        help="Minimum filename similarity to auto-pair two PDFs"
    )
with cfg2:
    skip_threshold = st.slider(
        "Skip if content similarity ≥", 0.80, 1.0, 0.98, 0.01,
        help="Pairs above this threshold are considered identical and skipped"
    )
with cfg3:
    max_display = st.number_input(
        "Max pairs to display", min_value=1, max_value=50, value=10,
        help="Limit how many pairs are rendered (large numbers slow the page)"
    )

# ─────────────────────────────────────────────
# STEP 3 — MATCH & RUN
# ─────────────────────────────────────────────
if files1 and files2:
    st.markdown('<div class="step-label">Step 3 — Match & Compare</div>', unsafe_allow_html=True)

    # ── Build pairs ──────────────────────────
    pairs: list[tuple] = []
    used_f2: set[str] = set()

    for f1 in files1:
        base1 = base_name(f1.name)
        best_match, highest_score = None, 0.0
        for f2 in files2:
            if f2.name in used_f2:
                continue
            score = calc_similarity(base1, base_name(f2.name))
            if score > highest_score:
                highest_score, best_match = score, f2
        if best_match and highest_score >= match_threshold:
            pairs.append((f1, best_match, highest_score))
            used_f2.add(best_match.name)

    # ── Unmatched warning ─────────────────────
    unmatched = [f.name for f in files1 if not any(f.name == p[0].name for p in pairs)]

    if pairs:
        with st.expander(f"📋 {len(pairs)} pair(s) matched", expanded=False):
            for f1, f2, score in pairs:
                st.markdown(
                    f'<div class="pair-card">'
                    f'<span class="fname">{f1.name}</span>'
                    f'<span class="arrow">⟶</span>'
                    f'<span class="fname">{f2.name}</span>'
                    f'<span class="score">{score:.0%}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        if unmatched:
            st.markdown(
                f'<div class="warn-box">⚠️ No match found for: {", ".join(unmatched)}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="warn-box">⚠️ No suitable pairs found. Try lowering the filename match threshold.</div>',
            unsafe_allow_html=True,
        )

    if pairs and st.button("▶  Run Comparison"):

        prog = st.progress(0, text="Extracting text…")

        # ── Pre-extract all text (cached) ─────
        # Read all bytes upfront — avoids fragile seek() dance
        file_data: dict[str, bytes] = {}
        for f1, f2, _ in pairs:
            for f in (f1, f2):
                if f.name not in file_data:
                    file_data[f.name] = f.read()

        extraction_errors: list[str] = []
        texts: dict[str, tuple[str, str]] = {}
        for name, data in file_data.items():
            text, method = extract_text(data, name)
            texts[name] = (text, method)
            if method == "failed":
                extraction_errors.append(name)

        # ── Show extraction issues ────────────
        if extraction_errors:
            st.markdown(
                f'<div class="error-box">⚠️ Could not extract text from: '
                f'{", ".join(extraction_errors)}. '
                f'They may be scanned images — consider OCR preprocessing.</div>',
                unsafe_allow_html=True,
            )

        # ── Compute similarity & bucket results
        skipped, to_display = [], []
        for f1, f2, _ in pairs:
            t1, m1 = texts[f1.name]
            t2, m2 = texts[f2.name]
            sim = calc_similarity(t1, t2)
            if sim >= skip_threshold:
                skipped.append((f1.name, f2.name, sim))
            else:
                to_display.append((f1, f2, sim, m1, m2))

        prog.empty()

        # ── Summary metrics ───────────────────
        st.markdown(
            f'<div class="metric-row">'
            f'<div class="metric-pill">📄 <span class="val">{len(pairs)}</span> pairs</div>'
            f'<div class="metric-pill">🔍 <span class="val">{len(to_display)}</span> compared</div>'
            f'<div class="metric-pill">✅ <span class="val">{len(skipped)}</span> skipped (≥{skip_threshold:.0%})</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Skipped list ──────────────────────
        if skipped:
            with st.expander(f"✅ {len(skipped)} identical pair(s) skipped"):
                for n1, n2, sim in skipped:
                    st.markdown(
                        f'<div class="pair-card">'
                        f'<span class="fname">{n1}</span>'
                        f'<span class="arrow">≈</span>'
                        f'<span class="fname">{n2}</span>'
                        f'<span class="score">{sim:.1%}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        # ── Display pairs ─────────────────────
        if to_display:
            display_count = min(len(to_display), int(max_display))
            if display_count < len(to_display):
                st.markdown(
                    f'<div class="info-box">ℹ️ Showing {display_count} of {len(to_display)} pairs. '
                    f'Increase "Max pairs to display" to see more.</div>',
                    unsafe_allow_html=True,
                )

            for f1, f2, sim, m1, m2 in to_display[:display_count]:
                cls = similarity_class(sim)
                emoji = similarity_emoji(sim)

                st.markdown(
                    f'<div class="compare-header">'
                    f'<div class="title">{f1.name}  ⟶  {f2.name}</div>'
                    f'<div class="sub">Extracted via {m1} · {m2}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f'<span class="sim-badge {cls}">'
                    f'{emoji} Content similarity: {sim:.1%}'
                    f'</span>',
                    unsafe_allow_html=True,
                )

                c1, c2 = st.columns(2, gap="medium")
                with c1:
                    st.markdown(f'<span class="pdf-label">SET 1 · {f1.name}</span>',
                                unsafe_allow_html=True)
                    pdf_viewer(file_data[f1.name], width="100%")
                with c2:
                    st.markdown(f'<span class="pdf-label">SET 2 · {f2.name}</span>',
                                unsafe_allow_html=True)
                    pdf_viewer(file_data[f2.name], width="100%")

                st.divider()

        elif not skipped:
            st.markdown(
                '<div class="info-box">ℹ️ No pairs to display after filtering.</div>',
                unsafe_allow_html=True,
            )

else:
    st.markdown(
        '<div style="color:#3a4560;font-size:0.88rem;padding:1.2rem 0;">'
        'Upload PDFs to both sets above to begin.'
        '</div>',
        unsafe_allow_html=True,
    )

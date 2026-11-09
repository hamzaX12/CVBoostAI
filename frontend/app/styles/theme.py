"""
CVBoost AI — Shared theme CSS injected via st.markdown
"""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --primary-dark: #09637E;
  --primary: #088395;
  --accent: #7AB2B2;
  --surface: #EBF4F6;
  --body-text: #0F2A33;
  --white: #FFFFFF;
  --error: #C0392B;
  --success: #1E8E5A;
  --border: rgba(7, 131, 149, 0.2);
  --shadow: 0 4px 20px rgba(9,99,126,0.08);
  --radius: 12px;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header, .stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }

/* ── Global ── */
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: 'Inter', sans-serif !important;
  color: var(--body-text) !important;
}

.stApp {
  background: var(--surface) !important;
}

h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4 {
  color: var(--primary-dark) !important;
  font-weight: 700 !important;
}

p, span, label,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stMarkdownContainer"] p {
  color: var(--body-text) !important;
}

.stTextInput input, .stTextArea textarea {
  color: var(--body-text) !important;
  background: white !important;
}

/* ── Buttons ── */
.stButton > button {
  background: var(--primary) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-family: 'Inter', sans-serif !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 2px 8px rgba(8,131,149,0.3) !important;
}
.stButton > button:hover {
  background: var(--primary-dark) !important;
  box-shadow: 0 4px 16px rgba(9,99,126,0.4) !important;
  transform: translateY(-1px);
}
.stButton > button[kind="secondary"] {
  background: transparent !important;
  color: var(--primary) !important;
  border: 1.5px solid var(--primary) !important;
  box-shadow: none !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
  border-radius: 8px !important;
  border: 1.5px solid var(--border) !important;
  font-family: 'Inter', sans-serif !important;
  background: white !important;
  transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(8,131,149,0.1) !important;
}

/* ── Expander (accordion sections) ── */
.streamlit-expanderHeader {
  background: white !important;
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
  font-weight: 600 !important;
  color: var(--primary-dark) !important;
  transition: background 0.2s !important;
}
.streamlit-expanderHeader:hover {
  background: var(--surface) !important;
}
.streamlit-expanderContent {
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--radius) var(--radius) !important;
  background: white !important;
}

/* ── Cards ── */
.cv-card {
  background: white;
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  margin-bottom: 16px;
}

/* ── Chips ── */
.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--surface);
  border: 1px solid var(--accent);
  border-radius: 20px;
  padding: 3px 10px;
  font-size: 13px;
  margin: 3px;
  cursor: pointer;
  transition: all 0.15s;
  color: var(--primary-dark);
  font-weight: 500;
}
.chip:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}
.chip.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}
.chip .remove-btn {
  opacity: 0.7;
  margin-left: 2px;
}

/* ── CVBoost AI Custom Components ── */
.cvw-top-cards {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.cvw-top-card {
  flex: 1;
  border: 1.5px solid #D1D5DB;
  border-radius: 10px;
  background: #FFFFFF;
  padding: 16px 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.cvw-top-card:hover {
  border-color: #088395;
  background: #F8FAFC;
  box-shadow: 0 4px 12px rgba(8,131,149,0.08);
}
.cvw-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #FFFFFF;
  border: 1.5px solid #94A3B8;
  border-radius: 24px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #334155;
  margin: 3px 2px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.cvw-pill:hover {
  border-color: #088395;
  color: #088395;
  background: #F0FDFA;
}
.cvw-entry-card {
  background: #FFFFFF;
  border: 1.5px solid #E2E8F0;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.cvw-download-btn {
  background: #1B64F2 !important;
  color: #FFFFFF !important;
  border-radius: 28px !important;
  padding: 10px 24px !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  box-shadow: 0 4px 14px rgba(27,100,242,0.35) !important;
}

/* ── Section labels ── */
.section-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--primary-dark);
  margin-bottom: 6px;
  opacity: 0.7;
}

/* ── Progress/status bar ── */
.status-bar {
  background: linear-gradient(135deg, var(--primary-dark), var(--primary));
  color: white;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 12px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.85; }
}

/* ── ATS Score badge ── */
.ats-score {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  font-size: 20px;
  font-weight: 800;
  border: 3px solid;
}
.ats-score.high { border-color: var(--success); color: var(--success); }
.ats-score.medium { border-color: #F39C12; color: #F39C12; }
.ats-score.low { border-color: var(--error); color: var(--error); }

/* ── Dividers ── */
.cv-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 16px 0;
}

/* ── Preview iframe ── */
.preview-frame {
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
}

/* ── Tooltips ── */
[title] { cursor: help; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }
</style>
"""

HIDE_STREAMLIT = """
<style>
#MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
header, [data-testid="stHeader"] {
  display: none !important;
  height: 0 !important;
  pointer-events: none !important;
  visibility: hidden !important;
  z-index: -9999 !important;
}
.main .block-container, [data-testid="stMainBlockContainer"], div[data-testid="stMainBlockContainer"] {
  padding-top: 0 !important;
  margin-top: 0 !important;
}
</style>
"""

"""
CVBoost AI — Builder Page
CVBoost AI builder layout and design using Tailwind CSS.
Renders full-height split editor & live preview panel matching the user's HTML specification.
"""
from __future__ import annotations

import json
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import importlib
from styles.theme import HIDE_STREAMLIT
import components.cv_state
importlib.reload(components.cv_state)
from components.cv_state import init_cv_state, get_cv, _empty_cv

st.set_page_config(
    page_title="CVBoost AI — Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(HIDE_STREAMLIT, unsafe_allow_html=True)
st.markdown("""
<style>
/* Remove all Streamlit default headers, footers, toolbars, and extra bottom spacing */
header, [data-testid="stHeader"], footer, [data-testid="stBottom"], [data-testid="stToolbar"] {
    display: none !important;
    height: 0 !important;
    max-height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    pointer-events: none !important;
    visibility: hidden !important;
    z-index: -9999 !important;
}

/* Lock outer page viewport to 100vh so no blank footer or outer scrolling exists */
html, body, .stApp, [data-testid="stAppViewContainer"], .main, .block-container {
    overflow: hidden !important;
    height: 100vh !important;
    max-height: 100vh !important;
    min-height: 100vh !important;
    width: 100vw !important;
    max-width: 100vw !important;
    padding: 0 !important;
    margin: 0 !important;
}

div[data-testid="stCustomComponentV1"] {
    width: 100vw !important;
    height: 100vh !important;
    max-height: 100vh !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}

/* Make builder iframe fit 100% of browser window with zero blank gap */
iframe {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    min-height: 100vh !important;
    max-height: 100vh !important;
    border: none !important;
    display: block !important;
    z-index: 10 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Navigation Listener ──
if st.query_params.get("page") == "landing":
    st.query_params.clear()
    for p in ["pages/1_Landing.py", "app/pages/1_Landing.py", "1_Landing"]:
        try:
            st.switch_page(p)
            break
        except Exception:
            pass

# ── Load CV Data ──
# Force-purge any stale or personal data anywhere in session state
cv_curr = st.session_state.get("cv", {})
if isinstance(cv_curr, dict):
    raw_str = json.dumps(cv_curr).lower()
    if any(k in raw_str for k in ["hamza", "ben allou", "benallou", "safi", "devo soft", "est safi"]):
        st.session_state["cv"] = _empty_cv()

init_cv_state()
cv = get_cv()
raw_str = json.dumps(cv).lower()
if any(k in raw_str for k in ["hamza", "ben allou", "benallou", "safi", "devo soft", "est safi"]) or not cv.get("personal", {}).get("first_name"):
    st.session_state["cv"] = _empty_cv()
    cv = get_cv()

cv_json = json.dumps(cv, ensure_ascii=False)
sample_cv_json = json.dumps(_empty_cv(), ensure_ascii=False)

# ── The HTML Template ──
builder_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  <title>CVBoost AI Resume Builder</title>
  <!-- Tailwind CSS CDN with forms and container queries plugins -->
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  <!-- Client-side PDF Generation Engine -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
  <!-- Tailwind Configuration -->
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            brand: {{
              50: '#eff6ff',
              100: '#dbeafe',
              500: '#3b82f6',
              600: '#1d68e0',
              700: '#1751b8',
            }},
            cvgray: {{
              50: '#F9FAFB',
              100: '#F3F4F6',
              200: '#E5E7EB',
              300: '#D1D5DB',
              400: '#9CA3AF',
              500: '#6B7280',
              600: '#4B5563',
              700: '#374151',
              800: '#1F2937',
              900: '#111827',
            }}
          }},
          fontFamily: {{
            sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
          }},
          boxShadow: {{
            'card-subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.03)',
            'paper': '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.08)',
          }}
        }}
      }}
    }}
  </script>
  <style data-purpose="custom-scrollbars">
    /* Subtle scrollbar for modern editor panels */
    ::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    ::-webkit-scrollbar-track {{
      background: transparent;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #D1D5DB;
      border-radius: 9999px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #9CA3AF;
    }}
    @media print {{
      body * {{
        visibility: hidden;
      }}
      #resumeSheet, #resumeSheet * {{
        visibility: visible;
      }}
      #resumeSheet {{
        position: absolute;
        left: 0;
        top: 0;
        width: 100% !important;
        box-shadow: none !important;
        border: none !important;
        margin: 0 !important;
        padding: 20mm !important;
      }}
    }}
  </style>
</head>
<body class="bg-gray-100 font-sans text-gray-800 antialiased min-h-screen flex flex-col h-screen overflow-hidden">

  <!-- BEGIN: ApplicationTopNav -->
  <header class="bg-white border-b border-gray-200 sticky top-0 z-40 px-4 lg:px-8 py-2.5 flex items-center justify-between flex-shrink-0" data-purpose="app-header">
    <!-- Left Navigation: Back to CVs -->
    <div class="flex items-center space-x-2">
      <button onclick="navigateToLanding()" class="inline-flex items-center space-x-1.5 px-3 py-1.5 border border-gray-200 hover:border-gray-400 rounded-lg text-xs md:text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition" title="Back to CVs">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M10 19l-7-7m0 0l7-7m-7 7h18" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
        </svg>
        <span>CVs</span>
      </button>
    </div>

    <!-- Middle: CV Name Input -->
    <div class="flex items-center justify-center flex-1 max-w-md mx-4">
      <div class="flex items-center space-x-2 px-3 py-1 rounded-lg border border-transparent hover:border-gray-200 hover:bg-gray-50 transition focus-within:border-blue-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-blue-100">
        <input id="cvNameHeaderInput" type="text" value="CV Alex Morgan" oninput="handleCvNameInput(this.value)" class="bg-transparent border-none text-xs md:text-sm font-semibold text-gray-800 focus:ring-0 p-0 text-center w-52 md:w-64 outline-none placeholder-gray-400" placeholder="CV Name"/>
        <svg id="cloudSyncIcon" class="w-4 h-4 text-gray-400 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24" title="Synced to cloud">
          <path d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 00-9.78 2.096A4.001 4.001 0 003 15z" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"></path>
        </svg>
      </div>
    </div>

    <!-- Top Action Buttons -->
    <div class="flex items-center space-x-3">
      <button onclick="toggleZoom()" class="px-3 py-1.5 text-xs md:text-sm font-medium text-gray-600 hover:text-gray-900 border border-gray-200 rounded-lg hover:bg-gray-50 transition" title="Toggle Preview Zoom">
        <span id="zoomLabel">Zoom 100%</span>
      </button>
      <button onclick="clearAllCvInfo()" class="px-3 py-1.5 text-xs md:text-sm font-medium text-red-600 hover:text-red-700 border border-red-200 hover:border-red-300 rounded-lg hover:bg-red-50 transition flex items-center space-x-1.5" title="Clear all CV information">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
        </svg>
        <span>Clear</span>
      </button>
      <!-- 3 TEMPLATES: Simple | Classic Navy | Executive Slate -->
      <div class="flex items-center space-x-1 border border-gray-200 rounded-lg p-0.5 bg-gray-50 text-xs">
        <button type="button" onclick="selectTemplate('simple')" id="tplBtnSimple" class="px-2.5 py-1 rounded-md font-semibold transition bg-white text-blue-700 shadow-xs" title="Simple Template (Sebastian Bennett Style)">
          Simple
        </button>
        <button type="button" onclick="selectTemplate('classic')" id="tplBtnClassic" class="px-2.5 py-1 rounded-md font-semibold transition text-gray-600 hover:text-gray-900" title="Classic Navy Template">
          Classic Navy
        </button>
        <button type="button" onclick="selectTemplate('executive')" id="tplBtnExecutive" class="px-2.5 py-1 rounded-md font-semibold transition text-gray-600 hover:text-gray-900" title="Executive Slate Template (Laura G. Levell Style)">
          Executive Slate
        </button>
      </div>
      <button onclick="downloadResume()" class="inline-flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded-lg text-xs md:text-sm font-semibold transition shadow-sm" title="Download Resume">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
        </svg>
        <span>Download</span>
      </button>
    </div>
  </header>
  <!-- END: ApplicationTopNav -->

  <!-- BEGIN: MainContentSplitLayout -->
  <main class="flex-1 flex overflow-hidden">

    <!-- BEGIN: LeftEditorPanel -->
    <aside class="w-full lg:w-[620px] xl:w-[680px] bg-white border-r border-gray-200 overflow-y-auto flex-shrink-0 flex flex-col justify-between" data-purpose="cv-editor-panel">
      <!-- Editor Form Content Area -->
      <div class="p-6 sm:p-8 space-y-6">

        <!-- DUAL TOP BUTTONS: Upload existing CV | Paste CV text -->
        <div class="grid grid-cols-2 gap-3 pb-2">
          <div id="uploadCvCardBtn" onclick="document.getElementById('cvFileUpload').click()" class="border border-gray-300 rounded-xl p-3.5 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50/40 transition group">
            <svg class="w-5 h-5 mx-auto text-gray-500 group-hover:text-blue-600 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
            </svg>
            <div class="text-xs font-semibold text-gray-800 group-hover:text-blue-600">Upload existing CV</div>
            <input type="file" id="cvFileUpload" class="hidden" accept=".pdf,.docx" onchange="handleFileUpload(event)"/>
          </div>
          <div onclick="togglePasteCvPanel()" id="pasteCvCardBtn" class="border border-gray-300 rounded-xl p-3.5 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50/40 transition group">
            <svg class="w-5 h-5 mx-auto text-gray-500 group-hover:text-blue-600 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <div class="text-xs font-semibold text-gray-800 group-hover:text-blue-600">Paste CV as text</div>
          </div>
        </div>

        <!-- INLINE PASTE CV TEXT DRAWER (shown when user clicks 'Paste CV as text') -->
        <div id="pasteCvPanel" class="hidden border border-blue-300 bg-blue-50/40 rounded-xl p-4 space-y-3 transition-all shadow-card-subtle">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="text-base">📋</span>
              <span class="text-xs font-bold text-gray-800 uppercase tracking-wide">Paste Your CV As Text</span>
            </div>
            <button onclick="togglePasteCvPanel()" type="button" class="text-xs text-gray-400 hover:text-gray-700 p-1" title="Close">✕</button>
          </div>
          <p class="text-[11px] text-gray-600">Paste your raw resume or profile text below. AI will automatically extract and structure your personal details, summary, education, experience, projects, skills, and languages.</p>
          <textarea id="pasteCvTextarea" rows="6" class="w-full text-xs rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 p-2.5 font-mono leading-relaxed placeholder-gray-400 bg-white" placeholder="Paste your entire CV text here...&#10;&#10;e.g.&#10;Alex Morgan&#10;Senior Data Scientist&#10;Email: alex.morgan@example.com | Phone: +1 555-019-2834&#10;&#10;EDUCATION&#10;Master of Science in AI - Stanford University (2021 - 2023)&#10;&#10;EXPERIENCE / PROJECTS&#10;Apex Analytics: Built enterprise RAG copilot..."></textarea>
          <div class="flex items-center justify-between pt-1">
            <span id="pasteCvStatusHint" class="text-[11px] text-blue-600 font-medium"></span>
            <div class="flex items-center space-x-2 ml-auto">
              <button onclick="togglePasteCvPanel()" type="button" class="px-3 py-1.5 text-xs text-gray-600 hover:text-gray-800 rounded-lg border border-gray-300 hover:bg-gray-100 transition">Cancel</button>
              <button onclick="extractCvFromPastedText()" id="extractTextBtn" type="button" class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition">
                <span>✨ Extract & Fill CV</span>
              </button>
            </div>
          </div>
        </div>

        <!-- TARGET JOB / JOB DESCRIPTION TEXTAREA -->
        <div id="targetJobSection" class="border border-gray-200 rounded-xl p-4 bg-white shadow-card-subtle space-y-2.5 transition-all" data-purpose="section-target-job">
          <div class="flex items-center justify-between">
            <label for="targetJobInput" class="block text-xs font-bold uppercase tracking-wider text-gray-700">
              🎯 Job Description / Target Job
            </label>
            <span class="text-[11px] text-gray-400">Describe the job you are applying for</span>
          </div>
          <textarea id="targetJobInput" oninput="handleJobInput()" rows="3" class="w-full text-xs rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 p-2.5 leading-relaxed placeholder-gray-400" placeholder="e.g. Data Scientist / Machine Learning Engineer: Responsible for designing predictive models, training LLMs, data pipelines with PyTorch, Spark and SQL..."></textarea>
          <div class="flex items-center justify-between pt-0.5">
            <span id="jobInputHint" class="text-[11px] text-blue-600 font-medium"></span>
            <button onclick="analyzeTargetJob()" type="button" class="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-lg text-xs font-semibold transition ml-auto">
              <svg class="w-3.5 h-3.5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 0110 2zm0 13a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 0110 15zm8-5a.75.75 0 01-.75.75h-1.5a.75.75 0 010-1.5h1.5A.75.75 0 0118 10zM5 10a.75.75 0 01-.75.75h-1.5a.75.75 0 010-1.5h1.5A.75.75 0 015 10zm10.657-5.657a.75.75 0 010 1.06l-1.06 1.061a.75.75 0 11-1.062-1.06l1.061-1.061a.75.75 0 011.061 0zm-9.193 9.192a.75.75 0 010 1.061l-1.06 1.06a.75.75 0 11-1.061-1.06l1.06-1.061a.75.75 0 011.061 0zm9.193 0a.75.75 0 01-1.061 0l-1.06-1.06a.75.75 0 111.06-1.061l1.061 1.06a.75.75 0 010 1.061zM6.464 4.343a.75.75 0 01-1.06 0l-1.061-1.06A.75.75 0 015.404 2.22l1.06 1.061a.75.75 0 010 1.06z"></path>
              </svg>
              <span>Analyze with AI</span>
            </button>
          </div>
        </div>

        <!-- SECTION: PERSONAL DETAILS (Collapsible Card) -->
        <div class="border border-gray-200 rounded-xl p-5 bg-white shadow-card-subtle space-y-4" data-purpose="section-personal-details">
          <div class="flex items-center justify-between cursor-pointer" onclick="toggleSection('personalBody')">
            <h2 class="text-base font-bold tracking-wide text-gray-900 select-none">
              Personal details
            </h2>
            <div class="flex items-center space-x-2">
              <button id="personalChevron" aria-label="Collapse Section" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-500 hover:text-gray-700 hover:border-gray-400 transition" type="button">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M5 15l7-7 7 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                </svg>
              </button>
            </div>
          </div>

          <div id="personalBody" class="space-y-4 pt-2">
            <!-- Row 1: Photo + First/Last Name -->
            <div class="flex items-start space-x-4">
              <!-- Photo Box -->
              <div class="flex-shrink-0 text-center">
                <label class="block text-xs font-semibold text-gray-500 mb-1">Photo</label>
                <div class="relative w-20 h-20 rounded-lg border border-gray-300 overflow-hidden bg-gray-50 group cursor-pointer" onclick="document.getElementById('photoInput').click()">
                  <img id="photoThumb" src="" alt="Avatar" class="w-full h-full object-cover"/>
                  <div class="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition text-white text-[10px] font-medium">Change</div>
                </div>
                <input type="file" id="photoInput" class="hidden" accept="image/*" onchange="handlePhotoUpload(event)"/>
              </div>

              <!-- Names -->
              <div class="flex-1 space-y-3">
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">First name</label>
                    <input id="inputFirstName" type="text" oninput="updatePersonal()" class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-2 px-3"/>
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Last name</label>
                    <input id="inputLastName" type="text" oninput="updatePersonal()" class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-2 px-3"/>
                  </div>
                </div>
                <!-- Desired position + toggle -->
                <div class="flex items-end space-x-3">
                  <div class="flex-1">
                    <label class="block text-xs font-medium text-gray-600 mb-1">Desired job position</label>
                    <input id="inputHeadline" type="text" oninput="updatePersonal()" placeholder="e.g. Data Scientist" class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-2 px-3"/>
                  </div>
                  <div class="flex items-center space-x-1.5 pb-2">
                    <input id="inputUseHeadline" type="checkbox" onchange="updatePersonal()" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4"/>
                    <label for="inputUseHeadline" class="text-xs text-gray-500 select-none whitespace-nowrap">Use as headline</label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Row 2: Email & Phone -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Email address</label>
                <input id="inputEmail" type="email" oninput="updatePersonal()" class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-2 px-3"/>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Phone number</label>
                <input id="inputPhone" type="tel" oninput="updatePersonal()" class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-2 px-3"/>
              </div>
            </div>

            <!-- Row 3: Address -->
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Address</label>
              <input id="inputAddress" type="text" oninput="updatePersonal()" class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-2 px-3"/>
            </div>

            <!-- Row 4: Postcode & City -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Postcode</label>
                <input id="inputPostcode" type="text" oninput="updatePersonal()" class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-2 px-3"/>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">City</label>
                <input id="inputCity" type="text" oninput="updatePersonal()" class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-2 px-3"/>
              </div>
            </div>

            <!-- Row 5: Date of birth -->
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Date of birth</label>
              <input id="inputDob" type="text" oninput="updatePersonal()" placeholder="10/19/2003" class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-2 px-3"/>
            </div>

            <!-- Dynamic Additional Fields Area -->
            <div id="extraFieldsArea" class="space-y-3 pt-1"></div>

            <!-- Extra Fields Add Pills -->
            <div class="flex flex-wrap gap-2 pt-2">
              <button onclick="addExtraField('Place of birth')" type="button" class="inline-flex items-center space-x-1 px-3 py-1 border border-gray-300 hover:border-gray-500 rounded-full text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 transition">
                <span>+ Place of birth</span>
              </button>
              <button onclick="addExtraField('Driving licence')" type="button" class="inline-flex items-center space-x-1 px-3 py-1 border border-gray-300 hover:border-gray-500 rounded-full text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 transition">
                <span>+ Driving licence</span>
              </button>
              <button onclick="addExtraField('Gender')" type="button" class="inline-flex items-center space-x-1 px-3 py-1 border border-gray-300 hover:border-gray-500 rounded-full text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 transition">
                <span>+ Gender</span>
              </button>
              <button onclick="addExtraField('Nationality')" type="button" class="inline-flex items-center space-x-1 px-3 py-1 border border-gray-300 hover:border-gray-500 rounded-full text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 transition">
                <span>+ Nationality</span>
              </button>
              <button onclick="addExtraField('Marital status')" type="button" class="inline-flex items-center space-x-1 px-3 py-1 border border-gray-300 hover:border-gray-500 rounded-full text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 transition">
                <span>+ Marital status</span>
              </button>
              <button onclick="addExtraField('Website')" type="button" class="inline-flex items-center space-x-1 px-3 py-1 border border-gray-300 hover:border-gray-500 rounded-full text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 transition">
                <span>+ Website</span>
              </button>
              <button onclick="addExtraField('LinkedIn')" type="button" class="inline-flex items-center space-x-1 px-3 py-1 border border-gray-300 hover:border-gray-500 rounded-full text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 transition">
                <span>+ LinkedIn</span>
              </button>
              <button onclick="addCustomExtraFieldInline()" type="button" class="inline-flex items-center space-x-1 px-3 py-1 border border-gray-300 hover:border-gray-500 rounded-full text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 transition">
                <span>+ Custom field</span>
              </button>
            </div>
          </div>
        </div>

        <!-- DRAGGABLE SECTIONS CONTAINER -->
        <div id="dynamicSectionsList" class="space-y-6">

          <!-- SECTION: COMPÉTENCES -->
          <div id="skillsSectionBlock" class="section-block border-b border-gray-200 pb-5 transition-all" draggable="true" data-sec-id="skills">
            <div class="flex items-center justify-between cursor-pointer group">
              <div class="flex items-center space-x-2">
                <span class="text-gray-400 hover:text-gray-600 cursor-grab flex items-center drag-handle" title="Drag to reorder section">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm6-8a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Z"></path>
                  </svg>
                </span>
                <h2 class="text-base font-bold tracking-wide text-gray-900 uppercase select-none">
                  Compétences
                </h2>
              </div>
              <div class="flex items-center space-x-2">
                <button onclick="toggleSection('skillsBody')" aria-label="Toggle Compétences Section" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-500 hover:border-gray-400 hover:text-gray-700 transition" type="button">
                  <svg id="skillsChevron" class="w-4 h-4 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M19 9l-7 7-7-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                  </svg>
                </button>
              </div>
            </div>

            <div id="skillsBody" class="space-y-4 pt-3">
              <div id="skillsItemsList" class="space-y-3"></div>
              <div class="flex items-center justify-between pt-1">
                <button onclick="addSkillInline()" class="inline-flex items-center space-x-1.5 px-4 py-2 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition" type="button">
                  <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                  </svg>
                  <span>Add skill category</span>
                </button>
                <button onclick="suggestAISkills()" class="inline-flex items-center space-x-2 px-4 py-2 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition" type="button">
                  <svg class="w-4 h-4 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 2a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 0110 2zm0 13a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 0110 15zm8-5a.75.75 0 01-.75.75h-1.5a.75.75 0 010-1.5h1.5A.75.75 0 0118 10zM5 10a.75.75 0 01-.75.75h-1.5a.75.75 0 010-1.5h1.5A.75.75 0 015 10zm10.657-5.657a.75.75 0 010 1.06l-1.06 1.061a.75.75 0 11-1.062-1.06l1.061-1.061a.75.75 0 011.061 0zm-9.193 9.192a.75.75 0 010 1.061l-1.06 1.06a.75.75 0 11-1.061-1.06l1.06-1.061a.75.75 0 011.061 0zm9.193 0a.75.75 0 01-1.061 0l-1.06-1.06a.75.75 0 111.06-1.061l1.061 1.06a.75.75 0 010 1.061zM6.464 4.343a.75.75 0 01-1.06 0l-1.061-1.06A.75.75 0 015.404 2.22l1.06 1.061a.75.75 0 010 1.06z"></path>
                  </svg>
                  <span>AI suggestions</span>
                </button>
              </div>
            </div>
          </div>

          <!-- SECTION: LANGUES (Active & Expanded) -->
          <div class="section-block space-y-4 border-b border-gray-200 pb-5" draggable="true" data-sec-id="languages">
            <!-- Section Title with drag grip, more options, and collapse toggles -->
            <div class="flex items-center justify-between pt-1">
              <div class="flex items-center space-x-2">
                <span class="text-gray-400 hover:text-gray-600 cursor-grab flex items-center drag-handle" title="Drag to reorder section">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm6-8a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Z"></path>
                  </svg>
                </span>
                <h2 class="text-base font-bold tracking-wide text-gray-900 uppercase select-none">
                  Langues
                </h2>
              </div>
              <div class="flex items-center space-x-2">
                <button onclick="toggleSection('languagesBody')" aria-label="Collapse Section" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-500 hover:text-gray-700 hover:border-gray-400 transition" type="button">
                  <svg id="languagesChevron" class="w-4 h-4 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M5 15l7-7 7 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Language Items Cards List -->
            <div id="languagesBody" class="space-y-3 pt-2">
              <div id="languagesList" class="space-y-3" data-purpose="language-items-list"></div>

              <!-- Action Button for Language: Add Language -->
              <div class="flex items-center justify-start pt-2">
                <button onclick="addLanguageInline()" class="inline-flex items-center space-x-1.5 px-4 py-2 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition" type="button">
                  <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                  </svg>
                  <span>Add language</span>
                </button>
              </div>
            </div>
          </div>

          <!-- SECTION: FORMATION -->
          <div class="section-block space-y-4 border-b border-gray-200 pb-5" draggable="true" data-sec-id="education">
            <div class="flex items-center justify-between pt-1">
              <div class="flex items-center space-x-2">
                <span class="text-gray-400 hover:text-gray-600 cursor-grab flex items-center drag-handle" title="Drag to reorder section">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm6-8a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Z"></path>
                  </svg>
                </span>
                <h2 class="text-base font-bold tracking-wide text-gray-900 uppercase select-none">
                  Formation
                </h2>
              </div>
              <div class="flex items-center space-x-2">
                <button onclick="toggleSection('educationBody')" aria-label="Collapse Section" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-500 hover:text-gray-700 hover:border-gray-400 transition" type="button">
                  <svg id="educationChevron" class="w-4 h-4 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M5 15l7-7 7 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                  </svg>
                </button>
              </div>
            </div>

            <div id="educationBody" class="space-y-3 pt-2">
              <div id="educationList" class="space-y-3"></div>
              <div class="flex items-center justify-start pt-2">
                <button onclick="addEducationInline()" class="inline-flex items-center space-x-1.5 px-4 py-2 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition" type="button">
                  <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                  </svg>
                  <span>Add education</span>
                </button>
              </div>
            </div>
          </div>

          <!-- SECTION: PROJETS -->
          <div class="section-block space-y-4 border-b border-gray-200 pb-5" draggable="true" data-sec-id="projects">
            <div class="flex items-center justify-between pt-1">
              <div class="flex items-center space-x-2">
                <span class="text-gray-400 hover:text-gray-600 cursor-grab flex items-center drag-handle" title="Drag to reorder section">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm6-8a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Z"></path>
                  </svg>
                </span>
                <h2 class="text-base font-bold tracking-wide text-gray-900 uppercase select-none">
                  Projets
                </h2>
              </div>
              <div class="flex items-center space-x-2">
                <button onclick="toggleSection('projectsBody')" aria-label="Collapse Section" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-500 hover:text-gray-700 hover:border-gray-400 transition" type="button">
                  <svg id="projectsChevron" class="w-4 h-4 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M5 15l7-7 7 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                  </svg>
                </button>
              </div>
            </div>

            <div id="projectsBody" class="space-y-3 pt-2">
              <div id="projectsList" class="space-y-3"></div>
              <div class="flex items-center justify-start pt-2">
                <button onclick="addProjectInline()" class="inline-flex items-center space-x-1.5 px-4 py-2 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition" type="button">
                  <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                  </svg>
                  <span>Add project</span>
                </button>
              </div>
            </div>
          </div>

          <!-- SECTION: PROFIL -->
          <div class="section-block space-y-4 border-b border-gray-200 pb-5" draggable="true" data-sec-id="profile">
            <div class="flex items-center justify-between pt-1">
              <div class="flex items-center space-x-2">
                <span class="text-gray-400 hover:text-gray-600 cursor-grab flex items-center drag-handle" title="Drag to reorder section">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm6-8a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Z"></path>
                  </svg>
                </span>
                <h2 class="text-base font-bold tracking-wide text-gray-900 uppercase select-none">
                  Profil
                </h2>
              </div>
              <div class="flex items-center space-x-2">
                <button onclick="toggleSection('profileBody')" aria-label="Collapse Section" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-500 hover:text-gray-700 hover:border-gray-400 transition" type="button">
                  <svg id="profileChevron" class="w-4 h-4 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M5 15l7-7 7 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                  </svg>
                </button>
              </div>
            </div>

            <div id="profileBody" class="space-y-3 pt-2">
              <div class="relative">
                <textarea id="inputSummary" oninput="updateSummary()" rows="4" class="w-full text-sm rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 p-3 leading-relaxed transition-all" placeholder="Write a compelling summary..."></textarea>
                <div id="summaryEmptyHint" class="hidden mt-1.5 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-md p-2 flex items-center space-x-1.5 animate-fadeIn">
                  <span class="text-amber-500 font-bold">⚠️</span>
                  <span>Please enter your summary first so the AI can enhance it!</span>
                </div>
              </div>
              <div class="flex items-center justify-end">
                <button id="btnImproveSummary" onclick="improveAISummary()" class="inline-flex items-center space-x-2 px-4 py-1.5 border border-gray-300 hover:border-blue-500 hover:text-blue-600 rounded-full text-xs font-medium text-gray-700 bg-white hover:bg-blue-50/50 shadow-sm transition" type="button">
                  <span id="btnImproveSummaryText">✨ Improve with AI</span>
                </button>
              </div>
            </div>
          </div>

          <!-- SECTION: HOBBIES (Hidden from left list by default, can be added from bottom pills) -->
          <div id="hobbiesSectionBlock" class="section-block space-y-4 hidden" draggable="true" data-sec-id="hobbies">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <span class="text-gray-400 hover:text-gray-600 cursor-grab flex items-center drag-handle" title="Drag to reorder section">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm6-8a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Z"></path>
                  </svg>
                </span>
                <h2 class="text-base font-bold tracking-tight text-gray-700 select-none">
                  Hobbies
                </h2>
              </div>
              <div class="flex items-center space-x-2">
                <button onclick="document.getElementById('hobbyInlineInput').focus()" aria-label="Add Hobbies" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-500 hover:text-gray-800 hover:border-gray-500 transition" type="button">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                  </svg>
                </button>
                <button onclick="removeHobbiesSection()" class="text-xs text-gray-400 hover:text-red-600 transition" title="Remove Hobbies">✕</button>
              </div>
            </div>
            <div class="flex items-center gap-2 pt-1">
              <input type="text" id="hobbyInlineInput" placeholder="Add a hobby and press Enter..."
                onkeydown="if(event.key==='Enter') addHobbyFromInput()"
                class="text-xs rounded-full border border-gray-300 focus:border-blue-500 focus:ring-blue-500 px-3 py-1.5 flex-1"/>
              <button onclick="addHobbyFromInput()" type="button" class="px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded-full font-medium transition">Add</button>
            </div>
            <div id="hobbiesChips" class="flex flex-wrap gap-2 pt-1"></div>
          </div>

        </div>

        <div class="border-t border-gray-200"></div>

        <div class="space-y-3 pt-1" data-purpose="add-section-pills">
          <div class="flex flex-wrap gap-2.5">
            <button data-pill-sec="hobbies" onclick="addNewSection('Hobbies', this)" class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-normal text-gray-800 bg-white hover:bg-gray-50 transition" type="button">
              <svg class="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
              <span>Hobbies</span>
            </button>
            <button data-pill-sec="courses" onclick="addNewSection('Courses', this)" class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-normal text-gray-800 bg-white hover:bg-gray-50 transition" type="button">
              <svg class="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
              <span>Courses</span>
            </button>
            <button data-pill-sec="internships" onclick="addNewSection('Internships', this)" class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-normal text-gray-800 bg-white hover:bg-gray-50 transition" type="button">
              <svg class="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
              <span>Internships</span>
            </button>
            <button data-pill-sec="extracurricular_activities" onclick="addNewSection('Extracurricular activities', this)" class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-normal text-gray-800 bg-white hover:bg-gray-50 transition" type="button">
              <svg class="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
              <span>Extracurricular activities</span>
            </button>
            <button data-pill-sec="qualities" onclick="addNewSection('Qualities', this)" class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-normal text-gray-800 bg-white hover:bg-gray-50 transition" type="button">
              <svg class="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
              <span>Qualities</span>
            </button>
            <button data-pill-sec="certificates" onclick="addNewSection('Certificates', this)" class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-normal text-gray-800 bg-white hover:bg-gray-50 transition" type="button">
              <svg class="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
              <span>Certificates</span>
            </button>
            <button data-pill-sec="achievements" onclick="addNewSection('Achievements', this)" class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-normal text-gray-800 bg-white hover:bg-gray-50 transition" type="button">
              <svg class="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
              <span>Achievements</span>
            </button>
            <button data-pill-sec="signature" onclick="addNewSection('Signature', this)" class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-normal text-gray-800 bg-white hover:bg-gray-50 transition" type="button">
              <svg class="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
              <span>Signature</span>
            </button>
            <button data-pill-sec="footer" onclick="addNewSection('Footer', this)" class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-normal text-gray-800 bg-white hover:bg-gray-50 transition" type="button">
              <svg class="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
              <span>Footer</span>
            </button>
            <!-- Custom section with dropdown indicator -->
            <button onclick="promptCustomSection()" class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-normal text-gray-800 bg-white hover:bg-gray-50 transition" type="button">
              <svg class="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
              <span>Custom section</span>
              <svg class="w-3.5 h-3.5 text-gray-500 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M19 9l-7 7-7-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
            </button>
          </div>
        </div>

      </div>

      <!-- BOTTOM BAR: Download Button Action Row -->
      <div class="p-6 border-t border-gray-100 flex items-center justify-end bg-white" data-purpose="editor-action-footer">
        <button onclick="downloadResume()" class="inline-flex items-center space-x-2.5 px-6 py-3 rounded-full bg-blue-600 hover:bg-blue-700 text-white font-semibold text-base shadow-sm hover:shadow transition duration-150 ease-in-out active:scale-95" type="button">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
          </svg>
          <span>Download</span>
        </button>
      </div>
    </aside>
    <!-- END: LeftEditorPanel -->

    <!-- BEGIN: RightLivePreviewPanel -->
    <section class="hidden lg:flex flex-1 overflow-y-auto p-8 lg:p-10 items-start justify-center transition-all" style="background:#e8edf2;" data-purpose="resume-live-preview">
      <!-- Resume Sheet A4 — exact PDF style -->
      <div id="resumeSheet" class="shadow-paper rounded-sm select-none transition-all flex overflow-hidden" style="width:595px;min-height:842px;font-family:'Roboto','Arial',sans-serif;">

        <!-- LEFT DARK SIDEBAR -->
        <div id="previewSidebar" style="width:202px;min-height:842px;background:#1F3855;color:#fff;flex-shrink:0;display:flex;flex-direction:column;padding:0;">

          <!-- Name + Title block (top of sidebar) -->
          <div style="padding:24px 20px 16px 20px;text-align:center;">
            <!-- Profile photo (circle) -->
            <div id="previewPhotoContainer" style="margin:0 auto 12px auto;width:80px;height:80px;border-radius:50%;overflow:hidden;border:3px solid rgba(203,213,225,0.4);background:#2D4A6B;flex-shrink:0;">
              <img id="previewPhoto" src=""
                style="width:100%;height:100%;object-fit:cover;display:block;" alt="Profile photo" />
            </div>
            <!-- Surname big -->
            <div id="previewLastName" style="font-size:18px;font-weight:900;letter-spacing:0.04em;line-height:1.15;color:#fff;text-transform:uppercase;">MORGAN</div>
            <!-- First name big -->
            <div id="previewFirstName" style="font-size:18px;font-weight:900;letter-spacing:0.04em;line-height:1.15;color:#fff;text-transform:uppercase;">ALEX</div>
            <!-- Title -->
            <div id="previewHeadline" style="font-size:7.5px;font-weight:400;letter-spacing:0.1em;color:#CBD5E1;margin-top:6px;text-transform:uppercase;">SENIOR DATA SCIENTIST</div>
          </div>

          <!-- Separator line -->
          <div style="height:1px;background:rgba(203,213,225,0.3);margin:0 20px;"></div>

          <!-- CONTACT section -->
          <div style="padding:16px 20px 14px 20px;">
            <div style="font-size:8px;font-weight:700;letter-spacing:0.14em;color:#fff;text-transform:uppercase;margin-bottom:10px;">CONTACT</div>
            <div id="previewSidebarEmail" style="font-size:7.5px;color:#CBD5E1;margin-bottom:5px;word-break:break-all;"></div>
            <div id="previewSidebarPhone" style="font-size:7.5px;color:#CBD5E1;margin-bottom:5px;"></div>
            <div id="previewSidebarCity" style="font-size:7.5px;color:#CBD5E1;margin-bottom:5px;"></div>
            <div id="previewSidebarDob" style="font-size:7.5px;color:#CBD5E1;margin-bottom:5px;display:none;"></div>
            <div id="previewSidebarLinkedin" style="font-size:7.5px;color:#CBD5E1;margin-bottom:5px;display:none;"></div>
            <div id="previewSidebarWebsite" style="font-size:7.5px;color:#CBD5E1;margin-bottom:5px;display:none;"></div>
            <div id="previewSidebarExtras" style="display:flex;flex-direction:column;gap:4px;margin-top:2px;"></div>
          </div>

          <!-- Separator -->
          <div style="height:1px;background:rgba(203,213,225,0.3);margin:0 20px;"></div>

          <!-- SKILLS section -->
          <div style="padding:14px 20px 14px 20px;">
            <div style="font-size:8px;font-weight:700;letter-spacing:0.14em;color:#fff;text-transform:uppercase;margin-bottom:10px;">SKILLS</div>
            <div id="previewSidebarSkills" style="font-size:7.5px;color:#CBD5E1;line-height:1.7;"></div>
          </div>

          <!-- Separator -->
          <div style="height:1px;background:rgba(203,213,225,0.3);margin:0 20px;"></div>

          <!-- LANGUAGES section -->
          <div style="padding:14px 20px 14px 20px;">
            <div style="font-size:8px;font-weight:700;letter-spacing:0.14em;color:#fff;text-transform:uppercase;margin-bottom:10px;">LANGUAGES</div>
            <div id="previewSidebarLanguages" style="font-size:7.5px;color:#CBD5E1;line-height:1.9;"></div>
          </div>

          <!-- Hobbies (hidden by default) -->
          <div id="previewSidebarHobbiesBlock" style="display:none;padding:14px 20px 14px 20px;">
            <div style="height:1px;background:rgba(203,213,225,0.3);margin:0 0 14px 0;"></div>
            <div style="font-size:8px;font-weight:700;letter-spacing:0.14em;color:#fff;text-transform:uppercase;margin-bottom:10px;">HOBBIES</div>
            <div id="previewSidebarHobbies" style="font-size:7.5px;color:#CBD5E1;line-height:1.9;"></div>
          </div>
        </div>

        <!-- RIGHT MAIN CONTENT -->
        <div style="flex:1;background:#fff;display:flex;flex-direction:column;padding:28px 24px 20px 24px;min-height:842px;">

          <!-- PROFESSIONAL SUMMARY (always first in right col) -->
          <div id="previewSummaryBlock" style="margin-bottom:16px;">
            <div style="font-size:9px;font-weight:700;letter-spacing:0.16em;color:#1F3855;text-transform:uppercase;border-bottom:1.5px solid #1F3855;padding-bottom:4px;margin-bottom:8px;">PROFESSIONAL SUMMARY</div>
            <p id="previewSummaryText" style="font-size:8px;color:#374151;line-height:1.65;"></p>
          </div>

          <!-- DYNAMIC sections (Education, Projects, custom) in user-defined order -->
          <div id="previewMainCol" style="display:flex;flex-direction:column;gap:16px;flex:1;">
            <!-- Populated by renderLivePreview() -->
          </div>
        </div>

      </div>
    </section>
    <!-- END: RightLivePreviewPanel -->

  </main>
  <!-- END: MainContentSplitLayout -->

  <!-- APPLICATION SCRIPT & REAL-TIME DATA BINDINGS -->
  <script>
    // Initialize CV State from Python
    const cvData = {cv_json};
    const SAMPLE_CV_DATA = {sample_cv_json};
    const DEFAULT_AVATAR = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64' fill='%2394A3B8'><circle cx='32' cy='24' r='14'/><path d='M10 56c0-11 10-18 22-18s22 7 22 18z'/></svg>";
    let currentTemplate = 'simple'; // 'simple', 'classic' or 'executive'
    let currentZoom = 100;
    let isCvNameCustomEdited = false;

    // Populate Initial Values
    function initEditor() {{
      const extraArea = document.getElementById('extraFieldsArea');
      if (extraArea) extraArea.innerHTML = '';
      const p = cvData.personal || {{}};
      document.getElementById('inputFirstName').value = p.first_name || '';
      document.getElementById('inputLastName').value = p.last_name || '';
      document.getElementById('inputHeadline').value = p.headline || '';
      document.getElementById('inputUseHeadline').checked = p.use_headline !== false;
      document.getElementById('inputEmail').value = p.email || '';
      document.getElementById('inputPhone').value = p.phone || '';
      document.getElementById('inputAddress').value = p.address || '';
      document.getElementById('inputPostcode').value = p.postcode || '';
      document.getElementById('inputCity').value = p.city || '';
      document.getElementById('inputDob').value = p.date_of_birth || '';
      document.getElementById('inputSummary').value = cvData.summary || '';

      const tj = document.getElementById('targetJobInput');
      if (tj && cvData.target_job) {{
        tj.value = cvData.target_job;
      }}

      const headerNameInput = document.getElementById('cvNameHeaderInput');
      if (headerNameInput) {{
        if (cvData.cv_name) {{
          headerNameInput.value = cvData.cv_name;
          isCvNameCustomEdited = true;
        }} else {{
          const fn = p.first_name || 'Alex';
          const ln = p.last_name || 'Morgan';
          headerNameInput.value = `CV ${{fn}} ${{ln}}`.trim();
        }}
      }}

      const avatarSrc = p.photo_url || DEFAULT_AVATAR;
      document.getElementById('photoThumb').src = avatarSrc;
      const prevPhoto = document.getElementById('previewPhoto');
      if (prevPhoto) prevPhoto.src = avatarSrc;

      if (p.linkedin) {{
        addExtraField('LinkedIn', p.linkedin);
      }}
      if (p.website) {{
        addExtraField('Website', p.website);
      }}
      if (p.driving_licence) {{
        addExtraField('Driving licence', p.driving_licence);
      }}
      if (p.place_of_birth) {{
        addExtraField('Place of birth', p.place_of_birth);
      }}
      if (p.gender) {{
        addExtraField('Gender', p.gender);
      }}
      if (p.nationality) {{
        addExtraField('Nationality', p.nationality);
      }}
      if (p.marital_status) {{
        addExtraField('Marital status', p.marital_status);
      }}
      if (Array.isArray(p.extras)) {{
        p.extras.forEach(ex => {{
          if (ex.label && ex.value) {{
            addExtraField(ex.label, ex.value);
          }}
        }});
      }}

      if (cvData.style && cvData.style.template) {{
        selectTemplate(cvData.style.template);
      }} else {{
        selectTemplate('simple');
      }}

      renderSkillsList();
      renderLanguagesList();
      renderEducationList();
      renderProjectsList();
      renderHobbiesList();
      renderCustomSectionsList();
      renderLivePreview();
      initDragAndDrop();
    }}

    // Real-Time Update Handlers
    function updatePersonal() {{
      const p = cvData.personal;
      p.first_name = document.getElementById('inputFirstName').value;
      p.last_name = document.getElementById('inputLastName').value;
      p.headline = document.getElementById('inputHeadline').value;
      p.use_headline = document.getElementById('inputUseHeadline').checked;
      p.email = document.getElementById('inputEmail').value;
      p.phone = document.getElementById('inputPhone').value;
      p.address = document.getElementById('inputAddress').value;
      p.postcode = document.getElementById('inputPostcode').value;
      p.city = document.getElementById('inputCity').value;
      p.date_of_birth = document.getElementById('inputDob').value;

      // Collect extra fields (LinkedIn, Website, Nationality, Driving licence, etc.)
      const extraArea = document.getElementById('extraFieldsArea');
      p.linkedin = '';
      p.website = '';
      p.extras = [];
      if (extraArea) {{
        extraArea.querySelectorAll('[id^="extra_"]').forEach(div => {{
          const key = div.id.replace('extra_', '');
          const label = div.getAttribute('data-field-label') || key;
          const inp = div.querySelector('input');
          const val = inp ? inp.value.trim() : '';
          p[key] = val;
          if (val) {{
            p.extras.push({{ key, label, value: val }});
          }}
        }});
      }}

      const docTitleEl = document.getElementById('docTitle');
      if (docTitleEl) docTitleEl.textContent = `${{p.first_name || 'My'}} ${{p.last_name || 'Resume'}} - Resume 2025`;

      if (!isCvNameCustomEdited) {{
        const headerNameInput = document.getElementById('cvNameHeaderInput');
        if (headerNameInput) {{
          const fn = p.first_name || '';
          const ln = p.last_name || '';
          headerNameInput.value = `CV ${{fn}} ${{ln}}`.trim() || 'CV Untitled';
        }}
      }}

      renderLivePreview();
      flashSaved();
    }}

    function handleCvNameInput(val) {{
      isCvNameCustomEdited = true;
      cvData.cv_name = val;
      const cloud = document.getElementById('cloudSyncIcon');
      if (cloud) {{
        cloud.classList.add('text-blue-600');
        setTimeout(() => {{
          cloud.classList.remove('text-blue-600');
        }}, 600);
      }}
      flashSaved();
    }}

    function updateSummary() {{
      const el = document.getElementById('inputSummary');
      cvData.summary = el.value;
      if (el.value.trim().length > 0) {{
        const hint = document.getElementById('summaryEmptyHint');
        if (hint) hint.classList.add('hidden');
        el.classList.remove('border-amber-400', 'ring-2', 'ring-amber-300', 'bg-amber-50');
      }}
      renderLivePreview();
      flashSaved();
    }}

    function handleJobInput() {{
      const tj = document.getElementById('targetJobInput');
      if (tj) {{
        cvData.target_job = tj.value;
        flashSaved();
      }}
    }}

    function skillItemName(sk) {{
      if (sk == null) return '';
      if (typeof sk === 'string') return sk.trim();
      return String(sk.name || sk.skill || sk.title || '').trim();
    }}

    function skillCategoryKey(cat) {{
      return String(cat || '')
        .toLowerCase()
        .replace(/[&/_(),.-]+/g, ' ')
        .replace(/\\b(skills?|competenc(?:e|es|y)|competences?)\\b/g, '')
        .replace(/\\s+/g, ' ')
        .trim();
    }}

    function isAiSkillName(name) {{
      const key = String(name || '').toLowerCase();
      return !!(key && (cvData.ai_skill_names || []).includes(key));
    }}

    function markAiSkillName(name) {{
      if (!cvData.ai_skill_names) cvData.ai_skill_names = [];
      const key = String(name || '').toLowerCase();
      if (key && !cvData.ai_skill_names.includes(key)) cvData.ai_skill_names.push(key);
    }}

    function unmarkAiSkillName(name) {{
      const key = String(name || '').toLowerCase();
      cvData.ai_skill_names = (cvData.ai_skill_names || []).filter(n => n !== key);
    }}

    function canonicalSkill(name) {{
      return String(name || '')
        .toLowerCase()
        .replace(/^apache\\s+/i, '')
        .replace(/\\.(js|py|ts)$/i, '')
        .replace(/[-_\\s/()]+/g, '')
        .trim();
    }}

    function cvAlreadyHasSkill(name) {{
      if (!cvData.skills || cvData.skills.length === 0) return false;
      const canon = canonicalSkill(name);
      if (!canon) return false;
      return cvData.skills.some(g =>
        (g.items || []).some(sk => {{
          const c = canonicalSkill(skillItemName(sk));
          return c === canon;
        }})
      );
    }}

    function findSkillGroupByCategory(category) {{
      const key = skillCategoryKey(category);
      if (!key) return null;
      return (cvData.skills || []).find(g => skillCategoryKey(g.category) === key) || null;
    }}

    function findBestCategoryForSkill(skillName, suggestedCategory) {{
      const sName = String(skillName || '').toLowerCase();
      const sCat = String(suggestedCategory || '').trim();

      // 1. Direct match with existing category on CV (if suggestedCategory was provided and is not generic)
      if (sCat && !/^(keywords?|technical|skills?|other|tools?)$/i.test(sCat)) {{
        const direct = findSkillGroupByCategory(sCat);
        if (direct) return direct.category;
      }}

      // 2. Semantic matching against each existing category on the candidate's CV
      const groups = cvData.skills || [];
      let bestGroup = null;
      let highestScore = 0;

      const domainMap = [
        {{
          terms: ['ml', 'machine learning', 'ia', 'ai', 'deep learning', 'nlp', 'llm', 'rag', 'fine tuning', 'finetuning', 'vision', 'transformer', 'hugging face', 'huggingface', 'vector', 'pytorch', 'tensorflow', 'scikit', 'model', 'training', 'diffusion', 'generative', 'prompt', 'langchain', 'llama', 'openai'],
          categoryMatch: ['machine learning', 'ia', 'ai', 'data science', 'intelligence artificielle', 'deep learning', 'modélisation', 'modeling']
        }},
        {{
          terms: ['spark', 'pyspark', 'etl', 'pipeline', 'kafka', 'airflow', 'dbt', 'hadoop', 'sql', 'nosql', 'lakehouse', 'data lake', 'warehouse', 'snowflake', 'databricks', 'flink', 'big data', 'bigdata', 'hive', 'redshift', 'bigquery'],
          categoryMatch: ['data engineering', 'ingénierie des données', 'data', 'big data', 'etl', 'pipelines']
        }},
        {{
          terms: ['mlops', 'llm ops', 'llmops', 'model deployment', 'model serving', 'ci/cd', 'cicd', 'docker', 'kubernetes', 'k8s', 'kubeflow', 'mlflow', 'wandb', 'dvc', 'terraform', 'cloud', 'aws', 'azure', 'gcp', 'devops', 'monitoring', 'infrastructure', 'ansible', 'helm'],
          categoryMatch: ['mlops', 'devops', 'cloud', 'infrastructure', 'déploiement', 'deployment', 'production']
        }},
        {{
          terms: ['power bi', 'powerbi', 'tableau', 'excel', 'bi', 'business intelligence', 'analytics', 'dashboard', 'reporting', 'kpi', 'looker', 'metabase', 'dax', 'data analysis', 'analyse'],
          categoryMatch: ['analyse', 'analytics', 'bi', 'business intelligence', 'visualisation', 'reporting']
        }},
        {{
          terms: ['python', 'r', 'scala', 'java', 'c++', 'go', 'rust', 'javascript', 'typescript', 'bash', 'c#'],
          categoryMatch: ['langages', 'languages', 'programming', 'programmation', 'code']
        }},
        {{
          terms: ['react', 'vue', 'angular', 'node', 'fastapi', 'flask', 'django', 'laravel', 'spring', 'api', 'graphql', 'html', 'css', 'tailwind', 'rest'],
          categoryMatch: ['web', 'frontend', 'backend', 'fullstack', 'développement web', 'software']
        }}
      ];

      for (const group of groups) {{
        const catNameLower = (group.category || '').toLowerCase();
        let score = 0;

        for (const domain of domainMap) {{
          const domainMatchesCat = domain.categoryMatch.some(cm => catNameLower.includes(cm));
          if (domainMatchesCat) {{
            for (const term of domain.terms) {{
              if (sName.includes(term) || term.includes(sName)) {{
                score += 3;
              }}
            }}
          }}
        }}

        (group.items || []).forEach(item => {{
          const iname = skillItemName(item).toLowerCase();
          if (iname && (sName.includes(iname) || iname.includes(sName))) {{
            score += 2;
          }}
        }});

        if (score > highestScore) {{
          highestScore = score;
          bestGroup = group;
        }}
      }}

      // If we found a good existing category match (score >= 2), place it there!
      if (bestGroup && highestScore >= 2) {{
        return bestGroup.category;
      }}

      // 3. If no existing category fits, determine a NEW clean, descriptive category name (NEVER 'Keywords', 'Technical', or 'Specialized Tools')
      if (sCat && !/^(keywords?|technical|skills?|other|tools?|specialized tools?)$/i.test(sCat)) {{
        return sCat;
      }}

      for (const domain of domainMap) {{
        for (const term of domain.terms) {{
          if (sName.includes(term) || term.includes(sName)) {{
            if (domain.categoryMatch.includes('mlops')) return 'MLOps & Deployment';
            if (domain.categoryMatch.includes('machine learning')) return 'Machine Learning & AI';
            if (domain.categoryMatch.includes('data engineering')) return 'Data Engineering';
            if (domain.categoryMatch.includes('analyse')) return 'Analytics & BI';
            if (domain.categoryMatch.includes('web')) return 'Web Development';
            if (domain.categoryMatch.includes('langages')) return 'Programming Languages';
          }}
        }}
      }}

      // Fallback: use first existing category or standard domain (NEVER 'Specialized Tools')
      if (groups.length > 0 && groups[0].category) {{
        return groups[0].category;
      }}
      return 'Machine Learning & AI';
    }}

    function ensureSkillGroup(category) {{
      if (!cvData.skills) cvData.skills = [];
      const existing = findSkillGroupByCategory(category);
      if (existing) return existing;
      const group = {{
        id: 'ai_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
        category: category,
        items: []
      }};
      cvData.skills.push(group);
      return group;
    }}

    function clearPreviousAiSkills() {{
      const aiSet = new Set(cvData.ai_skill_names || []);
      (cvData.skills || []).forEach(g => {{
        g.items = (g.items || []).filter(sk => !aiSet.has(skillItemName(sk).toLowerCase()));
      }});
      cvData.skills = (cvData.skills || []).filter(g => (g.items || []).length > 0);
      cvData.ai_skill_names = [];
    }}

    function parseJobAnalysisPayload(evt) {{
      let d = evt && (evt.data !== undefined ? evt.data : evt);
      if (typeof d === 'string') {{
        try {{ d = JSON.parse(d); }} catch (e) {{ return {{}}; }}
      }}
      if (d && d.data && (d.data.skills || d.data.suggested_skills)) d = d.data;
      return d || {{}};
    }}

    function isValidSkillName(name) {{
      if (!name || typeof name !== 'string') return false;
      const clean = name.trim();
      if (clean.length < 2 || clean.length > 35) return false;
      if (/[.!?:;\\n()\\[\\]{{}}—"']/.test(clean)) return false;
      const words = clean.split(/\\s+/);
      if (words.length > 3) return false;

      const badToken = /^(student|science|hands|into|building|actionable|insights|decisions|seeking|position|apply|my|skills|turning|support|grow|experience|master|applications|skilled|predictive|responsible|designing|work|working|team|company|candidate|strong|knowledge|good|solid|ability|proven|understanding|profile|summary|job|description|various|related|such|as|in|at|by|with|for|of|from|to)$/i;

      if (words.length === 1) {{
        if (badToken.test(clean)) return false;
        if (clean.length < 2 && !/^(r|c)$/i.test(clean)) return false;
        return true;
      }}

      for (const w of words) {{
        const wLower = w.toLowerCase();
        if (/^(hands|into|building|actionable|insights|decisions|seeking|position|apply|my|skills|turning|support|grow|experience|master|applications|skilled|predictive|in|at|by|from|to|with|for|of)$/.test(wLower)) {{
          return false;
        }}
      }}

      return true;
    }}

    function collectSuggestedSkills(d, query) {{
      const raw = Array.isArray(d.skills) ? d.skills
        : (Array.isArray(d.suggested_skills) ? d.suggested_skills : []);
      const out = [];
      const seen = new Set();

      raw.forEach(s => {{
        const name = skillItemName(s);
        if (!name || !isValidSkillName(name)) return;
        if (cvAlreadyHasSkill(name)) return;
        const key = canonicalSkill(name);
        if (seen.has(key)) return;
        seen.add(key);

        let rawCat = (typeof s === 'object' && (s.category || s.group)) ? String(s.category || s.group).trim() : '';
        if (/^(specialized tools?|keywords?|other|technical|skills?)$/i.test(rawCat)) {{
          rawCat = '';
        }}
        const bestCat = findBestCategoryForSkill(name, rawCat);
        out.push({{ name, category: bestCat }});
      }});

      // Note: ONLY skills validated by the LLM are accepted. Naive query word-splitting is strictly forbidden.
      // If CV skills are empty and LLM returned very few skills, supply standard core baseline (at least 5 per category):
      const isCvEmpty = !cvData.skills || cvData.skills.length === 0 || cvData.skills.every(g => !g.items || g.items.length === 0);
      if (isCvEmpty && out.length < 15) {{
        const qLower = String(query || '').toLowerCase();
        const roleDefaults = [];
        if (qLower.includes('data') || qLower.includes('ml') || qLower.includes('ai') || qLower.includes('learn')) {{
          roleDefaults.push(
            // Machine Learning & AI
            {{ name: 'PyTorch', category: 'Machine Learning & AI' }},
            {{ name: 'TensorFlow', category: 'Machine Learning & AI' }},
            {{ name: 'Scikit-Learn', category: 'Machine Learning & AI' }},
            {{ name: 'Deep Learning', category: 'Machine Learning & AI' }},
            {{ name: 'NLP', category: 'Machine Learning & AI' }},
            // Data Engineering
            {{ name: 'SQL', category: 'Data Engineering' }},
            {{ name: 'Apache Spark', category: 'Data Engineering' }},
            {{ name: 'PySpark', category: 'Data Engineering' }},
            {{ name: 'Data Pipelines', category: 'Data Engineering' }},
            {{ name: 'ETL', category: 'Data Engineering' }},
            // MLOps & Deployment
            {{ name: 'Docker', category: 'MLOps & Deployment' }},
            {{ name: 'Kubernetes', category: 'MLOps & Deployment' }},
            {{ name: 'MLOps', category: 'MLOps & Deployment' }},
            {{ name: 'CI/CD Pipelines', category: 'MLOps & Deployment' }},
            {{ name: 'Model Serving', category: 'MLOps & Deployment' }},
            // Analytics & BI
            {{ name: 'Power BI', category: 'Analytics & BI' }},
            {{ name: 'Tableau', category: 'Analytics & BI' }},
            {{ name: 'Data Analysis', category: 'Analytics & BI' }},
            {{ name: 'Pandas', category: 'Analytics & BI' }},
            {{ name: 'KPI Dashboards', category: 'Analytics & BI' }}
          );
        }} else {{
          roleDefaults.push(
            {{ name: 'Python', category: 'Programming Languages' }},
            {{ name: 'TypeScript', category: 'Programming Languages' }},
            {{ name: 'SQL', category: 'Programming Languages' }},
            {{ name: 'Bash', category: 'Programming Languages' }},
            {{ name: 'Git', category: 'Development Tools' }},
            {{ name: 'Docker', category: 'MLOps & Deployment' }},
            {{ name: 'CI/CD Pipelines', category: 'MLOps & Deployment' }},
            {{ name: 'Linux', category: 'MLOps & Deployment' }}
          );
        }}

        roleDefaults.forEach(item => {{
          if (!isValidSkillName(item.name)) return;
          const key = canonicalSkill(item.name);
          if (!seen.has(key) && !cvAlreadyHasSkill(item.name)) {{
            seen.add(key);
            out.push({{ name: item.name, category: findBestCategoryForSkill(item.name, item.category) }});
          }}
        }});
      }}

      return out;
    }}

    function applyAiSkillsToCv(suggested) {{
      clearPreviousAiSkills();
      let added = 0;
      const placedSummary = {{}};

      if (!cvData.skills) cvData.skills = [];

      // Permanently remove any category named 'Specialized Tools'
      cvData.skills = cvData.skills.filter(g => {{
        const cat = (g.category || '').trim();
        return cat && !/^(specialized tools?)$/i.test(cat);
      }});

      // Enforce MAXIMUM 4 CATEGORIES TOTAL
      const activeCats = [];
      cvData.skills.forEach(g => {{
        if (g.category && !activeCats.includes(g.category) && activeCats.length < 4) {{
          activeCats.push(g.category);
        }}
      }});

      // Determine categories for new skills, capped at 4 total categories
      suggested.forEach(item => {{
        if (!item.name || !isValidSkillName(item.name)) return;
        if (cvAlreadyHasSkill(item.name)) return;
        const targetCat = item.category || 'Machine Learning & AI';
        if (!activeCats.includes(targetCat) && activeCats.length < 4) {{
          activeCats.push(targetCat);
        }}
      }});

      if (activeCats.length === 0) {{
        activeCats.push('Machine Learning & AI', 'Data Engineering', 'MLOps & Deployment', 'Analytics & BI');
      }}

      suggested.forEach(item => {{
        if (!item.name || !isValidSkillName(item.name)) return;
        if (cvAlreadyHasSkill(item.name)) return;

        let targetCat = item.category;
        if (!activeCats.includes(targetCat)) {{
          targetCat = activeCats[0];
          const sLower = item.name.toLowerCase();
          for (const ac of activeCats) {{
            const acLower = ac.toLowerCase();
            if ((sLower.includes('python') || sLower.includes('sql') || sLower.includes('java') || sLower.includes('c++')) && (acLower.includes('program') || acLower.includes('langage'))) {{
              targetCat = ac; break;
            }}
            if ((sLower.includes('spark') || sLower.includes('etl') || sLower.includes('pipeline') || sLower.includes('data')) && acLower.includes('data')) {{
              targetCat = ac; break;
            }}
            if ((sLower.includes('docker') || sLower.includes('deploy') || sLower.includes('cloud') || sLower.includes('mlops') || sLower.includes('k8s')) && (acLower.includes('mlops') || acLower.includes('cloud') || acLower.includes('infra') || acLower.includes('deploy'))) {{
              targetCat = ac; break;
            }}
            if ((sLower.includes('torch') || sLower.includes('learn') || sLower.includes('ai') || sLower.includes('vision') || sLower.includes('nlp')) && (acLower.includes('machine') || acLower.includes('ai') || acLower.includes('ia'))) {{
              targetCat = ac; break;
            }}
          }}
        }}

        const group = ensureSkillGroup(targetCat);
        if (!group.items) group.items = [];
        // Allow up to 7 items per category
        if (group.items.length < 7) {{
          group.items.push(item.name);
          markAiSkillName(item.name);
          added += 1;
          placedSummary[group.category] = (placedSummary[group.category] || 0) + 1;
        }}
      }});

      // Guarantee AT LEAST 5 verified skills for each of the categories
      const domainBaselines = [
        {{
          match: ['machine learning', 'ia', 'ai', 'data science', 'deep learning'],
          skills: ['PyTorch', 'TensorFlow', 'Scikit-Learn', 'Deep Learning', 'NLP', 'Transformers', 'Hugging Face']
        }},
        {{
          match: ['data engineering', 'big data', 'données', 'databases', 'data pipelines', 'etl'],
          skills: ['SQL', 'Apache Spark', 'PySpark', 'Data Pipelines', 'ETL', 'Kafka', 'PostgreSQL', 'Snowflake']
        }},
        {{
          match: ['mlops', 'devops', 'cloud', 'infrastructure', 'déploiement', 'deployment', 'production'],
          skills: ['Docker', 'Kubernetes', 'MLOps', 'CI/CD Pipelines', 'Model Serving', 'Git', 'AWS', 'Linux']
        }},
        {{
          match: ['analyse', 'analytics', 'bi', 'business intelligence', 'visualisation', 'reporting'],
          skills: ['Power BI', 'Tableau', 'Data Analysis', 'Pandas', 'NumPy', 'SQL', 'KPI Dashboards']
        }},
        {{
          match: ['langages', 'languages', 'programming', 'programmation', 'code'],
          skills: ['Python', 'SQL', 'R', 'C++', 'Java', 'Bash', 'TypeScript']
        }},
        {{
          match: ['web', 'frontend', 'backend', 'fullstack', 'développement web', 'software'],
          skills: ['FastAPI', 'Flask', 'REST APIs', 'Node.js', 'React', 'Docker', 'PostgreSQL']
        }}
      ];

      (cvData.skills || []).forEach(group => {{
        if (!group.items) group.items = [];
        if (group.items.length < 5) {{
          const catLower = (group.category || '').toLowerCase();
          const base = domainBaselines.find(b => b.match.some(m => catLower.includes(m))) || domainBaselines[0];
          for (const sName of base.skills) {{
            if (group.items.length >= 5) break;
            const alreadyInGroup = group.items.some(x => skillItemName(x).toLowerCase() === sName.toLowerCase());
            if (!alreadyInGroup && !cvAlreadyHasSkill(sName)) {{
              group.items.push(sName);
              markAiSkillName(sName);
              added += 1;
              placedSummary[group.category] = (placedSummary[group.category] || 0) + 1;
            }}
          }}
        }}
      }});

      // Hard safety check: cvData.skills must NEVER exceed 4 categories total
      if (cvData.skills.length > 4) {{
        cvData.skills = cvData.skills.slice(0, 4);
      }}

      const skillsBody = document.getElementById('skillsBody');
      if (skillsBody) skillsBody.classList.remove('hidden');
      renderSkillsList();
      renderLivePreview();
      flashSaved();
      return {{ added, placedSummary }};
    }}

    function handleJobAnalysisEvent(evt, hint, query) {{
      if (!evt) return;
      if (evt.type === 'progress' && hint) {{
        hint.textContent = '⚡ ' + (evt.message || 'Analyzing...');
      }} else if (evt.type === 'result') {{
        const d = parseJobAnalysisPayload(evt);
        const suggested = collectSuggestedSkills(d, query);
        const roleName = d.role_detected || d.role_title || '';
        const {{ added, placedSummary }} = applyAiSkillsToCv(suggested);
        if (added > 0) {{
          const catList = Object.keys(placedSummary).map(c => `${{c}} (+${{placedSummary[c]}})`).join(', ');
          const msg = '✅ Added ' + added + ' AI skills into categories: ' + catList + '. Highlighted in cyan ✨';
          if (hint) hint.textContent = msg;
          showToast('🎯 Added ' + added + ' skills into matching categories!');
          scrollToSkillsSection();
        }} else if (cvData.skills && cvData.skills.length > 0) {{
          hint.textContent = '✅ Analysis complete! All suggested skills are already present on your CV.';
          scrollToSkillsSection();
        }} else {{
          hint.textContent = '✅ Analysis complete!';
          scrollToSkillsSection();
        }}
      }} else if (evt.type === 'error' && hint) {{
        hint.textContent = '⚠️ ' + evt.message;
      }}
    }}

    async function analyzeTargetJob() {{
      const tj = document.getElementById('targetJobInput');
      const val = tj ? tj.value.trim() : '';
      if (!val) {{
        showToast('Please describe your target job first.');
        return;
      }}
      const hint = document.getElementById('jobInputHint');
      if (hint) hint.textContent = '⚡ Connecting to AI agent (searching the web & analyzing requirements)...';

      const existingCategories = (cvData.skills || []).map(g => ({{
        name: g.category || '',
        skills: (g.items || []).map(s => skillItemName(s)).filter(Boolean)
      }})).filter(g => g.name);

      const currentSkills = [];
      existingCategories.forEach(g => {{
        g.skills.forEach(s => currentSkills.push(s));
      }});

      try {{
        const res = await fetch('http://localhost:8000/api/v1/jobs/analyze', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            query: val,
            current_skills: currentSkills,
            existing_categories: existingCategories
          }})
        }});

        if (!res.ok) throw new Error('HTTP ' + res.status);

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        const consumeBuffer = (flush) => {{
          const lines = buffer.split('\\n');
          if (!flush) buffer = lines.pop();
          else buffer = '';
          lines.forEach(line => {{
            if (!line || !line.startsWith('data: ')) return;
            try {{
              handleJobAnalysisEvent(JSON.parse(line.slice(6)), hint, val);
            }} catch (e) {{}}
          }});
        }};

        while (true) {{
          const {{ done, value }} = await reader.read();
          if (done) {{
            buffer += decoder.decode();
            consumeBuffer(true);
            break;
          }}
          buffer += decoder.decode(value, {{ stream: true }});
          consumeBuffer(false);
        }}
      }} catch (err) {{
        console.warn('Backend unavailable, running smart categorized extractor:', err);
        const suggested = collectSuggestedSkills({{ skills: [], keywords: [] }}, val);
        const {{ added, placedSummary }} = applyAiSkillsToCv(suggested);
        const catList = Object.keys(placedSummary).map(c => `${{c}} (+${{placedSummary[c]}})`).join(', ');
        if (hint) hint.textContent = '✨ Placed ' + added + ' skills into: ' + (catList || 'skills') + ' (Tip: run python run.py for live DuckDuckGo web search)';
        showToast('🎯 Placed ' + added + ' AI skills into matching categories!');
        flashSaved();
        scrollToSkillsSection();
      }}
    }}

    function scrollToSkillsSection() {{
      setTimeout(() => {{
        const skillsSec = document.getElementById('skillsSectionBlock') || document.querySelector('[data-sec-id="skills"]') || document.getElementById('skillsBody');
        if (skillsSec) {{
          const body = document.getElementById('skillsBody');
          if (body && body.classList.contains('hidden')) {{
            toggleSection('skillsBody');
          }}
          skillsSec.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
          skillsSec.classList.add('ring-2', 'ring-cyan-400', 'rounded-xl');
          setTimeout(() => skillsSec.classList.remove('ring-2', 'ring-cyan-400', 'rounded-xl'), 2500);
        }}
      }}, 500);
    }}

    function flashSaved() {{
      const badge = document.getElementById('saveBadge');
      if (badge) {{
        badge.textContent = 'Saving...';
        badge.className = 'ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-normal bg-blue-50 text-blue-700 border border-blue-200';
        clearTimeout(window._saveTimer);
        window._saveTimer = setTimeout(() => {{
          badge.textContent = 'Saved';
          badge.className = 'ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-normal bg-green-50 text-green-700 border border-green-200';
        }}, 500);
      }}
    }}

    // Render Lists in Editor (Interactive Inline Editable Cards)
    function renderLanguagesList() {{
      const container = document.getElementById('languagesList');
      container.innerHTML = '';
      (cvData.languages || []).forEach((lang, idx) => {{
        const card = document.createElement('div');
        card.className = 'border border-gray-300 rounded-xl p-3.5 bg-white shadow-card-subtle flex items-center justify-between gap-3';
        card.innerHTML = `
          <div class="grid grid-cols-2 gap-3 flex-1">
            <div>
              <label class="block text-[11px] font-medium text-gray-500 mb-0.5">Language</label>
              <input type="text" data-field="name" value="${{lang.name || ''}}" placeholder="e.g. Spanish, German"
                oninput="updateLanguageField(${{idx}}, 'name', this.value)"
                class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-1.5 px-3"/>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-gray-500 mb-0.5">Level</label>
              <select onchange="updateLanguageField(${{idx}}, 'level', this.value)"
                class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-1.5 px-3 bg-white">
                <option value="Native" ${{lang.level === 'Native' ? 'selected' : ''}}>Native</option>
                <option value="Very good" ${{lang.level === 'Very good' ? 'selected' : ''}}>Very good</option>
                <option value="Good" ${{lang.level === 'Good' || !lang.level ? 'selected' : ''}}>Good</option>
                <option value="Advanced" ${{lang.level === 'Advanced' ? 'selected' : ''}}>Advanced</option>
                <option value="Intermediate" ${{lang.level === 'Intermediate' ? 'selected' : ''}}>Intermediate</option>
                <option value="Basic" ${{lang.level === 'Basic' ? 'selected' : ''}}>Basic</option>
              </select>
            </div>
          </div>
          <button onclick="deleteLanguage(${{idx}})" aria-label="Delete" class="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center text-gray-400 hover:bg-red-50 hover:text-red-600 hover:border-red-300 transition flex-shrink-0" type="button" title="Delete">
            ✕
          </button>
        `;
        container.appendChild(card);
      }});
    }}

    function updateLanguageField(idx, field, val) {{
      if (cvData.languages && cvData.languages[idx]) {{
        cvData.languages[idx][field] = val;
        renderLivePreview();
        flashSaved();
      }}
    }}

    function addLanguageInline() {{
      if (!cvData.languages) cvData.languages = [];
      cvData.languages.push({{ name: '', level: 'Good' }});
      renderLanguagesList();
      renderLivePreview();
      flashSaved();
      setTimeout(() => {{
        const inputs = document.querySelectorAll('#languagesList input[data-field="name"]');
        if (inputs.length) inputs[inputs.length - 1].focus();
      }}, 50);
    }}

    function deleteLanguage(idx) {{
      cvData.languages.splice(idx, 1);
      renderLanguagesList();
      renderLivePreview();
      flashSaved();
    }}

    function renderEducationList() {{
      const container = document.getElementById('educationList');
      container.innerHTML = '';
      (cvData.education || []).forEach((edu, idx) => {{
        const card = document.createElement('div');
        card.className = 'border border-gray-300 rounded-xl p-4 bg-white shadow-card-subtle space-y-3';
        card.innerHTML = `
          <div class="flex items-center justify-between pb-1">
            <span class="font-bold text-sm text-gray-800">${{edu.degree || 'New Education'}}</span>
            <button onclick="deleteEducation(${{idx}})" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-400 hover:bg-red-50 hover:text-red-600 hover:border-red-300 transition" type="button" title="Delete">✕</button>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-[11px] font-medium text-gray-500 mb-0.5">Degree / Diploma</label>
              <input type="text" data-field="degree" value="${{edu.degree || ''}}" placeholder="e.g. Master's in Data Science"
                oninput="updateEduField(${{idx}}, 'degree', this.value)"
                class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-1.5 px-3"/>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-gray-500 mb-0.5">Institution / School</label>
              <input type="text" value="${{edu.institution || ''}}" placeholder="e.g. Stanford University"
                oninput="updateEduField(${{idx}}, 'institution', this.value)"
                class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-1.5 px-3"/>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-gray-500 mb-0.5">Start Date</label>
              <input type="text" value="${{edu.start_date || ''}}" placeholder="e.g. 2021"
                oninput="updateEduField(${{idx}}, 'start_date', this.value)"
                class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-1.5 px-3"/>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-gray-500 mb-0.5">End Date</label>
              <input type="text" value="${{edu.end_date || ''}}" placeholder="e.g. 2024 or Present"
                oninput="updateEduField(${{idx}}, 'end_date', this.value)"
                class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-1.5 px-3"/>
            </div>
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    function updateEduField(idx, field, val) {{
      if (cvData.education && cvData.education[idx]) {{
        cvData.education[idx][field] = val;
        const card = document.querySelectorAll('#educationList > div')[idx];
        if (card && field === 'degree') {{
          const header = card.querySelector('.font-bold');
          if (header) header.textContent = val || 'New Education';
        }}
        renderLivePreview();
        flashSaved();
      }}
    }}

    function addEducationInline() {{
      if (!cvData.education) cvData.education = [];
      cvData.education.push({{ degree: '', institution: '', start_date: '', end_date: '', current: false }});
      renderEducationList();
      renderLivePreview();
      flashSaved();
      setTimeout(() => {{
        const inputs = document.querySelectorAll('#educationList input[data-field="degree"]');
        if (inputs.length) inputs[inputs.length - 1].focus();
      }}, 50);
    }}

    function deleteEducation(idx) {{
      cvData.education.splice(idx, 1);
      renderEducationList();
      renderLivePreview();
      flashSaved();
    }}

    function renderProjectsList() {{
      const container = document.getElementById('projectsList');
      container.innerHTML = '';
      (cvData.projects || []).forEach((proj, idx) => {{
        const card = document.createElement('div');
        card.className = 'border border-gray-300 rounded-xl p-4 bg-white shadow-card-subtle space-y-3';
        const descText = (proj.description || []).map(b => (typeof b === 'object' ? b.text : b)).join('\\n');
        card.innerHTML = `
          <div class="flex items-center justify-between pb-1">
            <span class="font-bold text-sm text-gray-800">${{proj.title || 'New Project'}}</span>
            <button onclick="deleteProject(${{idx}})" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-400 hover:bg-red-50 hover:text-red-600 hover:border-red-300 transition" type="button" title="Delete">✕</button>
          </div>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-[11px] font-medium text-gray-500 mb-0.5">Project Title</label>
              <input type="text" data-field="title" value="${{proj.title || ''}}" placeholder="e.g. EduBot Moodle Plugin"
                oninput="updateProjField(${{idx}}, 'title', this.value)"
                class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-1.5 px-3"/>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-gray-500 mb-0.5">Role / Subtitle</label>
              <input type="text" value="${{proj.role || ''}}" placeholder="e.g. AI Developer"
                oninput="updateProjField(${{idx}}, 'role', this.value)"
                class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-1.5 px-3"/>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-gray-500 mb-0.5">Dates</label>
              <input type="text" value="${{proj.start_date || ''}}" placeholder="e.g. 02/2026 - 06/2026"
                oninput="updateProjField(${{idx}}, 'start_date', this.value)"
                class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-1.5 px-3"/>
            </div>
          </div>
          <div>
            <label class="block text-[11px] font-medium text-gray-500 mb-0.5">Description (one bullet per line)</label>
            <textarea rows="2" oninput="updateProjDesc(${{idx}}, this.value)" placeholder="Key achievements or responsibilities..."
              class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 p-2.5 resize-y leading-relaxed">${{descText}}</textarea>
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    function updateProjField(idx, field, val) {{
      if (cvData.projects && cvData.projects[idx]) {{
        cvData.projects[idx][field] = val;
        const card = document.querySelectorAll('#projectsList > div')[idx];
        if (card && field === 'title') {{
          const header = card.querySelector('.font-bold');
          if (header) header.textContent = val || 'New Project';
        }}
        renderLivePreview();
        flashSaved();
      }}
    }}

    function updateProjDesc(idx, val) {{
      if (cvData.projects && cvData.projects[idx]) {{
        const lines = val.split('\\n').filter(l => l.trim().length > 0);
        cvData.projects[idx].description = lines.map(text => ({{ text }}));
        renderLivePreview();
        flashSaved();
      }}
    }}

    function addProjectInline() {{
      if (!cvData.projects) cvData.projects = [];
      cvData.projects.push({{ title: '', role: '', start_date: '', description: [{{ text: '' }}] }});
      renderProjectsList();
      renderLivePreview();
      flashSaved();
      setTimeout(() => {{
        const inputs = document.querySelectorAll('#projectsList input[data-field="title"]');
        if (inputs.length) inputs[inputs.length - 1].focus();
      }}, 50);
    }}

    function deleteProject(idx) {{
      cvData.projects.splice(idx, 1);
      renderProjectsList();
      renderLivePreview();
      flashSaved();
    }}

    function renderSkillsList() {{
      const container = document.getElementById('skillsItemsList');
      container.innerHTML = '';
      (cvData.skills || []).forEach((group, gi) => {{
        const card = document.createElement('div');
        const items = group.items || [];
        const hasAi = items.some(sk => isAiSkillName(skillItemName(sk)) || (typeof sk === 'object' && sk.is_ai));
        card.className = hasAi
          ? 'border border-blue-200 rounded-lg p-3 bg-blue-50/40 space-y-2'
          : 'border border-gray-200 rounded-lg p-3 bg-gray-50 space-y-2';
        const badgesHtml = items.map((sk, si) => {{
          const name = skillItemName(sk);
          const isAi = isAiSkillName(name) || (typeof sk === 'object' && sk.is_ai);
          if (isAi) {{
            return `
              <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-400 shadow-xs" title="Generated by AI from the target job">
                <span class="text-blue-600">✨</span> ${{name}}
                <button onclick="removeSkillItem(${{gi}}, ${{si}})" class="text-blue-400 hover:text-red-600 ml-0.5" type="button">✕</button>
              </span>
            `;
          }}
          return `
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-white text-gray-700 border border-gray-300 shadow-xs">
              ${{name}}
              <button onclick="removeSkillItem(${{gi}}, ${{si}})" class="text-gray-400 hover:text-red-600 ml-0.5" type="button">✕</button>
            </span>
          `;
        }}).join('');

        card.innerHTML = `
          <div class="flex items-center justify-between gap-2">
            <div class="flex items-center gap-1.5 flex-1">
              <input type="text" data-cat-input="true" value="${{group.category || ''}}" placeholder="Category name..."
                oninput="updateSkillCategoryName(${{gi}}, this.value)"
                class="font-bold text-xs text-gray-800 uppercase tracking-wide bg-transparent border-b border-dashed border-gray-300 focus:border-blue-500 focus:bg-white outline-none px-1 py-0.5 flex-1"/>
            </div>
            <button onclick="deleteSkillGroup(${{gi}})" class="text-xs text-gray-400 hover:text-red-600 transition" type="button">Delete</button>
          </div>
          <div class="flex flex-wrap gap-1.5">${{badgesHtml}}</div>
          <div class="flex gap-2">
            <input type="text" placeholder="Type a skill & press Enter..." onkeydown="if(event.key==='Enter'){{addSkillItem(${{gi}}, this.value); this.value='';}}" class="text-xs rounded border-gray-300 flex-1 py-1 px-2"/>
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    function updateSkillCategoryName(gi, val) {{
      if (cvData.skills && cvData.skills[gi]) {{
        cvData.skills[gi].category = val;
        renderLivePreview();
        flashSaved();
      }}
    }}

    function addSkillInline() {{
      if (!cvData.skills) cvData.skills = [];
      cvData.skills.push({{ category: 'New Category', items: [] }});
      renderSkillsList();
      renderLivePreview();
      flashSaved();
    }}

    function renderHobbiesList() {{
      const container = document.getElementById('hobbiesChips');
      if (container) {{
        container.innerHTML = '';
        (cvData.hobbies || []).forEach((h, hi) => {{
          const chip = document.createElement('span');
          chip.className = 'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 border border-gray-300';
          chip.innerHTML = `${{h}} <button onclick="deleteHobby(${{hi}})" class="text-gray-400 hover:text-red-600" type="button">✕</button>`;
          container.appendChild(chip);
        }});
      }}
      const hBlock = document.getElementById('hobbiesSectionBlock');
      const hobPill = document.querySelector('[data-pill-sec="hobbies"]');
      const hasHobbiesInOrder = (cvData.sections_order || []).includes('hobbies');
      if (hBlock) {{
        if (hasHobbiesInOrder) {{
          hBlock.classList.remove('hidden');
          if (hobPill) {{ hobPill.disabled = true; hobPill.classList.add('opacity-40', 'cursor-not-allowed'); }}
        }} else {{
          hBlock.classList.add('hidden');
          if (hobPill) {{ hobPill.disabled = false; hobPill.classList.remove('opacity-40', 'cursor-not-allowed'); }}
        }}
      }}
    }}

    function addHobbyFromInput() {{
      const inp = document.getElementById('hobbyInlineInput');
      if (!inp) return;
      const val = inp.value.trim();
      if (val) {{
        if (!cvData.hobbies) cvData.hobbies = [];
        cvData.hobbies.push(val);
        inp.value = '';
        renderHobbiesList();
        renderLivePreview();
        flashSaved();
      }}
    }}

    function renderCustomSectionsList() {{
      const secList = document.getElementById('dynamicSectionsList');
      if (!secList) return;
      (cvData.custom_sections || []).forEach(sec => {{
        if (!sec || !sec.id) return;
        if (document.querySelector(`[data-sec-id="${{sec.id}}"]`)) return;

        const pillBtn = document.querySelector(`[data-pill-sec="${{sec.id}}"]`);
        if (pillBtn) {{
          pillBtn.disabled = true;
          pillBtn.classList.add('opacity-40', 'cursor-not-allowed');
        }}

        const key = sec.id;
        const secName = sec.label || sec.id;
        const block = document.createElement('div');
        block.className = 'section-block space-y-3 border-b border-gray-200 pb-5 pt-1';
        block.setAttribute('draggable', 'true');
        block.setAttribute('data-sec-id', key);
        block.setAttribute('data-sec-label', secName);

        const bodyId = `customBody_${{key}}`;
        const itemsId = `customItems_${{key}}`;

        block.innerHTML = `
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="text-gray-400 hover:text-gray-600 cursor-grab flex items-center drag-handle" title="Drag to reorder">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M5 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm6-8a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Z"></path>
                </svg>
              </span>
              <h2 class="text-base font-bold tracking-wide text-gray-900 uppercase select-none">${{secName}}</h2>
            </div>
            <div class="flex items-center space-x-2">
              <button onclick="toggleSection('${{bodyId}}')" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-500 hover:text-gray-700 hover:border-gray-400 transition" type="button" title="Collapse">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M5 15l7-7 7 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                </svg>
              </button>
              <button onclick="removeCustomSection('${{key}}', this)" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-400 hover:bg-red-50 hover:text-red-600 hover:border-red-300 transition" type="button" title="Remove section">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
                </svg>
              </button>
            </div>
          </div>
          <div id="${{bodyId}}" class="space-y-2 pt-1">
            <div id="${{itemsId}}" class="space-y-2"></div>
            <button onclick="addCustomItem('${{key}}')" class="inline-flex items-center space-x-1.5 px-4 py-2 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition mt-1" type="button">
              <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
              <span>Add item</span>
            </button>
          </div>
        `;

        const hobbiesBlock = document.getElementById('hobbiesSectionBlock');
        if (hobbiesBlock && hobbiesBlock.parentNode === secList) {{
          secList.insertBefore(block, hobbiesBlock);
        }} else {{
          secList.appendChild(block);
        }}

        initDragAndDropForBlock(block);

        const itemsContainer = document.getElementById(itemsId);
        (sec.items || []).forEach(val => {{
          const txt = typeof val === 'string' ? val : (val.text || '');
          const row = document.createElement('div');
          row.className = 'flex items-start gap-2';
          const inputId = `customItem_${{key}}_${{Date.now()}}_${{Math.random().toString(36).substr(2, 4)}}`;
          row.innerHTML = `
            <textarea id="${{inputId}}" rows="2"
              class="flex-1 text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 p-2.5 leading-relaxed resize-y"
              placeholder="Add content for this section..."
              oninput="updateCustomItem('${{key}}', this)">${{txt}}</textarea>
            <button onclick="removeCustomItem('${{key}}', this)" class="mt-1 w-7 h-7 flex-shrink-0 rounded-full border border-gray-300 flex items-center justify-center text-gray-400 hover:bg-red-50 hover:text-red-600 hover:border-red-300 transition" type="button" title="Remove item">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
            </button>
          `;
          itemsContainer.appendChild(row);
        }});
      }});
    }}

    // ── Live Preview Sheet Renderer ──
    function renderLivePreview() {{
      if (currentTemplate === 'executive') {{
        renderExecutiveSlatePreview();
      }} else if (currentTemplate === 'simple') {{
        renderSimplePreview();
      }} else {{
        renderClassicNavyPreview();
      }}
    }}

    function renderSimplePreview() {{
      const sheet = document.getElementById('resumeSheet');
      if (!sheet) return;

      const p = cvData.personal || {{}};
      const firstName = (p.first_name || '').trim();
      const lastName = (p.last_name || '').trim();
      const fullName = [firstName, lastName].filter(Boolean).join(' ').toUpperCase();
      const headline = (p.headline || '').trim();

      const phone = p.phone || '';
      const email = p.email || '';
      const location = [p.address, p.city, p.country].filter(Boolean).join(', ') || p.city || '';
      const linkedin = p.linkedin ? p.linkedin.replace(/^https?:\\/\\/(www\\.)?linkedin\\.com\\/in\\//, '') : '';
      const website = p.website ? p.website.replace(/^https?:\\/\\//, '') : '';

      // Contact line items
      let contactItems = [];
      if (phone) {{
        contactItems.push(`
          <span style="display:inline-flex;align-items:center;gap:4px;">
            <svg style="width:10px;height:10px;flex-shrink:0;color:#111827;" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 4V3z"/>
            </svg>
            <span>${{phone}}</span>
          </span>
        `);
      }}
      if (email) {{
        contactItems.push(`
          <span style="display:inline-flex;align-items:center;gap:4px;">
            <svg style="width:10px;height:10px;flex-shrink:0;color:#111827;" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
              <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
            </svg>
            <span>${{email}}</span>
          </span>
        `);
      }}
      if (location) {{
        contactItems.push(`
          <span style="display:inline-flex;align-items:center;gap:4px;">
            <svg style="width:10px;height:10px;flex-shrink:0;color:#111827;" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
            </svg>
            <span>${{location}}</span>
          </span>
        `);
      }}
      if (linkedin) {{
        contactItems.push(`
          <span style="display:inline-flex;align-items:center;gap:4px;">
            <span style="font-weight:bold;font-size:9.5px;color:#111827;">in</span>
            <span>${{linkedin}}</span>
          </span>
        `);
      }}
      if (website) {{
        contactItems.push(`
          <span style="display:inline-flex;align-items:center;gap:4px;">
            <span style="font-size:9px;">🌐</span>
            <span>${{website}}</span>
          </span>
        `);
      }}

      // Work Experience HTML
      let expHtml = '';
      (cvData.experience || []).forEach(exp => {{
        const title = exp.job_title || exp.title || exp.position || '';
        const company = exp.company || exp.employer || exp.organization || '';
        const loc = exp.location || '';
        const orgLine = [company, loc].filter(Boolean).join(' — ');
        const dateStr = [exp.start_date, (exp.current ? 'Present' : exp.end_date)].filter(Boolean).join(' – ');
        const headerSub = [orgLine, dateStr].filter(Boolean).join(' | ');

        let bullets = '';
        const rawBullets = exp.description || exp.bullets || [];
        if (Array.isArray(rawBullets) && rawBullets.length > 0) {{
          bullets = '<ul style="margin:4px 0 0 16px;padding:0;list-style-type:disc;font-size:8px;line-height:1.55;color:#374151;">' +
            rawBullets.map(b => `<li style="margin-bottom:2px;">${{typeof b === 'object' ? (b.text || '') : b}}</li>`).join('') +
            '</ul>';
        }} else if (typeof rawBullets === 'string' && rawBullets.trim()) {{
          bullets = `<p style="margin:4px 0 0 0;font-size:8px;line-height:1.55;color:#374151;">${{rawBullets.trim()}}</p>`;
        }}

        expHtml += `
          <div style="margin-bottom:12px;">
            ${{headerSub ? `<div style="font-size:8px;color:#6B7280;font-weight:500;margin-bottom:2px;">${{headerSub}}</div>` : ''}}
            ${{title ? `<div style="font-size:9.5px;font-weight:700;color:#111827;margin-bottom:3px;">${{title}}</div>` : ''}}
            ${{bullets}}
          </div>
        `;
      }});

      // Education HTML
      let eduHtml = '';
      (cvData.education || []).forEach(edu => {{
        const degree = edu.degree || '';
        const inst = edu.institution || '';
        const loc = edu.location || '';
        const orgLine = [inst, loc].filter(Boolean).join(' — ');
        const dateStr = [edu.start_date, (edu.current ? 'Present' : edu.end_date)].filter(Boolean).join(' – ');
        const headerSub = [orgLine, dateStr].filter(Boolean).join(' | ');

        let bullets = '';
        if (Array.isArray(edu.description) && edu.description.length > 0) {{
          bullets = '<ul style="margin:4px 0 0 16px;padding:0;list-style-type:disc;font-size:8px;line-height:1.55;color:#374151;">' +
            edu.description.map(b => `<li style="margin-bottom:2px;">${{typeof b === 'object' ? (b.text || '') : b}}</li>`).join('') +
            '</ul>';
        }} else if (typeof edu.description === 'string' && edu.description.trim()) {{
          bullets = `<p style="margin:4px 0 0 0;font-size:8px;line-height:1.55;color:#374151;">${{edu.description.trim()}}</p>`;
        }}

        eduHtml += `
          <div style="margin-bottom:12px;">
            ${{headerSub ? `<div style="font-size:8px;color:#6B7280;font-weight:500;margin-bottom:2px;">${{headerSub}}</div>` : ''}}
            ${{degree ? `<div style="font-size:9.5px;font-weight:700;color:#111827;margin-bottom:3px;">${{degree}}</div>` : ''}}
            ${{bullets}}
          </div>
        `;
      }});

      // Flat skills with NO categories, 3-column bullet grid
      const allSkills = [];
      (cvData.skills || []).forEach(group => {{
        (group.items || []).forEach(sk => {{
          const name = skillItemName(sk);
          if (name && !allSkills.includes(name)) {{
            allSkills.push(name);
          }}
        }});
      }});

      let skillsHtml = '';
      if (allSkills.length > 0) {{
        skillsHtml = `
          <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:6px 16px;font-size:8.5px;color:#374151;">
            ${{allSkills.map(sk => `
              <div style="display:flex;align-items:center;gap:6px;">
                <span style="font-size:9px;color:#111827;line-height:1;">•</span>
                <span style="color:#374151;">${{sk}}</span>
              </div>
            `).join('')}}
          </div>
        `;
      }}

      // Projects HTML
      let projHtml = '';
      (cvData.projects || []).forEach(proj => {{
        const title = proj.title || proj.role || '';
        const org = proj.organization || proj.company || '';
        const role = (proj.role && proj.role !== title) ? proj.role : '';
        const loc = proj.location || '';
        const orgLine = [org, role, loc].filter(Boolean).join(' — ');
        const dateStr = [proj.start_date, (proj.current ? 'Present' : proj.end_date)].filter(Boolean).join(' – ');
        const headerSub = [orgLine, dateStr].filter(Boolean).join(' | ');

        let bullets = '';
        const rawBullets = proj.description || proj.bullets || [];
        if (Array.isArray(rawBullets) && rawBullets.length > 0) {{
          bullets = '<ul style="margin:4px 0 0 16px;padding:0;list-style-type:disc;font-size:8px;line-height:1.55;color:#374151;">' +
            rawBullets.map(b => `<li style="margin-bottom:2px;">${{typeof b === 'object' ? (b.text || '') : b}}</li>`).join('') +
            '</ul>';
        }} else if (typeof rawBullets === 'string' && rawBullets.trim()) {{
          bullets = `<p style="margin:4px 0 0 0;font-size:8px;line-height:1.55;color:#374151;">${{rawBullets.trim()}}</p>`;
        }}

        projHtml += `
          <div style="margin-bottom:12px;">
            ${{headerSub ? `<div style="font-size:8px;color:#6B7280;font-weight:500;margin-bottom:2px;">${{headerSub}}</div>` : ''}}
            ${{title ? `<div style="font-size:9.5px;font-weight:700;color:#111827;margin-bottom:3px;">${{title}}</div>` : ''}}
            ${{bullets}}
          </div>
        `;
      }});

      // Languages HTML
      let langsHtml = '';
      if (Array.isArray(cvData.languages) && cvData.languages.length > 0) {{
        langsHtml = `
          <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:6px 16px;font-size:8.5px;color:#374151;">
            ${{cvData.languages.map(l => `
              <div style="display:flex;align-items:center;gap:6px;">
                <span style="font-size:9px;color:#111827;line-height:1;">•</span>
                <span><strong>${{l.name || ''}}</strong>${{l.level ? ` <span style="color:#6B7280;">(${{typeof l.level === 'string' ? (l.level.charAt(0).toUpperCase() + l.level.slice(1)) : ''}})</span>` : ''}}</span>
              </div>
            `).join('')}}
          </div>
        `;
      }}

      // Certifications HTML
      let certsHtml = '';
      if (Array.isArray(cvData.certificates) && cvData.certificates.length > 0) {{
        certsHtml = `
          <div style="display:grid;grid-template-columns:repeat(2, 1fr);gap:6px 16px;font-size:8.5px;color:#374151;">
            ${{cvData.certificates.map(c => `
              <div style="display:flex;align-items:center;gap:6px;">
                <span style="font-size:9px;color:#111827;line-height:1;">•</span>
                <span><strong>${{c.title || c.name || ''}}</strong>${{c.issuer ? ` — <span style="color:#6B7280;">${{c.issuer}}</span>` : ''}}</span>
              </div>
            `).join('')}}
          </div>
        `;
      }}

      // Hobbies HTML
      let hobbiesHtml = '';
      if (Array.isArray(cvData.hobbies) && cvData.hobbies.length > 0) {{
        hobbiesHtml = `
          <div style="font-size:8.5px;color:#374151;line-height:1.6;">
            ${{cvData.hobbies.join(' • ')}}
          </div>
        `;
      }}

      // Custom Sections HTML
      let customSecHtml = '';
      (cvData.custom_sections || []).forEach(cs => {{
        if (!cs.title) return;
        customSecHtml += `
          <div>
            <div style="font-size:11px;font-weight:800;letter-spacing:0.12em;color:#111827;text-transform:uppercase;margin-bottom:8px;">${{cs.title}}</div>
            <div style="font-size:8.5px;line-height:1.6;color:#374151;">${{cs.content || ''}}</div>
            <div style="height:1px;background:#4B5563;margin:14px 0 16px 0;opacity:0.85;"></div>
          </div>
        `;
      }});

      const divider = '<div style="height:1px;background:#4B5563;margin:14px 0 16px 0;opacity:0.85;"></div>';

      sheet.className = "shadow-paper rounded-sm select-none transition-all flex flex-col overflow-hidden";
      sheet.style.width = '595px';
      sheet.style.minHeight = '842px';
      sheet.style.fontFamily = "'Roboto', 'Arial', sans-serif";
      sheet.style.background = '#FFFFFF';
      sheet.style.color = '#111827';
      sheet.style.padding = '36px 38px 30px 38px';
      sheet.style.display = 'flex';
      sheet.style.flexDirection = 'column';

      sheet.innerHTML = `
        <!-- HEADER (Sebastian Bennett style) -->
        <div style="text-align:center;margin-bottom:18px;">
          <div style="font-size:26px;font-weight:800;letter-spacing:0.08em;color:#111827;text-transform:uppercase;line-height:1.15;margin-bottom:4px;">
            ${{fullName || 'SEBASTIAN BENNETT'}}
          </div>
          ${{headline ? `<div style="font-size:13px;font-weight:400;color:#374151;margin-bottom:12px;letter-spacing:0.02em;">${{headline}}</div>` : ''}}
          ${{contactItems.length > 0 ? `
            <div style="display:flex;justify-content:center;align-items:center;flex-wrap:wrap;gap:18px;font-size:8.5px;color:#374151;">
              ${{contactItems.join('')}}
            </div>
          ` : ''}}
        </div>

        <!-- ABOUT ME -->
        ${{cvData.summary ? `
          <div style="margin-top:4px;">
            <div style="font-size:11px;font-weight:800;letter-spacing:0.12em;color:#111827;text-transform:uppercase;margin-bottom:8px;">ABOUT ME</div>
            <p style="font-size:8.5px;line-height:1.6;color:#374151;margin:0;">${{cvData.summary}}</p>
            ${{divider}}
          </div>
        ` : ''}}

        <!-- EDUCATION -->
        ${{eduHtml ? `
          <div>
            <div style="font-size:11px;font-weight:800;letter-spacing:0.12em;color:#111827;text-transform:uppercase;margin-bottom:8px;">EDUCATION</div>
            <div>${{eduHtml}}</div>
            ${{divider}}
          </div>
        ` : ''}}

        <!-- WORK EXPERIENCE -->
        ${{expHtml ? `
          <div>
            <div style="font-size:11px;font-weight:800;letter-spacing:0.12em;color:#111827;text-transform:uppercase;margin-bottom:8px;">WORK EXPERIENCE</div>
            <div>${{expHtml}}</div>
            ${{divider}}
          </div>
        ` : ''}}

        <!-- SKILLS (NO CATEGORIES, 3-COLUMN BULLETS) -->
        ${{skillsHtml ? `
          <div>
            <div style="font-size:11px;font-weight:800;letter-spacing:0.12em;color:#111827;text-transform:uppercase;margin-bottom:8px;">SKILLS</div>
            <div>${{skillsHtml}}</div>
            ${{(projHtml || langsHtml || certsHtml || hobbiesHtml || customSecHtml) ? divider : ''}}
          </div>
        ` : ''}}

        <!-- PROJECTS -->
        ${{projHtml ? `
          <div>
            <div style="font-size:11px;font-weight:800;letter-spacing:0.12em;color:#111827;text-transform:uppercase;margin-bottom:8px;">PROJECTS</div>
            <div>${{projHtml}}</div>
            ${{(langsHtml || certsHtml || hobbiesHtml || customSecHtml) ? divider : ''}}
          </div>
        ` : ''}}

        <!-- LANGUAGES -->
        ${{langsHtml ? `
          <div>
            <div style="font-size:11px;font-weight:800;letter-spacing:0.12em;color:#111827;text-transform:uppercase;margin-bottom:8px;">LANGUAGES</div>
            <div>${{langsHtml}}</div>
            ${{(certsHtml || hobbiesHtml || customSecHtml) ? divider : ''}}
          </div>
        ` : ''}}

        <!-- CERTIFICATES -->
        ${{certsHtml ? `
          <div>
            <div style="font-size:11px;font-weight:800;letter-spacing:0.12em;color:#111827;text-transform:uppercase;margin-bottom:8px;">CERTIFICATIONS</div>
            <div>${{certsHtml}}</div>
            ${{(hobbiesHtml || customSecHtml) ? divider : ''}}
          </div>
        ` : ''}}

        <!-- HOBBIES -->
        ${{hobbiesHtml ? `
          <div>
            <div style="font-size:11px;font-weight:800;letter-spacing:0.12em;color:#111827;text-transform:uppercase;margin-bottom:8px;">HOBBIES</div>
            <div>${{hobbiesHtml}}</div>
            ${{customSecHtml ? divider : ''}}
          </div>
        ` : ''}}

        <!-- CUSTOM SECTIONS -->
        ${{customSecHtml}}
      `;
    }}

    function renderExecutiveSlatePreview() {{
      const sheet = document.getElementById('resumeSheet');
      if (!sheet) return;

      sheet.className = "shadow-paper rounded-sm select-none transition-all flex overflow-hidden";
      sheet.style.width = '595px';
      sheet.style.minHeight = '842px';
      sheet.style.fontFamily = "'Roboto', 'Arial', sans-serif";
      sheet.style.background = '#FFFFFF';
      sheet.style.color = '#111827';
      sheet.style.padding = '0';
      sheet.style.display = 'flex';
      sheet.style.flexDirection = 'row';

      const p = cvData.personal || {{}};
      const firstName = (p.first_name || '').trim();
      const lastName = (p.last_name || '').trim();
      const fullName = [firstName, lastName].filter(Boolean).join(' ').toUpperCase();
      const headline = (p.headline || '').trim();
      const photoSrc = p.photo_url || DEFAULT_AVATAR;

      // Contact HTML with white icons
      let contactHtml = '';
      if (p.phone) {{
        contactHtml += `
          <div style="display:flex;align-items:center;gap:8px;font-size:7.5px;color:#fff;">
            <svg style="width:11px;height:11px;flex-shrink:0;color:#CBD5E1;" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 4V3z"/>
            </svg>
            <span>${{p.phone}}</span>
          </div>
        `;
      }}
      if (p.email) {{
        contactHtml += `
          <div style="display:flex;align-items:center;gap:8px;font-size:7.5px;color:#fff;word-break:break-all;">
            <svg style="width:11px;height:11px;flex-shrink:0;color:#CBD5E1;" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
              <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
            </svg>
            <span>${{p.email}}</span>
          </div>
        `;
      }}
      const addr = p.address || p.city || '';
      if (addr) {{
        contactHtml += `
          <div style="display:flex;align-items:flex-start;gap:8px;font-size:7.5px;color:#fff;">
            <svg style="width:11px;height:11px;flex-shrink:0;color:#CBD5E1;margin-top:1px;" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
            </svg>
            <span>${{addr}}</span>
          </div>
        `;
      }}
      if (p.linkedin) {{
        contactHtml += `
          <div style="display:flex;align-items:center;gap:8px;font-size:7.5px;color:#fff;word-break:break-all;">
            <span style="font-weight:bold;font-size:9px;color:#CBD5E1;">in</span>
            <span>${{p.linkedin}}</span>
          </div>
        `;
      }}
      if (p.website) {{
        contactHtml += `
          <div style="display:flex;align-items:center;gap:8px;font-size:7.5px;color:#fff;">
            <span style="font-size:9px;">🌐</span>
            <span>${{p.website}}</span>
          </div>
        `;
      }}

      // Skills HTML: Category and its skills (matching Classic Navy format)
      let skillsHtml = '';
      (cvData.skills || []).forEach(group => {{
        const isGroupAi = !!group.is_ai;
        const items = (group.items || []).map(sk => {{
          const isAi = (typeof sk === 'object' && sk.is_ai) || isGroupAi || (typeof isAiSkillName === 'function' && isAiSkillName(skillItemName(sk)));
          const name = skillItemName(sk);
          if (!name) return '';
          if (isAi) {{
            return `<span style="color:#38BDF8;font-weight:700;display:inline-flex;align-items:center;gap:1.5px;" title="AI-Generated Skill"><span style="color:#67E8F9;font-size:6px;">✨</span>${{name}}</span>`;
          }}
          return `<span style="color:#CBD5E1;">${{name}}</span>`;
        }}).filter(Boolean);

        if (items.length > 0) {{
          const catTitle = group.category || '';
          const catColor = isGroupAi ? '#7DD3FC' : '#fff';
          skillsHtml += `
            <div style="margin-bottom:8px;">
              ${{catTitle ? `<div style="font-weight:700;color:${{catColor}};font-size:7.5px;margin-bottom:2px;">${{catTitle}}</div>` : ''}}
              <div style="font-size:7px;line-height:1.7;">${{items.join(', ')}}</div>
            </div>
          `;
        }}
      }});

      // Languages HTML with square bullets ▪
      let langsHtml = '';
      (cvData.languages || []).forEach(l => {{
        if (l.name) {{
          langsHtml += `
            <div style="font-size:7.5px;color:#E2E8F0;line-height:1.6;display:flex;align-items:baseline;gap:6px;margin-bottom:2.5px;">
              <span style="color:#CBD5E1;font-size:7.5px;">▪</span>
              <span>${{l.name}}${{l.level ? ' – ' + l.level : ''}}</span>
            </div>
          `;
        }}
      }});

      // Certifications / Extras HTML with square bullets ▪
      let certsHtml = '';
      if (Array.isArray(p.extras)) {{
        p.extras.forEach(ex => {{
          if (ex.label && ex.value) {{
            certsHtml += `
              <div style="font-size:7.5px;color:#E2E8F0;line-height:1.6;display:flex;align-items:baseline;gap:6px;margin-bottom:2.5px;">
                <span style="color:#CBD5E1;font-size:7.5px;">▪</span>
                <span><strong>${{ex.label}}:</strong> ${{ex.value}}</span>
              </div>
            `;
          }}
        }});
      }}
      if (Array.isArray(cvData.certificates)) {{
        cvData.certificates.forEach(c => {{
          if (c.name) {{
            certsHtml += `
              <div style="font-size:7.5px;color:#E2E8F0;line-height:1.6;display:flex;align-items:baseline;gap:6px;margin-bottom:2.5px;">
                <span style="color:#CBD5E1;font-size:7.5px;">▪</span>
                <span><strong>${{c.name}}</strong>${{c.issuer ? ' (' + c.issuer + ')' : ''}}</span>
              </div>
            `;
          }}
        }});
      }}

      // Hobbies HTML with square bullets ▪
      let hobbiesHtml = '';
      const isHobbiesActive = (cvData.sections_order || []).includes('hobbies');
      if (isHobbiesActive && Array.isArray(cvData.hobbies) && cvData.hobbies.length > 0) {{
        cvData.hobbies.forEach(h => {{
          const hText = (typeof h === 'string' ? h : (h.name || '')).trim();
          if (hText) {{
            hobbiesHtml += `
              <div style="font-size:7.5px;color:#E2E8F0;line-height:1.6;display:flex;align-items:baseline;gap:6px;margin-bottom:2.5px;">
                <span style="color:#CBD5E1;font-size:7.5px;">▪</span>
                <span>${{hText}}</span>
              </div>
            `;
          }}
        }});
      }}

      // Experience / Projects HTML
      let expHtml = '';
      const expList = (cvData.experience && cvData.experience.length > 0) ? cvData.experience : (cvData.projects || []);
      expList.forEach(exp => {{
        const title = exp.title || exp.position || '';
        let dateStr = '';
        if (exp.start_date && (exp.end_date || exp.current)) {{
          dateStr = `${{exp.start_date}} – ${{exp.current ? 'Present' : exp.end_date}}`;
        }} else if (exp.start_date) {{
          dateStr = exp.start_date;
        }} else if (exp.end_date) {{
          dateStr = exp.end_date;
        }}

        const company = exp.company || exp.employer || exp.organization || '';
        const role = exp.role || '';
        const subtitle = exp.subtitle || '';
        const location = exp.location || '';
        const subParts = [role, (company && company !== title ? company : ''), subtitle, location].filter(Boolean);
        const subLine = subParts.join(' • ');

        const bullets = (exp.bullets || exp.description || []).map(b => {{
          const txt = typeof b === 'object' ? (b.text || '') : b;
          if (!txt) return '';
          return `
            <div style="font-size:7.5px;color:#374151;line-height:1.55;display:flex;align-items:baseline;gap:6px;margin-bottom:2.5px;">
              <span style="color:#111827;font-size:8px;">▪</span>
              <span>${{txt}}</span>
            </div>
          `;
        }}).filter(Boolean).join('');

        expHtml += `
          <div style="margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px;">
              <div style="font-size:8.5px;font-weight:700;color:#111827;">${{title}}</div>
              ${{dateStr ? `<div style="font-size:8px;color:#4B5563;font-weight:400;white-space:nowrap;">${{dateStr}}</div>` : ''}}
            </div>
            ${{subLine ? `<div style="font-size:8px;color:#4B5563;margin-top:1px;margin-bottom:4px;">${{subLine}}</div>` : ''}}
            ${{bullets ? `<div style="margin-top:3px;">${{bullets}}</div>` : ''}}
          </div>
        `;
      }});

      // Separate Projects HTML if BOTH experience and projects exist
      let projSlateHtml = '';
      if (cvData.experience && cvData.experience.length > 0 && cvData.projects && cvData.projects.length > 0) {{
        cvData.projects.forEach(p => {{
          const title = p.title || p.position || '';
          const dateStr = [p.start_date, (p.current ? 'Present' : p.end_date)].filter(Boolean).join(' – ');
          const sub = [p.role, p.organization || p.company, p.location].filter(Boolean).join(' • ');
          const bullets = (p.description || []).map(b => {{
            const txt = typeof b === 'object' ? (b.text || '') : b;
            if (!txt) return '';
            return `
              <div style="font-size:7.5px;color:#374151;line-height:1.55;display:flex;align-items:baseline;gap:6px;margin-bottom:2.5px;">
                <span style="color:#111827;font-size:8px;">▪</span>
                <span>${{txt}}</span>
              </div>
            `;
          }}).filter(Boolean).join('');

          projSlateHtml += `
            <div style="margin-bottom:12px;">
              <div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px;">
                <div style="font-size:8.5px;font-weight:700;color:#111827;">${{title}}</div>
                ${{dateStr ? `<div style="font-size:8px;color:#4B5563;font-weight:400;white-space:nowrap;">${{dateStr}}</div>` : ''}}
              </div>
              ${{sub ? `<div style="font-size:8px;color:#4B5563;margin-top:1px;margin-bottom:4px;">${{sub}}</div>` : ''}}
              ${{bullets ? `<div style="margin-top:3px;">${{bullets}}</div>` : ''}}
            </div>
          `;
        }});
      }}

      // Education HTML
      let eduHtml = '';
      (cvData.education || []).forEach(edu => {{
        const degree = edu.degree || '';
        let eduDates = '';
        if (edu.start_date && (edu.end_date || edu.current)) {{
          eduDates = `${{edu.start_date}} – ${{edu.current ? 'Present' : edu.end_date}}`;
        }} else if (edu.end_date) {{
          eduDates = edu.end_date;
        }} else if (edu.start_date) {{
          eduDates = edu.start_date;
        }}

        const inst = edu.institution || '';
        const loc = edu.location || '';
        const subEdu = [inst, loc].filter(Boolean).join(', ');
        let bullets = '';
        if (Array.isArray(edu.description) && edu.description.length > 0) {{
          bullets = edu.description.map(b => {{
            const txt = typeof b === 'object' ? (b.text || '') : b;
            if (!txt) return '';
            return `
              <div style="font-size:7.5px;color:#374151;line-height:1.55;display:flex;align-items:baseline;gap:6px;margin-bottom:2.5px;">
                <span style="color:#111827;font-size:8px;">▪</span>
                <span>${{txt}}</span>
              </div>
            `;
          }}).filter(Boolean).join('');
        }}

        eduHtml += `
          <div style="margin-bottom:10px;">
            <div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px;">
              <div style="font-size:8.5px;font-weight:700;color:#111827;">${{degree}}</div>
              ${{eduDates ? `<div style="font-size:8px;color:#4B5563;font-weight:400;white-space:nowrap;">${{eduDates}}</div>` : ''}}
            </div>
            ${{subEdu ? `<div style="font-size:8px;color:#4B5563;margin-top:1px;">${{subEdu}}</div>` : ''}}
            ${{bullets ? `<div style="margin-top:3px;">${{bullets}}</div>` : ''}}
          </div>
        `;
      }});

      // Custom sections HTML (Courses, Internships, Extracurricular activities, Achievements, etc.)
      let customSecHtml = '';
      const customList = cvData.custom_sections || [];
      const order = cvData.sections_order || [];
      const orderedCustoms = [...customList].sort((a, b) => {{
        const idxA = order.indexOf(a.id);
        const idxB = order.indexOf(b.id);
        if (idxA === -1 && idxB === -1) return 0;
        if (idxA === -1) return 1;
        if (idxB === -1) return -1;
        return idxA - idxB;
      }});

      orderedCustoms.forEach(cs => {{
        if (!cs || !cs.id) return;
        const items = (cs.items || []).map(i => typeof i === 'string' ? i : (i.text || '')).filter(t => t.trim());
        const bullets = items.map(txt => `
          <div style="font-size:7.5px;color:#374151;line-height:1.55;display:flex;align-items:baseline;gap:6px;margin-bottom:2.5px;">
            <span style="color:#111827;font-size:8px;">▪</span>
            <span>${{txt}}</span>
          </div>
        `).join('');

        customSecHtml += `
          <div style="margin-bottom:12px;">
            <div style="font-size:11px;font-weight:800;letter-spacing:0.2em;color:#3A546D;text-transform:uppercase;margin-bottom:6px;margin-top:12px;">${{(cs.label || cs.id).toUpperCase()}}</div>
            <div>${{bullets || '<div style="font-size:7.5px;color:#9CA3AF;font-style:italic;">No items yet</div>'}}</div>
          </div>
        `;
      }});

      sheet.innerHTML = `
        <!-- LEFT SLATE SIDEBAR -->
        <div style="width:202px;min-height:842px;background:#3A546D;color:#fff;flex-shrink:0;display:flex;flex-direction:column;padding:22px 18px;">
          <!-- Profile photo (square with subtle radius) -->
          <div style="width:100%;height:165px;border-radius:4px;overflow:hidden;background:#486581;margin-bottom:18px;flex-shrink:0;">
            <img src="${{photoSrc}}" style="width:100%;height:100%;object-fit:cover;display:block;" alt="Photo" />
          </div>

          <!-- Contact info with white icons -->
          <div style="display:flex;flex-direction:column;gap:7px;margin-bottom:16px;">
            ${{contactHtml}}
          </div>

          <!-- SKILLS -->
          ${{skillsHtml ? `
            <div style="font-size:10px;font-weight:800;letter-spacing:0.18em;color:#fff;text-transform:uppercase;margin-top:12px;margin-bottom:8px;">SKILLS</div>
            <div style="margin-bottom:10px;">${{skillsHtml}}</div>
          ` : ''}}

          <!-- LANGUAGES -->
          ${{langsHtml ? `
            <div style="font-size:10px;font-weight:800;letter-spacing:0.18em;color:#fff;text-transform:uppercase;margin-top:12px;margin-bottom:8px;">LANGUAGES</div>
            <div style="margin-bottom:10px;">${{langsHtml}}</div>
          ` : ''}}

          <!-- CERTIFICATIONS -->
          ${{certsHtml ? `
            <div style="font-size:10px;font-weight:800;letter-spacing:0.18em;color:#fff;text-transform:uppercase;margin-top:12px;margin-bottom:8px;">CERTIFICATIONS</div>
            <div style="margin-bottom:10px;">${{certsHtml}}</div>
          ` : ''}}

          <!-- HOBBIES -->
          ${{isHobbiesActive && hobbiesHtml ? `
            <div style="font-size:10px;font-weight:800;letter-spacing:0.18em;color:#fff;text-transform:uppercase;margin-top:12px;margin-bottom:8px;">HOBBIES</div>
            <div>${{hobbiesHtml}}</div>
          ` : ''}}
        </div>

        <!-- RIGHT MAIN CONTENT -->
        <div style="flex:1;background:#fff;padding:28px 26px 20px 26px;display:flex;flex-direction:column;min-height:842px;">
          <!-- Name (large slate uppercase) -->
          ${{fullName ? `
          <div style="font-size:24px;font-weight:800;letter-spacing:0.12em;color:#3A546D;text-transform:uppercase;line-height:1.15;margin-bottom:4px;">
            ${{fullName}}
          </div>` : ''}}

          <!-- Job title -->
          ${{headline ? `<div style="font-size:11.5px;font-weight:700;color:#111827;margin-bottom:8px;">${{headline}}</div>` : ''}}

          <!-- Summary -->
          ${{cvData.summary ? `<p style="font-size:8px;color:#374151;line-height:1.6;margin-bottom:18px;">${{cvData.summary}}</p>` : ''}}

          <!-- EXPERIENCE -->
          ${{expHtml ? `
            <div style="font-size:11px;font-weight:800;letter-spacing:0.2em;color:#3A546D;text-transform:uppercase;margin-bottom:10px;margin-top:8px;">${{(cvData.experience && cvData.experience.length > 0) ? 'E X P E R I E N C E' : 'P R O J E C T S'}}</div>
            <div>${{expHtml}}</div>
          ` : ''}}

          <!-- PROJECTS (if separate) -->
          ${{projSlateHtml ? `
            <div style="font-size:11px;font-weight:800;letter-spacing:0.2em;color:#3A546D;text-transform:uppercase;margin-bottom:10px;margin-top:12px;">P R O J E C T S</div>
            <div>${{projSlateHtml}}</div>
          ` : ''}}

          <!-- EDUCATION -->
          ${{eduHtml ? `
            <div style="font-size:11px;font-weight:800;letter-spacing:0.2em;color:#3A546D;text-transform:uppercase;margin-bottom:10px;margin-top:12px;">E D U C A T I O N</div>
            <div>${{eduHtml}}</div>
          ` : ''}}

          <!-- CUSTOM SECTIONS -->
          ${{customSecHtml}}
        </div>
      `;
    }}

    function ensureClassicNavyDom(sheet) {{
      sheet.className = "shadow-paper rounded-sm select-none transition-all flex overflow-hidden";
      sheet.style.width = '595px';
      sheet.style.minHeight = '842px';
      sheet.style.fontFamily = "'Roboto', 'Arial', sans-serif";
      sheet.style.background = '#FFFFFF';
      sheet.style.color = '#111827';
      sheet.style.padding = '0';
      sheet.style.display = 'flex';
      sheet.style.flexDirection = 'row';

      if (!sheet.querySelector('#previewSidebar') || !sheet.querySelector('#previewMainCol')) {{
        sheet.innerHTML = `
          <!-- LEFT DARK SIDEBAR -->
          <div id="previewSidebar" style="width:202px;min-height:842px;background:#1F3855;color:#fff;flex-shrink:0;display:flex;flex-direction:column;padding:0;">
            <div style="padding:24px 20px 16px 20px;text-align:center;">
              <div id="previewPhotoContainer" style="margin:0 auto 12px auto;width:80px;height:80px;border-radius:50%;overflow:hidden;border:3px solid rgba(203,213,225,0.4);background:#2D4A6B;flex-shrink:0;">
                <img id="previewPhoto" src="" style="width:100%;height:100%;object-fit:cover;display:block;" alt="Profile photo" />
              </div>
              <div id="previewLastName" style="font-size:18px;font-weight:900;letter-spacing:0.04em;line-height:1.15;color:#fff;text-transform:uppercase;">MORGAN</div>
              <div id="previewFirstName" style="font-size:18px;font-weight:900;letter-spacing:0.04em;line-height:1.15;color:#fff;text-transform:uppercase;">ALEX</div>
              <div id="previewHeadline" style="font-size:7.5px;font-weight:400;letter-spacing:0.1em;color:#CBD5E1;margin-top:6px;text-transform:uppercase;">SENIOR DATA SCIENTIST</div>
            </div>
            <div style="height:1px;background:rgba(203,213,225,0.3);margin:0 20px;"></div>
            <div style="padding:16px 20px 14px 20px;">
              <div style="font-size:8px;font-weight:700;letter-spacing:0.14em;color:#fff;text-transform:uppercase;margin-bottom:10px;">CONTACT</div>
              <div id="previewSidebarEmail" style="font-size:7.5px;color:#CBD5E1;margin-bottom:5px;word-break:break-all;"></div>
              <div id="previewSidebarPhone" style="font-size:7.5px;color:#CBD5E1;margin-bottom:5px;"></div>
              <div id="previewSidebarCity" style="font-size:7.5px;color:#CBD5E1;margin-bottom:5px;"></div>
              <div id="previewSidebarDob" style="font-size:7.5px;color:#CBD5E1;margin-bottom:5px;display:none;"></div>
              <div id="previewSidebarLinkedin" style="font-size:7.5px;color:#CBD5E1;margin-bottom:5px;display:none;"></div>
              <div id="previewSidebarWebsite" style="font-size:7.5px;color:#CBD5E1;margin-bottom:5px;display:none;"></div>
              <div id="previewSidebarExtras" style="display:flex;flex-direction:column;gap:4px;margin-top:2px;"></div>
            </div>
            <div style="height:1px;background:rgba(203,213,225,0.3);margin:0 20px;"></div>
            <div style="padding:14px 20px 14px 20px;">
              <div style="font-size:8px;font-weight:700;letter-spacing:0.14em;color:#fff;text-transform:uppercase;margin-bottom:10px;">SKILLS</div>
              <div id="previewSidebarSkills" style="font-size:7.5px;color:#CBD5E1;line-height:1.7;"></div>
            </div>
            <div style="height:1px;background:rgba(203,213,225,0.3);margin:0 20px;"></div>
            <div style="padding:14px 20px 14px 20px;">
              <div style="font-size:8px;font-weight:700;letter-spacing:0.14em;color:#fff;text-transform:uppercase;margin-bottom:10px;">LANGUAGES</div>
              <div id="previewSidebarLanguages" style="font-size:7.5px;color:#CBD5E1;line-height:1.9;"></div>
            </div>
            <div id="previewSidebarHobbiesBlock" style="display:none;padding:14px 20px 14px 20px;">
              <div style="height:1px;background:rgba(203,213,225,0.3);margin:0 0 14px 0;"></div>
              <div style="font-size:8px;font-weight:700;letter-spacing:0.14em;color:#fff;text-transform:uppercase;margin-bottom:10px;">HOBBIES</div>
              <div id="previewSidebarHobbies" style="font-size:7.5px;color:#CBD5E1;line-height:1.9;"></div>
            </div>
          </div>
          <!-- RIGHT MAIN CONTENT -->
          <div style="flex:1;background:#fff;display:flex;flex-direction:column;padding:28px 24px 20px 24px;min-height:842px;">
            <div id="previewSummaryBlock" style="margin-bottom:16px;">
              <div style="font-size:9px;font-weight:700;letter-spacing:0.16em;color:#1F3855;text-transform:uppercase;border-bottom:1.5px solid #1F3855;padding-bottom:4px;margin-bottom:8px;">PROFESSIONAL SUMMARY</div>
              <p id="previewSummaryText" style="font-size:8px;color:#374151;line-height:1.65;"></p>
            </div>
            <div id="previewMainCol" style="display:flex;flex-direction:column;gap:16px;flex:1;"></div>
          </div>
        `;
      }}
    }}

    function renderClassicNavyPreview() {{
      const sheet = document.getElementById('resumeSheet');
      if (!sheet) return;
      ensureClassicNavyDom(sheet);

      const p = cvData.personal || {{}};
      const lastName  = (p.last_name !== undefined ? p.last_name : 'MORGAN').toUpperCase();
      const firstName = (p.first_name !== undefined ? p.first_name : 'ALEX').toUpperCase();

      // Dynamic Profile Photo (placeholder shown when no image is uploaded)
      const photoEl = document.getElementById('previewPhoto');
      const photoBox = document.getElementById('previewPhotoContainer');
      const photoSrc = p.photo_url || DEFAULT_AVATAR;
      if (photoEl) {{
        photoEl.src = photoSrc;
      }}
      if (photoBox) {{
        photoBox.style.display = 'block';
      }}

      // Sidebar name
      const lnEl = document.getElementById('previewLastName');
      const fnEl = document.getElementById('previewFirstName');
      if (lnEl) lnEl.textContent = lastName || (firstName ? '' : 'LAST NAME');
      if (fnEl) fnEl.textContent = firstName || (lastName ? '' : 'FIRST NAME');

      // Headline / title
      const headlineEl = document.getElementById('previewHeadline');
      if (headlineEl) {{
        const hl = (p.headline || '').toUpperCase();
        headlineEl.textContent = hl;
        headlineEl.style.display = hl ? 'block' : 'none';
      }}

      // Contact in sidebar
      const emailEl = document.getElementById('previewSidebarEmail');
      const phoneEl = document.getElementById('previewSidebarPhone');
      const cityEl  = document.getElementById('previewSidebarCity');
      const dobEl   = document.getElementById('previewSidebarDob');
      const liEl    = document.getElementById('previewSidebarLinkedin');
      const webEl   = document.getElementById('previewSidebarWebsite');
      const extrasDiv = document.getElementById('previewSidebarExtras');

      if (emailEl) emailEl.textContent = p.email || '';
      if (phoneEl) phoneEl.textContent = p.phone || '';
      if (cityEl)  cityEl.textContent  = (p.address || p.city || '');

      // Date of birth
      if (dobEl) {{
        if (p.date_of_birth && p.date_of_birth.trim()) {{
          dobEl.innerHTML = `<span style="color:#94A3B8;">Born:</span> <span style="color:#CBD5E1;">${{p.date_of_birth.trim()}}</span>`;
          dobEl.style.display = 'block';
        }} else {{
          dobEl.innerHTML = '';
          dobEl.style.display = 'none';
        }}
      }}

      // LinkedIn
      if (liEl) {{
        if (p.linkedin && p.linkedin.trim()) {{
          const raw = p.linkedin.trim();
          let display = raw;
          let href = raw.startsWith('http') ? raw : `https://${{raw}}`;
          if (raw.includes('linkedin.com/in/')) {{
            const slug = raw.split('linkedin.com/in/')[1].split('/')[0].split('?')[0];
            const parts = slug.replace(/[-_]/g, ' ');
            display = `${{parts}} | LinkedIn`;
          }} else if (!raw.toLowerCase().includes('linkedin')) {{
            display = `${{raw}} | LinkedIn`;
          }}
          liEl.innerHTML = `<a href="${{href}}" target="_blank" style="color:#CBD5E1;text-decoration:none;" class="hover:underline" title="${{raw}}">${{display}}</a>`;
          liEl.style.display = 'block';
        }} else {{
          liEl.innerHTML = '';
          liEl.style.display = 'none';
        }}
      }}

      // Website
      if (webEl) {{
        if (p.website && p.website.trim()) {{
          const raw = p.website.trim();
          let display = raw.replace(/^https?:\\/\\//, '').replace(/\\/$/, '');
          let href = raw.startsWith('http') ? raw : `https://${{raw}}`;
          webEl.innerHTML = `<a href="${{href}}" target="_blank" style="color:#CBD5E1;text-decoration:none;" class="hover:underline" title="${{raw}}">🌐 ${{display}}</a>`;
          webEl.style.display = 'block';
        }} else {{
          webEl.innerHTML = '';
          webEl.style.display = 'none';
        }}
      }}

      // Dynamic Extra Fields
      if (extrasDiv) {{
        extrasDiv.innerHTML = '';
        (p.extras || []).forEach(item => {{
          if (item.key === 'linkedin' || item.key === 'website') return;
          if (!item.value || !item.value.trim()) return;

          const itemEl = document.createElement('div');
          itemEl.style.cssText = 'font-size:7.5px;color:#CBD5E1;margin-bottom:3px;line-height:1.4;';
          if (item.value.startsWith('http://') || item.value.startsWith('https://')) {{
            const cleanUrl = item.value.replace(/^https?:\\/\\//, '').replace(/\\/$/, '');
            itemEl.innerHTML = `<span style="color:#94A3B8;">${{item.label}}:</span> <a href="${{item.value}}" target="_blank" style="color:#CBD5E1;text-decoration:none;" class="hover:underline">${{cleanUrl}}</a>`;
          }} else {{
            itemEl.innerHTML = `<span style="color:#94A3B8;">${{item.label}}:</span> <span style="color:#CBD5E1;">${{item.value}}</span>`;
          }}
          extrasDiv.appendChild(itemEl);
        }});
      }}

      // SKILLS in sidebar
      const skillsDiv = document.getElementById('previewSidebarSkills');
      if (skillsDiv) {{
        skillsDiv.innerHTML = '';
        (cvData.skills || []).forEach(group => {{
          const catDiv = document.createElement('div');
          catDiv.style.cssText = 'margin-bottom:8px;';
          const isGroupAi = !!group.is_ai;

          const itemsHtml = (group.items || []).map(sk => {{
            const isAi = (typeof sk === 'object' && sk.is_ai) || isGroupAi;
            const name = typeof sk === 'object' ? sk.name : sk;
            if (isAi) {{
              return `<span style="color:#38BDF8;font-weight:700;display:inline-flex;align-items:center;gap:1.5px;" title="AI-Generated Skill"><span style="color:#67E8F9;font-size:6px;">✨</span>${{name}}</span>`;
            }}
            return `<span style="color:#CBD5E1;">${{name}}</span>`;
          }}).join(', ');

          const catTitle = group.category || '';
          const catColor = isGroupAi ? '#7DD3FC' : '#fff';

          catDiv.innerHTML = `
            <div style="font-weight:700;color:${{catColor}};font-size:7.5px;margin-bottom:2px;">${{catTitle}}</div>
            <div style="font-size:7px;line-height:1.7;">${{itemsHtml}}</div>
          `;
          skillsDiv.appendChild(catDiv);
        }});
      }}

      // LANGUAGES in sidebar
      const langsDiv = document.getElementById('previewSidebarLanguages');
      if (langsDiv) {{
        langsDiv.innerHTML = (cvData.languages || []).map(l =>
          `<div style="margin-bottom:4px;"><span style="color:#fff;font-weight:600;">${{l.name}}</span> <span style="color:#94A3B8;">- ${{l.level}}</span></div>`
        ).join('');
      }}

      // HOBBIES in sidebar
      const hobbiesBlock = document.getElementById('previewSidebarHobbiesBlock');
      const hobbiesDiv   = document.getElementById('previewSidebarHobbies');
      const hEditorBlock = document.getElementById('hobbiesSectionBlock');
      const isHobbiesOn  = hEditorBlock && !hEditorBlock.classList.contains('hidden');
      if (hobbiesBlock) {{
        if (isHobbiesOn && cvData.hobbies && cvData.hobbies.length > 0) {{
          hobbiesBlock.style.display = 'block';
          if (hobbiesDiv) hobbiesDiv.innerHTML = (cvData.hobbies || []).map(h =>
            `<div style="margin-bottom:2px;">${{h}}</div>`
          ).join('');
        }} else {{
          hobbiesBlock.style.display = 'none';
        }}
      }}

      // PROFESSIONAL SUMMARY (always shown at top right)
      const summaryEl = document.getElementById('previewSummaryText');
      const summaryBlock = document.getElementById('previewSummaryBlock');
      if (summaryEl) {{
        if (cvData.summary) {{
          summaryEl.textContent = cvData.summary;
          if (summaryBlock) summaryBlock.style.display = 'block';
        }} else {{
          if (summaryBlock) summaryBlock.style.display = 'none';
        }}
      }}

      // DYNAMIC right-column sections
      const mainCol = document.getElementById('previewMainCol');
      if (mainCol) {{
        mainCol.innerHTML = '';
        let secOrder = (cvData.sections_order && cvData.sections_order.length > 0)
          ? [...cvData.sections_order]
          : ['education', 'projects'];

        const hasEdu = secOrder.some(k => ['education', 'formation'].includes((k || '').toLowerCase()));
        const hasProj = secOrder.some(k => ['projects', 'projets', 'experience'].includes((k || '').toLowerCase()));
        if (!hasEdu) secOrder.push('education');
        if (!hasProj) secOrder.push('projects');

        secOrder.forEach(secKey => {{
          const k = (secKey || '').toLowerCase();
          if (k === 'profile' || k === 'profil' || k === 'skills' || k === 'languages' || k === 'hobbies') return;

          // EDUCATION
          if (k === 'education' || k === 'formation') {{
            const block = document.createElement('div');
            let itemsHtml = '';
            (cvData.education || []).forEach(edu => {{
              const dates = `${{edu.start_date || ''}} - ${{edu.current ? 'Present' : (edu.end_date || '')}}`;
              let bullets = '';
              if (Array.isArray(edu.description) && edu.description.length > 0) {{
                bullets = edu.description.map(b => {{
                  const txt = typeof b === 'object' ? (b.text || '') : b;
                  return txt ? `<div style="font-size:7.5px;color:#374151;line-height:1.6;padding-left:10px;position:relative;margin-bottom:2px;"><span style="position:absolute;left:0;color:#1F3855;">•</span>${{txt}}</div>` : '';
                }}).filter(Boolean).join('');
              }}
              itemsHtml += `
                <div style="margin-bottom:10px;">
                  <div style="display:flex;justify-content:space-between;align-items:baseline;">
                    <div style="font-size:8px;font-weight:700;color:#1F3855;">${{edu.degree || ''}}</div>
                    <div style="font-size:7px;color:#6B7280;white-space:nowrap;margin-left:8px;">${{dates}}</div>
                  </div>
                  <div style="font-size:7.5px;color:#4B5563;margin-top:1px;">${{edu.institution || ''}}${{edu.location ? ', ' + edu.location : ''}}</div>
                  ${{bullets ? `<div style="margin-top:2px;">${{bullets}}</div>` : ''}}
                </div>
              `;
            }});
            block.innerHTML = `
              <div style="font-size:9px;font-weight:700;letter-spacing:0.16em;color:#1F3855;text-transform:uppercase;border-bottom:1.5px solid #1F3855;padding-bottom:4px;margin-bottom:8px;">FORMATION</div>
              <div>${{itemsHtml || '<div style="font-size:7.5px;color:#9CA3AF;font-style:italic;">No education listed</div>'}}</div>
            `;
            mainCol.appendChild(block);
          }}

          // PROJECTS / EXPERIENCE
          else if (k === 'projects' || k === 'projets' || k === 'experience') {{
            const block = document.createElement('div');
            let itemsHtml = '';
            const projList = (cvData.projects && cvData.projects.length > 0)
              ? cvData.projects
              : (cvData.experience || []);

            projList.forEach(proj => {{
              const bullets = (proj.description || proj.bullets || []).map(b => {{
                const txt = typeof b === 'object' ? (b.text || '') : b;
                if (!txt) return '';
                return `<div style="font-size:7.5px;color:#374151;line-height:1.6;padding-left:10px;position:relative;margin-bottom:2px;"><span style="position:absolute;left:0;color:#1F3855;">•</span>${{txt}}</div>`;
              }}).filter(Boolean).join('');

              const title = proj.title || proj.job_title || proj.position || '';
              const dateStr = [proj.start_date, (proj.current ? 'Present' : proj.end_date)].filter(Boolean).join(' – ') || (proj.start_date || '');
              const subLine = [proj.role, proj.company || proj.organization, proj.location].filter(Boolean).join(' • ');

              itemsHtml += `
                <div style="margin-bottom:12px;">
                  <div style="display:flex;justify-content:space-between;align-items:baseline;">
                    <div style="font-size:8px;font-weight:700;color:#1F3855;">${{title}}</div>
                    ${{dateStr ? `<div style="font-size:7px;color:#6B7280;white-space:nowrap;margin-left:8px;">${{dateStr}}</div>` : ''}}
                  </div>
                  ${{subLine ? `<div style="font-size:7.5px;font-weight:600;color:#374151;text-transform:uppercase;letter-spacing:0.06em;margin-top:1px;">${{subLine}}</div>` : ''}}
                  ${{proj.subtitle ? `<div style="font-size:7px;color:#6B7280;font-style:italic;margin-top:1px;">${{proj.subtitle}}</div>` : ''}}
                  ${{bullets ? `<div style="margin-top:3px;">${{bullets}}</div>` : ''}}
                </div>
              `;
            }});
            block.innerHTML = `
              <div style="font-size:9px;font-weight:700;letter-spacing:0.16em;color:#1F3855;text-transform:uppercase;border-bottom:1.5px solid #1F3855;padding-bottom:4px;margin-bottom:8px;">${{k === 'experience' ? 'EXPÉRIENCE' : 'PROJETS'}}</div>
              <div>${{itemsHtml || '<div style="font-size:7.5px;color:#9CA3AF;font-style:italic;">No projects listed</div>'}}</div>
            `;
            mainCol.appendChild(block);

            // If BOTH cvData.projects and cvData.experience exist separately and we are rendering projects, also render Experience block
            if (cvData.projects && cvData.projects.length > 0 && cvData.experience && cvData.experience.length > 0 && k !== 'experience') {{
              const expBlock = document.createElement('div');
              let expItems = '';
              cvData.experience.forEach(exp => {{
                const bHtml = (exp.description || exp.bullets || []).map(b => {{
                  const txt = typeof b === 'object' ? (b.text || '') : b;
                  if (!txt) return '';
                  return `<div style="font-size:7.5px;color:#374151;line-height:1.6;padding-left:10px;position:relative;margin-bottom:2px;"><span style="position:absolute;left:0;color:#1F3855;">•</span>${{txt}}</div>`;
                }}).filter(Boolean).join('');
                const eTitle = exp.title || exp.job_title || exp.position || '';
                const eDates = [exp.start_date, (exp.current ? 'Present' : exp.end_date)].filter(Boolean).join(' – ');
                const eSub = [exp.role, exp.company || exp.employer, exp.location].filter(Boolean).join(' • ');
                expItems += `
                  <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:baseline;">
                      <div style="font-size:8px;font-weight:700;color:#1F3855;">${{eTitle}}</div>
                      ${{eDates ? `<div style="font-size:7px;color:#6B7280;white-space:nowrap;margin-left:8px;">${{eDates}}</div>` : ''}}
                    </div>
                    ${{eSub ? `<div style="font-size:7.5px;font-weight:600;color:#374151;text-transform:uppercase;letter-spacing:0.06em;margin-top:1px;">${{eSub}}</div>` : ''}}
                    ${{bHtml ? `<div style="margin-top:3px;">${{bHtml}}</div>` : ''}}
                  </div>
                `;
              }});
              expBlock.innerHTML = `
                <div style="font-size:9px;font-weight:700;letter-spacing:0.16em;color:#1F3855;text-transform:uppercase;border-bottom:1.5px solid #1F3855;padding-bottom:4px;margin-bottom:8px;">EXPÉRIENCE</div>
                <div>${{expItems || '<div style="font-size:7.5px;color:#9CA3AF;font-style:italic;">No experience listed</div>'}}</div>
              `;
              mainCol.appendChild(expBlock);
            }}
          }}

          // CUSTOM SECTIONS
          else {{
            const customSec = (cvData.custom_sections || []).find(s => s.id === k);
            if (customSec) {{
              const block = document.createElement('div');
              const itemsHtml = (customSec.items || []).filter(i => (typeof i === 'string' ? i : (i.text || '')).trim()).map(i => {{
                const t = typeof i === 'string' ? i : (i.text || '');
                return `<div style="font-size:7.5px;color:#374151;line-height:1.6;padding-left:10px;position:relative;margin-bottom:2px;"><span style="position:absolute;left:0;color:#1F3855;">•</span>${{t}}</div>`;
              }}).join('');
              block.innerHTML = `
                <div style="font-size:9px;font-weight:700;letter-spacing:0.16em;color:#1F3855;text-transform:uppercase;border-bottom:1.5px solid #1F3855;padding-bottom:4px;margin-bottom:8px;">${{(customSec.label || customSec.id).toUpperCase()}}</div>
                <div>${{itemsHtml || '<div style="font-size:7.5px;color:#9CA3AF;font-style:italic;">No items yet</div>'}}</div>
              `;
              mainCol.appendChild(block);
            }}
          }}
        }});
      }}
    }}
    // ── Drag & Drop Section Reordering (HTML5) ──
    let _draggedItem = null;

    function initDragAndDropForBlock(item) {{
      const container = document.getElementById('dynamicSectionsList');
      item.addEventListener('dragstart', (e) => {{
        _draggedItem = item;
        item.classList.add('opacity-40');
        e.dataTransfer.effectAllowed = 'move';
      }});
      item.addEventListener('dragend', () => {{
        if (_draggedItem) {{
          _draggedItem.classList.remove('opacity-40');
          _draggedItem = null;
        }}
        const newOrder = Array.from(container.querySelectorAll('.section-block')).map(el => el.getAttribute('data-sec-id'));
        cvData.sections_order = newOrder;
        renderLivePreview();
        flashSaved();
      }});
      item.addEventListener('dragover', (e) => {{
        e.preventDefault();
        const target = e.target.closest('.section-block');
        if (target && target !== _draggedItem) {{
          const rect = target.getBoundingClientRect();
          const next = (e.clientY - rect.top) / (rect.bottom - rect.top) > 0.5;
          container.insertBefore(_draggedItem, next && target.nextSibling || target);
        }}
      }});
    }}

    function initDragAndDrop() {{
      const container = document.getElementById('dynamicSectionsList');
      container.querySelectorAll('.section-block').forEach(item => {{
        initDragAndDropForBlock(item);
      }});
    }}

    // ── Inline Skill Item Helpers ──
    function addSkillItem(gi, skill) {{
      if (skill && skill.trim()) {{
        cvData.skills[gi].items.push(skill.trim());
        renderSkillsList();
        renderLivePreview();
        flashSaved();
      }}
    }}

    function removeSkillItem(gi, si) {{
      cvData.skills[gi].items.splice(si, 1);
      renderSkillsList();
      renderLivePreview();
      flashSaved();
    }}

    function deleteSkillGroup(gi) {{
      cvData.skills.splice(gi, 1);
      renderSkillsList();
      renderLivePreview();
      flashSaved();
    }}

    function deleteHobby(hi) {{
      cvData.hobbies.splice(hi, 1);
      renderHobbiesList();
      renderLivePreview();
      flashSaved();
    }}

    function addCustomExtraFieldInline() {{
      const pillsContainer = document.querySelector('.flex.flex-wrap.gap-2.pt-2');
      if (!pillsContainer) return;
      let existingRow = document.getElementById('customExtraFieldInlineRow');
      if (existingRow) {{
        existingRow.querySelector('input').focus();
        return;
      }}
      const row = document.createElement('div');
      row.id = 'customExtraFieldInlineRow';
      row.className = 'w-full flex items-center gap-2 mt-2 pt-1';
      row.innerHTML = `
        <input id="customExtraFieldNameInput" type="text" placeholder="Field name (e.g. GitHub, Portfolio)..."
          class="text-xs rounded-full border border-gray-300 focus:border-blue-500 focus:ring-blue-500 px-3 py-1.5 flex-1"
          onkeydown="if(event.key==='Enter') confirmCustomExtraFieldInline()"/>
        <button onclick="confirmCustomExtraFieldInline()" type="button" class="px-3 py-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded-full font-medium transition">Add</button>
        <button onclick="document.getElementById('customExtraFieldInlineRow').remove()" type="button" class="px-3 py-1.5 text-xs border border-gray-300 text-gray-600 hover:bg-gray-50 rounded-full transition">Cancel</button>
      `;
      pillsContainer.parentElement.appendChild(row);
      document.getElementById('customExtraFieldNameInput').focus();
    }}

    function confirmCustomExtraFieldInline() {{
      const inp = document.getElementById('customExtraFieldNameInput');
      if (!inp) return;
      const name = inp.value.trim();
      if (!name) return;
      const row = document.getElementById('customExtraFieldInlineRow');
      if (row) row.remove();
      addExtraField(name);
    }}

    function addExtraField(fieldName, initVal = '') {{
      if (!fieldName) return;
      const container = document.getElementById('extraFieldsArea');
      const key = fieldName.toLowerCase().replace(/[^a-z0-9]/g, '_');
      const fId = 'extra_' + key;
      if (document.getElementById(fId)) {{
        const inp = document.getElementById(fId).querySelector('input');
        if (inp) inp.focus();
        return;
      }}

      const div = document.createElement('div');
      div.id = fId;
      div.setAttribute('data-field-label', fieldName);
      div.className = 'flex items-center space-x-2';
      div.innerHTML = `
        <div class="flex-1">
          <label class="block text-xs font-medium text-gray-600 mb-1">${{fieldName}}</label>
          <input type="text" value="${{initVal}}" oninput="updatePersonal()" placeholder="${{fieldName}}..." class="w-full text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 py-1.5 px-3"/>
        </div>
        <button onclick="document.getElementById('${{fId}}').remove(); updatePersonal();" class="text-gray-400 hover:text-red-600 pt-5" type="button" title="Remove field">✕</button>
      `;
      container.appendChild(div);
      const inputEl = div.querySelector('input');
      if (inputEl && !initVal) inputEl.focus();
      updatePersonal();
    }}

    function showToast(msg) {{
      let t = document.getElementById('toastNotif');
      if (!t) {{
        t = document.createElement('div');
        t.id = 'toastNotif';
        t.className = 'fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-5 py-2.5 rounded-xl bg-gray-900 text-white text-sm font-medium shadow-lg transition-all opacity-0 pointer-events-none';
        document.body.appendChild(t);
      }}
      t.textContent = msg;
      t.style.opacity = '1';
      clearTimeout(window._toastTimer);
      window._toastTimer = setTimeout(() => {{ t.style.opacity = '0'; }}, 2200);
    }}

    function addNewSection(secName, fromPillBtn) {{
      const key = secName.toLowerCase().replace(/\\s+/g, '_');

      // Hobbies: reveal hidden block
      if (key === 'hobbies') {{
        const hBlock = document.getElementById('hobbiesSectionBlock');
        if (hBlock) {{
          hBlock.classList.remove('hidden');
          hBlock.scrollIntoView({{ behavior: 'smooth' }});
        }}
        if (!cvData.sections_order.includes('hobbies')) {{
          cvData.sections_order.push('hobbies');
        }}
        if (fromPillBtn) {{
          fromPillBtn.disabled = true;
          fromPillBtn.classList.add('opacity-40','cursor-not-allowed');
        }}
        const inp = document.getElementById('hobbyInlineInput');
        if (inp) inp.focus();
        renderHobbiesList();
        renderLivePreview();
        flashSaved();
        return;
      }}

      // If section block already exists in list, scroll to it
      const existing = document.querySelector(`[data-sec-id="${{key}}"]`);
      if (existing) {{
        existing.scrollIntoView({{ behavior: 'smooth' }});
        showToast(`"${{secName}}" is already added`);
        return;
      }}

      // Disable the pill button
      if (fromPillBtn) {{
        fromPillBtn.disabled = true;
        fromPillBtn.classList.add('opacity-40','cursor-not-allowed');
      }}

      // Ensure cvData.custom_sections exists
      if (!cvData.custom_sections) cvData.custom_sections = [];
      const secData = {{ id: key, label: secName, items: [] }};
      cvData.custom_sections.push(secData);

      if (!cvData.sections_order.includes(key)) {{
        cvData.sections_order.push(key);
      }}

      // Build the new section DOM block
      const secList = document.getElementById('dynamicSectionsList');
      const block = document.createElement('div');
      block.className = 'section-block space-y-3 border-b border-gray-200 pb-5 pt-1';
      block.setAttribute('draggable', 'true');
      block.setAttribute('data-sec-id', key);
      block.setAttribute('data-sec-label', secName);

      const bodyId = `customBody_${{key}}`;
      const itemsId = `customItems_${{key}}`;

      block.innerHTML = `
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="text-gray-400 hover:text-gray-600 cursor-grab flex items-center drag-handle" title="Drag to reorder">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                <path d="M5 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm6-8a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm0 4a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Z"></path>
              </svg>
            </span>
            <h2 class="text-base font-bold tracking-wide text-gray-900 uppercase select-none">${{secName}}</h2>
          </div>
          <div class="flex items-center space-x-2">
            <button onclick="toggleSection('${{bodyId}}')" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-500 hover:text-gray-700 hover:border-gray-400 transition" type="button" title="Collapse">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M5 15l7-7 7 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
            </button>
            <button onclick="removeCustomSection('${{key}}', this)" class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center text-gray-400 hover:bg-red-50 hover:text-red-600 hover:border-red-300 transition" type="button" title="Remove section">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
              </svg>
            </button>
          </div>
        </div>
        <div id="${{bodyId}}" class="space-y-2 pt-1">
          <div id="${{itemsId}}" class="space-y-2"></div>
          <button onclick="addCustomItem('${{key}}')" class="inline-flex items-center space-x-1.5 px-4 py-2 border border-gray-400 hover:border-gray-600 rounded-full text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition mt-1" type="button">
            <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
            </svg>
            <span>Add item</span>
          </button>
        </div>
      `;

      // Insert before the hobbies block (which is always last in the list)
      const hobbiesBlock = document.getElementById('hobbiesSectionBlock');
      if (hobbiesBlock && hobbiesBlock.parentNode === secList) {{
        secList.insertBefore(block, hobbiesBlock);
      }} else {{
        secList.appendChild(block);
      }}

      // Make the new block draggable
      initDragAndDropForBlock(block);

      // Automatically add the first input item ready for the user
      addCustomItem(key);

      block.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
      renderLivePreview();
      flashSaved();
    }}

    function addCustomItem(secKey) {{
      const itemsContainer = document.getElementById(`customItems_${{secKey}}`);
      if (!itemsContainer) return;

      const secData = (cvData.custom_sections || []).find(s => s.id === secKey);

      const idx = secData ? secData.items.length : 0;
      if (secData) secData.items.push('');

      const row = document.createElement('div');
      row.className = 'flex items-start gap-2';
      const inputId = `customItem_${{secKey}}_${{Date.now()}}`;
      row.innerHTML = `
        <textarea id="${{inputId}}" rows="2"
          class="flex-1 text-sm rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 p-2.5 leading-relaxed resize-y"
          placeholder="Add content for this section..."
          oninput="updateCustomItem('${{secKey}}', this)"></textarea>
        <button onclick="removeCustomItem('${{secKey}}', this)" class="mt-1 w-7 h-7 flex-shrink-0 rounded-full border border-gray-300 flex items-center justify-center text-gray-400 hover:bg-red-50 hover:text-red-600 hover:border-red-300 transition" type="button" title="Remove item">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
          </svg>
        </button>
      `;
      itemsContainer.appendChild(row);
      row.querySelector('textarea').focus();
    }}

    function updateCustomItem(secKey, textarea) {{
      const secData = (cvData.custom_sections || []).find(s => s.id === secKey);
      if (!secData) return;
      const rows = Array.from(textarea.closest('[id^="customItems_"]').querySelectorAll('textarea'));
      const rowIdx = rows.indexOf(textarea);
      if (rowIdx >= 0) {{
        while (secData.items.length <= rowIdx) secData.items.push('');
        secData.items[rowIdx] = textarea.value;
      }}
      renderLivePreview();
      flashSaved();
    }}

    function removeCustomItem(secKey, btn) {{
      const row = btn.closest('.flex.items-start');
      const container = row.parentElement;
      const rows = Array.from(container.querySelectorAll('.flex.items-start'));
      const rowIdx = rows.indexOf(row);
      const secData = (cvData.custom_sections || []).find(s => s.id === secKey);
      if (secData && rowIdx >= 0) secData.items.splice(rowIdx, 1);
      row.remove();
      renderLivePreview();
      flashSaved();
    }}

    function removeCustomSection(secKey, btn) {{
      // Remove block from DOM
      const block = btn.closest('.section-block');
      if (block) block.remove();

      // Remove from cvData
      cvData.custom_sections = (cvData.custom_sections || []).filter(s => s.id !== secKey);
      cvData.sections_order = cvData.sections_order.filter(s => s !== secKey);

      // Re-enable the pill button
      const pillBtn = document.querySelector(`[data-pill-sec="${{secKey}}"]`);
      if (pillBtn) {{
        pillBtn.disabled = false;
        pillBtn.classList.remove('opacity-40','cursor-not-allowed');
      }}

      renderLivePreview();
      flashSaved();
    }}

    function removeHobbiesSection() {{
      const hBlock = document.getElementById('hobbiesSectionBlock');
      if (hBlock) hBlock.classList.add('hidden');
      cvData.hobbies = [];
      cvData.sections_order = (cvData.sections_order || []).filter(s => s !== 'hobbies');
      renderHobbiesList();
      // Re-enable hobbies pill
      const hobPill = document.querySelector('[data-pill-sec="hobbies"]');
      if (hobPill) {{ hobPill.disabled = false; hobPill.classList.remove('opacity-40','cursor-not-allowed'); }}
      renderLivePreview();
      flashSaved();
    }}

    function promptCustomSection() {{
      // Show inline input for custom section name
      const pillsArea = document.querySelector('[data-purpose="add-section-pills"]');
      if (!pillsArea) return;

      // Don't add a second input if one already exists
      if (document.getElementById('customSecNameInput')) {{
        document.getElementById('customSecNameInput').focus();
        return;
      }}

      const inputRow = document.createElement('div');
      inputRow.className = 'flex items-center gap-2 mt-2';
      inputRow.innerHTML = `
        <input id="customSecNameInput" type="text" maxlength="40"
          class="flex-1 text-sm rounded-full border border-gray-400 focus:border-blue-500 focus:ring-blue-500 py-1.5 px-4"
          placeholder="Section name (e.g. Volunteering)..." />
        <button onclick="confirmCustomSection()" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-full font-medium transition" type="button">Add</button>
        <button onclick="this.parentElement.remove()" class="px-3 py-1.5 border border-gray-300 text-gray-600 hover:bg-gray-50 text-sm rounded-full transition" type="button">Cancel</button>
      `;
      pillsArea.appendChild(inputRow);
      const inp = document.getElementById('customSecNameInput');
      inp.focus();
      inp.addEventListener('keydown', (e) => {{
        if (e.key === 'Enter') confirmCustomSection();
        if (e.key === 'Escape') inputRow.remove();
      }});
    }}

    function confirmCustomSection() {{
      const inp = document.getElementById('customSecNameInput');
      if (!inp) return;
      const name = inp.value.trim();
      if (!name) {{ inp.focus(); return; }}
      const inputRow = inp.closest('.flex.items-center.gap-2');
      if (inputRow) inputRow.remove();
      addNewSection(name, null);
    }}

    function toggleSection(id) {{
      const el = document.getElementById(id);
      if (el) {{
        el.classList.toggle('hidden');
      }}
    }}

    function toggleZoom() {{
      const sheet = document.getElementById('resumeSheet');
      if (currentZoom === 100) {{
        currentZoom = 80;
        sheet.style.transform = 'scale(0.85)';
        sheet.style.transformOrigin = 'top center';
        document.getElementById('zoomLabel').textContent = 'Zoom 85%';
      }} else {{
        currentZoom = 100;
        sheet.style.transform = 'scale(1)';
        document.getElementById('zoomLabel').textContent = 'Zoom 100%';
      }}
    }}

    function clearAllCvInfo() {{

      // Reset cvData
      cvData.personal = {{
        first_name: '',
        last_name: '',
        headline: '',
        use_headline: false,
        email: '',
        phone: '',
        address: '',
        postcode: '',
        city: '',
        date_of_birth: '',
        photo_url: '',
        linkedin: '',
        extras: []
      }};
      cvData.summary = '';
      cvData.target_job = '';
      cvData.cv_name = 'CV Untitled';
      cvData.skills = [];
      cvData.ai_skill_names = [];
      cvData.languages = [];
      cvData.education = [];
      cvData.projects = [];
      cvData.hobbies = [];
      cvData.custom_sections = [];
      cvData.sections_order = ['education', 'projects'];

      // Reset form fields
      document.getElementById('inputFirstName').value = '';
      document.getElementById('inputLastName').value = '';
      document.getElementById('inputHeadline').value = '';
      document.getElementById('inputUseHeadline').checked = false;
      document.getElementById('inputEmail').value = '';
      document.getElementById('inputPhone').value = '';
      document.getElementById('inputAddress').value = '';
      document.getElementById('inputPostcode').value = '';
      document.getElementById('inputCity').value = '';
      document.getElementById('inputDob').value = '';
      document.getElementById('inputSummary').value = '';
      document.getElementById('photoThumb').src = DEFAULT_AVATAR;
      const pPhoto = document.getElementById('previewPhoto');
      if (pPhoto) pPhoto.src = DEFAULT_AVATAR;

      const tj = document.getElementById('targetJobInput');
      if (tj) tj.value = '';

      const headerNameInput = document.getElementById('cvNameHeaderInput');
      if (headerNameInput) headerNameInput.value = 'CV Untitled';

      // Clear extra fields area
      const extraArea = document.getElementById('extraFieldsArea');
      if (extraArea) extraArea.innerHTML = '';

      // Hide hobbies section block
      const hBlock = document.getElementById('hobbiesSectionBlock');
      if (hBlock) hBlock.classList.add('hidden');

      // Remove dynamically added custom section DOM blocks
      document.querySelectorAll('#dynamicSectionsList .section-block').forEach(el => {{
        const secId = el.getAttribute('data-sec-id');
        if (secId && !['skills', 'languages', 'education', 'projects', 'profile', 'hobbies'].includes(secId)) {{
          el.remove();
        }}
      }});

      // Re-enable all bottom pills
      document.querySelectorAll('[data-pill-sec]').forEach(btn => {{
        btn.disabled = false;
        btn.classList.remove('opacity-40', 'cursor-not-allowed');
      }});

      // Re-render editor lists and preview
      renderSkillsList();
      renderLanguagesList();
      renderEducationList();
      renderProjectsList();
      renderHobbiesList();
      renderLivePreview();
      showToast('CV cleared! Ready for new information.');
      flashSaved();
    }}

    function loadSampleCvInfo() {{
      const extraArea = document.getElementById('extraFieldsArea');
      if (extraArea) extraArea.innerHTML = '';

      const sample = JSON.parse(JSON.stringify(SAMPLE_CV_DATA));
      for (const k in sample) {{
        cvData[k] = sample[k];
      }}

      initEditor();

      const hBlock = document.getElementById('hobbiesSectionBlock');
      if (hBlock) {{
        if (cvData.hobbies && cvData.hobbies.length > 0) {{
          hBlock.classList.remove('hidden');
        }} else {{
          hBlock.classList.add('hidden');
        }}
      }}

      renderSkillsList();
      renderLanguagesList();
      renderEducationList();
      renderProjectsList();
      renderHobbiesList();
      renderLivePreview();
      showToast('Sample template loaded! Feel free to customize.');
      flashSaved();
    }}

    function selectTemplate(tpl) {{
      if (tpl === 'executive') {{
        currentTemplate = 'executive';
      }} else if (tpl === 'classic' || tpl === 'sidebar') {{
        currentTemplate = 'classic';
      }} else {{
        currentTemplate = 'simple';
      }}
      if (!cvData.style) cvData.style = {{}};
      cvData.style.template = currentTemplate === 'simple' ? 'simple' : (currentTemplate === 'executive' ? 'executive' : 'sidebar');

      const btnSimple = document.getElementById('tplBtnSimple');
      const btnClassic = document.getElementById('tplBtnClassic');
      const btnExecutive = document.getElementById('tplBtnExecutive');
      const activeClass = 'px-2.5 py-1 rounded-md font-semibold transition bg-white text-blue-700 shadow-xs';
      const inactiveClass = 'px-2.5 py-1 rounded-md font-semibold transition text-gray-600 hover:text-gray-900';

      if (btnSimple) btnSimple.className = currentTemplate === 'simple' ? activeClass : inactiveClass;
      if (btnClassic) btnClassic.className = currentTemplate === 'classic' ? activeClass : inactiveClass;
      if (btnExecutive) btnExecutive.className = currentTemplate === 'executive' ? activeClass : inactiveClass;

      if (currentTemplate === 'simple') {{
        showToast('Switched to Simple template!');
      }} else if (currentTemplate === 'executive') {{
        showToast('Switched to Executive Slate template!');
      }} else {{
        showToast('Switched to Classic Navy template!');
      }}
      renderLivePreview();
      flashSaved();
    }}

    function toggleTemplate() {{
      if (currentTemplate === 'simple') selectTemplate('classic');
      else if (currentTemplate === 'classic') selectTemplate('executive');
      else selectTemplate('simple');
    }}

    async function downloadResume() {{
      const sheet = document.getElementById('resumeSheet');
      if (!sheet) {{
        showToast('Error: Resume preview sheet not found');
        return;
      }}

      // Dynamic filename taken from the top CV name input (e.g. "CV Alex Morgan" -> "CV Alex Morgan.pdf")
      const headerInput = document.getElementById('cvNameHeaderInput');
      let baseTitle = (headerInput && headerInput.value ? headerInput.value : (cvData.cv_name || '')).trim();
      let filename = '';
      if (baseTitle) {{
        const sanitized = baseTitle.replace(/[/\\?%*:|"<>]/g, '_').trim();
        filename = sanitized.replace(/\\.pdf$/i, '') + '.pdf';
      }} else {{
        const p = cvData.personal || {{}};
        const fn = (p.first_name || 'Resume').trim().replace(/[^a-zA-Z0-9_-]/g, '_');
        const ln = (p.last_name || '').trim().replace(/[^a-zA-Z0-9_-]/g, '_');
        filename = `CV_${{fn}}_${{ln}}.pdf`.replace(/__+/g, '_').replace(/_\\.pdf$/, '.pdf');
      }}

      // Update download buttons to show loading state
      const dlBtns = document.querySelectorAll('button[onclick="downloadResume()"]');
      const prevBtnContents = [];
      dlBtns.forEach((b, idx) => {{
        prevBtnContents[idx] = b.innerHTML;
        b.innerHTML = `
          <svg class="w-4 h-4 animate-spin text-white mr-1.5 inline" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <span>Downloading PDF...</span>
        `;
        b.disabled = true;
      }});

      showToast('Generating your PDF file...');

      try {{
        // SEPARATE PDF EXPORT PIPELINE:
        // Dedicated offscreen clone for PDF export so the on-screen preview is NOT touched.
        const offscreen = document.createElement('div');
        offscreen.style.position = 'fixed';
        offscreen.style.left = '-9999px';
        offscreen.style.top = '0';
        offscreen.style.width = '595px';
        offscreen.style.minHeight = '842px';
        offscreen.style.height = '842px';
        offscreen.style.overflow = 'hidden';
        offscreen.style.zIndex = '-99999';
        offscreen.style.backgroundColor = '#ffffff';
        document.body.appendChild(offscreen);

        const clone = sheet.cloneNode(true);
        clone.id = 'pdfExportSheetClone';
        clone.style.width = '595px';
        clone.style.minHeight = '842px';
        clone.style.height = '842px';
        clone.style.boxShadow = 'none';
        clone.style.borderRadius = '0';
        clone.style.margin = '0';
        clone.style.padding = '0';
        clone.style.overflow = 'hidden';
        clone.style.display = 'flex';

        let photoCoords = null;
        let boxWidth = 104;
        let boxHeight = 104;

        if (currentTemplate === 'simple') {{
          clone.style.width = '595px';
          clone.style.minHeight = '842px';
          clone.style.height = '842px';
          clone.style.boxShadow = 'none';
          clone.style.borderRadius = '0';
          clone.style.margin = '0';
          clone.style.padding = '36px 38px 30px 38px';
          clone.style.overflow = 'hidden';
          clone.style.display = 'flex';
          clone.style.flexDirection = 'column';
          clone.style.backgroundColor = '#ffffff';

          offscreen.appendChild(clone);
        }} else {{
          // Keep sidebar at full A4 proportional height (842px)
          const sideCol = clone.querySelector('#previewSidebar') || clone.firstElementChild;
          if (sideCol) {{
            sideCol.style.width = '202px';
            sideCol.style.minHeight = '842px';
            sideCol.style.height = '842px';
            sideCol.style.flexShrink = '0';
          }}
          // Keep right column at full A4 proportional height (842px)
          const rightCol = clone.children[1] || clone.lastElementChild;
          if (rightCol && rightCol !== sideCol) {{
            rightCol.style.minHeight = '842px';
            rightCol.style.height = '842px';
            rightCol.style.flex = '1';
          }}

          // Fix photo in clone so html2canvas renders it with zero distortion
          const isCircle = currentTemplate === 'classic';
          const photoSrc = (cvData.personal && cvData.personal.photo_url) ? cvData.personal.photo_url : DEFAULT_AVATAR;
          const photoBox = clone.querySelector('#previewPhotoContainer') ||
                           clone.querySelector('div[style*="height:165px"]') ||
                           clone.querySelector('#execPhotoContainer') ||
                           (sideCol ? sideCol.querySelector('div[style*="border-radius"]') : null);

          // Increase circle size and set spacing in Classic Navy PDF export without touching template preview
          if (isCircle && sideCol) {{
            const topBlock = sideCol.firstElementChild;
            if (topBlock) {{
              topBlock.style.padding = '36px 20px 20px 20px';
            }}
            if (photoBox) {{
              photoBox.style.width = '104px';
              photoBox.style.height = '104px';
              photoBox.style.margin = '0 auto 18px auto';
            }}
          }}

          offscreen.appendChild(clone);

          if (photoBox) {{
            const cloneRect = clone.getBoundingClientRect();
            const bRect = photoBox.getBoundingClientRect();
            boxWidth = bRect.width || (isCircle ? 104 : 166);
            boxHeight = bRect.height || (isCircle ? 104 : 165);
            const scaleX = 595.28 / (cloneRect.width || 595);
            const scaleY = 841.89 / (cloneRect.height || 842);
            photoCoords = {{
              x: (bRect.left - cloneRect.left) * scaleX,
              y: (bRect.top - cloneRect.top) * scaleY,
              w: boxWidth * scaleX,
              h: boxHeight * scaleY
            }};
            // Hide photoBox in html2canvas so no low-res or leaking edges/crescents are drawn
            photoBox.style.visibility = 'hidden';
          }}
        }}

        // Render high-res avatar in parallel on a dedicated offscreen canvas (only for templates with photo)
        const avatarPromise = (currentTemplate === 'simple') ? Promise.resolve(null) : new Promise((resolve) => {{
          const isCircle = currentTemplate === 'classic';
          const photoSrc = (cvData.personal && cvData.personal.photo_url) ? cvData.personal.photo_url : DEFAULT_AVATAR;
          if (!photoSrc || !photoCoords) return resolve(null);
          const img = new Image();
          img.crossOrigin = 'anonymous';
          img.onload = () => {{
            try {{
              const targetW = 800;
              const targetH = isCircle ? 800 : Math.round(800 * (boxHeight / (boxWidth || 1)));
              const c = document.createElement('canvas');
              c.width = targetW;
              c.height = targetH;
              const ctx = c.getContext('2d');
              ctx.imageSmoothingEnabled = true;
              ctx.imageSmoothingQuality = 'high';

              if (isCircle) {{
                const center = targetW / 2;
                const strokeW = targetW * (3.5 / boxWidth);
                const radius = (targetW / 2) - (strokeW / 2);

                // Base navy fill
                ctx.save();
                ctx.beginPath();
                ctx.arc(center, center, radius, 0, Math.PI * 2);
                ctx.closePath();
                ctx.fillStyle = '#2D4A6B';
                ctx.fill();

                // Circular clipping mask
                ctx.clip();

                // Draw image aspect-cover
                const nw = img.naturalWidth || 1;
                const nh = img.naturalHeight || 1;
                const minDim = Math.min(nw, nh);
                const sx = (nw - minDim) / 2;
                const sy = (nh - minDim) / 2;
                ctx.drawImage(img, sx, sy, minDim, minDim, 0, 0, targetW, targetH);
                ctx.restore();

                // Crisp anti-aliased border ring
                ctx.beginPath();
                ctx.arc(center, center, radius, 0, Math.PI * 2);
                ctx.lineWidth = strokeW;
                ctx.strokeStyle = 'rgba(203, 213, 225, 0.45)';
                ctx.stroke();
              }} else {{
                const radius = targetW * (4 / boxWidth);
                ctx.save();
                ctx.beginPath();
                if (ctx.roundRect) {{
                  ctx.roundRect(0, 0, targetW, targetH, radius);
                }} else {{
                  ctx.rect(0, 0, targetW, targetH);
                }}
                ctx.closePath();
                ctx.fillStyle = '#486581';
                ctx.fill();
                ctx.clip();

                const nw = img.naturalWidth || 1;
                const nh = img.naturalHeight || 1;
                const imgAspect = nw / nh;
                const targetAspect = targetW / targetH;
                let sx = 0, sy = 0, sw = nw, sh = nh;
                if (imgAspect > targetAspect) {{
                  sw = nh * targetAspect;
                  sx = (nw - sw) / 2;
                }} else {{
                  sh = nw / targetAspect;
                  sy = (nh - sh) / 2;
                }}
                ctx.drawImage(img, sx, sy, sw, sh, 0, 0, targetW, targetH);
                ctx.restore();
              }}
              resolve(c.toDataURL('image/png'));
            }} catch (err) {{
              console.warn('Avatar canvas error:', err);
              resolve(null);
            }}
          }};
          img.onerror = () => {{
            console.warn('Avatar load error');
            resolve(null);
          }};
          setTimeout(() => resolve(null), 2500);
          img.src = photoSrc;
        }});

        // Render clone to high-resolution canvas using html2canvas
        const canvasPromise = html2canvas(clone, {{
          scale: 3,
          useCORS: true,
          logging: false,
          scrollX: 0,
          scrollY: 0,
          width: 595,
          height: 842,
          windowWidth: 595,
          windowHeight: 842
        }});

        const [canvas, avatarPng] = await Promise.all([canvasPromise, avatarPromise]);

        // Immediately clean up offscreen DOM
        document.body.removeChild(offscreen);

        const imgData = canvas.toDataURL('image/jpeg', 0.98);

        // Export via jsPDF (maps directly 1:1 to A4 points 595.28 x 841.89 with zero margins)
        const jsPdfClass = (window.jspdf && window.jspdf.jsPDF) ? window.jspdf.jsPDF : (window.jsPDF || null);
        if (jsPdfClass) {{
          const pdf = new jsPdfClass({{
            orientation: 'portrait',
            unit: 'pt',
            format: 'a4'
          }});
          pdf.addImage(imgData, 'JPEG', 0, 0, 595.28, 841.89);
          if (avatarPng && photoCoords) {{
            pdf.addImage(avatarPng, 'PNG', photoCoords.x, photoCoords.y, photoCoords.w, photoCoords.h);
          }}
          pdf.save(filename);
          showToast('✅ PDF downloaded successfully to your computer!');
          return;
        }}

        // Fallback: html2pdf worker
        if (typeof html2pdf !== 'undefined') {{
          const opt = {{
            margin: 0,
            filename: filename,
            image: {{ type: 'jpeg', quality: 0.98 }},
            html2canvas: {{ scale: 2.5, useCORS: true, logging: false }},
            jsPDF: {{ unit: 'pt', format: 'a4', orientation: 'portrait' }}
          }};
          await html2pdf().set(opt).from(canvas).toPdf().get('pdf').then(function(pdf) {{
            pdf.deletePage(1);
            pdf.addPage('a4', 'portrait');
            pdf.addImage(imgData, 'JPEG', 0, 0, 595.28, 841.89);
            if (avatarPng && photoCoords) {{
              pdf.addImage(avatarPng, 'PNG', photoCoords.x, photoCoords.y, photoCoords.w, photoCoords.h);
            }}
            pdf.save(filename);
          }});
          showToast('✅ PDF downloaded successfully to your computer!');
          return;
        }}

        // Fallback: Backend /api/v1/cv/pdf
        const resp = await fetch('http://localhost:8000/api/v1/cv/pdf', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(cvData)
        }});

        if (resp.ok) {{
          const blob = await resp.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
          showToast('✅ PDF downloaded successfully to your computer!');
          return;
        }} else {{
          throw new Error('Backend PDF generation failed');
        }}
      }} catch (err) {{
        console.warn('Direct PDF download error, attempting browser print fallback:', err);
        showToast('⚠️ Opening browser print dialog to save as PDF...');
        window.print();
      }} finally {{
        dlBtns.forEach((b, idx) => {{
          if (prevBtnContents[idx]) b.innerHTML = prevBtnContents[idx];
          b.disabled = false;
        }});
      }}
    }}

    function navigateToLanding() {{
      try {{
        const origin = window.parent.location.origin;
        window.parent.location.href = origin + '/';
      }} catch (e) {{
        try {{
          window.top.location.href = '/';
        }} catch (e2) {{
          window.location.href = '/';
        }}
      }}
    }}

    function togglePasteCvPanel() {{
      const p = document.getElementById('pasteCvPanel');
      if (!p) return;
      p.classList.toggle('hidden');
      if (!p.classList.contains('hidden')) {{
        const ta = document.getElementById('pasteCvTextarea');
        if (ta) {{
          setTimeout(() => ta.focus(), 100);
        }}
      }}
    }}

    function applyExtractedCvData(extracted) {{
      if (!extracted) return;
      const cv = extracted.cv || extracted;

      // 1. Personal details
      if (cv.personal) {{
        cvData.personal = Object.assign(cvData.personal || {{}}, cv.personal);
      }}

      // 2. Summary
      if (cv.summary) {{
        cvData.summary = cv.summary;
      }}

      // 3. Education
      if (Array.isArray(cv.education) && cv.education.length > 0) {{
        cvData.education = cv.education.map(ed => ({{
          id: ed.id || 'edu_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
          degree: ed.degree || ed.title || '',
          institution: ed.institution || ed.school || '',
          location: ed.location || ed.city || '',
          start_date: ed.start_date || '',
          end_date: ed.end_date || '',
          description: ed.description || ''
        }}));
      }}

      // 4. Experience / Work history
      if (Array.isArray(cv.experience) && cv.experience.length > 0) {{
        cvData.experience = cv.experience.map(exp => ({{
          id: exp.id || 'exp_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
          title: exp.title || exp.position || '',
          company: exp.company || exp.employer || '',
          location: exp.location || '',
          start_date: exp.start_date || '',
          end_date: exp.end_date || '',
          bullets: Array.isArray(exp.bullets) ? exp.bullets.map(b => (typeof b === 'object' && b.text ? b.text : String(b))) : []
        }}));
      }}

      // 5. Projects
      if (Array.isArray(cv.projects) && cv.projects.length > 0) {{
        cvData.projects = cv.projects.map(prj => ({{
          id: prj.id || 'prj_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
          title: prj.title || prj.name || '',
          subtitle: prj.subtitle || prj.role || '',
          start_date: prj.start_date || '',
          end_date: prj.end_date || '',
          bullets: Array.isArray(prj.bullets) ? prj.bullets.map(b => (typeof b === 'object' && b.text ? b.text : String(b))) : []
        }}));
      }}

      // 6. Skills (strictly at most 4 categories, clean names, no Specialized Tools)
      if (Array.isArray(cv.skills) && cv.skills.length > 0) {{
        const cleanGroups = [];
        cv.skills.forEach(g => {{
          const cat = (g.category || g.group || '').trim();
          if (!cat || /^(specialized tools?|keywords?|other)$/i.test(cat)) return;
          if (cleanGroups.length >= 4) return;
          const items = Array.isArray(g.items) ? g.items.map(it => skillItemName(it)).filter(n => isValidSkillName(n)) : [];
          if (items.length > 0) {{
            cleanGroups.push({{
              id: 'skg_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
              category: cat,
              items: items.slice(0, 8)
            }});
          }}
        }});
        if (cleanGroups.length > 0) {{
          cvData.skills = cleanGroups.slice(0, 4);
        }}
      }}

      // 7. Languages
      if (Array.isArray(cv.languages) && cv.languages.length > 0) {{
        cvData.languages = cv.languages.map(l => ({{
          name: l.name || l.language || '',
          level: l.level || 'Good'
        }}));
      }}

      // Clear extra fields container before re-populating
      const extraArea = document.getElementById('extraFieldsArea');
      if (extraArea) extraArea.innerHTML = '';

      initEditor();
      renderLivePreview();
      flashSaved();
    }}

    function parseCvTextClientSide(text) {{
      const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
      const out = {{
        personal: {{}},
        summary: '',
        skills: [],
        languages: [],
        education: [],
        experience: [],
        projects: []
      }};

      // Email
      const emailMatch = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}/);
      if (emailMatch) out.personal.email = emailMatch[0];

      // Phone
      const phoneMatch = text.match(/(?:\\+?\\d{{1,3}}[-.\\s]?)?\\(?\\d{{2,4}}\\)?[-.\\s]?\\d{{3,4}}[-.\\s]?\\d{{3,4}}/);
      if (phoneMatch) out.personal.phone = phoneMatch[0].trim();

      // Name (first non-empty line that isn't email/phone or section title)
      for (const line of lines) {{
        if (!line.includes('@') && !/\\d{{5,}}/.test(line) && !/^(resume|cv|curriculum|profile|summary|experience|education)/i.test(line)) {{
          const parts = line.split(/\\s+/);
          if (parts.length >= 2 && parts.length <= 4) {{
            out.personal.first_name = parts[0];
            out.personal.last_name = parts.slice(1).join(' ');
            break;
          }} else if (parts.length === 1 && line.length >= 2) {{
            out.personal.first_name = parts[0];
            break;
          }}
        }}
      }}

      // Headline / Title (next line with role terms)
      const roleLine = lines.find(l => /(engineer|developer|scientist|analyst|manager|consultant|architect|specialist|designer|student|intern)/i.test(l) && !l.includes('@'));
      if (roleLine && roleLine.length < 60) {{
        out.personal.headline = roleLine;
      }}

      // Summary
      const summaryMatch = text.match(/(?:summary|profile|about\\s+me|résumé|profil)[:\\s]+([\\s\\S]*?)(?=\\n[A-Z\\s]{{4,}}|$)/i);
      if (summaryMatch) {{
        out.summary = summaryMatch[1].trim().slice(0, 1000);
      }}

      // Skills: Extract known technical tools
      const knownSkills = [
        {{ name: 'Python', category: 'Programming Languages' }},
        {{ name: 'SQL', category: 'Data Engineering' }},
        {{ name: 'PyTorch', category: 'Machine Learning & AI' }},
        {{ name: 'TensorFlow', category: 'Machine Learning & AI' }},
        {{ name: 'Scikit-Learn', category: 'Machine Learning & AI' }},
        {{ name: 'Deep Learning', category: 'Machine Learning & AI' }},
        {{ name: 'NLP', category: 'Machine Learning & AI' }},
        {{ name: 'Apache Spark', category: 'Data Engineering' }},
        {{ name: 'PySpark', category: 'Data Engineering' }},
        {{ name: 'Docker', category: 'MLOps & Deployment' }},
        {{ name: 'Kubernetes', category: 'MLOps & Deployment' }},
        {{ name: 'MLOps', category: 'MLOps & Deployment' }},
        {{ name: 'Power BI', category: 'Analytics & BI' }},
        {{ name: 'Tableau', category: 'Analytics & BI' }},
        {{ name: 'Git', category: 'Programming Languages' }},
        {{ name: 'FastAPI', category: 'Web Development' }}
      ];
      const groups = {{}};
      knownSkills.forEach(sk => {{
        const re = new RegExp('\\\\b' + sk.name.replace(/[-_\\s]/g, '[-_\\\\s]') + '\\\\b', 'i');
        if (re.test(text)) {{
          if (!groups[sk.category]) groups[sk.category] = [];
          if (!groups[sk.category].includes(sk.name)) groups[sk.category].push(sk.name);
        }}
      }});
      out.skills = Object.keys(groups).slice(0, 4).map(cat => ({{
        category: cat,
        items: groups[cat]
      }}));

      // Languages: English, French, Arabic, German, Spanish
      const knownLangs = ['English', 'French', 'Arabic', 'Spanish', 'German', 'Italian', 'Portuguese'];
      knownLangs.forEach(lang => {{
        const re = new RegExp('\\\\b' + lang + '\\\\b', 'i');
        if (re.test(text)) {{
          out.languages.push({{ name: lang, level: 'Good' }});
        }}
      }});

      return out;
    }}

    async function extractCvFromPastedText() {{
      const ta = document.getElementById('pasteCvTextarea');
      const text = ta ? ta.value.trim() : '';
      const hint = document.getElementById('pasteCvStatusHint');
      const btn = document.getElementById('extractTextBtn');

      if (!text) {{
        showToast('Please paste your CV text first.');
        if (ta) ta.focus();
        return;
      }}

      if (btn) {{
        btn.disabled = true;
        btn.innerHTML = '<span>⚡ Extracting...</span>';
      }}
      if (hint) hint.textContent = '⚡ AI is analyzing and structuring your CV data...';

      try {{
        let extractedData = null;
        try {{
          const resp = await fetch('http://localhost:8000/api/v1/cv/extract-text', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ text }})
          }});
          if (resp.ok) {{
            const payload = await resp.json();
            extractedData = payload.cv || payload.data || payload;
          }}
        }} catch (e) {{
          console.warn('Backend unavailable, parsing text on client:', e);
        }}

        if (!extractedData || (!extractedData.personal && !extractedData.summary && (!extractedData.skills || extractedData.skills.length === 0))) {{
          extractedData = parseCvTextClientSide(text);
        }}

        applyExtractedCvData(extractedData);
        showToast('🎉 Successfully created CV from your text!');
        if (hint) hint.textContent = '✅ Extraction complete!';
        setTimeout(() => {{
          togglePasteCvPanel();
          if (hint) hint.textContent = '';
        }}, 800);
      }} catch (err) {{
        console.error('Extract error:', err);
        showToast('⚠️ Could not extract CV from text.');
        if (hint) hint.textContent = '⚠️ Failed to extract CV.';
      }} finally {{
        if (btn) {{
          btn.disabled = false;
          btn.innerHTML = '<span>✨ Extract & Fill CV</span>';
        }}
      }}
    }}

    async function handleFileUpload(e) {{
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      const card = document.getElementById('uploadCvCardBtn');
      const origCardHtml = card ? card.innerHTML : '';
      if (card) {{
        card.innerHTML = `
          <svg class="w-5 h-5 mx-auto text-blue-600 animate-spin mb-1" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <div class="text-xs font-semibold text-blue-600 animate-pulse">Extracting with AI...</div>
        `;
        card.style.pointerEvents = 'none';
      }}

      showToast('📄 Uploading ' + file.name + ' for AI extraction...');

      const formData = new FormData();
      formData.append('file', file);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 45000);

      try {{
        const resp = await fetch('http://localhost:8000/api/v1/cv/extract', {{
          method: 'POST',
          body: formData,
          signal: controller.signal
        }});
        clearTimeout(timeoutId);

        if (resp.ok) {{
          const payload = await resp.json();
          const extractedData = payload.cv || payload.data || payload;
          applyExtractedCvData(extractedData);
          showToast('🎉 Successfully imported ' + file.name + ' into your CV!');
        }} else {{
          const errData = await resp.json().catch(() => ({{}}));
          const msg = errData.detail || 'Could not parse this file.';
          showToast('⚠️ ' + msg);
          const p = document.getElementById('pasteCvPanel');
          if (p && p.classList.contains('hidden')) {{
            togglePasteCvPanel();
          }}
        }}
      }} catch (err) {{
        clearTimeout(timeoutId);
        console.warn('Backend file extraction error:', err);
        if (err.name === 'AbortError') {{
          showToast('⚠️ Upload timed out. Please try "Paste CV as text" instead!');
        }} else {{
          showToast('⚠️ Backend upload error. Check backend or use "Paste CV as text"!');
        }}
        const p = document.getElementById('pasteCvPanel');
        if (p && p.classList.contains('hidden')) {{
          togglePasteCvPanel();
        }}
      }} finally {{
        if (card && origCardHtml) {{
          card.innerHTML = origCardHtml;
          card.style.pointerEvents = 'auto';
        }}
        e.target.value = '';
      }}
    }}

    function handlePhotoUpload(e) {{
      const file = e.target.files[0];
      if (file) {{
        const reader = new FileReader();
        reader.onload = (evt) => {{
          cvData.personal.photo_url = evt.target.result;
          document.getElementById('photoThumb').src = evt.target.result;
          renderLivePreview();
          flashSaved();
        }};
        reader.readAsDataURL(file);
      }}
    }}

    // AI Suggestions Hooks: Scroll up to Job Description
    function suggestAISkills() {{
      const tj = document.getElementById('targetJobInput');
      const targetSec = document.getElementById('targetJobSection') || tj;
      const hint = document.getElementById('jobInputHint');

      // 1. Scroll up smoothly to the job description input area
      if (targetSec) {{
        targetSec.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      }}

      // 2. Focus on the job description input area
      if (tj) {{
        setTimeout(() => {{
          tj.focus();
          tj.classList.add('border-blue-500', 'ring-2', 'ring-blue-300', 'bg-blue-50/40');
          setTimeout(() => tj.classList.remove('bg-blue-50/40'), 2500);
        }}, 350);

        if (!tj.value.trim()) {{
          tj.placeholder = '✍️ Describe your target job here (e.g. Data Scientist with PyTorch, MLOps, Spark and LLMs)...';
        }}
      }}

      // 3. Message telling him to describe the job to generate matched skills
      const msg = '🎯 Describe your job here to generate matched skills!';
      if (hint) {{
        hint.textContent = msg;
        hint.className = 'text-[11px] text-blue-600 font-semibold animate-pulse';
        setTimeout(() => hint.classList.remove('animate-pulse'), 3500);
      }}
      showToast(msg);
    }}

    function cleanAiDashes(text) {{
      if (!text) return '';
      return text
        .replace(/\\s*[—–]\\s*(.*?)\\s*[—–]\\s*/g, ', $1, ')
        .replace(/\\s*[—–]\\s*/g, ', ')
        .replace(/\\s*--\\s*/g, ', ')
        .replace(/\\s*,\\s*,+/g, ',')
        .replace(/\\s*,\\s*\\./g, '.')
        .replace(/\\s+,/g, ',')
        .replace(/^,\\s*/, '')
        .replace(/\\s{{2,}}/g, ' ')
        .trim();
    }}

    function elevateSummaryFallback(text, jobTitle) {{
      const clean = cleanAiDashes(text);
      const title = jobTitle || 'Professional';
      if (clean.length < 25) {{
        return `Results-driven ${{title}} with proven expertise in modern industry practices, problem-solving, and cross-functional execution. Demonstrated track record of delivering high-quality outcomes and optimizing operational efficiency. Passionate about leveraging technical proficiency to drive business impact.`;
      }}
      let res = clean.charAt(0).toUpperCase() + clean.slice(1);
      if (!res.endsWith('.')) res += '.';
      return `Results-driven and detail-oriented ${{title}} with a track record of success: ${{res}} Adept at collaborating cross-functionally and applying industry best practices to achieve organizational objectives.`;
    }}

    async function improveAISummary() {{
      const el = document.getElementById('inputSummary');
      const hint = document.getElementById('summaryEmptyHint');
      const btn = document.getElementById('btnImproveSummary');
      const btnText = document.getElementById('btnImproveSummaryText');
      if (!el) return;

      const currentVal = (el.value || '').trim();

      // If summary is empty: focus cursor in input, show message, and visual cues
      if (!currentVal) {{
        el.focus();
        el.placeholder = '✍️ Please enter your summary here first so AI can enhance it...';
        el.classList.add('border-amber-400', 'ring-2', 'ring-amber-300', 'bg-amber-50');
        if (hint) {{
          hint.classList.remove('hidden');
          hint.innerHTML = '<span class="text-amber-500 font-bold mr-1">⚠️</span> Please enter your summary first so the AI can enhance it!';
        }}
        showToast('⚠️ Please enter your summary first so the AI can enhance it!');

        setTimeout(() => {{
          el.classList.remove('bg-amber-50');
        }}, 2000);
        return;
      }}

      // Summary is present: proceed to enhance with LLM
      if (hint) hint.classList.add('hidden');
      el.classList.remove('border-amber-400', 'ring-2', 'ring-amber-300');

      if (btn) btn.disabled = true;
      if (btnText) btnText.innerHTML = '<span class="inline-block animate-spin mr-1">🌀</span> Enhancing...';
      showToast('✨ Enhancing your summary with AI...');

      const jobContext = cvData.target_job || (cvData.personal ? cvData.personal.job_title : '') || '';

      try {{
        const resp = await fetch('http://localhost:8000/api/v1/cv/improve-summary', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            summary: currentVal,
            context: jobContext
          }})
        }});

        if (!resp.ok) {{
          throw new Error('Server status ' + resp.status);
        }}

        const data = await resp.json();
        if (data && data.improved && data.improved.trim()) {{
          el.value = cleanAiDashes(data.improved);
          updateSummary();
          el.classList.add('border-green-400', 'ring-2', 'ring-green-200');
          setTimeout(() => el.classList.remove('border-green-400', 'ring-2', 'ring-green-200'), 2500);
          showToast('✨ AI successfully elevated your summary!');
        }} else {{
          throw new Error('No improved text in response');
        }}
      }} catch (err) {{
        console.warn('Backend call failed, using client-side fallback:', err);
        const fallbackText = elevateSummaryFallback(currentVal, jobContext);
        el.value = cleanAiDashes(fallbackText);
        updateSummary();
        showToast('✨ Summary enhanced! (Tip: run python run.py for live AI model)');
      }} finally {{
        if (btn) btn.disabled = false;
        if (btnText) btnText.innerHTML = '✨ Improve with AI';
      }}
    }}

    // Boot editor
    if (document.readyState === 'loading') {{
      window.addEventListener('DOMContentLoaded', initEditor);
    }} else {{
      initEditor();
    }}
  </script>
</body>
</html>
"""

# Render via st.components.v1.html (fixed to 100vh with no blank space or outer scrolling)
st.components.v1.html(builder_html, height=1000, scrolling=False)

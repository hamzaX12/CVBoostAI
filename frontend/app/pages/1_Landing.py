"""
CVBoost AI — Landing Page
Rendered as a full HTML page via st.components.v1.html with Tailwind CDN.
"""
from __future__ import annotations

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


from styles.theme import HIDE_STREAMLIT
from components.api_client import submit_contact

def _go_to_builder():
    for p in ["pages/2_Builder.py", "app/pages/2_Builder.py", "2_Builder"]:
        try:
            st.switch_page(p)
            return
        except Exception:
            pass

if st.query_params.get("page") == "builder":
    st.query_params.clear()
    _go_to_builder()

st.markdown("""
<style>
/* Remove all Streamlit default headers, footers, toolbars, and decoration */
header, [data-testid="stHeader"], footer, [data-testid="stBottom"], [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], #MainMenu, .stDeployButton {
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

/* Eliminate all top padding and margins from Streamlit's container chain */
html, body, .stApp, [data-testid="stAppViewContainer"], .main, section.main, .block-container, [data-testid="stVerticalBlock"], [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    margin: 0 !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
    gap: 0 !important;
}

/* Explicitly zero out top padding on block container where Streamlit defaults to 3.5rem - 6rem */
.main .block-container, [data-testid="stMainBlockContainer"], div[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin-top: 0 !important;
}

/* Collapse empty elements and script wrappers that take up vertical space */
div[data-testid="stElementContainer"]:has(style),
div[data-testid="stElementContainer"]:has(script),
div[data-testid="stElementContainer"]:empty,
div[data-testid="stHtml"] {
    display: none !important;
    height: 0 !important;
    max-height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stCustomComponentV1"] {
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
}

iframe {
    width: 100% !important;
    border: none !important;
    display: block !important;
    margin: 0 !important;
    padding: 0 !important;
}
</style>
""", unsafe_allow_html=True)

if hasattr(st, "html"):
    st.html("""
    <script>
    window.addEventListener("message", function(e) {
      if (e.data === "navigate_to_builder" || (e.data && e.data.type === "navigate_to_builder")) {
        try {
          const origin = (window.parent && window.parent.location) ? window.parent.location.origin : window.location.origin;
          window.parent.location.href = origin + '/builder';
        } catch (err) {
          window.location.href = '/builder';
        }
      }
    });
    </script>
    """, unsafe_allow_javascript=True)


LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="CVBoost AI — AI-powered ATS CV builder. Upload your CV, target a job, and download an optimized PDF in minutes.">
<title>CVBoost AI — Enhance your CV for better job chances</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
  theme: {
    extend: {
      colors: {
        'primary-dark': '#09637E',
        'primary': '#088395',
        'accent': '#7AB2B2',
        'surface': '#EBF4F6',
      },
      fontFamily: {
        inter: ['Inter', 'system-ui', 'sans-serif'],
      },
    }
  }
}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  * { font-family: 'Inter', sans-serif; }
  body { background: #EBF4F6; margin: 0; padding: 0; }

  /* Animations */
  @keyframes fadeInUp { from { opacity:0; transform:translateY(30px); } to { opacity:1; transform:translateY(0); } }
  @keyframes float { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-10px); } }
  @keyframes shimmer { 0% { background-position: -200% center; } 100% { background-position: 200% center; } }
  @keyframes pulse-ring { 0% { transform:scale(0.95); box-shadow:0 0 0 0 rgba(8,131,149,0.4); } 70% { transform:scale(1); box-shadow:0 0 0 15px rgba(8,131,149,0); } 100% { transform:scale(0.95); } }

  .fade-in-up { animation: fadeInUp 0.8s ease forwards; }
  .delay-100 { animation-delay: 0.1s; opacity: 0; }
  .delay-200 { animation-delay: 0.2s; opacity: 0; }
  .delay-300 { animation-delay: 0.3s; opacity: 0; }
  .delay-400 { animation-delay: 0.4s; opacity: 0; }
  .float { animation: float 3s ease-in-out infinite; }
  .pulse-btn { animation: pulse-ring 2s infinite; }

  .gradient-text {
    background: linear-gradient(135deg, #09637E 0%, #088395 50%, #7AB2B2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .gradient-text-shimmer {
    background: linear-gradient(90deg, #09637E, #088395, #7AB2B2, #088395, #09637E);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite;
  }

  .hero-bg {
    background: linear-gradient(135deg, #09637E 0%, #088395 40%, #0a9eb2 70%, #7AB2B2 100%);
    position: relative;
    overflow: hidden;
  }
  .hero-bg::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 600px;
    height: 600px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
    pointer-events: none !important;
  }
  .hero-bg::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: -10%;
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
    pointer-events: none !important;
  }

  .glass-card {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(122,178,178,0.2);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(9,99,126,0.08);
    transition: all 0.3s ease;
  }
  .glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(9,99,126,0.16);
    border-color: rgba(8,131,149,0.3);
  }

  .feature-icon {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    background: linear-gradient(135deg, #EBF4F6, #d4eef2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 16px;
    transition: all 0.3s;
  }
  .glass-card:hover .feature-icon {
    background: linear-gradient(135deg, #088395, #09637E);
    transform: scale(1.1) rotate(5deg);
  }

  .step-number {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, #088395, #09637E);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 18px;
    flex-shrink: 0;
    box-shadow: 0 4px 16px rgba(8,131,149,0.4);
  }

  .cta-btn {
    background: linear-gradient(135deg, #088395, #09637E);
    color: white;
    padding: 16px 40px;
    border-radius: 50px;
    font-weight: 700;
    font-size: 17px;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(8,131,149,0.4);
    border: none;
    cursor: pointer;
  }
  .cta-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 48px rgba(8,131,149,0.5);
    background: linear-gradient(135deg, #09637E, #07707F);
  }

  .nav-link {
    color: rgba(255,255,255,0.85);
    text-decoration: none;
    font-weight: 500;
    font-size: 15px;
    transition: color 0.2s;
    padding: 6px 12px;
    border-radius: 8px;
  }
  .nav-link:hover { color: white; background: rgba(255,255,255,0.1); }

  .section-tag {
    display: inline-block;
    background: rgba(8,131,149,0.1);
    color: #088395;
    border: 1px solid rgba(8,131,149,0.2);
    border-radius: 20px;
    padding: 4px 16px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 12px;
    letter-spacing: 0.5px;
  }

  .contact-input {
    width: 100%;
    padding: 12px 16px;
    border: 1.5px solid rgba(122,178,178,0.4);
    border-radius: 10px;
    font-size: 14px;
    font-family: 'Inter', sans-serif;
    outline: none;
    background: white;
    transition: border-color 0.2s;
    color: #0F2A33;
  }
  .contact-input:focus { border-color: #088395; box-shadow: 0 0 0 3px rgba(8,131,149,0.1); }

  .footer-gradient {
    background: linear-gradient(135deg, #09637E 0%, #07505f 100%);
  }

  /* Stats */
  .stat-card {
    text-align: center;
    padding: 20px;
  }
  .stat-number {
    font-size: 36px;
    font-weight: 900;
    color: white;
    line-height: 1;
  }
  .stat-label {
    font-size: 13px;
    color: rgba(255,255,255,0.7);
    margin-top: 4px;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #EBF4F6; }
  ::-webkit-scrollbar-thumb { background: #7AB2B2; border-radius: 3px; }
</style>
</head>

<body class="text-gray-900">

<!-- ═══════════════════════ NAVBAR ═══════════════════════ -->
<nav class="sticky top-0" style="background:linear-gradient(135deg, #09637E 0%, #088395 100%);box-shadow:0 4px 20px rgba(9,99,126,0.3);position:relative;z-index:9999;">
  <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between" style="position:relative;z-index:10000;">
    <a href="#" class="flex items-center gap-3 text-white no-underline" style="position:relative;z-index:10001;">
      <div style="width:36px;height:36px;background:rgba(255,255,255,0.2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px">🚀</div>
      <div>
        <div style="font-weight:800;font-size:18px;letter-spacing:-0.5px">CVBoost AI</div>
        <div style="font-size:10px;opacity:0.7;letter-spacing:1px;text-transform:uppercase">AI-Powered CV Builder</div>
      </div>
    </a>
    <div class="hidden md:flex items-center gap-2" style="position:relative;z-index:10001;pointer-events:auto;">
      <a href="#" class="nav-link">Home</a>
      <a href="#learn-more" class="nav-link">Learn More</a>
      <a href="#contact" class="nav-link">Contact</a>
      <button id="getStartedBtn" class="cta-btn" onclick="navigateToBuilder(event)" style="padding:10px 24px;font-size:14px;border-radius:30px;margin-left:8px;cursor:pointer!important;position:relative;z-index:10002;pointer-events:auto!important;">
        Get Started →
      </button>
    </div>
  </div>
</nav>

<!-- ═══════════════════════ HERO ═══════════════════════ -->
<section class="hero-bg" style="padding:80px 24px 100px;position:relative;z-index:1">
  <div class="max-w-4xl mx-auto text-center">

    <div class="float inline-block" style="font-size:64px;margin-bottom:20px">📄</div>

    <div class="fade-in-up" style="display:inline-block;background:rgba(255,255,255,0.15);color:white;border:1px solid rgba(255,255,255,0.3);border-radius:24px;padding:6px 20px;font-size:13px;font-weight:600;margin-bottom:20px;letter-spacing:0.5px">
      ✨ Powered by AI
    </div>

    <h1 class="fade-in-up delay-100 text-white" style="font-size:clamp(36px,6vw,64px);font-weight:900;line-height:1.1;margin-bottom:20px;letter-spacing:-1px">
      Enhance your CV for<br>
      <span style="opacity:0.9">better job chances</span>
    </h1>

    <p class="fade-in-up delay-200 text-white" style="font-size:18px;opacity:0.85;max-width:580px;margin:0 auto 40px;line-height:1.6;font-weight:400">
      AI extracts your existing CV, analyzes real job requirements, and generates an ATS-optimized PDF — all in minutes.
    </p>

    <div class="fade-in-up delay-300" style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap">
      <button id="buildCvBtn" class="cta-btn pulse-btn" onclick="navigateToBuilder(event)">
        🚀 Build My CV
      </button>
      <a href="#learn-more" class="cta-btn" style="background:rgba(255,255,255,0.15);box-shadow:none;backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.3)">
        Learn More ↓
      </a>
    </div>

    <!-- Stats bar -->
    <div class="fade-in-up delay-400" style="display:flex;justify-content:center;gap:40px;margin-top:60px;flex-wrap:wrap">
      <div class="stat-card"><div class="stat-number">95%</div><div class="stat-label">ATS Pass Rate</div></div>
      <div class="stat-card"><div class="stat-number">3</div><div class="stat-label">Professional Templates</div></div>
      <div class="stat-card"><div class="stat-number">50+</div><div class="stat-label">Skill Categories</div></div>
      <div class="stat-card"><div class="stat-number">3</div><div class="stat-label">Languages (EN/FR/AR)</div></div>
    </div>
  </div>
</section>

<!-- Wave separator -->
<div style="margin-top:-1px;overflow:hidden;line-height:0">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 60" style="display:block">
    <path fill="#EBF4F6" d="M0,30 C360,60 1080,0 1440,30 L1440,60 L0,60 Z"/>
  </svg>
</div>

<!-- ═══════════════════════ FEATURES ═══════════════════════ -->
<section id="learn-more" style="background:#EBF4F6;padding:80px 24px">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-14">
      <div class="section-tag">✨ Features</div>
      <h2 style="font-size:36px;font-weight:800;color:#09637E;letter-spacing:-0.5px">Everything you need to land your dream job</h2>
      <p style="color:#7AB2B2;margin-top:10px;font-size:16px">Powered by the latest AI models and designed for real results</p>
    </div>

    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px">

      <div class="glass-card" style="padding:28px">
        <div class="feature-icon">🤖</div>
        <h3 style="font-weight:700;font-size:18px;color:#09637E;margin-bottom:8px">AI CV Extraction</h3>
        <p style="color:#6b7280;line-height:1.6;font-size:14px">Upload your existing CV (PDF or DOCX) and our Gemini-powered agent intelligently extracts every detail — education, projects, skills, and more — with confidence scoring.</p>
      </div>

      <div class="glass-card" style="padding:28px">
        <div class="feature-icon">🎯</div>
        <h3 style="font-weight:700;font-size:18px;color:#09637E;margin-bottom:8px">Job-Targeted Skills</h3>
        <p style="color:#6b7280;line-height:1.6;font-size:14px">Type a job description and watch AI search the web in real-time, extract actual job requirements, and suggest skills ranked by importance — each backed by real sources.</p>
      </div>

      <div class="glass-card" style="padding:28px">
        <div class="feature-icon">📄</div>
        <h3 style="font-weight:700;font-size:18px;color:#09637E;margin-bottom:8px">ATS-Optimized PDF</h3>
        <p style="color:#6b7280;line-height:1.6;font-size:14px">Generate beautiful, recruiter-approved PDFs with a real text layer. Our ATS checker validates section detection, contact parsing, skill keywords, and reading order.</p>
      </div>

      <div class="glass-card" style="padding:28px">
        <div class="feature-icon">✏️</div>
        <h3 style="font-weight:700;font-size:18px;color:#09637E;margin-bottom:8px">Interactive CV Editor</h3>
        <p style="color:#6b7280;line-height:1.6;font-size:14px">Edit your CV with a professional side-by-side editor. Drag and drop sections, choose between 3 tailored templates (Simple, Classic Navy & Executive Slate), customize colors, fonts, and spacing — see changes live.</p>
      </div>

    </div>
  </div>
</section>

<!-- ═══════════════════════ HOW IT WORKS ═══════════════════════ -->
<section style="background:white;padding:80px 24px">
  <div class="max-w-4xl mx-auto">
    <div class="text-center mb-14">
      <div class="section-tag">📋 Process</div>
      <h2 style="font-size:36px;font-weight:800;color:#09637E;letter-spacing:-0.5px">3 steps to your perfect CV</h2>
    </div>

    <div style="display:flex;flex-direction:column;gap:0">

      <div style="display:flex;gap:24px;align-items:flex-start;padding:28px;border-radius:20px;transition:all 0.3s" onmouseover="this.style.background='#EBF4F6'" onmouseout="this.style.background='transparent'">
        <div class="step-number">1</div>
        <div>
          <h3 style="font-weight:700;font-size:20px;color:#09637E;margin-bottom:8px">Upload your existing CV</h3>
          <p style="color:#6b7280;line-height:1.7;font-size:15px">Drag and drop your current PDF or DOCX. Our AI reads and structures every section — no manual data entry. Works even with image-heavy CVs via OCR fallback. LinkedIn PDF export also supported.</p>
        </div>
      </div>

      <div style="margin-left:24px;width:1px;height:20px;background:linear-gradient(to bottom,#7AB2B2,transparent)"></div>

      <div style="display:flex;gap:24px;align-items:flex-start;padding:28px;border-radius:20px;transition:all 0.3s" onmouseover="this.style.background='#EBF4F6'" onmouseout="this.style.background='transparent'">
        <div class="step-number">2</div>
        <div>
          <h3 style="font-weight:700;font-size:20px;color:#09637E;margin-bottom:8px">Target your dream job</h3>
          <p style="color:#6b7280;line-height:1.7;font-size:15px">Paste a job description or just type "Data Scientist at a bank in Casablanca". The AI agent searches the web, reads real job postings, and suggests skills grouped by category with importance ratings and source links.</p>
        </div>
      </div>

      <div style="margin-left:24px;width:1px;height:20px;background:linear-gradient(to bottom,#7AB2B2,transparent)"></div>

      <div style="display:flex;gap:24px;align-items:flex-start;padding:28px;border-radius:20px;transition:all 0.3s" onmouseover="this.style.background='#EBF4F6'" onmouseout="this.style.background='transparent'">
        <div class="step-number">3</div>
        <div>
          <h3 style="font-weight:700;font-size:20px;color:#09637E;margin-bottom:8px">Download ATS-optimized PDF</h3>
          <p style="color:#6b7280;line-height:1.7;font-size:15px">Choose a template, customize colors and spacing, and download a professionally formatted PDF. Our ATS validator checks your score before download — giving you actionable fixes to reach 100/100.</p>
        </div>
      </div>
    </div>

    <div class="text-center mt-12">
      <button class="cta-btn" onclick="navigateToBuilder()">Start Building — It's Free 🚀</button>
    </div>
  </div>
</section>

<!-- ═══════════════════════ CONTACT ═══════════════════════ -->
<section id="contact" style="background:#EBF4F6;padding:80px 24px">
  <div class="max-w-5xl mx-auto">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start" class="contact-grid">

      <!-- Contact info -->
      <div>
        <div class="section-tag">📬 Contact</div>
        <h2 style="font-size:32px;font-weight:800;color:#09637E;margin-bottom:16px">Get in touch</h2>
        <p style="color:#6b7280;line-height:1.7;margin-bottom:32px">Have questions or feedback? I'd love to hear from you.</p>

        <div style="display:flex;flex-direction:column;gap:16px">
          <div style="display:flex;align-items:center;gap:14px;padding:14px 18px;background:white;border-radius:12px;box-shadow:0 2px 8px rgba(9,99,126,0.06)">
            <div style="width:40px;height:40px;background:#EBF4F6;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px">👨‍💻</div>
            <div><div style="font-size:12px;color:#7AB2B2;font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Platform</div><div style="font-weight:600;color:#09637E">CVBoost AI Team</div></div>
          </div>
          <div style="display:flex;align-items:center;gap:14px;padding:14px 18px;background:white;border-radius:12px;box-shadow:0 2px 8px rgba(9,99,126,0.06)">
            <div style="width:40px;height:40px;background:#EBF4F6;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px">✉️</div>
            <div><div style="font-size:12px;color:#7AB2B2;font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Email</div><div style="font-weight:600;color:#09637E">support@cvboost.ai</div></div>
          </div>
          <div style="display:flex;align-items:center;gap:14px;padding:14px 18px;background:white;border-radius:12px;box-shadow:0 2px 8px rgba(9,99,126,0.06)">
            <div style="width:40px;height:40px;background:#EBF4F6;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px">📍</div>
            <div><div style="font-size:12px;color:#7AB2B2;font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Support</div><div style="font-weight:600;color:#09637E">Global / 24/7 Online</div></div>
          </div>
          <div style="display:flex;align-items:center;gap:14px;padding:14px 18px;background:white;border-radius:12px;box-shadow:0 2px 8px rgba(9,99,126,0.06)">
            <div style="width:40px;height:40px;background:#EBF4F6;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px">🌐</div>
            <div><div style="font-size:12px;color:#7AB2B2;font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Website</div><a href="https://cvboost.ai" style="font-weight:600;color:#088395;text-decoration:none">cvboost.ai</a></div>
          </div>
        </div>
      </div>

      <!-- Contact form -->
      <div class="glass-card" style="padding:32px">
        <h3 style="font-weight:700;font-size:20px;color:#09637E;margin-bottom:24px">Send a message</h3>
        <form id="contactForm" onsubmit="submitContact(event)" style="display:flex;flex-direction:column;gap:16px">
          <!-- Honeypot (spam protection) -->
          <input type="text" name="honeypot" id="honeypot" style="display:none" tabindex="-1" autocomplete="off">

          <div>
            <label style="font-size:13px;font-weight:600;color:#09637E;display:block;margin-bottom:6px">Your Name *</label>
            <input type="text" id="contactName" required class="contact-input" placeholder="Alex Morgan">
          </div>
          <div>
            <label style="font-size:13px;font-weight:600;color:#09637E;display:block;margin-bottom:6px">Email *</label>
            <input type="email" id="contactEmail" required class="contact-input" placeholder="you@example.com">
          </div>
          <div>
            <label style="font-size:13px;font-weight:600;color:#09637E;display:block;margin-bottom:6px">Message *</label>
            <textarea id="contactMessage" required class="contact-input" rows="5" placeholder="Your message here..." style="resize:vertical"></textarea>
          </div>
          <button type="submit" class="cta-btn" id="submitBtn" style="width:100%;justify-content:center;border-radius:12px">
            Send Message ✉️
          </button>
          <div id="contactStatus" style="display:none;padding:10px;border-radius:8px;font-size:14px;text-align:center"></div>
        </form>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════════════════ FOOTER ═══════════════════════ -->
<footer class="footer-gradient" style="padding:40px 24px;color:white">
  <div class="max-w-6xl mx-auto">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px">
      <div style="display:flex;align-items:center;gap:10px">
        <span style="font-size:24px">🚀</span>
        <div>
          <div style="font-weight:800;font-size:18px">CVBoost AI</div>
          <div style="font-size:12px;opacity:0.65">Enhance your CV for better job chances</div>
        </div>
      </div>
      <div style="font-size:13px;opacity:0.6;text-align:center">
        © 2026 CVBoost AI · Intelligent ATS Resume Builder & Optimization Platform<br>
        <span style="opacity:0.8">Data processed by Gemini API · <a href="#" style="color:rgba(255,255,255,0.7)">Privacy Notice</a></span>
      </div>
      <div style="display:flex;gap:12px">
        <a href="#" class="nav-link" style="font-size:13px">Privacy</a>
        <a href="#contact" class="nav-link" style="font-size:13px">Contact</a>
        <button class="nav-link" onclick="navigateToBuilder(event)" style="font-size:13px;background:none;border:none;cursor:pointer">Builder</button>
      </div>
    </div>
  </div>
</footer>

<script>
function navigateToBuilder(e) {
  if (e && e.preventDefault) e.preventDefault();

  // Clean URL navigation directly to /builder
  try {
    const origin = (window.parent && window.parent.location) ? window.parent.location.origin : window.location.origin;
    window.parent.location.href = origin + '/builder';
    return;
  } catch (err) {}

  try {
    const origin = (window.top && window.top.location) ? window.top.location.origin : window.location.origin;
    window.top.location.href = origin + '/builder';
    return;
  } catch (err) {}

  window.location.href = '/builder';
}

function submitContact(e) {
  e.preventDefault();
  const btn = document.getElementById('submitBtn');
  const status = document.getElementById('contactStatus');
  const honeypot = document.getElementById('honeypot').value;

  if (honeypot) return; // Bot detected

  btn.textContent = 'Sending... ⏳';
  btn.disabled = true;

  const data = {
    name: document.getElementById('contactName').value,
    email: document.getElementById('contactEmail').value,
    message: document.getElementById('contactMessage').value,
    honeypot: honeypot,
  };

  fetch('/api/v1/contact/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data),
  })
  .then(r => r.json())
  .then(d => {
    status.style.display = 'block';
    status.style.background = '#e8f5e9';
    status.style.color = '#1E8E5A';
    status.textContent = '✅ ' + (d.message || 'Message sent! Thank you.');
    document.getElementById('contactForm').reset();
  })
  .catch(() => {
    status.style.display = 'block';
    status.style.background = '#fde8e8';
    status.style.color = '#C0392B';
    status.textContent = '❌ Failed to send. Please email directly.';
  })
  .finally(() => {
    btn.textContent = 'Send Message ✉️';
    btn.disabled = false;
  });
}

// Observe scroll for animations
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, {threshold: 0.1});

document.querySelectorAll('.glass-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});
</script>

</body>
</html>
"""

# Render the full landing page
st.components.v1.html(LANDING_HTML, height=4000, scrolling=True)

# Handle navigation (if user clicked "Build My CV")
if st.session_state.get("navigate_to_builder"):
    _go_to_builder()

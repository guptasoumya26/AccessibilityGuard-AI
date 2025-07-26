
from src.vision.openai_vision import analyze_screenshot_with_openai_vision
from src.selenium_utils.selenium_scraper import capture_screenshot_and_dom

import streamlit as st
import os
import sys
import re
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
st.markdown("""
    <style>
    .main-header {
        font-size: 2.6rem;
        font-weight: 800;
        color: #0053a0;
        margin-bottom: 0.2em;
        letter-spacing: -1px;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #fff !important;
        margin-bottom: 1.5em;
    }
    .stTextInput>div>div>input {
        font-size: 1.1rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #0053a0 60%, #ffd600 100%);
        color: #212121;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        padding: 0.6em 2em;
        font-size: 1.1rem;
        margin-top: 0.5em;
        margin-bottom: 1.5em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        transition: background 0.2s, color 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #ffd600 60%, #0053a0 100%);
        color: #0053a0;
    }
    </style>
    <div class=\"main-header\">🛡️ AccessibilityGuard-AI</div>
    <div class=\"subtitle\">Compare two versions of your web page for new accessibility issues using Vision LLM Model.</div>
""", unsafe_allow_html=True)

base_url = st.text_input("Base URL (main branch, staging, etc.)", "http://localhost:8000")
pr_url = st.text_input("PR URL (feature branch, preview, etc.)", "http://localhost:8001")
run_btn = st.button("Compare Accessibility")

def diff_reports(base_report, pr_report):
    # Clean and filter out "No issue found." entries and empty lines
    base_points = [line.strip() for line in base_report.splitlines() 
                   if line.strip() and "no issue found" not in line.lower()]
    pr_points = [line.strip() for line in pr_report.splitlines() 
                 if line.strip() and "no issue found" not in line.lower()]
    
    # Convert to sets for comparison
    base_set = set(base_points)
    pr_set = set(pr_points)
    
    # Find issues that are in PR but not in base
    new_issues = [issue for issue in pr_points if issue not in base_set]
    
    return "\n".join(new_issues) if new_issues else "No new accessibility issues found!"

def extract_issue_types(report):
    lines = report.lower().splitlines()
    types = []
    for line in lines:
        if 'contrast' in line:
            types.append('Contrast')
        if 'alt' in line:
            types.append('Alt Text')
        if 'focus' in line:
            types.append('Focus')
        if 'label' in line:
            types.append('Label')
        if 'aria' in line:
            types.append('ARIA')
    return types

if run_btn and base_url and pr_url:
    st.info("Step 1: Capturing screenshots and DOMs...")
    base_screenshot, _ = capture_screenshot_and_dom(base_url, screenshot_path="base_screenshot.png", dom_path="base_dom.html")
    pr_screenshot, _ = capture_screenshot_and_dom(pr_url, screenshot_path="pr_screenshot.png", dom_path="pr_dom.html")

    col1, col2 = st.columns(2)
    with col1:
        st.image(base_screenshot, caption="Base Screenshot", use_container_width=True)
    with col2:
        st.image(pr_screenshot, caption="PR Screenshot", use_container_width=True)

    st.info("Step 2: Analyzing with Vision LLM...")
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        custom_prompt = (
            "Analyze this web page screenshot for accessibility issues. "
            "Be very specific and only mention issues you can actually see and verify in this screenshot. "
            "For each issue, describe the exact element or location where the problem occurs. "
            "Examples: 'Button at top-right has insufficient color contrast (appears to be light gray on white)', "
            "'Image in the main content area lacks visible alt text indicator', "
            "'Form input field at [location] has no visible label'. "
            "Do not make generic assumptions - only report what you can specifically observe. "
            "List up to 5 concrete, location-specific accessibility problems. "
            "Format as a numbered list."
        )
        base_report = analyze_screenshot_with_openai_vision(base_screenshot, api_key=api_key, prompt=custom_prompt)
        pr_report = analyze_screenshot_with_openai_vision(pr_screenshot, api_key=api_key, prompt=custom_prompt)

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Base Report")
            st.write(base_report)
            base_types = extract_issue_types(base_report)
            if base_types:
                base_df = pd.DataFrame({'Type': base_types})
                base_fig = px.bar(base_df.value_counts().reset_index(), x='Type', y='count',
                                  title='Base: Accessibility Issue Types', color='Type',
                                  labels={'count': 'Count'}, height=300)
                st.plotly_chart(base_fig, use_container_width=True)
        with col4:
            st.subheader("PR Report")
            st.write(pr_report)
            pr_types = extract_issue_types(pr_report)
            if pr_types:
                pr_df = pd.DataFrame({'Type': pr_types})
                pr_fig = px.bar(pr_df.value_counts().reset_index(), x='Type', y='count',
                                title='PR: Accessibility Issue Types', color='Type',
                                labels={'count': 'Count'}, height=300)
                st.plotly_chart(pr_fig, use_container_width=True)

        st.subheader("🆕 New Accessibility Issues in PR:")
        st.code(diff_reports(base_report, pr_report))
    except Exception as e:
        st.error(f"Error during analysis: {e}")


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
                   if line.strip() and "no issue found" not in line.lower() 
                   and "no significant accessibility issues" not in line.lower()]
    pr_points = [line.strip() for line in pr_report.splitlines() 
                 if line.strip() and "no issue found" not in line.lower()
                 and "no significant accessibility issues" not in line.lower()]
    
    # If base has no issues but PR has issues, all PR issues are new
    if not base_points and pr_points:
        return "\n".join(pr_points)
    
    # If both have no issues
    if not base_points and not pr_points:
        return "No new accessibility issues found!"
    
    # Compare and find new issues
    base_set = set(base_points)
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
        
        # First, analyze the base version to establish a baseline
        base_prompt = (
            "Analyze this web page screenshot and identify any visible accessibility issues. "
            "Focus on what you can actually observe in the interface. "
            "If the page appears to have no obvious accessibility problems, simply state 'No significant accessibility issues observed.' "
            "Be specific about locations and elements if issues are found."
        )
        
        # Then analyze the PR version with more detailed scrutiny
        pr_prompt = (
            "Analyze this web page screenshot for accessibility issues with particular attention to: "
            "1. New UI elements or changes that might have accessibility problems "
            "2. Color contrast issues in buttons, text, or interactive elements "
            "3. Missing visual indicators for form fields, buttons, or interactive areas "
            "4. Layout or design changes that could impact accessibility "
            "5. Any new content that lacks proper visual cues "
            "Be very specific about the location and nature of any issues you observe. "
            "Only report issues you can actually see and verify in this screenshot. "
            "Format as a numbered list."
        )
        
        base_report = analyze_screenshot_with_openai_vision(base_screenshot, api_key=api_key, prompt=base_prompt)
        pr_report = analyze_screenshot_with_openai_vision(pr_screenshot, api_key=api_key, prompt=pr_prompt)

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
            else:
                # Add some visual content when no issues are found
                st.success("✅ No significant accessibility issues detected in the base version")
                st.info("💡 **This is good!** The base version appears to have a solid accessibility foundation.")
                
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
            else:
                # Add visual content when no issues in PR either
                st.success("✅ No accessibility issues detected in the PR version")
                st.info("💡 **Excellent!** This PR maintains good accessibility standards.")

        st.subheader("🆕 New Accessibility Issues in PR:")
        st.code(diff_reports(base_report, pr_report))
    except Exception as e:
        st.error(f"Error during analysis: {e}")

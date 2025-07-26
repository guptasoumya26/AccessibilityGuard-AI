# Streamlit app UI for AccessibilityGuard-AI
import streamlit as st
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from selenium_utils.selenium_scraper import capture_screenshot_and_dom
from vision.openai_vision import analyze_screenshot_with_openai_vision

st.set_page_config(page_title="AccessibilityGuard-AI", layout="centered")
st.title("🛡️ AccessibilityGuard-AI")
st.write("Compare two versions of your web page for new accessibility issues using AI vision models.")

base_url = st.text_input("Enter the **Base** URL (main branch, staging, etc.):", "https://www.example.com")
pr_url = st.text_input("Enter the **PR** URL (feature branch, preview, etc.):", "https://www.example.com")
run_btn = st.button("Compare Accessibility")

def diff_reports(base_report, pr_report):
    base_lines = set(base_report.splitlines())
    pr_lines = set(pr_report.splitlines())
    new_issues = pr_lines - base_lines
    return "\n".join(new_issues) if new_issues else "No new accessibility issues found!"

if run_btn and base_url and pr_url:
    st.info("Step 1: Capturing screenshots and DOMs...")
    base_screenshot, _ = capture_screenshot_and_dom(base_url, screenshot_path="base_screenshot.png", dom_path="base_dom.html")
    pr_screenshot, _ = capture_screenshot_and_dom(pr_url, screenshot_path="pr_screenshot.png", dom_path="pr_dom.html")
    st.image(base_screenshot, caption="Base Screenshot", use_column_width=True)
    st.image(pr_screenshot, caption="PR Screenshot", use_column_width=True)

    st.info("Step 2: Analyzing with OpenAI Vision...")
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        base_report = analyze_screenshot_with_openai_vision(base_screenshot, api_key=api_key)
        pr_report = analyze_screenshot_with_openai_vision(pr_screenshot, api_key=api_key)
        st.subheader("Base Report")
        st.write(base_report)
        st.subheader("PR Report")
        st.write(pr_report)
        st.subheader("🆕 New Accessibility Issues in PR:")
        st.code(diff_reports(base_report, pr_report))
    except Exception as e:
        st.error(f"Error during analysis: {e}")

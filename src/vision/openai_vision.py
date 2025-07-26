# Handles image analysis using OpenAI Vision models
import openai
import os

def analyze_screenshot_with_openai_vision(image_path, prompt=None, api_key=None, model="gpt-4o"):
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API key must be provided or set in OPENAI_API_KEY env var.")

    if prompt is None:
        prompt = (
            "You are an accessibility expert. Analyze this web page screenshot for accessibility issues "
            "(such as color contrast, missing alt text, focus indicators, etc.) and provide a concise report."
        )

    import base64
    client = openai.OpenAI(api_key=api_key)
    with open(image_path, "rb") as img_file:
        image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert accessibility auditor."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]}
        ],
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

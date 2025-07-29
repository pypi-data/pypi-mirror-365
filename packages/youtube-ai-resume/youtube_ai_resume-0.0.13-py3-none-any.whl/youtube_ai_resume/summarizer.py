from __future__ import annotations
from openai import OpenAI
from .config import load

_cfg = load()
DEFAULT_MODEL      = _cfg.get("openai_model", "gpt-3.5-turbo")
DEFAULT_OUTPUT_LANG = _cfg.get("output_lang", "en")

SYSTEM_PROMPT = (
    "You are a professional note-taker. Produce a concise, insightful summary in {lang}. "
    "Do not mention or indicate the language of the summary at any point. "
    "Use clear paragraphs and bullet points where helpful. Avoid filler; focus on key ideas, arguments, and facts. "
    "Always end the summary with a distinct 'Conclusion' section that synthesizes the main takeaways."
)

def summarize(
    transcript: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    out_lang: str = DEFAULT_OUTPUT_LANG,
) -> str:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(lang=out_lang)},
            {"role": "user",   "content": transcript},
        ],
        temperature=0.3,
    )
    content = response.choices[0].message.content or ""
    return content.strip()

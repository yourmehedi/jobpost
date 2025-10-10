from transformers import pipeline

# Load Hugging Face text-generation pipeline
try:
    jd_pipe = pipeline("text-generation", model="gpt2")  # অথবা তোমার পছন্দের মডেল
except Exception as e:
    print("⚠️ ai_engine.utils: job description model load error:", e)
    jd_pipe = None

# job_recommendation/utils.py
from transformers import pipeline
recommend_model = pipeline("text2text-generation", model="google/flan-t5-base")

def ai_recommend_jobs(profile_text, job_list):
    prompt = (
        f"Based on this candidate profile:\n{profile_text}\n\n"
        f"Suggest the top 5 most relevant job roles from the following list:\n{', '.join(job_list)}"
    )
    try:
        result = recommend_model(prompt, max_length=200)
        return result[0]['generated_text'].split(',')
    except Exception as e:
        print("Recommendation Error:", e)
        return []

import re
import openai
from django.conf import settings

EMAIL_REGEX = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
PHONE_REGEX = r'(\+?\d[\d\-\s]{8,}\d)'

def extract_email(text):
    match = re.search(EMAIL_REGEX, text)
    return match.group(0) if match else None


def extract_phone(text):
    match = re.search(PHONE_REGEX, text)
    if match:
        # strip out non-digit except leading '+'
        num = match.group(0)
        return re.sub(r'[^\d+]', '', num)
    return None


def extract_name(text):
    lines = text.strip().split('\n')
    for line in lines[:5]:  # Search in first few lines
        if len(line.strip().split(' ')) >= 2:
            return line.strip()
    return None

def extract_skills(text):
    known_skills = ['python', 'django', 'rest', 'javascript', 'sql', 'excel', 'html', 'css']
    found = [skill for skill in known_skills if skill.lower() in text.lower()]
    return ', '.join(found)

def extract_experience(text):
    if 'experience' in text.lower():
        try:
            section = text.lower().split('experience')[1][:500]
            return section.strip()
        except:
            return None
    return None

def extract_education(text):
    if 'education' in text.lower():
        try:
            section = text.lower().split('education')[1][:500]
            return section.strip()
        except:
            return None
    return None

def generate_tags(skills, experience):
    skill_tags = skills.split(',') if skills else []
    exp_tags = []
    if experience:
        exp_tags = [kw for kw in ['intern', 'manager', 'developer', 'trainer', 'engineer'] if kw in experience.lower()]
    return ', '.join(set(skill_tags + exp_tags))

def ai_generate_tags(text: str) -> str:
    """
    Use OpenAI to generate comma-separated tags from resume text.
    Output: e.g., "Python, Django, Backend Developer, Healthcare"
    """
    try:
        openai.api_key = settings.OPENAI_API_KEY

        prompt = (
            "Extract 5-10 relevant tags from the following resume. Tags should be skills, job roles, or sectors. "
            "Return them as a comma-separated list only.\n\n"
            f"{text}"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a resume analysis expert."},
                {"role": "user", "content": prompt}
            ]
        )

        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("AI tag generation error:", e)
        return ""

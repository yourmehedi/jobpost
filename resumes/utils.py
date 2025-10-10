# import re
# from transformers import pipeline

# # ✅ Initialize Hugging Face pipeline (once)
# tag_generator = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# EMAIL_REGEX = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
# PHONE_REGEX = r'(\+?\d[\d\-\s]{8,}\d)'


# def extract_email(text):
#     match = re.search(EMAIL_REGEX, text)
#     return match.group(0) if match else None


# def extract_phone(text):
#     match = re.search(PHONE_REGEX, text)
#     if match:
#         num = match.group(0)
#         return re.sub(r'[^\d+]', '', num)
#     return None


# def extract_name(text):
#     lines = text.strip().split('\n')
#     for line in lines[:5]:
#         if len(line.strip().split(' ')) >= 2:
#             return line.strip()
#     return None


# def extract_skills(text):
#     known_skills = ['python', 'django', 'rest', 'javascript', 'sql', 'excel', 'html', 'css', 'react', 'java']
#     found = [skill for skill in known_skills if skill.lower() in text.lower()]
#     return ', '.join(found)


# def extract_experience(text):
#     if 'experience' in text.lower():
#         try:
#             section = text.lower().split('experience')[1][:500]
#             return section.strip()
#         except Exception:
#             return None
#     return None


# def extract_education(text):
#     if 'education' in text.lower():
#         try:
#             section = text.lower().split('education')[1][:500]
#             return section.strip()
#         except Exception:
#             return None
#     return None


# def generate_tags(skills, experience):
#     skill_tags = skills.split(',') if skills else []
#     exp_tags = []
#     if experience:
#         exp_tags = [kw for kw in ['intern', 'manager', 'developer', 'trainer', 'engineer'] if kw in experience.lower()]
#     return ', '.join(set(skill_tags + exp_tags))


# def ai_generate_tags(text: str) -> str:
#     """
#     Use Hugging Face zero-shot model to extract relevant job/skill tags.
#     Works offline (no API key needed).
#     """
#     candidate_labels = [
#         "Python", "Django", "Machine Learning", "AI", "Data Science", "React",
#         "Frontend Developer", "Backend Developer", "Full Stack", "Project Manager",
#         "Marketing", "Finance", "Teacher", "Engineer", "Customer Support", "Designer",
#         "HR", "Remote Work", "Healthcare", "Sales", "Content Writing"
#     ]

#     try:
#         result = tag_generator(text[:1000], candidate_labels)
#         top_labels = [label for label, score in zip(result['labels'], result['scores']) if score > 0.35]
#         return ', '.join(top_labels)
#     except Exception as e:
#         print("⚠️ HuggingFace Tag Generation Error:", e)
#         return ""


# resume/utils.py
import re
from transformers import pipeline

# Zero-shot or text2text approach — using zero-shot classification for tags
try:
    tag_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
except Exception as e:
    print("⚠️ resume.utils: tag model load error:", e)
    tag_pipeline = None

EMAIL_REGEX = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
PHONE_REGEX = r'(\+?\d[\d\-\s]{8,}\d)'

def extract_email(text):
    m = re.search(EMAIL_REGEX, text)
    return m.group(0) if m else None

def extract_phone(text):
    m = re.search(PHONE_REGEX, text)
    if m:
        num = m.group(0)
        return re.sub(r'[^\d+]', '', num)
    return None

def extract_name(text):
    lines = text.strip().split('\n')
    for line in lines[:6]:
        if len(line.strip().split(' ')) >= 2:
            return line.strip()
    return None

def extract_skills(text):
    known_skills = ['python','django','rest','javascript','sql','excel','html','css','react','java']
    found = [s for s in known_skills if s.lower() in text.lower()]
    return ', '.join(found)

def extract_experience(text):
    if 'experience' in text.lower():
        try:
            return text.lower().split('experience',1)[1][:500].strip()
        except:
            return ""
    return ""

def extract_education(text):
    if 'education' in text.lower():
        try:
            return text.lower().split('education',1)[1][:500].strip()
        except:
            return ""
    return ""

def generate_tags(skills, experience):
    tags = []
    if skills:
        tags += [s.strip() for s in skills.split(',') if s.strip()]
    if experience:
        for kw in ['intern','manager','developer','trainer','engineer','senior','lead']:
            if kw in experience.lower():
                tags.append(kw)
    return ', '.join(sorted(set(tags)))

def ai_generate_tags(text: str) -> str:
    if not tag_pipeline:
        return ""
    candidate_labels = [
        "Python", "Django", "Machine Learning", "AI", "Data Science", "React",
        "Frontend Developer", "Backend Developer", "Full Stack", "Project Manager",
        "Marketing", "Finance", "Teacher", "Engineer", "Customer Support", "Designer",
        "HR", "Remote Work", "Healthcare", "Sales", "Content Writing"
    ]
    try:
        out = tag_pipeline(text[:1000], candidate_labels)
        labels = [label for label, score in zip(out['labels'], out['scores']) if score > 0.35]
        return ', '.join(labels)
    except Exception as e:
        print("⚠️ ai_generate_tags error:", e)
        return ""

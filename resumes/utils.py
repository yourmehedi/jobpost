import re

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'(\+?\d{10,13})', text)
    return match.group(0) if match else None

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

import re
from .models import RestrictedWord

def moderate_text(text: str) -> str:
    # Vulgar word replace
    restricted = RestrictedWord.objects.values_list('word', flat=True)
    for word in restricted:
        pattern = r'\b' + re.escape(word) + r'\b'
        text = re.sub(pattern, '***', text, flags=re.IGNORECASE)

    # Contact info remove
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'\+?\d[\d\s\-]{7,}\d'
    url_pattern = r'(http[s]?://|www\.)\S+'

    text = re.sub(email_pattern, '***', text)
    text = re.sub(phone_pattern, '***', text)
    text = re.sub(url_pattern, '***', text)

    return text

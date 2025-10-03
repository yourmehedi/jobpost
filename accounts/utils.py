import requests
from django.conf import settings
from core_ui.utils import is_feature_enabled

def send_telegram_message(chat_id, message):
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    return requests.post(url, data={'chat_id': chat_id, 'text': message})
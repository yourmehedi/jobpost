# ai_engine/utils/hf_models.py
import threading
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer

_lock = threading.Lock()
_models = {}

# Default lightweight model choices (changeable via AISettings.active_models)
DEFAULTS = {
    "parser": "dslim/bert-base-NER",   # NER model for basic resume parsing
    "matcher": "sentence-transformers/all-MiniLM-L6-v2",
    "summarizer": "sshleifer/distilbart-cnn-12-6",
    "dialogue": "microsoft/DialoGPT-small",
}

def get_parser(model_name=None):
    with _lock:
        key = model_name or DEFAULTS["parser"]
        k = f"parser::{key}"
        if k not in _models:
            ner = pipeline("ner", model=key, tokenizer=key, grouped_entities=True)
            _models[k] = ner
        return _models[k]

def get_matcher(model_name=None):
    with _lock:
        key = model_name or DEFAULTS["matcher"]
        k = f"matcher::{key}"
        if k not in _models:
            model = SentenceTransformer(key)
            _models[k] = model
        return _models[k]

def get_summarizer(model_name=None):
    with _lock:
        key = model_name or DEFAULTS["summarizer"]
        k = f"summarizer::{key}"
        if k not in _models:
            summarizer = pipeline("summarization", model=key, device=-1)
            _models[k] = summarizer
        return _models[k]

def get_dialogue(model_name=None):
    with _lock:
        key = model_name or DEFAULTS["dialogue"]
        k = f"dialogue::{key}"
        if k not in _models:
            tokenizer = AutoTokenizer.from_pretrained(key)
            model = AutoModelForCausalLM.from_pretrained(key)
            _models[k] = {"tokenizer": tokenizer, "model": model}
        return _models[k]

def preload_all(models_map=None):
    """
    Optional helper to preload chosen models. models_map can override defaults.
    e.g. {"parser": "dslim/bert-base-NER", ...}
    """
    models_map = models_map or DEFAULTS
    get_parser(models_map.get("parser"))
    get_matcher(models_map.get("matcher"))
    get_summarizer(models_map.get("summarizer"))
    get_dialogue(models_map.get("dialogue"))
    return True

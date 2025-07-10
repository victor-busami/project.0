# ==========================================
# 📄 analyzers/sentiment_analyzer.py
# ==========================================
from transformers import pipeline

classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_threat_level(weapons):
    if not weapons:
        return "LOW"
    summary = " ".join([w['severity'] for w in weapons])
    result = classifier(summary)[0]
    return result['label']  # 'POSITIVE' or 'NEGATIVE'

# ==========================================
# 📄 analyzers/sentiment_analyzer.py
# ==========================================
from transformers import pipeline
import re

# Initialize multiple classifiers for better threat detection
try:
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    violence_classifier = pipeline("text-classification", model="unitary/toxic-bert")
    print("Using enhanced sentiment analysis with violence detection")
except:
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    print("Using basic sentiment analysis")

# Violence-related keywords
VIOLENCE_KEYWORDS = [
    "gun", "weapon", "knife", "violence", "threat", "danger", "attack", "fight",
    "shoot", "kill", "harm", "dangerous", "aggressive", "hostile", "violent",
    "firearm", "pistol", "rifle", "shotgun", "blade", "dagger", "sword",
    "bomb", "explosive", "threaten", "assault", "robbery", "crime"
]

def analyze_threat_level(weapons, image_description=""):
    """Enhanced threat level analysis with violence detection"""
    if not weapons and not image_description:
        return "LOW"
    
    # Combine weapon information and image description
    threat_text = ""
    if weapons:
        weapon_names = [w.get('weapon', '') for w in weapons]
        severities = [w.get('severity', '') for w in weapons]
        threat_text += f"Detected objects: {', '.join(weapon_names)}. Severity levels: {', '.join(severities)}. "
    
    if image_description:
        threat_text += f"Image context: {image_description}"
    
    # Check for violence keywords
    violence_score = 0
    for keyword in VIOLENCE_KEYWORDS:
        if keyword.lower() in threat_text.lower():
            violence_score += 1
    
    # Analyze sentiment
    try:
        sentiment_result = classifier(threat_text[:512])[0]  # Limit text length
        sentiment_score = sentiment_result['score']
        sentiment_label = sentiment_result['label']
        
        # Violence detection
        violence_result = violence_classifier(threat_text[:512])[0]
        violence_score += violence_result['score'] if violence_result['label'] == 'toxic' else 0
    except:
        sentiment_score = 0.5
        sentiment_label = 'NEUTRAL'
    
    # Determine threat level based on multiple factors
    if violence_score > 2 or any(w.get('severity') == 'SERIOUS-URGENT' for w in weapons):
        return "SERIOUS-URGENT"
    elif violence_score > 1 or any(w.get('severity') == 'SERIOUS' for w in weapons):
        return "SERIOUS"
    elif violence_score > 0.5 or any(w.get('severity') == 'MEDIUM' for w in weapons):
        return "MEDIUM"
    elif sentiment_label == 'NEGATIVE' and sentiment_score > 0.7:
        return "MEDIUM"
    else:
        return "LOW"

def analyze_image_context(image_description):
    """Analyze image context for violent content"""
    if not image_description:
        return "LOW"
    
    # Check for violence indicators in description
    violence_indicators = 0
    for keyword in VIOLENCE_KEYWORDS:
        if keyword.lower() in image_description.lower():
            violence_indicators += 1
    
    if violence_indicators >= 2:
        return "SERIOUS"
    elif violence_indicators >= 1:
        return "MEDIUM"
    else:
        return "LOW"

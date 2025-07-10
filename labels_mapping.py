# ==========================================
# 📄 utils/labels_mapping.py
# ==========================================
def assign_alert_level(sentiment):
    if sentiment == "NEGATIVE":
        return "SERIOUS-URGENT", "🔴 Red"
    elif sentiment == "POSITIVE":
        return "LOW", "🟢 Green"
    else:
        return "SERIOUS", "🟡 Yellow"

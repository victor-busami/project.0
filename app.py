# ==========================================
# 📄 app.py (Main Interface)
# ==========================================
import streamlit as st
from object_detector import detect_weapons
from sentiment_analyzer import analyze_threat_level
from geolocator import get_location
from labels_mapping import assign_alert_level
import json
import os

st.set_page_config(page_title="AI Crime Reporter", layout="wide")
st.title("🛡️ AI - Crime Threat Detector")

# Upload image
image = st.file_uploader("Upload a crime-related image", type=['jpg', 'jpeg', 'png'])
if image:
    st.image(image, caption="Uploaded Image", use_container_width=True)
    weapons = detect_weapons(image)
    alert = analyze_threat_level(weapons)
    alert_level, alert_color = assign_alert_level(alert)
    st.markdown(f"### 📊 Alert Level: {alert_color} **{alert_level}**")

    # Get location (auto/manual fallback)
    location = get_location()

    # Display results
    with st.expander("📑 Incident Report JSON"):
        report = {
            "weapons_detected": weapons,
            "alert_level": alert_level,
            "location": location
        }
        st.json(report)

    # Save to file
    os.makedirs("data", exist_ok=True)
    with open("data/reports.json", "a") as f:
        f.write(json.dumps(report) + "\n")

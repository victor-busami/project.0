# ==========================================
# 📄 app.py (Main Interface)
# ==========================================
import streamlit as st
from object_detector import detect_weapons
from PIL import Image
import json
import os
from datetime import datetime

# Mock functions for missing modules
def analyze_threat_level(weapons):
    """Mock sentiment analyzer"""
    threat_levels = [w['severity'] for w in weapons]
    if "SERIOUS-URGENT" in threat_levels:
        return "SERIOUS-URGENT"
    elif "SERIOUS" in threat_levels:
        return "SERIOUS"
    return "LOW"

def get_location():
    """Mock geolocator"""
    return {
        "latitude": -1.286389,  # Default Nairobi coordinates
        "longitude": 36.817223,
        "address": "Nairobi, Kenya"
    }

def assign_alert_level(threat_level):
    """Convert threat level to visual indicators"""
    if threat_level == "SERIOUS-URGENT":
        return "RED ALERT", "🔴"
    elif threat_level == "SERIOUS":
        return "YELLOW ALERT", "🟡"
    return "GREEN ALERT", "🟢"

# Streamlit UI Configuration
st.set_page_config(page_title="AI Crime Reporter", layout="wide")
st.title("🛡️ AI - Crime Threat Detector")
st.markdown("""
    *Real-time weapon detection and threat assessment for Kenyan security*
""")

# Image Upload Section
image_file = st.file_uploader(
    "Upload crime scene image", 
    type=['jpg', 'jpeg', 'png'],
    help="Upload an image containing potential weapons"
)

# Processing Section
if image_file:
    st.image(image_file, caption="Uploaded Image", use_column_width=True)
    
    with st.spinner("🔍 Analyzing image for threats..."):
        # Step 1: Detect weapons
        weapons = detect_weapons(image_file)
        
        # Step 2: Analyze threat level
        threat_level = analyze_threat_level(weapons)
        
        # Step 3: Get location
        location = get_location()
        
        # Step 4: Assign alert level
        alert_level, alert_icon = assign_alert_level(threat_level)

    # Results Display
    st.success("Analysis Complete!")
    
    # Alert Level Banner
    st.markdown(f"""
    <div style='background-color: {'#ff4b4b' if alert_level.startswith('RED') else 
                      '#faca2b' if alert_level.startswith('YELLOW') else '#2ecc71'}; 
                padding: 1rem; 
                border-radius: 0.5rem;
                text-align: center;'>
        <h2 style='color: white; margin: 0;'>
            {alert_icon} {alert_level}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Weapons Detected Section
    if weapons:
        st.subheader("⚠️ Detected Weapons")
        for weapon in weapons:
            st.write(f"""
            - **{weapon['weapon']}**  
              Severity: {weapon['severity']}  
              Confidence: {weapon['confidence']:.1%}
            """)
    else:
        st.info("✅ No weapons detected in this image")

    # Location Information
    st.subheader("📍 Incident Location")
    st.write(f"Latitude: {location['latitude']}, Longitude: {location['longitude']}")
    st.write(f"Approximate Address: {location['address']}")

    # Generate Report
    report = {
        "timestamp": datetime.now().isoformat(),
        "weapons_detected": weapons,
        "threat_level": threat_level,
        "location": location,
        "alert_level": alert_level
    }

    # Report Download Options
    st.subheader("📑 Incident Report")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("View JSON Report"):
            st.json(report)
    
    with col2:
        st.download_button(
            label="Download JSON Report",
            data=json.dumps(report, indent=2),
            file_name="crime_report.json",
            mime="application/json"
        )

    # Save report to local storage
    os.makedirs("data/reports", exist_ok=True)
    with open(f"data/reports/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(report, f)

    st.markdown("---")
    st.info("Report automatically saved to local storage")
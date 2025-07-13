import streamlit as st
from object_detector import detect_weapons
from PIL import Image
import json
import os
from datetime import datetime

# Streamlit UI Configuration
st.set_page_config(page_title="AI Crime Reporter", layout="wide")
st.title("🛡️ AI Weapon Detection System")
st.markdown("""
    *Real-time weapon detection for security applications*
""")

# Image Upload Section
uploaded_file = st.file_uploader(
    "Upload security camera image", 
    type=['jpg', 'jpeg', 'png'],
    help="Upload images containing potential weapons"
)

def analyze_threat_level(weapons):
    """Determine overall threat level"""
    if not weapons:
        return "LOW"
    
    severities = [w["severity"] for w in weapons]
    if "SERIOUS-URGENT" in severities:
        return "SERIOUS-URGENT"
    elif "SERIOUS" in severities:
        return "SERIOUS"
    return "MEDIUM" if "MEDIUM" in severities else "LOW"

def get_alert_color(threat_level):
    """Get color coding for threat level"""
    return {
        "SERIOUS-URGENT": "red",
        "SERIOUS": "orange",
        "MEDIUM": "yellow",
        "LOW": "green"
    }.get(threat_level, "gray")

# Process uploaded image
if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    
    with st.spinner("Analyzing for weapons..."):
        weapons = detect_weapons(uploaded_file)
        threat_level = analyze_threat_level(weapons)
        alert_color = get_alert_color(threat_level)
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "weapons_detected": weapons,
            "threat_level": threat_level,
            "alert_color": alert_color
        }

    # Display results
    st.subheader("🔍 Detection Results")
    
    if weapons:
        st.markdown(f"""
        <div style='background-color: {alert_color}; padding: 1rem; border-radius: 0.5rem;'>
            <h3 style='color: white; text-align: center;'>
                {threat_level.replace("-", " ").title()} THREAT DETECTED
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        for weapon in weapons:
            st.markdown(f"""
            - **{weapon['weapon'].title()}**  
              ⚠️ Severity: {weapon['severity']}  
              🎯 Confidence: {weapon['confidence']:.0%}  
              📏 Bounding Box: {weapon['bbox']}
            """)
    else:
        st.success("✅ No weapons detected")
        st.markdown("""
        <div style='background-color: green; padding: 1rem; border-radius: 0.5rem;'>
            <h3 style='color: white; text-align: center;'>ALL CLEAR</h3>
        </div>
        """, unsafe_allow_html=True)

    # Report download section
    st.subheader("📄 Incident Report")
    st.download_button(
        label="Download JSON Report",
        data=json.dumps(report, indent=2),
        file_name=f"weapon_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

    # Save to local storage (optional)
    os.makedirs("reports", exist_ok=True)
    with open(f"reports/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(report, f)
import streamlit as st
from object_detector import detect_weapons
from sentiment_analyzer import analyze_threat_level, analyze_image_context
from PIL import Image
import json
import os
from datetime import datetime

# Streamlit UI Configuration
st.set_page_config(page_title="AI Crime Reporter", layout="wide")
st.title("🛡️ AI Weapon Detection System")
st.markdown("""
    *Enhanced real-time weapon detection for security applications*
""")

# Image Upload Section
uploaded_file = st.file_uploader(
    "Upload security camera image", 
    type=['jpg', 'jpeg', 'png'],
    help="Upload images containing potential weapons or violent activities"
)

# Optional image description
image_description = st.text_area(
    "Image Description (Optional)",
    placeholder="Describe what you see in the image, including any weapons, violent activities, or threatening behavior...",
    help="Provide additional context about the image to improve threat detection accuracy"
)

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
    
    with st.spinner("Analyzing for weapons and threats..."):
        weapons = detect_weapons(uploaded_file)
        
        # Enhanced threat analysis with image description
        threat_level = analyze_threat_level(weapons, image_description)
        
        # Additional context analysis
        context_threat = analyze_image_context(image_description)
        
        # Combine threat levels
        if threat_level == "SERIOUS-URGENT" or context_threat == "SERIOUS":
            final_threat_level = "SERIOUS-URGENT"
        elif threat_level == "SERIOUS" or context_threat == "MEDIUM":
            final_threat_level = "SERIOUS"
        elif threat_level == "MEDIUM" or context_threat == "LOW":
            final_threat_level = "MEDIUM"
        else:
            final_threat_level = "LOW"
        
        alert_color = get_alert_color(final_threat_level)
        
        # Generate comprehensive report
        report = {
            "timestamp": datetime.now().isoformat(),
            "weapons_detected": weapons,
            "threat_level": final_threat_level,
            "object_detection_threat": threat_level,
            "context_threat": context_threat,
            "alert_color": alert_color,
            "image_description": image_description,
            "analysis_notes": []
        }
        
        # Add analysis notes
        if weapons:
            report["analysis_notes"].append(f"Detected {len(weapons)} potential weapon(s)")
        if image_description:
            report["analysis_notes"].append("Image description provided for context analysis")
        if final_threat_level != "LOW":
            report["analysis_notes"].append(f"Threat level elevated to {final_threat_level}")

    # Display results
    st.subheader("🔍 Enhanced Detection Results")
    
    if weapons or final_threat_level != "LOW":
        st.markdown(f"""
        <div style='background-color: {alert_color}; padding: 1rem; border-radius: 0.5rem;'>
            <h3 style='color: white; text-align: center;'>
                {final_threat_level.replace("-", " ").title()} THREAT DETECTED
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        if weapons:
            st.markdown("### 🚨 Detected Objects:")
            for weapon in weapons:
                st.markdown(f"""
                - **{weapon['weapon'].title()}**  
                  ⚠️ Severity: {weapon['severity']}  
                  🎯 Confidence: {weapon['confidence']:.0%}  
                  📏 Bounding Box: {weapon['bbox']}
                  🏷️ Original Label: {weapon.get('original_label', 'N/A')}
                """)
        
        if image_description and context_threat != "LOW":
            st.markdown("### 📝 Context Analysis:")
            st.warning(f"Image description indicates {context_threat} threat level")
            st.info(f"Description: {image_description}")
    else:
        st.success("✅ No weapons or threats detected")
        st.markdown("""
        <div style='background-color: green; padding: 1rem; border-radius: 0.5rem;'>
            <h3 style='color: white; text-align: center;'>ALL CLEAR</h3>
        </div>
        """, unsafe_allow_html=True)

    # Detailed analysis section
    st.subheader("📊 Analysis Details")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Object Detection Threat", threat_level)
        st.metric("Context Threat", context_threat)
    
    with col2:
        st.metric("Final Threat Level", final_threat_level)
        st.metric("Objects Detected", len(weapons) if weapons else 0)

    # Report download section
    st.subheader("📄 Comprehensive Incident Report")
    st.download_button(
        label="Download JSON Report",
        data=json.dumps(report, indent=2),
        file_name=f"enhanced_weapon_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

    # Save to local storage
    os.makedirs("reports", exist_ok=True)
    with open(f"reports/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(report, f)
    
    st.success("✅ Report saved to local storage")
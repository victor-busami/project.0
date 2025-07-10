# ==========================================
# 📄 geolocation/geolocator.py
# ==========================================
import geocoder
import streamlit as st

def get_location():
    g = geocoder.ip('me')
    auto = g.latlng if g.ok else None

    st.subheader("📍 Location Info")
    if auto:
        st.success(f"Auto location: {auto}")
    else:
        st.warning("Couldn't fetch location automatically. Please enter manually.")

    manual = {
        "county": st.text_input("County"),
        "sub_county": st.text_input("Sub-county"),
        "ward": st.text_input("Ward"),
        "location": st.text_input("Location"),
        "sub_location": st.text_input("Sub-location")
    }

    return {"auto": auto, "manual": manual}
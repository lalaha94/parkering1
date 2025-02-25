import streamlit as st
import requests

# API URL – Sett opp Flask API på Vercel først, eller bruk en placeholder URL
API_URL = "https://parkering-sms.vercel.app"

st.title("🚗 Parkering SMS-Varling")
st.write("Meld deg på for å få varsel når Kasernen P-hus blir ledig.")

phone = st.text_input("📱 Telefonnummer (+47...)", "")

col1, col2 = st.columns(2)

with col1:
    if st.button("✅ Meld meg på"):
        if phone:
            response = requests.post(f"{API_URL}/subscribe", json={"phone": phone})
            if response.status_code == 200:
                st.success("✅ Du er nå påmeldt!")
            else:
                st.error("❌ Feil ved påmelding.")
        else:
            st.warning("⚠️ Skriv inn et gyldig nummer.")

with col2:
    if st.button("🚫 Meld meg av"):
        if phone:
            response = requests.post(f"{API_URL}/unsubscribe", json={"phone": phone})
            if response.status_code == 200:
                st.success("✅ Du er nå avmeldt.")
            else:
                st.error("❌ Feil ved avmelding.")
        else:
            st.warning("⚠️ Skriv inn et gyldig nummer.")

st.markdown("---")
st.subheader("🔍 Sjekk om parkering er tilgjengelig")
if st.button("🔄 Sjekk nå"):
    response = requests.get(f"{API_URL}/check")
    if response.status_code == 200:
        data = response.json()
        if data["available"]:
            st.success("🎉 Parkering er tilgjengelig!")
        else:
            st.error("🚧 Fortsatt utsolgt.")
    else:
        st.error("⚠️ Kunne ikke hente status.")

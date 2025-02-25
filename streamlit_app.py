import streamlit as st
import requests
from twilio.rest import Client

# Hent Twilio credentials fra Streamlit Secrets
account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
twilio_number = st.secrets["TWILIO_PHONE_NUMBER"]

client = Client(account_sid, auth_token)

st.title("🚗 Parkering SMS-Varling")

phone = st.text_input("📱 Telefonnummer (+47...)", "")

if st.button("✅ Meld meg på"):
    if phone:
        try:
            message = client.messages.create(
                body="🚗 Hei! Parkeringsplassen er nå tilgjengelig! Sjekk her: https://aimopark-permit.giantleap.no/",
                from_=twilio_number,
                to=phone
            )
            st.success(f"✅ SMS sendt til {phone}!")
        except Exception as e:
            st.error(f"❌ Feil ved sending av SMS: {e}")
    else:
        st.warning("⚠️ Skriv inn et gyldig telefonnummer.")


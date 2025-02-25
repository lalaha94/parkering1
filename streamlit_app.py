import os
import time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client

# Twilio konfigurasjon (Bruk secrets eller .env for sikkerhet)
TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = st.secrets["TWILIO_PHONE_NUMBER"]

# URL til booking-siden
BOOKING_URL = "https://aimopark-permit.giantleap.no/embedded-user-shop.html#/shop/select-facility/3007"

# Streamlit UI
st.title("🚗 Aimo Park Varsling")
st.write("Sjekk om Kasernen P-hus er ledig og få SMS-varsling!")

# Input for telefonnummer
phone_number = st.text_input("📱 Ditt telefonnummer (+47...)", "")

# Funksjon for å sjekke parkeringsstatus
def check_parking_availability():
    """Bruker Selenium for å sjekke om parkering er ledig."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(BOOKING_URL)
        time.sleep(5)  # Vent på at siden laster inn
        page_text = driver.page_source
        driver.quit()

        if "Utsolgt" in page_text:
            return False
        else:
            return True

    except Exception as e:
        driver.quit()
        st.error(f"⚠️ Feil ved sjekk: {e}")
        return False

# Funksjon for å sende SMS
def send_sms(phone):
    """Sender en SMS-varsling hvis parkering er ledig."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body="🚗 Kasernen P-hus er NÅ LEDIG! Sjekk her: " + BOOKING_URL,
        from_=TWILIO_PHONE_NUMBER,
        to=phone
    )
    return message.sid

# Knapp for å sjekke tilgjengelighet
if st.button("🔍 Sjekk parkeringsstatus"):
    available = check_parking_availability()
    if available:
        st.success("🎉 Parkeringsplassen er LEDIG!")
    else:
        st.error("🚧 Parkeringsplassen er fortsatt utsolgt.")

# Knapp for å melde seg på SMS-varsling
if st.button("📩 Meld meg på SMS-varsling"):
    if phone_number:
        available = check_parking_availability()
        if available:
            sid = send_sms(phone_number)
            st.success(f"✅ SMS sendt til {phone_number}! (SID: {sid})")
        else:
            st.warning("🚧 Fortsatt utsolgt. Ingen SMS sendt.")
    else:
        st.warning("⚠️ Vennligst skriv inn et telefonnummer.")

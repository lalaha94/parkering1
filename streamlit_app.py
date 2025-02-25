import os
import streamlit as st
import httpx
from selectolax.parser import HTMLParser
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

def check_parking_availability():
    """Bruker httpx og selectolax for å sjekke om parkering er ledig."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = httpx.get(BOOKING_URL, headers=headers, timeout=10)
        
        if response.status_code != 200:
            st.error("⚠️ Kunne ikke hente nettsiden. Sjekk URL-en.")
            return False

        # Logg hele HTML-en vi mottar
        raw_html = response.text
        with open("debug_page.html", "w", encoding="utf-8") as file:
            file.write(raw_html)
        
        # Parse HTML med selectolax
        tree = HTMLParser(raw_html)

        # Sjekk hva HTML-en inneholder
        st.text_area("🔍 Debug HTML", raw_html, height=300)

        # Sjekk om "Utsolgt" finnes på siden
        if "Utsolgt" in tree.text():
            return False
        else:
            return True

    except Exception as e:
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

import os
import streamlit as st
import httpx
from selectolax.parser import HTMLParser
from twilio.rest import Client
from datetime import datetime

# Twilio konfigurasjon (Bruk secrets eller .env for sikkerhet)
TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = st.secrets["TWILIO_PHONE_NUMBER"]

# URL til booking-siden
BOOKING_URL = "https://aimopark-permit.giantleap.no/embedded-user-shop.html#/shop/select-facility/3007"

# Liste over påmeldte mottakere
SUBSCRIBERS = ["+4797655108"]  # Bytt ut med riktige nummer

# Historikk for tidligere sjekker
if "history" not in st.session_state:
    st.session_state.history = []

def check_parking_availability():
    """Følger redirect og sjekker om parkering er tilgjengelig."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        
        # Følg redirect til riktig side
        with httpx.Client(headers=headers, follow_redirects=True) as client:
            response = client.get(BOOKING_URL, timeout=10)

            if response.status_code != 200:
                return False

            # Parse HTML
            tree = HTMLParser(response.text)

            # Sjekk om "Utsolgt" finnes
            return "Utsolgt" not in tree.text()

    except Exception:
        return False

def send_sms(phone):
    """Sender en SMS-varsling hvis parkering er ledig."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body="🚗 Kasernen P-hus er NÅ LEDIG! Sjekk her: " + BOOKING_URL,
        from_=TWILIO_PHONE_NUMBER,
        to=phone
    )
    return message.sid

def daily_check():
    """Kjører automatisk sjekk én gang per dag og sender varsel hvis ledig."""
    available = check_parking_availability()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if available:
        for phone in SUBSCRIBERS:
            send_sms(phone)
        st.session_state.history.append(f"{timestamp} - ✅ LEDIG - SMS sendt!")
    else:
        st.session_state.history.append(f"{timestamp} - ❌ UTSOLGT")

# UI
st.title("🚗 Aimo Park Varsling")
st.write("Sjekk om Kasernen P-hus er ledig og få SMS-varsling!")

# Knapp for manuell sjekk
if st.button("🔍 Sjekk parkeringsstatus nå"):
    available = check_parking_availability()
    if available:
        st.success("🎉 Parkeringsplassen er LEDIG!")
    else:
        st.error("🚧 Parkeringsplassen er fortsatt utsolgt.")

# Knapp for å kjøre daglig sjekk manuelt
if st.button("⏳ Kjør daglig sjekk nå"):
    daily_check()
    st.success("Daglig sjekk fullført!")

# Vise historikk
st.subheader("📜 Sjekkhistorikk")
for entry in st.session_state.history[-10:]:
    st.write(entry)

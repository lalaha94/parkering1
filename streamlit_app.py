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
    """Følger redirect, finner riktig side og sjekker om parkering er ledig."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}

        # 1️⃣ Hent første side (redirect-side)
        with httpx.Client(headers=headers, follow_redirects=True) as client:
            response = client.get(BOOKING_URL, timeout=10)

            if response.status_code != 200:
                st.error("⚠️ Kunne ikke hente nettsiden.")
                return False

            # 2️⃣ Finn den faktiske URL-en vi blir omdirigert til
            final_url = str(response.url)  # Dette er den virkelige siden der "Utsolgt" vises
            st.write(f"🔄 Omdirigert til: {final_url}")  # Debugging

            # 3️⃣ Hent den faktiske siden
            response = client.get(final_url, timeout=10)
            if response.status_code != 200:
                st.error("⚠️ Kunne ikke hente den endelige siden.")
                return False

            # 4️⃣ Parse HTML
            tree = HTMLParser(response.text)

            # 5️⃣ Finn `<i18n>`-elementet med klassen "negative"
            sold_out_element = tree.css_first("i18n.negative")

            # 6️⃣ Debug: Vis hele HTML-en
            st.text_area("🔍 Debug HTML (Final Page)", response.text, height=300)

            # 7️⃣ Hvis elementet finnes og inneholder "Utsolgt", er det utsolgt
            if sold_out_element and "Utsolgt" in sold_out_element.text():
                return False
            else:
                return True

    except Exception as e:
        st.error(f"⚠️ Feil ved sjekk: {e}")
        return False

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

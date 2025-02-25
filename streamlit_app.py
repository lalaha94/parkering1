import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import os

# Twilio konfigurasjon (Bruk secrets eller .env for sikkerhet)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBER = "+4797655108"  # Bytt ut med ditt nummer

# URL-er
MAIN_URL = "https://www.aimopark.no/en/cities/kristiansand/kasernen/"
BOOKING_URL = "https://aimopark-permit.giantleap.no/embedded-user-shop.html#/shop/select-facility/3007"

def check_parking_availability():
    """Sjekker om langtidsparkering er tilgjengelig på Kasernen P-hus."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(MAIN_URL, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        booking_link = soup.find("a", class_="facilitypage__cta--longterm")

        if booking_link:
            print("🔗 Fant booking-knappen! Sjekker om det er ledig...")
            return check_booking_page()
        else:
            print("❌ Kunne ikke finne booking-knappen. Kanskje ingen langtidsplasser?")
            return False

    except requests.RequestException as e:
        print(f"⚠️ Feil ved henting av nettsiden: {e}")
        return False

def check_booking_page():
    """Sjekker om parkeringsabonnementet er ledig."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(BOOKING_URL, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        if "Utsolgt" in soup.text:
            print("🚧 Parkeringsplassen er fortsatt utsolgt.")
            return False
        else:
            print("🎉 Parkeringsplassen er LEDIG!")
            return True

    except requests.RequestException as e:
        print(f"⚠️ Feil ved henting av booking-siden: {e}")
        return False

def send_sms():
    """Sender en SMS-varsling hvis parkering er ledig."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body="🚗 Kasernen P-hus er NÅ LEDIG! Sjekk her: " + BOOKING_URL,
        from_=TWILIO_PHONE_NUMBER,
        to=RECIPIENT_PHONE_NUMBER
    )
    print(f"✅ SMS sendt! SID: {message.sid}")

if __name__ == "__main__":
    if check_parking_availability():
        send_sms()
    else:
        print("🔍 Fortsatt utsolgt. Ingen SMS sendt.")

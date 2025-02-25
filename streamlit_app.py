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
BOOKING_URL = "https://aimopark-permit.giantleap.no/embedded-user-shop.html#/shop/select-facility/3007"

def check_parking_availability():
    """Sjekker om parkeringsabonnementet er ledig."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(BOOKING_URL, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Logg hele HTML for debugging (valgfritt, men nyttig)
        with open("page_source.html", "w", encoding="utf-8") as file:
            file.write(soup.prettify())

        # 1️⃣ Sjekk etter "Utsolgt" i spesifikke elementer
        sold_out_element = soup.find("i18n", class_="negative")
        if sold_out_element and "Utsolgt" in sold_out_element.get_text(strip=True):
            print("🚧 Parkeringsplassen er fortsatt utsolgt.")
            return False

        # 2️⃣ Sjekk om "Utsolgt" finnes i hele nettsidens tekst
        if "Utsolgt" in soup.get_text():
            print("🚧 Parkeringsplassen er fortsatt utsolgt.")
            return False

        # 3️⃣ Hvis vi ikke fant "Utsolgt", antar vi at den er ledig
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

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client

# Twilio konfigurasjon (Bruk secrets eller .env for sikkerhet)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBER = "+4797655108"  # Bytt ut med ditt nummer

# URL til booking-siden
BOOKING_URL = "https://aimopark-permit.giantleap.no/embedded-user-shop.html#/shop/select-facility/3007"

# Oppsett av Chrome WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Kjører i bakgrunnen uten å åpne nettleseren
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def check_parking_availability():
    """Bruker Selenium for å sjekke om parkering er ledig."""
    try:
        driver.get(BOOKING_URL)
        time.sleep(5)  # Vent på at siden laster inn

        # Finn hele nettside-teksten
        page_text = driver.page_source

        if "Utsolgt" in page_text:
            print("🚧 Parkeringsplassen er fortsatt utsolgt.")
            return False
        else:
            print("🎉 Parkeringsplassen er LEDIG!")
            return True

    except Exception as e:
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

    driver.quit()  # Lukk nettleseren

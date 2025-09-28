#!/usr/bin/env python3
import os
import requests

def send_simple_message():
    return requests.post(
        "https://api.mailgun.net/v3/sandboxf90562952520491fad01367504bb7bb4.mailgun.org/messages",
        auth=("api", os.getenv('MAILGUN_API_KEY', 'API_KEY')),
        data={"from": "Mailgun Sandbox <postmaster@sandboxf90562952520491fad01367504bb7bb4.mailgun.org>",
            "to": "Panayiotis Papallis <panayiotis@papallis.com>",
            "subject": "Hello Panayiotis Papallis",
            "text": "Congratulations Panayiotis Papallis, you just sent an email with Mailgun! You are truly awesome!"})

if __name__ == "__main__":
    print("Sending test email...")
    print(f"Using API key: {os.getenv('MAILGUN_API_KEY', 'NOT_SET')}")
    
    response = send_simple_message()
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Email sent successfully!")
    else:
        print("❌ Email sending failed!")
#!/usr/bin/env python3
import os

print("=== Environment Variables Debug ===")
print(f"MAILGUN_DOMAIN: {os.getenv('MAILGUN_DOMAIN', 'NOT_SET')}")
print(f"MAILGUN_API_KEY: {os.getenv('MAILGUN_API_KEY', 'NOT_SET')}")
print(f"FROM_EMAIL: {os.getenv('FROM_EMAIL', 'NOT_SET')}")
print(f"DATABASE_PATH: {os.getenv('DATABASE_PATH', 'NOT_SET')}")
print(f"HOST: {os.getenv('HOST', 'NOT_SET')}")
print(f"SHOW_BROWSER: {os.getenv('SHOW_BROWSER', 'NOT_SET')}")

# Test the same configuration as main.py
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL', f'noreply@{MAILGUN_DOMAIN}' if MAILGUN_DOMAIN else 'noreply@example.com')

print("\n=== Processed Configuration ===")
print(f"MAILGUN_DOMAIN: {MAILGUN_DOMAIN}")
print(f"MAILGUN_API_KEY: {MAILGUN_API_KEY}")
print(f"FROM_EMAIL: {FROM_EMAIL}")

if not MAILGUN_DOMAIN or not MAILGUN_API_KEY:
    print("\n❌ Mailgun configuration incomplete!")
    print("This is why emails are not being sent.")
else:
    print("\n✅ Mailgun configuration looks good!")
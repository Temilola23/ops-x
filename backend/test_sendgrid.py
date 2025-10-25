"""
Quick test to verify SendGrid is working
"""
import os
import sys
from pathlib import Path

# Load env
env_file = Path(__file__).parent.parent / "scripts" / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

from integrations.email_service import send_otp_email

# Test email
print("\n" + "="*60)
print("Testing SendGrid Email Service")
print("="*60)

result = send_otp_email(
    to_email="declanfortune5@gmail.com",
    otp="123456",
    name="Test User"
)

if result:
    print("\n✅ SUCCESS! Email sent via SendGrid")
else:
    print("\n❌ FAILED! Check console output above")

print("="*60 + "\n")


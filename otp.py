# otp.py
import secrets

def generate_otp():
    return f"{secrets.randbelow(1000000):06d}"

def create_and_send_otp(recipient_email, filename):
    otp = generate_otp()
    
    # Simulated email sending
    print(f"\n📧 Simulated Email to {recipient_email}:")
    print(f"Subject: Your HexaLock OTP")
    print(f"OTP for file '{filename}': {otp}\n")

    # Return (otp, sent_status)
    return otp, True

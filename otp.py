import secrets
import time

# ---------------- CONFIG ----------------
OTP_LENGTH = 6
OTP_VALIDITY_SECONDS = 300  # 5 minutes
OTP_COOLDOWN_SECONDS = 30   # prevent spam

# Track last OTP request time per user (basic in-memory control)
_last_otp_request = {}


# ---------------- OTP GENERATION ----------------
def generate_otp() -> str:
    """
    Generate a secure numeric OTP of fixed length.
    """
    return f"{secrets.randbelow(10**OTP_LENGTH):0{OTP_LENGTH}d}"


# ---------------- COOLDOWN CHECK ----------------
def can_generate_otp(user: str) -> bool:
    """
    Prevent OTP spam by enforcing cooldown.
    """
    now = time.time()

    if user in _last_otp_request:
        if now - _last_otp_request[user] < OTP_COOLDOWN_SECONDS:
            return False

    _last_otp_request[user] = now
    return True


# ---------------- OTP CREATION + SEND ----------------
def create_and_send_otp(recipient_email: str, filename: str):
    """
    Generate OTP and simulate sending via email.
    Returns (otp, sent_status)
    """

    # Basic cooldown protection
    if not can_generate_otp(recipient_email):
        print("⏳ Please wait before requesting another OTP.")
        return None, False

    otp = generate_otp()

    try:
        # Simulated email sending
        print(f"\n📧 Simulated Email to {recipient_email}:")
        print("Subject: Your HexaLock OTP")
        print(f"OTP for file '{filename}': {otp}")
        print(f"Valid for {OTP_VALIDITY_SECONDS // 60} minutes\n")

        sent = True

    except Exception:
        sent = False

    return otp, sent

import random

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(to_email: str, otp: str) -> bool:
    # Print OTP directly in the VS Code terminal for seamless testing
    print("\n" + "="*40)
    print(f"🔑 [DEV OTP] To: {to_email}")
    print(f"🔑 [DEV OTP] Code: {otp}")
    print("="*40 + "\n")
    return True

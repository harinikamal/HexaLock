# main.py
#!/usr/bin/env python3
import os
import time
import getpass
from datetime import datetime
from encryption import encrypt_file, decrypt_file
from db import init_db, log_access, store_otp, validate_and_consume_otp, get_recent_logs
from otp import generate_otp, create_and_send_otp

def format_timestamp(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

def create_test_file():
    content = """This is a test file for HexaLock encryption demo.
You can replace this content with your own text."""
    with open("test_file.txt", "w") as f:
        f.write(content)
    print("✓ Created test_file.txt")
    log_access("test_file.txt", "created", "demo")

def main():
    print("🔒 HexaLock - Secure File Encryption System")
    print("=" * 50)

    init_db()
    print("✓ Database initialized")

    if not os.path.exists("test_file.txt"):
        create_test_file()

    while True:
        print("\nOptions:")
        print("1. Encrypt a file")
        print("2. Decrypt a file")
        print("3. Demo encrypt/decrypt cycle")
        print("4. Generate OTP")
        print("5. Email OTP")
        print("6. Decrypt with OTP")
        print("7. View logs")
        print("8. Exit")

        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            file_path = input("Enter file path to encrypt: ").strip()
            if not os.path.exists(file_path):
                print("❌ File not found")
                continue
            password = getpass.getpass("Enter password: ")
            user = input("Enter your name/ID: ") or "unknown"
            try:
                encrypted = encrypt_file(file_path, password)
                log_access(os.path.basename(file_path), "encrypted", user)
                print(f"✓ File encrypted: {encrypted}")
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "2":
            file_path = input("Enter encrypted file path: ").strip()
            if not os.path.exists(file_path):
                print("❌ File not found")
                continue
            password = getpass.getpass("Enter password: ")
            user = input("Enter your name/ID: ") or "unknown"
            try:
                decrypted = decrypt_file(file_path, password)
                log_access(os.path.basename(file_path), "decrypted", user)
                print(f"✓ File decrypted: {decrypted}")
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "3":
            password = getpass.getpass("Enter password for demo: ")
            try:
                with open("test_file.txt") as f:
                    print("\n📝 Original content:")
                    print(f.read())
                encrypted = encrypt_file("test_file.txt", password)
                log_access("test_file.txt", "demo_encrypted", "demo")
                decrypted = decrypt_file(encrypted, password, "decrypted_test.txt")
                log_access("test_file.txt", "demo_decrypted", "demo")
                with open(decrypted) as f:
                    print("\n📝 Decrypted content:")
                    print(f.read())
                os.remove(encrypted)
                os.remove(decrypted)
                print("✓ Demo completed")
            except Exception as e:
                print(f"❌ Demo failed: {e}")

        elif choice == "4":
            recipient = input("Enter recipient name/ID: ")
            filename = input("Enter filename for OTP: ")
            if not recipient or not filename:
                print("❌ Missing info")
                continue
            otp = generate_otp()
            ttl = int(input("Enter OTP TTL in seconds (default 300): ") or 300)
            store_otp(otp, recipient, filename, ttl)
            log_access(filename, "otp_generated", recipient)
            print(f"✓ OTP: {otp} (valid until {format_timestamp(time.time() + ttl)})")

        elif choice == "5":
            email = input("Enter recipient email: ")
            filename = input("Enter filename: ")
            if not email or not filename:
                print("❌ Missing info")
                continue
            otp, sent = create_and_send_otp(email, filename)
            ttl = 300
            store_otp(otp, email, filename, ttl)
            log_access(filename, "otp_sent", email)
            print(f"✓ OTP valid until {format_timestamp(time.time() + ttl)}")

        elif choice == "6":
            file_path = input("Enter encrypted file path: ").strip()
            if not os.path.exists(file_path):
                print("❌ File not found")
                continue
            recipient = input("Enter your name/ID: ")
            filename = input("Enter original filename: ")
            otp = input("Enter OTP: ")
            if validate_and_consume_otp(otp, recipient, filename):
                password = getpass.getpass("Enter decryption password: ")
                try:
                    decrypted = decrypt_file(file_path, password)
                    log_access(filename, "otp_decrypt_success", recipient)
                    print(f"✓ File decrypted: {decrypted}")
                except Exception as e:
                    log_access(filename, "otp_decrypt_fail", recipient)
                    print(f"❌ Error: {e}")
            else:
                print("❌ Invalid or expired OTP")

        elif choice == "7":
            logs = get_recent_logs()
            print("\n📋 Access Logs")
            print("-" * 50)
            for filename, action, user, ts in logs:
                print(f"{format_timestamp(ts)} | {user:10} | {action:15} | {filename}")

        elif choice == "8":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()

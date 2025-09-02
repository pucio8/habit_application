import secrets

# Generate secure 32-byte key in hexadecimal format (64 characters)
secret_key = secrets.token_hex(32)

print("Secret key:")
print(secret_key)
print("\nCopy and paste this key to your .env file")
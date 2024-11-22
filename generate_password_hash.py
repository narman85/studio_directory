from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

# Load current environment variables
load_dotenv()

# Get the plain password from environment
password = os.getenv('ADMIN_PASSWORD')
if not password:
    print("Error: ADMIN_PASSWORD not found in .env file")
    exit(1)

# Generate password hash
password_hash = generate_password_hash(password)
print(f"\nGenerated password hash: {password_hash}\n")
print("Add this line to your .env file:")
print(f"ADMIN_PASSWORD_HASH={password_hash}")

import subprocess
import os
import hashlib
from paperbase import config
from paperbase import __file__ as base_file

AUTH_EXEC = os.path.join(os.path.dirname(base_file), "addon", "auth_handler.exe")


def createUser(email, password):
    password = encryptSHA(password)
    print("Running:", [AUTH_EXEC, "createUser", email, password, config.UID])
    print("CWD:", os.getcwd())
    result = subprocess.run(
        [AUTH_EXEC, "createUser", email, password, config.UID],
        capture_output=True, text=True
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    return result.stdout

def signInUser(email, password):
    password = encryptSHA(password)
    if not config.UID:
        print("Project ID not connected. Use config.connect(project_id) first.")
        return
    try:
        result = subprocess.run(
            [AUTH_EXEC, "signInUser", email, password, config.UID],
            capture_output=True,
            encoding='utf-8',
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error signing in: {e.stderr}")

def deleteUser(email):
    password = encryptSHA(password)
    if not config.UID:
        print("Project ID not connected. Use config.connect(project_id) first.")
        return
    try:
        result = subprocess.run(
            [AUTH_EXEC, "deleteUser", email, config.UID],
            capture_output=True,
            encoding='utf-8',
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error deleting user: {e.stderr}")


def encryptSHA(input_string):
    """Encrypts a string using SHA-256."""
    sha_signature = hashlib.sha256(input_string.encode()).hexdigest()
    return sha_signature

def decryptSHA(encrypted_string):
    """SHA-256 is a one-way encryption algorithm and cannot be decrypted."""
    raise NotImplementedError("SHA-256 is a one-way hash function and cannot be decrypted.")
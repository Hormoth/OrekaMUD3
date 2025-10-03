import os
import json
import hashlib

PLAYER_DIR = os.path.join(os.path.dirname(__file__), 'oreka_mud', 'data', 'players')

def hash_password(password):
    if not password:
        return None
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def migrate_player_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # If password exists and hashed_password does not, hash and migrate
    password = data.get('password')
    hashed_password = data.get('hashed_password')

    if password and not hashed_password:
        data['hashed_password'] = hash_password(password)
        print(f"Migrated password for {filepath}")

    # Remove plain text password field
    if 'password' in data:
        del data['password']

    # Save back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    for filename in os.listdir(PLAYER_DIR):
        if filename.endswith('.json'):
            migrate_player_file(os.path.join(PLAYER_DIR, filename))

if __name__ == '__main__':
    main()
import os
import json
import hashlib

def update_passwords(players_dir):
    for fname in os.listdir(players_dir):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(players_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                print(f"Skipping corrupt file: {fname}")
                continue
        # If file is a list, use first element
        if isinstance(data, list):
            data = data[0]
        name = data.get("name", fname.replace(".json", ""))
        print(f"Updating password for: {name}")
        pw = input(f"Enter new password for {name}: ").strip()
        if not pw:
            print("No password entered, skipping.")
            continue
        hashed = hashlib.sha256(pw.encode()).hexdigest()
        data["hashed_password"] = hashed
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {fname} with hashed_password.")

if __name__ == "__main__":
    players_dir = os.path.join("oreka_mud", "data", "players")
    if not os.path.exists(players_dir):
        print("Players directory not found!")
    else:
        update_passwords(players_dir)
os.system('python update_player_passwords.py')
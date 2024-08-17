# Automatically unpack XAPK (the new format with multiple apks) then install apks to device.
# not compatible with old xapk that use obb files.
import sys
import subprocess
import zipfile
import tempfile
from pathlib import Path


def check_adb_exists():
    try:
        subprocess.run(['adb', 'version'], check=True, capture_output=True)
        return True
    except FileNotFoundError:
        print("Error: adb is not installed or not found in PATH.")
        return False
    except subprocess.CalledProcessError:
        print("Error: adb command failed.")
        return False


def check_device_connected():
    try:
        result = subprocess.run(
            ['adb', 'devices'], check=True, capture_output=True, text=True
        )
        devices = result.stdout.strip().split('\n')[1:]

        if not any(device.strip() for device in devices):
            print("Error: No devices connected.")
            return False

        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to check connected devices.")
        return False


def main(argv=None):
    if len(argv) < 2:
        print("Syntax: install-xapk-bundle <path_to_xapk_file>")
        sys.exit(1)

    xapk_file = Path(sys.argv[1])

    if not xapk_file.is_file():
        print(f"Error: File '{xapk_file}' does not exist.")
        sys.exit(1)

    if not check_adb_exists():
        sys.exit(1)

    if not check_device_connected():
        sys.exit(1)

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with zipfile.ZipFile(xapk_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            print("Error: Failed to unpack the .xapk file (bad zip file).")
            sys.exit(1)

        temp_path = Path(temp_dir)

        apk_paths = list(temp_path.rglob("*.apk"))

        apk_files = " ".join([apk_path.name for apk_path in apk_paths])

        if apk_paths:
            print(f"Installing {apk_files} to device...")

            result = subprocess.run(
                ['adb', 'install-multiple'] + apk_paths,
                shell=True,
                capture_output=True,
                check=False,
                text=True
            )

            if result.returncode == 0:
                print(result.stdout)
                input('pause...')
            else:
                print(result.stderr)
                print("Error: Failed to install APKs.")
                sys.exit(1)
        else:
            print("Error: No APK files found in the extracted .xapk package.")
            sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)

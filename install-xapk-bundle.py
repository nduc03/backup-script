# Automatically unpack XAPK (the new format with multiple apks) then install apks to device.
# not compatible with old xapk that use obb files.
import sys
import os
import subprocess
import zipfile
import tempfile


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
        print("Error: Please provide the path to the .xapk file.")
        sys.exit(1)

    xapk_file = sys.argv[1]

    if not os.path.isfile(xapk_file):
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

        apk_files = [
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if os.path.isfile(os.path.join(temp_dir, f)) and f.endswith('.apk')
        ]

        if apk_files:
            print(f"Installing {apk_files} to device...")

            try:
                result = subprocess.run(
                    ['adb', 'install-multiple'] + apk_files, shell=True, capture_output=True, check=True)

                if result.returncode == 0:
                    print(result.stdout.decode())
                else:
                    print(result.stderr.decode())
            except subprocess.CalledProcessError as e:
                print(f"Error: Failed to install APKs. {e}")
                sys.exit(1)
        else:
            print("Error: No APK files found in the extracted .xapk package.")
            sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)

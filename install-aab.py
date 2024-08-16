import subprocess
import sys
import re
import tempfile
from pathlib import Path
from getpass import getpass


def set_pwd_manually():
    try:
        pwd = getpass('Enter password: ')
        return pwd
    except Exception:
        print('Error: Cannot set the password manually.')
        sys.exit(-1)


device_spec = Path.home() / 'my-device-spec.json'
if not device_spec.exists():
    print('Error: my-device-spec.json is not found in user home directory')
    sys.exit(1)

keystore_path = Path.home() / 'androidKey'
if not keystore_path.exists():
    print(f'Error: {str(keystore_path)} is not found')
    sys.exit(1)

kjs_path = keystore_path / 'nduc-android-key.jks'
if not kjs_path.exists():
    print(f'Error: {str(kjs_path)} is not found')
    sys.exit(1)

pwd_path = keystore_path / 'nduc-key-and-keystore.pwd'
key_password = None
if not pwd_path.exists():
    print(f'Error: {str(pwd_path)} is not found')
    if input('Do you want to set password manually? (y/n): ').strip().lower() == 'y':
        key_password = set_pwd_manually()
    sys.exit(1)
else:
    key_password = pwd_path.read_text().strip()

KEY_ALIAS = 'nduc'


def main(argv=None):
    if len(argv) < 2:
        print('Syntax: install-aab <path-to-aab-file>')
        sys.exit(1)
    aab_path = Path(argv[1])

    if any(' ' in char for char in str(aab_path)):
        print('Error: The path to the aab file contains spaces. Please move the file to a directory without spaces or rename the file.')
        sys.exit(1)

    if not aab_path.exists():
        print(f'Error: {str(aab_path)} is not exist')
        sys.exit(1)

    with tempfile.TemporaryDirectory() as temp_dir:
        out_path = Path(temp_dir) / 'output.apks'

        bundletool_path = Path(__file__).parent / 'bundletool.jar'
        if not bundletool_path.exists():
            print('Error: bundletool.jar is not found in the same directory as this script. Did you forget to rename it?')
            sys.exit(1)

        convert = subprocess.run([
            'java', '-jar', str(bundletool_path),
            'build-apks',
            f'--bundle={aab_path}',
            f'--output={out_path}',
            f'--device-spec={device_spec}',
            f'--ks={kjs_path}',
            f'--ks-pass=pass:{key_password}',
            F'--ks-key-alias={KEY_ALIAS}'
        ], check=False, capture_output=True, shell=True, text=True)

        if convert.returncode != 0:
            print(convert.stderr)
            print('Error: Failed to convert aab file to apks')
            sys.exit(1)
        print(convert.stdout)

        serial_id_path = Path.home() / 'my-s23-serial-id.txt'
        if not serial_id_path.exists():
            print('Error: my-s23-serial-id.txt is not found in user home directory. Cannot retrieve serial id.')
            sys.exit(1)

        serial_id = serial_id_path.read_text().strip()

        adb_devices = subprocess.run(
            ['adb', 'devices'], check=False, capture_output=True, text=True, shell=True
        )

        if adb_devices.returncode != 0:
            print('Error: Cannot retrieve list of devices. Installation will be aborted.')
            sys.exit(1)

        if serial_id not in re.split('\t|\n', adb_devices.stdout):
            print('Error: ADB failed to connect to my phone.')
            sys.exit(1)

        install = subprocess.run([
            'bundletool',
            'install-apks',
            f'--apks={out_path}',
            f'--device-id={serial_id}'
        ], check=False, capture_output=True, text=True, shell=True)

        if install.returncode != 0:
            print(install.stderr)
            sys.exit(1)
        print(install.stdout)


if __name__ == '__main__':
    main(sys.argv)

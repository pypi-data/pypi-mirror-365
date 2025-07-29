import subprocess
import re

def get_wifi_secrets():
    output = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], encoding='utf-8')
    profiles = re.findall(r"All User Profile\s*:\s(.*)", output)

    wifi_details = []

    for profile in profiles:
        profile = profile.strip().strip('"')
        try:
            profile_info = subprocess.check_output(
                ['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'],
                encoding='utf-8'
            )
            password_match = re.search(r"Key Content\s*:\s(.*)", profile_info)
            password = password_match.group(1).strip() if password_match else None

            wifi_details.append({
                'SSID': profile,
                'Password': password
            })
        except subprocess.CalledProcessError:
            wifi_details.append({
                'SSID': profile,
                'Password': None
            })

    return wifi_details
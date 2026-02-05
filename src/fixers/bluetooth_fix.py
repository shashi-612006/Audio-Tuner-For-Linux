import subprocess
import os
import shutil

class BluetoothFixer:
    def __init__(self, profile):
        self.profile = profile
        self.init = profile.get("init_system", "systemd").lower()
        self.vendor = profile.get("vendor_name", "Unknown")

    def apply_coex_fix(self):
        print(f"[*] Detecting coexistence strategy for {self.vendor}...")

        fix_map = {
            "Realtek": (
                "rtw88_core",
                "# AirTIGHT Bluetooth/WiFi Coex Fix\n"
                "options rtw88_core disable_lps_deep=y\n"
                "options rtw_pci disable_aspm=y\n"
            ),
            "Intel": (
                "iwlwifi",
                "# AirTIGHT Stability Fix\n"
                "options iwlwifi power_save=0\n"
            ),
            "Broadcom": (
                "brcmfmac",
                "# AirTIGHT Stability Fix\n"
                "options brcmfmac roamoff=1\n"
            )
        }

        if self.vendor in fix_map:
            module, config = fix_map[self.vendor]
            self._write_modprobe_conf("airtight_coex.conf", config)
            self._reload_module_if_loaded(module)
        else:
            print(f"[!] No known coex fix for {self.vendor}. Skipping.")


    def restart_bluetooth(self):
        print(f"[*] Restarting Bluetooth via {self.init}...")

        commands = {
            "systemd": ["systemctl", "restart", "bluetooth"],
            "openrc": ["rc-service", "bluetooth", "restart"],
            "runit": ["sv", "restart", "bluetooth"]
        }

        cmd = commands.get(self.init)
        if cmd and shutil.which(cmd[0]):
            try:
                subprocess.run(cmd, check=True)
                print("[✓] Bluetooth service restarted.")
            except subprocess.CalledProcessError:
                print("[!] Failed to restart Bluetooth automatically.")
        else:
            print("[!] Could not detect service manager. Restart manually.")

    # ---------------- Helpers ---------------- #

    def _write_modprobe_conf(self, filename, content):
        path = f"/etc/modprobe.d/{filename}"
        backup = path + ".bak"

        try:
            if os.path.exists(path) and not os.path.exists(backup):
                shutil.copy(path, backup)
                print(f"[*] Backup created: {backup}")

            with open(path, "w") as f:
                f.write(content)

            print(f"[✓] Config written: {path}")
        except PermissionError:
            print("[!] Permission denied. Run AirTIGHT with sudo.")

    def _reload_module_if_loaded(self, module_name):
        try:
            lsmod = subprocess.check_output(["lsmod"], text=True)
            if module_name in lsmod:
                print(f"[*] Reloading {module_name} (network may flicker)...")
                subprocess.run(["modprobe", "-r", module_name], stderr=subprocess.DEVNULL)
                subprocess.run(["modprobe", module_name], stderr=subprocess.DEVNULL)
            else:
                print(f"[!] Module {module_name} not currently loaded. Skipping reload.")
        except Exception:
            print("[!] Could not verify module state.")


if __name__ == "__main__":
    dummy_profile = {"vendor_name": "Realtek", "init_system": "systemd"}
    fixer = BluetoothFixer(dummy_profile)
    fixer.apply_coex_fix()
    fixer.restart_bluetooth()



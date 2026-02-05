import subprocess
import os
import shutil


class BluetoothFixer:
    def __init__(self, profile):
        self.profile = profile
        self.init = profile.get("init_system", "systemd").lower()
        self.vendor = profile.get("vendor_name", "Unknown")
        self.conf_path = "/etc/modprobe.d/airtight_coex.conf"

   
    def apply_coex_fix(self):
        print(f"[*] Evaluating Bluetooth/WiFi coexistence for {self.vendor}...")

        fix_map = {
            "Realtek": (
                "rtw88_core",
                "# AirTIGHT Coexistence Fix\n"
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

        if self.vendor not in fix_map:
            print("[!] No known coexistence tweaks for this chipset.")
            return

        module, config = fix_map[self.vendor]

        if self._config_already_applied(config):
            print("[✓] Coexistence fix already applied. Skipping.")
            return

        self._write_modprobe_conf(config)
        self._reload_module_if_loaded(module)

    

    def restart_bluetooth(self):
        print(f"[*] Restarting Bluetooth service via {self.init}...")

        commands = {
            "systemd": ["systemctl", "restart", "bluetooth"],
            "openrc": ["rc-service", "bluetooth", "restart"],
            "runit": ["sv", "restart", "bluetooth"]
        }

        cmd = commands.get(self.init)
        if cmd and shutil.which(cmd[0]):
            subprocess.run(cmd, stderr=subprocess.DEVNULL)
            print("[✓] Bluetooth service restarted.")
        else:
            print("[!] Could not detect service manager. Restart manually if needed.")

   
    def _config_already_applied(self, new_config):
        """Check if config file already contains our settings."""
        if not os.path.exists(self.conf_path):
            return False

        with open(self.conf_path, "r") as f:
            existing = f.read()
        return new_config.strip() in existing.strip()

    def _write_modprobe_conf(self, content):
        backup = self.conf_path + ".bak"

        try:
            if os.path.exists(self.conf_path) and not os.path.exists(backup):
                shutil.copy(self.conf_path, backup)
                print(f"[*] Backup created: {backup}")

            with open(self.conf_path, "w") as f:
                f.write(content)

            print(f"[✓] Coexistence config written: {self.conf_path}")
        except Exception as e:
            print(f"[!] Failed to write modprobe config: {e}")

    def _reload_module_if_loaded(self, module_name):
        try:
            lsmod = subprocess.check_output(["lsmod"], text=True)
            if module_name in lsmod:
                print(f"[*] Reloading {module_name} (network may flicker)...")
                subprocess.run(["modprobe", "-r", module_name], stderr=subprocess.DEVNULL)
                subprocess.run(["modprobe", module_name], stderr=subprocess.DEVNULL)
            else:
                print(f"[!] Module {module_name} not loaded. Reboot may be required.")
        except Exception:
            print("[!] Could not verify kernel module state.")

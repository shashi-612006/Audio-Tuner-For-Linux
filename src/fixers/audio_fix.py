import subprocess
import os
import shutil


class AudioFixer:
    def __init__(self):
        self.conf_path = "/etc/modprobe.d/airtight_audio.conf"

  

    def disable_power_save(self):
        """Prevents audio controller sleep (fixes pop after silence)."""
        print("[*] Checking audio power-save configuration...")

        config = (
            "# AirTIGHT Audio Stability Fix\n"
            "options snd_hda_intel power_save=0 power_save_controller=N\n"
        )

        if self._config_already_applied(config):
            print("[✓] Audio power-save already disabled.")
            return

        backup = self.conf_path + ".bak"

        try:
            if os.path.exists(self.conf_path) and not os.path.exists(backup):
                shutil.copy(self.conf_path, backup)
                print(f"[*] Backup created: {backup}")

            with open(self.conf_path, "w") as f:
                f.write(config)

            print(f"[✓] Persistent audio fix written: {self.conf_path}")
        except Exception as e:
            print(f"[!] Failed to write audio config: {e}")


    def warm_up_alsa(self):
        """Ensures audio path is active without changing user's volume aggressively."""
        print("[*] Ensuring ALSA channels are active...")

        try:
            
            subprocess.run(["amixer", "sset", "Master", "unmute"], stderr=subprocess.DEVNULL)
            print("[✓] ALSA channels unmuted.")
        except FileNotFoundError:
            print("[!] amixer not found. Skipping ALSA warm-up.")

  

    def apply_all(self):
        self.disable_power_save()
        self.warm_up_alsa()
        print("[*] Audio fixes applied. Reboot recommended for kernel-level changes.")



    def _config_already_applied(self, new_config):
        if not os.path.exists(self.conf_path):
            return False

        with open(self.conf_path, "r") as f:
            existing = f.read()

        return new_config.strip() in existing.strip()

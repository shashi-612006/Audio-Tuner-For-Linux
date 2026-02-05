
import subprocess
import os
import shutil


class AudioFixer:
    def __init__(self):
        self.conf_path = "/etc/modprobe.d/airtight_audio.conf"

    def disable_power_save(self):
        """Prevents audio controller from entering sleep (fixes pop after silence)."""
        print("[*] Applying kernel audio power-save fix...")

        config = (
            "# AirTIGHT Audio Stability Fix\n"
            "options snd_hda_intel power_save=0 power_save_controller=N\n"
        )

        try:
            backup = self.conf_path + ".bak"
            if os.path.exists(self.conf_path) and not os.path.exists(backup):
                shutil.copy(self.conf_path, backup)
                print(f"[*] Backup created: {backup}")

            with open(self.conf_path, "w") as f:
                f.write(config)

            print(f"[✓] Persistent audio fix written: {self.conf_path}")
        except Exception as e:
            print(f"[!] Failed to write kernel config: {e}")


    def warm_up_alsa(self):
        """Ensures mixer is active and unmuted so audio starts instantly."""
        print("[*] Warming up ALSA mixer channels...")

        try:
            subprocess.run(["amixer", "sset", "Master", "unmute"], stderr=subprocess.DEVNULL)
            subprocess.run(["amixer", "sset", "Master", "70%"], stderr=subprocess.DEVNULL)
            print("[✓] ALSA channels active and volume set safely.")
        except FileNotFoundError:
            print("[!] amixer not found. Skipping ALSA warm-up.")


    def apply_all(self):
        self.disable_power_save()
        self.warm_up_alsa()
        print("[*] Audio fixes applied. Reboot recommended for kernel changes.")


if __name__ == "__main__":
    fixer = AudioFixer()
    fixer.apply_all()

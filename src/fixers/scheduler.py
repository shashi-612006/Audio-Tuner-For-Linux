import subprocess
import shutil
import os


class SchedulerOptimizer:
    def __init__(self):
        self.rtkit_available = shutil.which("rtkitctl") is not None
        self.limits_path = "/etc/security/limits.d/airtight_audio.conf"

  

    def boost_audio_priority(self):
        print("[*] Evaluating audio process scheduling...")

        targets = ["pipewire", "wireplumber", "bluetoothd"]

        for proc in targets:
            pids = self._get_pids(proc)
            for pid in pids:
                if not self._already_boosted(pid):
                    if self.rtkit_available:
                        self._apply_rtkit(pid)
                    else:
                        self._manual_boost(pid)
                else:
                    print(f"[✓] PID {pid} already optimized.")

    

    def _apply_rtkit(self, pid):
        try:
            subprocess.run(
                ["rtkitctl", "set-rtprio", pid, "10"],
                stderr=subprocess.DEVNULL
            )
            print(f"[✓] RTKit applied to PID {pid}")
        except Exception:
            print(f"[!] RTKit failed for PID {pid}")

  

    def _manual_boost(self, pid):
        subprocess.run(["renice", "-n", "-12", "-p", pid], stderr=subprocess.DEVNULL)
        subprocess.run(["ionice", "-c", "2", "-n", "0", "-p", pid], stderr=subprocess.DEVNULL)
        print(f"[✓] PID {pid} boosted via renice/ionice")

  

    def apply_rt_limits(self):
        print("[*] Checking PAM real-time limits...")

        config = (
            "# AirTIGHT Real-Time Audio Limits\n"
            "@audio   -   rtprio   95\n"
            "@audio   -   memlock  unlimited\n"
            "@audio   -   nice    -15\n"
        )

        if self._limits_already_set(config):
            print("[✓] RT limits already configured.")
            return

        try:
            with open(self.limits_path, "w") as f:
                f.write(config)
            print("[✓] RT limits written. Re-login required.")
        except Exception as e:
            print(f"[!] Failed to write limits: {e}")

   

    def _get_pids(self, name):
        try:
            return subprocess.check_output(["pgrep", name], text=True).split()
        except subprocess.CalledProcessError:
            return []

    def _already_boosted(self, pid):
        """Checks if process already has high priority."""
        try:
            output = subprocess.check_output(["ps", "-o", "ni=", "-p", pid], text=True)
            nice_value = int(output.strip())
            return nice_value <= -10
        except Exception:
            return False

    def _limits_already_set(self, new_config):
        if not os.path.exists(self.limits_path):
            return False

        with open(self.limits_path, "r") as f:
            existing = f.read()

        return new_config.strip() in existing.strip()

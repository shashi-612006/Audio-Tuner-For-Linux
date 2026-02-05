import subprocess
import shutil

class SchedulerOptimizer:
    def __init__(self):
        self.rtkit_available = shutil.which("rtkitctl") is not None

   

    def boost_audio_priority(self):
        print("[*] Optimizing Audio Process Scheduling...")

        targets = ["pipewire", "wireplumber", "bluetoothd"]

        for proc in targets:
            pids = self._get_pids(proc)
            for pid in pids:
                if self.rtkit_available:
                    self._apply_rtkit(pid)
                else:
                    self._manual_boost(pid)

    def _apply_rtkit(self, pid):
        """Request RT scheduling via RTKit (safe method)."""
        try:
            subprocess.run(
                ["rtkitctl", "set-rtprio", pid, "10"],
                stderr=subprocess.DEVNULL
            )
            print(f"[✓] RTKit applied to PID {pid}")
        except Exception:
            print(f"[!] RTKit failed for PID {pid}")

    def _manual_boost(self, pid):
        """Fallback priority boost (less aggressive)."""
        subprocess.run(["renice", "-n", "-12", "-p", pid], stderr=subprocess.DEVNULL)
        subprocess.run(["ionice", "-c", "2", "-n", "0", "-p", pid], stderr=subprocess.DEVNULL)
        print(f"[✓] PID {pid} boosted via renice/ionice")

    def _get_pids(self, name):
        try:
            return subprocess.check_output(["pgrep", name], text=True).split()
        except subprocess.CalledProcessError:
            return []


    def apply_rt_limits(self):
        print("[*] Writing system RT limits (requires reboot)...")

        limit_config = (
            "# AirTIGHT Real-Time Audio Limits\n"
            "@audio   -   rtprio   95\n"
            "@audio   -   memlock  unlimited\n"
            "@audio   -   nice    -15\n"
        )

        try:
            with open("/etc/security/limits.d/airtight_audio.conf", "w") as f:
                f.write(limit_config)
            print("[✓] RT limits written. Re-login required.")
        except Exception as e:
            print(f"[!] Failed to write limits: {e}")


if __name__ == "__main__":
    sched = SchedulerOptimizer()
    sched.apply_rt_limits()
    sched.boost_audio_priority()

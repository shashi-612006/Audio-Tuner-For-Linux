import subprocess
import time
import sys

try:
    import psutil
except ImportError:
    print("[!] psutil not found. Please run: pip install psutil")
    sys.exit(1)


class PerformanceMonitor:
    def __init__(self):
        self.last_xrun_count = self.get_xrun_total()

    def get_xrun_total(self):
        """Fetches total ERR count from PipeWire's pw-top."""
        try:
            output = subprocess.check_output(
                ["pw-top", "-n", "1"],
                text=True,
                stderr=subprocess.DEVNULL
            )
            total = 0
            for line in output.splitlines():
                parts = line.split()
                if len(parts) > 5 and parts[-1].isdigit():
                    total += int(parts[-1])
            return total
        except Exception:
            return 0


    def get_cpu_load(self):
        return psutil.cpu_percent(interval=0.5)

    def get_ram_usage(self):
        return psutil.virtual_memory().percent

    
    def get_stats(self):
        """Returns a snapshot of system and audio health."""
        cpu = self.get_cpu_load()
        ram = self.get_ram_usage()

        current_xruns = self.get_xrun_total()
        new_xruns = max(0, current_xruns - self.last_xrun_count)
        self.last_xrun_count = current_xruns

        status = "stable"
        if new_xruns > 0:
            status = "xrun_detected"
        elif cpu > 85:
            status = "high_cpu"

        return {
            "timestamp": time.strftime("%H:%M:%S"),
            "cpu": cpu,
            "ram": ram,
            "new_xruns": new_xruns,
            "status": status
        }

if __name__ == "__main__":
    monitor = PerformanceMonitor()

    print("\n" + "═" * 60)
    print("   AirTIGHT LIVE PERFORMANCE TRACKER   ".center(60))
    print("   (Press Ctrl+C to stop)   ".center(60))
    print("═" * 60)
    print(f"{'TIME':<12} | {'CPU %':<10} | {'RAM %':<10} | {'XRUNS':<8} | STATUS")
    print("─" * 60)

    try:
        while True:
            stats = monitor.get_stats()
            alert = ""
            if stats["status"] == "xrun_detected":
                alert = "⚠️ STUTTER"
            elif stats["status"] == "high_cpu":
                alert = "🔥 LOAD"

            print(f"{stats['timestamp']:<12} | {stats['cpu']:<10}% | {stats['ram']:<10}% | {stats['new_xruns']:<8} | {alert}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[*] Monitoring stopped.")

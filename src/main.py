import os
import sys
import time
import subprocess

from src.profiler import Profiler
from src.monitor import PerformanceMonitor
from src.decision_engine import DecisionEngine
from src.fixers.bluetooth_fix import BluetoothFixer
from src.fixers.audio_fix import AudioFixer
from src.fixers.scheduler import SchedulerOptimizer


class AirTIGHT:
    def __init__(self):
        self.profiler = Profiler()
        self.monitor = PerformanceMonitor()
        self.profile = None

    def banner(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print("═" * 60)
        print("   AirTIGHT: UNIVERSAL LINUX AUDIO OPTIMIZER   ".center(60))
        print("   Mode: INTERACTIVE ANALYSIS   ".center(60))
        print("═" * 60)


    def run(self):
        self.banner()

        print("[*] Phase 1: System Audit...")
        self.profile = self.profiler.run_audit()
        self.profiler.print_report()

        print("\n[*] Phase 2: Live Health Check (5 seconds)...")
        print(f"{'TIME':<12} | {'CPU %':<10} | {'XRUNS':<8} | STATUS")
        print("─" * 60)

        captured_stats = []
        for _ in range(5):
            stats = self.monitor.get_stats()
            captured_stats.append(stats)
            alert = "⚠️ XRUN" if stats["new_xruns"] > 0 else "✓"
            print(f"{stats['timestamp']:<12} | {stats['cpu']:<10}% | {stats['new_xruns']:<8} | {alert}")
            time.sleep(1)

        total_xruns = sum(s["new_xruns"] for s in captured_stats)
        peak_cpu = max(s["cpu"] for s in captured_stats)
        status = "high_cpu" if peak_cpu > 80 else "stable"

        engine = DecisionEngine(self.profile, {
            "new_xruns": total_xruns,
            "cpu": peak_cpu,
            "status": status
        })

        plan = engine.analyze()
        print(engine.get_recommendations())

        if plan:
            confirm = input("\n[?] Apply recommended optimizations? (y/n): ")
            if confirm.lower() == 'y':
                self.execute_optimizations(plan)
            else:
                print("[*] No changes applied.")
        else:
            print("\n[✓] No optimizations required. System is AirTIGHT.")


    def execute_optimizations(self, plan):
        
        if os.geteuid() != 0:
            print("\n[!] Root privileges required for system/kernel tweaks.")
            print("[*] Re-running with sudo...")
            os.execvp("sudo", ["sudo", sys.executable] + sys.argv)

        for action in plan:
            print(f"\n[⚡] Executing: {action.replace('_', ' ')}...")

            if action == "APPLY_RT_SCHEDULER_BOOST":
                sched = SchedulerOptimizer()
                sched.apply_rt_limits()
                sched.boost_audio_priority()

            elif action == "APPLY_BLUETOOTH_COEX_FIX":
                bt = BluetoothFixer(self.profile)
                bt.apply_coex_fix()
                bt.restart_bluetooth()

            elif action == "DISABLE_AUDIO_POWER_SAVE":
                audio = AudioFixer()
                audio.apply_all()

        print("\n" + "═" * 60)
        print("   OPTIMIZATION COMPLETE   ".center(60))
        print("   Reboot recommended for kernel-level changes   ".center(60))
        print("═" * 60)



if __name__ == "__main__":
    try:
        app = AirTIGHT()
        app.run()
    except KeyboardInterrupt:
        print("\n\n[*] AirTIGHT: Session Terminated.")

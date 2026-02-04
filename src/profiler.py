import subprocess
import os
import sys
import shutil
import platform

class Profiler:
    def __init__(self):
        self.ensure_root()
      
        self.vendors = {
            "10ec": "Realtek",
            "8086": "Intel",
            "14c3": "MediaTek",
            "168c": "Qualcomm",
            "14e4": "Broadcom"
        }
        
        self.profile = {
            "init_system": "Unknown",
            "vendor_name": "Unknown",
            "chip_id": "Unknown",
            "distro": self.get_distro(),
            "missing_deps": []
        }

    def ensure_root(self):
        """Restarts the script with sudo if not already root."""
        if os.geteuid() != 0:
            print("[*] AirTIGHT requires root privileges. Escalating...")
            try:
                os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
            except Exception as e:
                print(f"[!] Escalation failed: {e}")
                sys.exit(1)

    def get_distro(self):
        try:
            return subprocess.check_output(["lsb_release", "-sd"], text=True).strip()
        except:
            return platform.system()

    def detect_init(self):
        """Detects the init system for cross-distro service management."""
        if shutil.which("systemctl"): self.profile["init_system"] = "Systemd"
        elif shutil.which("rc-service"): self.profile["init_system"] = "OpenRC"
        elif shutil.which("sv"): self.profile["init_system"] = "Runit"
        return self.profile["init_system"]

    def check_dependencies(self):
        """Checks for system binaries and python libs."""
        deps = {
            "lspci": "pciutils",
            "pw-top": "pipewire",
            "bluetoothctl": "bluez"
        }
        for cmd, pkg in deps.items():
            if not shutil.which(cmd):
                self.profile["missing_deps"].append(pkg)
        
        try:
            import psutil
        except ImportError:
            self.profile["missing_deps"].append("python3-psutil")

    def detect_hardware(self):
        """Prioritizes Network/Wireless controller detection."""
        try:
            output = subprocess.check_output(["lspci", "-nn"], text=True)
            for line in output.splitlines():
                if "Network" in line or "Wireless" in line:
                    for vid, name in self.vendors.items():
                        if vid in line:
                            self.profile["vendor_name"] = name
                            self.profile["chip_id"] = line.strip()
                            return
            self.profile["vendor_name"] = "Generic/Not Found"
        except Exception as e:
            self.profile["vendor_name"] = f"Error: {e}"

    def get_install_hint(self):
        missing = self.profile["missing_deps"]
        if not missing: return None
        
        if shutil.which("apt"): return f"sudo apt install {' '.join(missing)}"
        if shutil.which("pacman"): return f"sudo pacman -S {' '.join(missing)}"
        if shutil.which("dnf"): return f"sudo dnf install {' '.join(missing)}"
        return "Please install missing packages manually."

    def run_audit(self):
        self.detect_init()
        self.detect_hardware()
        self.check_dependencies()
        
        print("\n" + "═"*50)
        print("   AirTIGHT UNIVERSAL AUDIT   ".center(50))
        print("═"*50)
        print(f"[*] OS Distro    : {self.profile['distro']}")
        print(f"[*] Init System  : {self.profile['init_system']}")
        print(f"[*] Chip Vendor  : {self.profile['vendor_name']}")
        print(f"[*] Device ID    : {self.profile['chip_id'][:45]}...")
        print("─"*50)
        
        if self.profile["missing_deps"]:
            print(f"[!] Missing: {', '.join(self.profile['missing_deps'])}")
            print(f"[?] Run: {self.get_install_hint()}")
        else:
            print("[✓] System Environment: READY")
        print("═"*50 + "\n")

if __name__ == "__main__":
    p = Profiler()
    p.run_audit()

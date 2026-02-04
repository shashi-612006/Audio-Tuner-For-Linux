import subprocess
import shutil
import platform


class Profiler:
    def __init__(self):
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
            "audio_server": "Unknown",
            "missing_deps": []
        }

   

    def get_distro(self):
        try:
            return subprocess.check_output(["lsb_release", "-sd"], text=True).strip()
        except Exception:
            return platform.system()

    def detect_init(self):
        try:
            init = subprocess.check_output(
                ["ps", "-p", "1", "-o", "comm="],
                text=True
            ).strip()
            self.profile["init_system"] = init
        except Exception:
            pass
        return self.profile["init_system"]

    

    def detect_audio_server(self):
        try:
            output = subprocess.check_output(["ps", "-A"], text=True).lower()
            if "pipewire" in output:
                self.profile["audio_server"] = "PipeWire"
            elif "pulseaudio" in output:
                self.profile["audio_server"] = "PulseAudio (Legacy)"
            else:
                self.profile["audio_server"] = "ALSA/Unknown"
        except Exception:
            self.profile["audio_server"] = "Unknown"

    def get_upgrade_command(self):
        distro_cmds = {
            "apt": "sudo apt update && sudo apt install pipewire-audio wireplumber",
            "pacman": "sudo pacman -S pipewire-pulse pipewire-alsa pipewire-jack wireplumber",
            "dnf": "sudo dnf swap pulseaudio pipewire-pulseaudio --allowerasing"
        }

        for manager, cmd in distro_cmds.items():
            if shutil.which(manager):
                return cmd
        return "Manual installation of PipeWire recommended."

    

    def check_dependencies(self):
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

    def get_install_hint(self):
        missing = self.profile["missing_deps"]
        if not missing:
            return None

        if shutil.which("apt"):
            return f"sudo apt install {' '.join(missing)}"
        if shutil.which("pacman"):
            return f"sudo pacman -S {' '.join(missing)}"
        if shutil.which("dnf"):
            return f"sudo dnf install {' '.join(missing)}"

        return "Please install missing packages manually."

    

    def detect_hardware(self):
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

   

    def run_audit(self):
        self.detect_init()
        self.detect_audio_server()
        self.detect_hardware()
        self.check_dependencies()
        return self.profile

    
    def print_report(self):
        chip = self.profile["chip_id"]
        chip_display = chip[:45] + "..." if len(chip) > 45 else chip

        print("\n" + "═" * 50)
        print("   AirTIGHT UNIVERSAL AUDIT   ".center(50))
        print("═" * 50)
        print(f"[*] OS Distro    : {self.profile['distro']}")
        print(f"[*] Init System  : {self.profile['init_system']}")
        print(f"[*] Audio Server : {self.profile['audio_server']}")
        print(f"[*] Chip Vendor  : {self.profile['vendor_name']}")
        print(f"[*] Device ID    : {chip_display}")
        print("─" * 50)

        if self.profile["audio_server"] != "PipeWire":
            print("[!] PipeWire not detected!")
            print(f"[?] Suggested Fix: {self.get_upgrade_command()}")

        if self.profile["missing_deps"]:
            print(f"[!] Missing: {', '.join(self.profile['missing_deps'])}")
            print(f"[?] Run: {self.get_install_hint()}")
        else:
            print("[✓] System Environment: READY")

        print("═" * 50 + "\n")


if __name__ == "__main__":
    profiler = Profiler()
    profiler.run_audit()
    profiler.print_report()

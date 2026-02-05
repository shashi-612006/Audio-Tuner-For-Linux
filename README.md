# 🎧 AirTIGHT – Linux Audio Stability Optimizer

AirTIGHT is a smart system tool that automatically detects and fixes common causes of Bluetooth audio stutter, pops, and latency issues on Linux.

It analyzes your hardware, monitors real-time performance, and applies safe system-level optimizations to keep your audio smooth — even under heavy CPU or Wi-Fi load.

# 🚀 What Problems Does AirTIGHT Fix?
Issue	Cause	AirTIGHT Solution
Bluetooth audio stutter	Wi-Fi / Bluetooth antenna conflict	Tunes driver coexistence settings
Audio crackle / pop after silence	Audio device power saving	Disables aggressive audio sleep
Stutter during heavy load	CPU scheduler interference	Boosts audio process priority
Random glitches	Poor default system tuning	Applies adaptive optimizations

# 🧠 How It Works

System Audit
Detects Linux distro, init system, chipset vendor, and audio stack.

Live Monitoring
Watches CPU load and PipeWire XRUNs (audio buffer underruns).

Decision Engine
Determines the most likely cause of instability.

Targeted Fixes
Applies only the necessary system optimizations.

# 🛠 Installation
git clone https://github.com/shashi-612006/Audio-Tuner-For-Linux.git
cd Audio-Tuner-For-Linux
sudo bash setup.sh


After installation, run:

airtight

# ⚙️ What the Installer Does

✔ Installs required dependencies
✔ Places AirTIGHT in /opt/airtight
✔ Creates the airtight command
✔ Detects init system (systemd / OpenRC / runit)
✔ Optionally sets up a background service

# 🖥 Requirements

Linux system with PipeWire audio

Python 3.8+

Bluetooth audio device (for BT optimizations)

Root privileges for system-level tweaks

# 📦 Project Structure
src/
 ├── main.py              # Control loop
 ├── profiler.py          # Hardware & system detection
 ├── monitor.py           # Real-time performance tracking
 ├── decision_engine.py   # Smart optimization logic
 └── fixers/
      ├── bluetooth_fix.py
      ├── audio_fix.py
      └── scheduler.py

# ⚠️ Safety Notes

AirTIGHT only modifies well-known kernel and system parameters used in audio optimization.
All changes are:

Logged

Backed up when possible

Reversible

A reboot may be required for some kernel-level changes.

# 🤝 Contributing

Pull requests and issue reports are welcome!
If you test AirTIGHT on different hardware, your feedback helps improve compatibility.

# 📜 License

MIT License – Free to use and modify.

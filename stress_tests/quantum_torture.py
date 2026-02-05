import subprocess
import time

print("============================================================")
print("   AirTIGHT PIPEWIRE QUANTUM STRESS TEST")
print("============================================================")
print("[!] This will temporarily lower audio buffer size.")
print("[!] Audio may crackle — this is normal during testing.")
print("Press Ctrl+C to restore defaults.\n")

quantum_levels = [128, 96, 64, 48, 32]

def set_quantum(q):
    subprocess.run([
        "pw-metadata", "-n", "settings", "0",
        "clock.force-quantum", str(q)
    ], stderr=subprocess.DEVNULL)

try:
    for q in quantum_levels:
        print(f"[*] Setting quantum to {q} samples...")
        set_quantum(q)
        time.sleep(10)

    print("\n[*] Lowest level reached. Observe audio behavior.")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n[*] Restoring default PipeWire behavior...")
    subprocess.run([
        "pw-metadata", "-n", "settings", "0",
        "clock.force-quantum", "0"
    ])
    print("[✓] Defaults restored.")

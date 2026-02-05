class DecisionEngine:
    def __init__(self, profile, monitor_stats):
        self.profile = profile
        self.stats = monitor_stats
        self.plan = []

    
    def analyze(self):
        xruns = self.stats.get("new_xruns", 0)
        cpu = self.stats.get("cpu", 0)
        status = self.stats.get("status", "stable")
        vendor = self.profile.get("vendor_name", "")
        audio_server = self.profile.get("audio_server", "").lower()

        
        if cpu > 80 or status == "high_cpu":
            self.plan.append("APPLY_RT_SCHEDULER_BOOST")

      
        if xruns > 0 and cpu < 60:
            if vendor in ["Realtek", "Intel", "Broadcom"]:
                self.plan.append("APPLY_BLUETOOTH_COEX_FIX")

       
        if xruns > 0 and "pipewire" in audio_server:
            self.plan.append("DISABLE_AUDIO_POWER_SAVE")

        return self._prioritized_unique_plan()

    

    def _prioritized_unique_plan(self):
        """Removes duplicates and enforces safe execution order."""

        priority_order = [
            "APPLY_RT_SCHEDULER_BOOST",   
            "APPLY_BLUETOOTH_COEX_FIX",   
            "DISABLE_AUDIO_POWER_SAVE"   
        ]

        return [action for action in priority_order if action in self.plan]

   

    def get_recommendations(self):
        plan = self.analyze()

        if not plan:
            return "[✓] System is stable. No optimization required."

        report = ["\n[!] AirTIGHT Decision Engine Recommendations:"]
        for action in plan:
            report.append(f"  → {action.replace('_', ' ')}")

        return "\n".join(report)

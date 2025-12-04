# themes.py
import re

class ThemeExtractor:
    """Rule-based keyword theming."""

    THEMES = {
        "Account Access Issues": [
            "login", "logout", "pin", "password", "otp",
            "fingerprint", "authentication", "session", "access"
        ],
        "Transaction Performance": [
            "transaction", "payment", "transfer", "bill", "delay", "money", "lag"
            "recharge", "airtime", "balance", "deduct", "deposit", "withdraw", "failed"
        ],
        "User Interface & Experience": [
            "ui", "design", "interface", "easy", "user", "friendly", "good", "convenient"
            "experience", "smooth", "simple", "layout", "beautiful", "wow", "amazing"

        ],
        "Customer Support": [
            "support", "help", "service", "customer care", "assist", "assistance", "contact"
        ],
        "Bugs & Crashes": [
            "error", "crash", "lag", "bug", "fail", "failed", "issue", "bad"
            "problem", "stuck", "glitch", "freeze", "slow", "not",
        ],
    }

    def assign_theme(self, text):
        text = str(text).lower()
        assigned = []

        for theme, keywords in self.THEMES.items():
            if any(re.search(rf"\b{k}\b", text) for k in keywords):
                assigned.append(theme)

        return assigned if assigned else ["Other"]

    def apply(self, df, text_col="review"):
        df["identified_theme"] = df[text_col].apply(self.assign_theme)
        return df

"""
Daily Forex Fundamentals + Technicals Playbook App
----------------------------------------------------
A simple daily-use companion app: a morning checklist, a per-currency
fundamental bias scorecard, and a freeform notes/journal tab.

Data is stored locally on-device with Kivy's JsonStore, so it works
fully offline and persists between sessions.
"""

import datetime

from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

APP_TITLE = "Forex Fundamentals"

CHECKLIST_ITEMS = [
    ("cal", "Checked economic calendar for today + tomorrow, flagged red events"),
    ("overlap", "Noted which pairs have overlapping/simultaneous releases"),
    ("review48", "Reviewed last 48h of data for each currency I trade"),
    ("bias", "Updated bullish/neutral/bearish tag for each currency"),
    ("levels", "Marked key technical levels before high-impact release"),
    ("agree", "Identified where fundamentals & technicals agree (A+ setups)"),
    ("conflict", "Identified where they conflict (my caution list today)"),
    ("sizing", "Set position sizing plan for any news windows today"),
]

CURRENCIES = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"]

BIAS_CYCLE = ["neutral", "bullish", "bearish"]

BIAS_COLORS = {
    "neutral": (0.55, 0.55, 0.55, 1),
    "bullish": (0.20, 0.62, 0.32, 1),
    "bearish": (0.75, 0.24, 0.24, 1),
}

GUIDE_TEXT = (
    "EVENT-DAY PLAYBOOK\n\n"
    "BEFORE (30-60 min prior)\n"
    "- Mark key technical levels now, before volatility hits.\n"
    "- Note consensus vs previous so you can classify the outcome instantly.\n"
    "- Reduce size or avoid new trades on the affected pair.\n"
    "- Decide now whether to hold or step aside on open trades.\n\n"
    "DURING (first 1-5 minutes)\n"
    "- Expect an algo reaction to the headline number, often followed by\n"
    "  a partial reversal once details/revisions are digested.\n"
    "- Don't chase the first spike. Wait for a candle close to confirm.\n"
    "- If the print sharply contradicts your bias, update your bias --\n"
    "  don't fight it.\n\n"
    "AFTER (rest of session)\n"
    "- Look for a retest of a key level with the new info priced in.\n"
    "- Reassess your scorecard if the data meaningfully shifted the story.\n\n"
    "ALIGNING FUNDAMENTALS WITH TECHNICALS\n"
    "- Bias bullish + setup bullish -> highest conviction, full plan size.\n"
    "- Bias bullish + setup bearish -> caution, reduce size if taken at all.\n"
    "- Bias neutral + clean setup -> trade the technicals, expect more chop.\n"
    "- Bias and technicals flatly disagree -> warning sign, re-check your\n"
    "  calendar before trading either direction.\n"
)


def today_str():
    return datetime.date.today().isoformat()


class ForexApp(App):
    title = APP_TITLE

    def build(self):
        self.store = JsonStore(self.user_data_dir + "/forex_data.json")
        self._roll_day_if_needed()

        root = TabbedPanel(do_default_tab=False)

        root.add_widget(self._build_checklist_tab())
        root.add_widget(self._build_bias_tab())
        root.add_widget(self._build_notes_tab())
        root.add_widget(self._build_guide_tab())

        return root

    # ---------- daily rollover ----------

    def _roll_day_if_needed(self):
        today = today_str()

        if not self.store.exists("meta"):
            self.store.put("meta", date=today, streak=0)
            self.store.put("checklist", **{k: False for k, _ in CHECKLIST_ITEMS})
            self.store.put("bias", **{c: "neutral" for c in CURRENCIES})
            self.store.put("notes", text="")
            return

        meta = self.store.get("meta")
        if meta["date"] == today:
            return

        checklist = self.store.get("checklist") if self.store.exists("checklist") else {}
        all_done = all(checklist.get(k, False) for k, _ in CHECKLIST_ITEMS)
        new_streak = meta.get("streak", 0) + 1 if all_done else 0

        self.store.put("meta", date=today, streak=new_streak)
        self.store.put("checklist", **{k: False for k, _ in CHECKLIST_ITEMS})
        self.store.put("bias", **{c: "neutral" for c in CURRENCIES})
        # Notes are left as-is; it doubles as a running journal.

    # ---------- checklist tab ----------

    def _build_checklist_tab(self):
        tab = TabbedPanelItem(text="Checklist")
        outer = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        streak = self.store.get("meta").get("streak", 0)
        header = Label(
            text=f"Streak: {streak} day(s) fully completed",
            size_hint_y=None,
            height=dp(28),
        )
        outer.add_widget(header)

        self.progress = ProgressBar(max=len(CHECKLIST_ITEMS), size_hint_y=None, height=dp(18))
        outer.add_widget(self.progress)
        self.progress_label = Label(text="", size_hint_y=None, height=dp(24))
        outer.add_widget(self.progress_label)

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(6))
        grid.bind(minimum_height=grid.setter("height"))

        checklist_data = self.store.get("checklist")
        self._checkboxes = {}

        for key, text in CHECKLIST_ITEMS:
            row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))
            cb = CheckBox(active=checklist_data.get(key, False), size_hint_x=None, width=dp(40))
            cb.bind(active=self._make_checklist_handler(key))
            lbl = Label(text=text, halign="left", valign="middle", text_size=(dp(240), None))
            row.add_widget(cb)
            row.add_widget(lbl)
            grid.add_widget(row)
            self._checkboxes[key] = cb

        scroll.add_widget(grid)
        outer.add_widget(scroll)
        tab.add_widget(outer)

        self._refresh_progress()
        return tab

    def _make_checklist_handler(self, key):
        def handler(checkbox, value):
            checklist = self.store.get("checklist")
            checklist[key] = value
            self.store.put("checklist", **checklist)
            self._refresh_progress()
        return handler

    def _refresh_progress(self):
        checklist = self.store.get("checklist")
        done = sum(1 for k, _ in CHECKLIST_ITEMS if checklist.get(k, False))
        total = len(CHECKLIST_ITEMS)
        self.progress.value = done
        self.progress_label.text = f"{done} / {total} completed today"

    # ---------- bias tab ----------

    def _build_bias_tab(self):
        tab = TabbedPanelItem(text="Bias")
        outer = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        outer.add_widget(Label(
            text="Tap a currency to cycle: neutral -> bullish -> bearish",
            size_hint_y=None,
            height=dp(40),
        ))

        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        bias_data = self.store.get("bias")
        self._bias_buttons = {}

        for currency in CURRENCIES:
            state = bias_data.get(currency, "neutral")
            btn = Button(
                text=f"{currency}\n{state.upper()}",
                size_hint_y=None,
                height=dp(80),
                background_color=BIAS_COLORS[state],
                background_normal="",
            )
            btn.bind(on_release=self._make_bias_handler(currency))
            grid.add_widget(btn)
            self._bias_buttons[currency] = btn

        outer.add_widget(grid)
        tab.add_widget(outer)
        return tab

    def _make_bias_handler(self, currency):
        def handler(button):
            bias_data = self.store.get("bias")
            current = bias_data.get(currency, "neutral")
            next_state = BIAS_CYCLE[(BIAS_CYCLE.index(current) + 1) % len(BIAS_CYCLE)]
            bias_data[currency] = next_state
            self.store.put("bias", **bias_data)
            button.text = f"{currency}\n{next_state.upper()}"
            button.background_color = BIAS_COLORS[next_state]
        return handler

    # ---------- notes tab ----------

    def _build_notes_tab(self):
        tab = TabbedPanelItem(text="Notes")
        outer = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        outer.add_widget(Label(
            text="Daily journal (auto-saves as you type)",
            size_hint_y=None,
            height=dp(28),
        ))

        notes_data = self.store.get("notes")
        self.notes_input = TextInput(
            text=notes_data.get("text", ""),
            multiline=True,
        )
        self.notes_input.bind(text=self._on_notes_changed)
        outer.add_widget(self.notes_input)
        tab.add_widget(outer)
        return tab

    def _on_notes_changed(self, instance, value):
        self.store.put("notes", text=value)

    # ---------- guide tab ----------

    def _build_guide_tab(self):
        tab = TabbedPanelItem(text="Guide")
        scroll = ScrollView()
        lbl = Label(
            text=GUIDE_TEXT,
            size_hint_y=None,
            halign="left",
            valign="top",
            padding=(dp(12), dp(12)),
        )
        lbl.bind(texture_size=lambda instance, size: setattr(lbl, "height", size[1]))
        lbl.bind(width=lambda instance, width: setattr(lbl, "text_size", (width - dp(24), None)))
        scroll.add_widget(lbl)
        tab.add_widget(scroll)
        return tab


if __name__ == "__main__":
    ForexApp().run()

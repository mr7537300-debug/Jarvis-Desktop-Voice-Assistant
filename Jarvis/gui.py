import datetime
import queue
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

try:
    from jarvis import handle_command, load_name, set_assistant_name, takecommand
except ImportError:
    from Jarvis.jarvis import (
        handle_command,
        load_name,
        set_assistant_name,
        takecommand,
    )


BACKGROUND = "#0B1020"
SIDEBAR = "#10182B"
SURFACE = "#151F35"
SURFACE_HOVER = "#1C2943"
ACCENT = "#64E7D2"
TEXT = "#F3F6FC"
MUTED = "#91A0BA"
SUBTLE = "#65738E"


class JarvisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis | Desktop Assistant")
        self.root.geometry("1120x760")
        self.root.minsize(900, 620)
        self.root.configure(bg=BACKGROUND)

        self.events = queue.Queue()
        self.busy = False
        self.online = True

        self._build_layout()
        self._append_message(
            "assistant",
            "Welcome back. I’m {0}, your desktop assistant. "
            "Ask me for the time, a Wikipedia summary, music, a joke, "
            "a screenshot, or to open Google and YouTube.".format(load_name()),
        )
        self.root.after(100, self._poll_events)
        self.root.after(1000, self._update_clock)
        self.input.focus_set()

    def _build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=248)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=SIDEBAR)
        brand.pack(fill="x", padx=22, pady=(25, 28))
        mark = tk.Canvas(
            brand, width=42, height=42, bg=SIDEBAR, highlightthickness=0
        )
        mark.create_oval(2, 2, 40, 40, fill="#183A48", outline=ACCENT, width=1)
        mark.create_text(
            21, 21, text="J", fill=ACCENT, font=("Segoe UI Semibold", 19)
        )
        mark.pack(side="left")
        brand_text = tk.Frame(brand, bg=SIDEBAR)
        brand_text.pack(side="left", padx=(11, 0))
        tk.Label(
            brand_text,
            text="JARVIS",
            fg=TEXT,
            bg=SIDEBAR,
            font=("Segoe UI Semibold", 15),
        ).pack(anchor="w")
        tk.Label(
            brand_text,
            text="DESKTOP ASSISTANT",
            fg=SUBTLE,
            bg=SIDEBAR,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            self.sidebar,
            text="WORKSPACE",
            fg=SUBTLE,
            bg=SIDEBAR,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=22, pady=(0, 10))
        self._sidebar_item("◉", "Assistant", active=True)
        self._sidebar_item("◷", "Quick actions")

        tk.Frame(self.sidebar, bg="#202B41", height=1).pack(
            fill="x", padx=22, pady=22
        )
        tk.Label(
            self.sidebar,
            text="YOUR ASSISTANT",
            fg=SUBTLE,
            bg=SIDEBAR,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=22, pady=(0, 10))
        identity = tk.Frame(self.sidebar, bg="#172239", padx=12, pady=12)
        identity.pack(fill="x", padx=16)
        tk.Label(
            identity,
            text="●",
            fg=ACCENT,
            bg="#172239",
            font=("Segoe UI", 10),
        ).pack(side="left")
        self.name_label = tk.Label(
            identity,
            text=load_name(),
            fg=TEXT,
            bg="#172239",
            font=("Segoe UI Semibold", 10),
        )
        self.name_label.pack(side="left", padx=(8, 0))
        tk.Button(
            self.sidebar,
            text="Change assistant name",
            command=self._change_name,
            anchor="w",
            bg=SIDEBAR,
            fg=MUTED,
            activebackground=SURFACE_HOVER,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9),
            padx=8,
            pady=9,
        ).pack(fill="x", padx=16, pady=(7, 0))

        footer = tk.Frame(self.sidebar, bg=SIDEBAR)
        footer.pack(side="bottom", fill="x", padx=22, pady=22)
        tk.Label(
            footer,
            text="VOICE ASSISTANT",
            fg=TEXT,
            bg=SIDEBAR,
            font=("Segoe UI Semibold", 9),
        ).pack(anchor="w")
        tk.Label(
            footer,
            text="Your desktop, a little closer.",
            fg=SUBTLE,
            bg=SIDEBAR,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(4, 0))

        self.content = tk.Frame(self.root, bg=BACKGROUND)
        self.content.pack(side="left", fill="both", expand=True)
        header = tk.Frame(self.content, bg=BACKGROUND)
        header.pack(fill="x", padx=38, pady=(26, 23))
        tk.Label(
            header,
            text="Assistant",
            fg=TEXT,
            bg=BACKGROUND,
            font=("Segoe UI Semibold", 20),
        ).pack(side="left")
        self.clock = tk.Label(
            header,
            text="",
            fg=MUTED,
            bg=BACKGROUND,
            font=("Segoe UI", 9),
        )
        self.clock.pack(side="right", padx=(0, 18))
        self.status = tk.Label(
            header,
            text="●  READY",
            fg=ACCENT,
            bg="#122A32",
            padx=12,
            pady=7,
            font=("Segoe UI Semibold", 8),
        )
        self.status.pack(side="right")

        body = tk.Frame(self.content, bg=BACKGROUND)
        body.pack(fill="both", expand=True, padx=38)

        tk.Label(
            body,
            text="What can I help you with?",
            fg=TEXT,
            bg=BACKGROUND,
            font=("Segoe UI Semibold", 23),
        ).pack(anchor="w", pady=(0, 5))
        tk.Label(
            body,
            text="Choose a shortcut or ask Jarvis in your own words.",
            fg=MUTED,
            bg=BACKGROUND,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 18))

        actions = tk.Frame(body, bg=BACKGROUND)
        actions.pack(fill="x", pady=(0, 18))
        quick_actions = (
            ("◷", "Tell me the time", "time"),
            ("⌕", "Search Wikipedia", "wikipedia"),
            ("♫", "Play music", "play music"),
            ("✦", "Tell me a joke", "tell me a joke"),
        )
        self.action_buttons = []
        for icon, label, command in quick_actions:
            button = tk.Button(
                actions,
                text="{0}   {1}".format(icon, label),
                command=lambda text=command: self._submit_text(text),
                bg=SURFACE,
                fg=TEXT,
                activebackground=SURFACE_HOVER,
                activeforeground=ACCENT,
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 9),
                padx=13,
                pady=11,
            )
            button.pack(side="left", padx=(0, 8))
            self.action_buttons.append(button)

        conversation = tk.Frame(body, bg=SURFACE, padx=1, pady=1)
        conversation.pack(fill="both", expand=True)
        transcript_frame = tk.Frame(conversation, bg=SURFACE)
        transcript_frame.pack(fill="both", expand=True, padx=18, pady=15)
        tk.Label(
            transcript_frame,
            text="CONVERSATION",
            fg=SUBTLE,
            bg=SURFACE,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        transcript_area = tk.Frame(transcript_frame, bg=SURFACE)
        transcript_area.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(
            transcript_area,
            orient="vertical",
            bg=SURFACE,
            troughcolor=SURFACE,
            activebackground=SUBTLE,
            relief="flat",
            bd=0,
        )
        scrollbar.pack(side="right", fill="y")
        self.transcript = tk.Text(
            transcript_area,
            wrap="word",
            bg=SURFACE,
            fg=TEXT,
            insertbackground=ACCENT,
            selectbackground="#30415F",
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            padx=4,
            yscrollcommand=scrollbar.set,
            state="disabled",
            spacing1=3,
            spacing3=11,
        )
        self.transcript.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=self.transcript.yview)
        self.transcript.tag_configure(
            "assistant", foreground=TEXT, lmargin1=4, lmargin2=4
        )
        self.transcript.tag_configure(
            "user", foreground=ACCENT, lmargin1=4, lmargin2=4
        )
        self.transcript.tag_configure(
            "label", foreground=SUBTLE, font=("Segoe UI Semibold", 8)
        )

        composer = tk.Frame(body, bg="#111A2C", padx=12, pady=10)
        composer.pack(fill="x", pady=(13, 0))
        self.input = tk.Entry(
            composer,
            bg="#111A2C",
            fg=TEXT,
            insertbackground=ACCENT,
            disabledbackground="#111A2C",
            disabledforeground=SUBTLE,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10),
        )
        self.input.pack(side="left", fill="x", expand=True, padx=(4, 10), ipady=7)
        self.input.insert(0, "Type a message or ask Jarvis to do something...")
        self.input.configure(fg=SUBTLE)
        self.input.bind("<FocusIn>", self._clear_placeholder)
        self.input.bind("<Return>", lambda _event: self._submit_from_input())
        self.send_button = tk.Button(
            composer,
            text="Send  ↗",
            command=self._submit_from_input,
            bg="#1A665F",
            fg=TEXT,
            activebackground="#21867A",
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 9),
            padx=15,
            pady=9,
        )
        self.send_button.pack(side="right")
        self.listen_button = tk.Button(
            composer,
            text="🎙  Listen",
            command=self._listen,
            bg="#1C2943",
            fg=ACCENT,
            activebackground=SURFACE_HOVER,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI Semibold", 9),
            padx=13,
            pady=9,
        )
        self.listen_button.pack(side="right", padx=(0, 8))
        tk.Label(
            body,
            text="Voice recognition requires a microphone and an internet connection.",
            fg=SUBTLE,
            bg=BACKGROUND,
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(8, 12))

    def _sidebar_item(self, icon, label, active=False):
        background = "#19263D" if active else SIDEBAR
        foreground = ACCENT if active else MUTED
        row = tk.Frame(self.sidebar, bg=background, padx=12, pady=10)
        row.pack(fill="x", padx=16, pady=2)
        tk.Label(
            row, text=icon, fg=foreground, bg=background, font=("Segoe UI", 11)
        ).pack(side="left")
        tk.Label(
            row,
            text=label,
            fg=TEXT if active else MUTED,
            bg=background,
            font=("Segoe UI Semibold" if active else "Segoe UI", 9),
        ).pack(side="left", padx=(10, 0))

    def _clear_placeholder(self, _event=None):
        if self.input.get() == "Type a message or ask Jarvis to do something...":
            self.input.delete(0, "end")
            self.input.configure(fg=TEXT)

    def _append_message(self, role, message):
        self.transcript.configure(state="normal")
        label = "YOU" if role == "user" else load_name().upper()
        self.transcript.insert("end", label + "\n", "label")
        self.transcript.insert("end", message + "\n\n", role)
        self.transcript.configure(state="disabled")
        self.transcript.see("end")

    def _submit_from_input(self):
        query = self.input.get().strip()
        if not query or query == "Type a message or ask Jarvis to do something...":
            return
        self.input.delete(0, "end")
        self.input.configure(fg=TEXT)
        self._submit_text(query)

    def _submit_text(self, query, confirmed=False):
        if self.busy or not self.online:
            return
        query = query.strip()
        if not query:
            return
        lowered = query.lower()
        if not confirmed and ("shutdown" in lowered or "restart" in lowered):
            action = "shut down" if "shutdown" in lowered else "restart"
            if not messagebox.askyesno(
                "Confirm system action",
                "Are you sure you want Jarvis to {0} this computer?".format(action),
                parent=self.root,
            ):
                self._append_message("assistant", "System action cancelled.")
                return

        if "change your name" in lowered and not lowered.split(
            "change your name", 1
        )[1].strip():
            name = simpledialog.askstring(
                "Rename assistant",
                "What would you like to call your assistant?",
                initialvalue=load_name(),
                parent=self.root,
            )
            if name is None:
                return
            operation = lambda: (set_assistant_name(name), True)
        else:
            operation = lambda: handle_command(query)
        self._start_task(operation, user_message=query)

    def _change_name(self):
        name = simpledialog.askstring(
            "Rename assistant",
            "What would you like to call your assistant?",
            initialvalue=load_name(),
            parent=self.root,
        )
        if name:
            self._start_task(
                lambda: set_assistant_name(name),
                user_message="Change your name to {0}".format(name.strip()),
            )

    def _listen(self):
        if self.busy or not self.online:
            return
        self._set_busy(True)

        def listen_and_respond():
            confirmation_requested = False
            try:
                query = takecommand(
                    status_callback=lambda text: self.events.put(("status", text))
                )
                if not query:
                    self.events.put(
                        ("reply", "I couldn't catch that. Check your microphone and try again.")
                    )
                    return
                self.events.put(("user", query))
                if "shutdown" in query or "restart" in query:
                    confirmation_requested = True
                    self.events.put(("done", None))
                    self.events.put(("confirm", query))
                    return
                reply, keep_running = handle_command(query)
                self.events.put(("reply", reply))
                if "change your name" in query:
                    self.events.put(("name", None))
                if not keep_running:
                    self.events.put(("offline", None))
            except Exception as error:
                self.events.put(
                    ("reply", "I couldn't complete that command: {0}".format(error))
                )
            finally:
                if not confirmation_requested:
                    self.events.put(("done", None))

        threading.Thread(target=listen_and_respond, daemon=True).start()

    def _start_task(self, operation, user_message=None):
        if self.busy or not self.online:
            return
        self._set_busy(True)
        if user_message:
            self._append_message("user", user_message)

        def run():
            try:
                result = operation()
                if isinstance(result, tuple):
                    reply, keep_running = result
                else:
                    reply, keep_running = result, True
                self.events.put(("reply", reply))
                if not keep_running:
                    self.events.put(("offline", None))
                if user_message and "change your name" in user_message.lower():
                    self.events.put(("name", None))
            except Exception as error:
                self.events.put(
                    ("reply", "I couldn't complete that command: {0}".format(error))
                )
            finally:
                self.events.put(("done", None))

        threading.Thread(target=run, daemon=True).start()

    def _set_busy(self, busy):
        self.busy = busy
        state = "disabled" if busy or not self.online else "normal"
        self.input.configure(state=state)
        self.send_button.configure(state=state)
        self.listen_button.configure(state=state)
        for button in self.action_buttons:
            button.configure(state=state)
        self._set_status("WORKING..." if busy else "READY", ACCENT)

    def _set_status(self, text, color):
        self.status.configure(text="●  " + text, fg=color)

    def _poll_events(self):
        while True:
            try:
                event, value = self.events.get_nowait()
            except queue.Empty:
                break
            if event == "status":
                self._set_status(value.upper(), ACCENT)
            elif event == "user":
                self._append_message("user", value)
            elif event == "reply":
                self._append_message("assistant", value)
            elif event == "name":
                self.name_label.configure(text=load_name())
            elif event == "confirm":
                action = "shut down" if "shutdown" in value else "restart"
                confirmed = messagebox.askyesno(
                    "Confirm system action",
                    "Are you sure you want Jarvis to {0} this computer?".format(action),
                    parent=self.root,
                )
                if confirmed:
                    self._submit_text(value, confirmed=True)
                else:
                    self._append_message("assistant", "System action cancelled.")
            elif event == "offline":
                self.online = False
                self._set_status("OFFLINE", SUBTLE)
            elif event == "done":
                self._set_busy(False)
                if not self.online:
                    self._set_status("OFFLINE", SUBTLE)
                    self.input.configure(state="disabled")
                    self.send_button.configure(state="disabled")
                    self.listen_button.configure(state="disabled")
                    for button in self.action_buttons:
                        button.configure(state="disabled")
        self.root.after(100, self._poll_events)

    def _update_clock(self):
        self.clock.configure(
            text=datetime.datetime.now().strftime("%A, %B %d  ·  %I:%M %p")
        )
        self.root.after(30000, self._update_clock)


def launch_gui():
    root = tk.Tk()
    JarvisApp(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()

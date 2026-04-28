"""
STM32 Mini PLC - Ladder Editor
A graphical tool to design ladder programs and download them to the STM32 PLC.
"""

import customtkinter as ctk
from tkinter import Canvas

# ---------- Configuration ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
TOOLBOX_WIDTH = 220
STATUS_HEIGHT = 80

# Canvas drawing constants
CANVAS_BG = "#2b2b2b"
CANVAS_GRID = "#3a3a3a"
CANVAS_RAIL = "#888888"
ELEMENT_COLOR = "#5fa8d3"
ELEMENT_TEXT = "#ffffff"
ELEMENT_HOVER = "#7ec8eb"

RAIL_X_LEFT = 80
RAIL_MARGIN_RIGHT = 80
RUNG_HEIGHT = 80           # vertical space per rung
RUNG_TOP_OFFSET = 60       # distance from top of canvas to first rung
ELEMENT_WIDTH = 80         # how wide each element is when drawn
ELEMENT_HEIGHT = 40        # how tall
GRID_SNAP = 100            # x-spacing for element placement

# Ladder element types
ELEMENT_TYPES = [
    ("Contact",       "─| |─",   "I0"),
    ("Not Contact",   "─|/|─",   "I0"),
    ("Coil",          "─( )─",   "Q0"),
    ("Timer (TON)",   "─(TON)─", "T0"),
    ("Counter (CTU)", "─(CTU)─", "C0"),
    ("Reset (RST)",   "─(RST)─", "C0"),
]


# ---------- Main Editor Class ----------
class LadderEditor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("STM32 Mini PLC - Ladder Editor")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(900, 500)

        # State
        self.connected = False
        self.selected_tool = None
        # Program model — list of rungs, each rung a list of elements
        self.program = {"rungs": [{"elements": []}]}  # start with 1 empty rung

        # Build UI
        self._build_layout()
        self._build_toolbox()
        self._build_canvas()
        self._build_status_bar()

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

    def _build_toolbox(self):
        self.toolbox = ctk.CTkFrame(self, width=TOOLBOX_WIDTH, corner_radius=0)
        self.toolbox.grid(row=0, column=0, sticky="nsew")
        self.toolbox.grid_propagate(False)

        title = ctk.CTkLabel(self.toolbox, text="Toolbox",
                             font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(20, 10))

        subtitle = ctk.CTkLabel(self.toolbox,
                                text="Click element, then click rung",
                                font=ctk.CTkFont(size=10),
                                text_color="gray")
        subtitle.pack(pady=(0, 20))

        self.tool_buttons = {}
        for name, symbol, default_addr in ELEMENT_TYPES:
            btn = ctk.CTkButton(
                self.toolbox,
                text=f"{symbol}\n{name}",
                width=180, height=50,
                command=lambda n=name: self._select_tool(n)
            )
            btn.pack(pady=4)
            self.tool_buttons[name] = btn

        ctk.CTkLabel(self.toolbox, text="").pack(pady=10)

        ctk.CTkButton(
            self.toolbox, text="+ Add Rung", width=180, height=40,
            fg_color="#2a7a2a", hover_color="#1f5f1f",
            command=self._on_add_rung
        ).pack(pady=4)

        ctk.CTkButton(
            self.toolbox, text="Clear All", width=180, height=40,
            fg_color="#7a2a2a", hover_color="#5f1f1f",
            command=self._on_clear
        ).pack(pady=4)

    def _build_canvas(self):
        canvas_frame = ctk.CTkFrame(self, corner_radius=0)
        canvas_frame.grid(row=0, column=1, sticky="nsew")
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)

        self.canvas = Canvas(canvas_frame, bg=CANVAS_BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self._redraw_canvas())
        self.canvas.bind("<Button-1>", self._on_canvas_click)

    def _build_status_bar(self):
        self.status_frame = ctk.CTkFrame(self, height=STATUS_HEIGHT, corner_radius=0)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_frame.grid_propagate(False)

        ctk.CTkLabel(self.status_frame, text="COM Port:").pack(side="left", padx=(15, 5), pady=20)
        self.com_dropdown = ctk.CTkComboBox(
            self.status_frame, values=["COM1", "COM3", "COM9"], width=120
        )
        self.com_dropdown.set("COM9")
        self.com_dropdown.pack(side="left", padx=5)

        self.connect_btn = ctk.CTkButton(self.status_frame, text="Connect",
                                         width=100, command=self._on_connect)
        self.connect_btn.pack(side="left", padx=10)

        ctk.CTkButton(self.status_frame, text="Compile", width=100,
                      command=self._on_compile).pack(side="left", padx=5)
        ctk.CTkButton(self.status_frame, text="Download", width=100,
                      command=self._on_download).pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(
            self.status_frame, text="Ready", text_color="gray"
        )
        self.status_label.pack(side="right", padx=15)

    # ============================================================
    # Canvas geometry helpers
    # ============================================================
    def _rung_y(self, rung_index):
        """Return canvas Y position for a given rung index."""
        return RUNG_TOP_OFFSET + rung_index * RUNG_HEIGHT

    def _rail_x_right(self):
        return self.canvas.winfo_width() - RAIL_MARGIN_RIGHT

    def _rung_at_y(self, y):
        """Given a canvas Y click, find which rung was clicked. Returns None if outside."""
        for i in range(len(self.program["rungs"])):
            ry = self._rung_y(i)
            if ry - RUNG_HEIGHT / 2 <= y <= ry + RUNG_HEIGHT / 2:
                return i
        return None

    def _snap_x(self, x):
        """Snap an X coordinate to the grid (nearest GRID_SNAP)."""
        return round((x - RAIL_X_LEFT) / GRID_SNAP) * GRID_SNAP + RAIL_X_LEFT

    # ============================================================
    # Canvas Drawing
    # ============================================================
    def _redraw_canvas(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            return  # not yet sized

        rail_right = self._rail_x_right()

        # Draw rails (vertical lines on left and right)
        bottom_y = self._rung_y(len(self.program["rungs"]) - 1) + RUNG_HEIGHT / 2
        self.canvas.create_line(RAIL_X_LEFT, 30, RAIL_X_LEFT, bottom_y,
                                fill=CANVAS_RAIL, width=3)
        self.canvas.create_line(rail_right, 30, rail_right, bottom_y,
                                fill=CANVAS_RAIL, width=3)

        # Draw each rung
        for rung_idx, rung in enumerate(self.program["rungs"]):
            self._draw_rung(rung_idx, rung)

        # Empty hint
        if all(len(r["elements"]) == 0 for r in self.program["rungs"]):
            self.canvas.create_text(
                w / 2, h / 2,
                text="Pick an element from the toolbox, then click a rung",
                fill="gray", font=("Arial", 12)
            )

    def _draw_rung(self, rung_idx, rung):
        """Draw a single rung: horizontal wire + elements."""
        y = self._rung_y(rung_idx)
        rail_right = self._rail_x_right()

        # Horizontal wire (rung itself)
        self.canvas.create_line(RAIL_X_LEFT, y, rail_right, y,
                                fill=CANVAS_RAIL, width=2)

        # Rung label on the left
        self.canvas.create_text(40, y, text=f"R{rung_idx}",
                                fill="gray", font=("Arial", 10))

        # Each element on this rung
        for elem in rung["elements"]:
            self._draw_element(elem, y)

    def _draw_element(self, elem, y):
        """Draw a single ladder element at its x position on the given rung Y."""
        x = elem["x"]
        kind = elem["type"]
        addr = elem.get("addr", "?")

        # All elements share a rectangle background + black wire stub through it
        x1 = x - ELEMENT_WIDTH / 2
        x2 = x + ELEMENT_WIDTH / 2
        y1 = y - ELEMENT_HEIGHT / 2
        y2 = y + ELEMENT_HEIGHT / 2

        # Wire stub goes through the element (continuation of rung)
        self.canvas.create_line(x1, y, x2, y, fill=CANVAS_RAIL, width=2)

        # Draw element-specific symbol
        if kind == "Contact":
            # Two vertical bars, gap in the middle:   | |
            self.canvas.create_line(x - 12, y - 15, x - 12, y + 15,
                                    fill=ELEMENT_COLOR, width=3)
            self.canvas.create_line(x + 12, y - 15, x + 12, y + 15,
                                    fill=ELEMENT_COLOR, width=3)
        elif kind == "Not Contact":
            # Two vertical bars + diagonal line:   |/|
            self.canvas.create_line(x - 12, y - 15, x - 12, y + 15,
                                    fill=ELEMENT_COLOR, width=3)
            self.canvas.create_line(x + 12, y - 15, x + 12, y + 15,
                                    fill=ELEMENT_COLOR, width=3)
            self.canvas.create_line(x - 14, y + 14, x + 14, y - 14,
                                    fill=ELEMENT_COLOR, width=2)
        elif kind == "Coil":
            # Parentheses-like circle:   ( )
            self.canvas.create_arc(x - 18, y - 18, x + 18, y + 18,
                                   start=45, extent=270, style="arc",
                                   outline=ELEMENT_COLOR, width=3)
        elif kind == "Timer (TON)":
            # Box with "TON" inside
            self.canvas.create_rectangle(x - 22, y - 16, x + 22, y + 16,
                                         outline=ELEMENT_COLOR, width=2)
            self.canvas.create_text(x, y, text="TON",
                                    fill=ELEMENT_COLOR, font=("Arial", 10, "bold"))
        elif kind == "Counter (CTU)":
            self.canvas.create_rectangle(x - 22, y - 16, x + 22, y + 16,
                                         outline=ELEMENT_COLOR, width=2)
            self.canvas.create_text(x, y, text="CTU",
                                    fill=ELEMENT_COLOR, font=("Arial", 10, "bold"))
        elif kind == "Reset (RST)":
            self.canvas.create_rectangle(x - 22, y - 16, x + 22, y + 16,
                                         outline=ELEMENT_COLOR, width=2)
            self.canvas.create_text(x, y, text="RST",
                                    fill=ELEMENT_COLOR, font=("Arial", 10, "bold"))

        # Address label below the element
        self.canvas.create_text(x, y + 28, text=addr,
                                fill=ELEMENT_TEXT, font=("Arial", 11, "bold"))

    # ============================================================
    # Canvas Interactions
    # ============================================================
    def _on_canvas_click(self, event):
        if not self.selected_tool:
            self.status_label.configure(text="Select a tool first")
            return

        # Find which rung was clicked
        rung_idx = self._rung_at_y(event.y)
        if rung_idx is None:
            self.status_label.configure(text="Click on a rung")
            return

        # Check click is between rails
        rail_right = self._rail_x_right()
        if event.x < RAIL_X_LEFT + 30 or event.x > rail_right - 30:
            self.status_label.configure(text="Click between the rails")
            return

        # Snap x to grid and add element
        x = self._snap_x(event.x)
        # Find default addr for this tool
        default_addr = next((addr for n, _, addr in ELEMENT_TYPES
                             if n == self.selected_tool), "?")

        new_element = {
            "type": self.selected_tool,
            "addr": default_addr,
            "x": x
        }
        self.program["rungs"][rung_idx]["elements"].append(new_element)

        print(f"[place] rung={rung_idx} type={self.selected_tool} x={x}")
        self.status_label.configure(
            text=f"Placed {self.selected_tool} on rung {rung_idx}"
        )
        self._redraw_canvas()

    # ============================================================
    # Toolbox Actions
    # ============================================================
    def _select_tool(self, name):
        self.selected_tool = name
        for n, btn in self.tool_buttons.items():
            if n == name:
                btn.configure(fg_color="#1f6aa5")
            else:
                btn.configure(fg_color=("#3a7ebf", "#1f6aa5"))
        print(f"[toolbox] Selected: {name}")
        self.status_label.configure(text=f"Selected: {name} — click a rung")

    def _on_add_rung(self):
        self.program["rungs"].append({"elements": []})
        print(f"[action] Added rung (now {len(self.program['rungs'])} rungs)")
        self.status_label.configure(
            text=f"Now {len(self.program['rungs'])} rungs"
        )
        self._redraw_canvas()

    def _on_clear(self):
        self.program = {"rungs": [{"elements": []}]}
        self.selected_tool = None
        for btn in self.tool_buttons.values():
            btn.configure(fg_color=("#3a7ebf", "#1f6aa5"))
        self.status_label.configure(text="Cleared")
        self._redraw_canvas()

    # ============================================================
    # Connection / Compile / Download (still mocks)
    # ============================================================
    def _on_connect(self):
        if not self.connected:
            self.connected = True
            self.connect_btn.configure(text="Disconnect")
            self.status_label.configure(text=f"Connected to {self.com_dropdown.get()}")
        else:
            self.connected = False
            self.connect_btn.configure(text="Connect")
            self.status_label.configure(text="Disconnected")

    def _on_compile(self):
        # Print the program model — preview before real compilation
        print("\n=== Program model ===")
        for i, rung in enumerate(self.program["rungs"]):
            print(f"Rung {i}: {len(rung['elements'])} elements")
            for elem in rung["elements"]:
                print(f"  - {elem['type']} {elem['addr']} at x={elem['x']}")
        print("=====================\n")
        self.status_label.configure(text="Program printed to console")

    def _on_download(self):
        self.status_label.configure(text="Download: not yet implemented")


# ---------- Run the editor ----------
if __name__ == "__main__":
    app = LadderEditor()
    app.mainloop()
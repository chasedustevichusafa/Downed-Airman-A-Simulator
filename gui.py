"""Desktop viewer for static A* exploration and shortest-path comparison."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from map_choices import dead_end_grid
from map_loader import load_map
from pathfinding import SearchResult, dijkstra_result, search_steps


MAP_DIRECTORY = Path(__file__).resolve().parent / "maps"
BUNDLED_MAPS = {
    "Forced detour": "detour.txt",
    "Direct route": "direct.txt",
    "Unreachable goal": "unreachable.txt",
    "Open grid comparison": "comparison.txt",
    "Dead-end maze": None,
}

BACKGROUND = "#eef2f6"
CELL_STYLES = {
    ".": ("#ffffff", "", "#263449"),
    "#": ("#35445b", "", "#ffffff"),
    "checked": ("#c4d5f3", "×", "#193763"),
    "queued": ("#ace3ee", "○", "#17414f"),
    "selected": ("#ffd078", "●", "#523309"),
    "S": ("#a5e6c1", "S", "#113f2b"),
    "E": ("#e9c4f1", "E", "#512764"),
}
ROUTE_COLOR = "#107150"


class GridView(tk.Canvas):
    """Draw a square-cell grid with an optional route through cell centers."""

    def __init__(self, parent):
        super().__init__(parent, background=BACKGROUND, highlightthickness=0, height=300)
        self.grid_map = None
        self.marks = {}
        self.route = ()
        self.bind("<Configure>", self.redraw)

    def show(self, grid_map, marks=None, route=()):
        self.grid_map = grid_map
        self.marks = marks or {}
        self.route = route
        self.redraw()

    def redraw(self, _event=None):
        self.delete("all")
        if self.grid_map is None:
            return

        rows = self.grid_map.rows
        view_width, view_height = self.winfo_width(), self.winfo_height()
        if view_width <= 24 or view_height <= 24:
            return

        cell_size = min((view_width - 24) / len(rows[0]), (view_height - 24) / len(rows), 64)
        left = (view_width - len(rows[0]) * cell_size) / 2
        top = (view_height - len(rows) * cell_size) / 2
        labels = []
        for row, line in enumerate(rows):
            for column, tile in enumerate(line):
                horizontal = left + column * cell_size
                vertical = top + row * cell_size
                center = horizontal + cell_size / 2, vertical + cell_size / 2
                # Keep start and goal labels readable on the final route.
                state = tile if tile in "SE" else self.marks.get((row, column), tile)
                fill, symbol, ink = CELL_STYLES[state]
                self.create_rectangle(
                    horizontal, vertical, horizontal + cell_size, vertical + cell_size,
                    fill=fill, outline="#c1ccdb", tags="cell",
                )
                if symbol and (cell_size >= 14 or tile in "SE"):
                    labels.append((center, symbol, fill, ink))

        if len(self.route) > 1:
            points = []
            for row, column in self.route:
                points.extend((left + (column + 0.5) * cell_size, top + (row + 0.5) * cell_size))
            self.create_line(*points, fill=ROUTE_COLOR, width=max(2, cell_size / 8),
                             capstyle=tk.ROUND, joinstyle=tk.ROUND, tags="route")

        for center, symbol, fill, ink in labels:
            if self.route and symbol in "SE":
                horizontal, vertical = center
                radius = cell_size * 0.22
                self.create_oval(horizontal - radius, vertical - radius,
                                 horizontal + radius, vertical + radius,
                                 fill=fill, outline=ROUTE_COLOR)
            self.create_text(*center, text=symbol, fill=ink,
                             font=("TkDefaultFont", max(7, min(16, int(cell_size / 3))), "bold"))


class SearchWindow:
    """Play A* one step at a time and show both algorithms' final routes."""

    def __init__(self, window):
        self.window = window
        self.timer = None
        window.title("Downed Airman | A* Search")
        window.geometry("980x650")
        window.minsize(740, 530)

        content = ttk.Frame(window, padding=18)
        content.pack(fill="both", expand=True)
        ttk.Label(content, text="A* search", font=("TkDefaultFont", 20, "bold")).pack(anchor="w")
        controls = ttk.Frame(content, padding=(0, 10))
        controls.pack(fill="x")
        self.map_choice = tk.StringVar(value="Forced detour")
        picker = ttk.Combobox(
            controls, textvariable=self.map_choice, values=tuple(BUNDLED_MAPS),
            state="readonly", width=20,
        )
        picker.pack(side="left", padx=(0, 6))
        picker.bind("<<ComboboxSelected>>", self.load_selection)
        for label, action in (
            ("Open map", self.open_file), ("Run", self.run), ("Pause", self.pause),
            ("Step", self.step), ("Reset", self.reset),
        ):
            ttk.Button(controls, text=label, command=action).pack(side="left", padx=3)

        self.tabs = ttk.Notebook(content)
        self.tabs.pack(fill="both", expand=True)
        self.exploration = ttk.Frame(self.tabs, padding=10)
        self.comparison = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(self.exploration, text="Search exploration")
        self.tabs.add(self.comparison, text="Final routes")
        self.search_status = tk.StringVar()
        ttk.Label(self.exploration, textvariable=self.search_status, wraplength=680,
                  justify="left").pack(anchor="w")
        self.exploration_grid = GridView(self.exploration)
        self.exploration_grid.pack(fill="both", expand=True, pady=8)
        ttk.Label(self.exploration, text="S  Start     E  Goal     ●  Selected     ○  Queued     ×  Checked"
                  ).pack(anchor="w")
        self.comparison_status = tk.StringVar()
        ttk.Label(self.comparison, textvariable=self.comparison_status, wraplength=680,
                  justify="left").pack(anchor="w", pady=(0, 8))
        boards = ttk.Frame(self.comparison)
        boards.pack(fill="both", expand=True)
        boards.columnconfigure((0, 1), weight=1, uniform="route")
        boards.rowconfigure(0, weight=1)
        self.final_views = []
        for column, name in enumerate(("A*", "Dijkstra")):
            board = ttk.LabelFrame(boards, text=name, padding=8)
            board.grid(row=0, column=column, sticky="nsew", padx=4)
            summary = ttk.Label(board)
            summary.pack(anchor="w")
            view = GridView(board)
            view.pack(fill="both", expand=True, pady=(6, 0))
            self.final_views.append((summary, view))

        self.load_selection()

    def load_selection(self, _event=None):
        name = self.map_choice.get()
        filename = BUNDLED_MAPS[name]
        self.current_map = load_map(MAP_DIRECTORY / filename) if filename else dead_end_grid(9, 13)
        self.reset()

    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=(("Text maps", "*.txt"), ("All files", "*")))
        if not filename:
            return
        try:
            grid_map = load_map(Path(filename))
        except (OSError, ValueError) as error:
            messagebox.showerror("Could not open map", str(error), parent=self.window)
            return
        self.current_map = grid_map
        self.map_choice.set(Path(filename).name)
        self.reset()

    def reset(self):
        self.pause()
        self.events = search_steps(self.current_map)
        self.checked = set()
        self.queued = {self.current_map.start}
        self.selected = None
        self.finished = False
        self.search_status.set("Select Run to watch the search, or Step to advance one tile.")
        self.comparison_status.set("Run the search to compare the final routes and tiles expanded.")
        self.exploration_grid.show(self.current_map)
        for summary, view in self.final_views:
            summary.configure(text="Waiting for search")
            view.show(self.current_map)
        self.tabs.select(self.exploration)

    def pause(self):
        if self.timer is not None:
            self.window.after_cancel(self.timer)
            self.timer = None

    def run(self):
        if self.timer is None and not self.finished:
            self.advance_playback()

    def advance_playback(self):
        self.timer = None
        self.advance_search()
        if not self.finished:
            self.timer = self.window.after(180, self.advance_playback)

    def step(self):
        self.pause()
        if not self.finished:
            self.advance_search()

    def advance_search(self):
        event = next(self.events)
        if isinstance(event, SearchResult):
            self.show_results(event)
            return
        if self.selected is not None:
            self.checked.add(self.selected)
        self.selected = event.selected
        self.queued.discard(event.selected)
        self.queued.update(event.newly_queued)
        marks = dict.fromkeys(self.checked, "checked")
        marks.update(dict.fromkeys(self.queued, "queued"))
        marks[event.selected] = "selected"
        self.exploration_grid.show(self.current_map, marks)
        self.search_status.set(
            f"Selected tile {event.selected} — moves so far {event.moves_so_far}, "
            f"estimated moves remaining {event.estimated_moves_remaining}, "
            f"estimated total moves {event.moves_so_far + event.estimated_moves_remaining}."
        )

    def show_results(self, astar):
        self.finished = True
        dijkstra = dijkstra_result(self.current_map)
        for result, (summary, view) in zip((astar, dijkstra), self.final_views):
            route_description = "No route" if result.cost is None else f"Path cost {result.cost}"
            summary.configure(text=f"{route_description}  |  {result.tiles_expanded} tiles expanded")
            view.show(self.current_map, route=result.path or ())
        if astar.cost is None and dijkstra.cost is None:
            self.search_status.set("The queue ran out before A* reached the goal.")
            self.comparison_status.set("Both searches found the goal unreachable.")
        elif astar.cost == dijkstra.cost:
            self.search_status.set("A* selected the goal with the lowest estimate in the queue.")
            self.comparison_status.set(
                "Both searches found the same shortest cost. They may choose different "
                "equally short routes. Green lines show the final paths. A tile counts as "
                "expanded when its neighbors are checked."
            )
        else:
            self.comparison_status.set("The search results disagree. Check the reported path costs.")
        self.tabs.select(self.comparison)


def main():
    window = tk.Tk()
    SearchWindow(window)
    window.mainloop()


if __name__ == "__main__":
    main()

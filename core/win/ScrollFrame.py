import tkinter as tk


class ScrollableFrame(tk.Frame):
    def __init__(self, container, **kwargs):
        super().__init__(container, **kwargs)
        self.canvas = tk.Canvas(self, **kwargs)
        self.scrollable_frame = tk.Frame(self.canvas, **kwargs)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.grid()

        self.canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas=self.canvas), "+")

        self.state = True

    def _on_mousewheel(self, event, canvas):
        if not self.state:
            return
        height = canvas.winfo_height()
        _, _, _, items_height = canvas.bbox(tk.ALL)
        if (items_height < height):
            direction = 0
        else:
            direction = event.delta
        migration = int(-1 * (direction / 120))
        canvas.yview_scroll(migration, "units")

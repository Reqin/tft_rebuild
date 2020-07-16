import tkinter as tk


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, *args, **kwargs)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, *args, **kwargs)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas = canvas
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.position = 0

    def _on_mousewheel(self, event):
        height = self.canvas.winfo_height()
        _, _, _, items_height = self.canvas.bbox(tk.ALL)
        if (items_height < height):
            direction = 0
        else:
            direction = event.delta
        migration = int(-1*(direction/120))
        # self.position = self.position + migration
        self.canvas.yview_scroll(migration, "units")

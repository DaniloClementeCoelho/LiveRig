import customtkinter as ctk


class LibraryItem(ctk.CTkFrame):

    def __init__(
        self,
        master,
        song,
        selected=False,
        on_click=None,
        on_drag_start=None,
    ):
        super().__init__(
            master,
            corner_radius=8,
            fg_color=("gray86", "gray22") if not selected else "#1f6fff"
        )

        self.song = song
        self.on_click = on_click
        self.on_drag_start = on_drag_start
        

        self.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(
            self,
            text=song.title,
            anchor="w",
            font=("Arial", 15, "bold"),
        )
        self.title.grid(
            row=0,
            column=0,
            padx=12,
            pady=(8,0),
            sticky="ew",
        )

        self.artist = ctk.CTkLabel(
            self,
            text=song.artist,
            anchor="w",
            font=("Arial", 13),
        )
        self.artist.grid(
            row=1,
            column=0,
            padx=12,
            pady=(0,8),
            sticky="ew",
        )
        self.bind("<ButtonPress-1>", self._drag_start)
        self.bind("<ButtonPress-1>", self._drag_start)
        self.title.bind("<ButtonPress-1>", self._drag_start)
        self.artist.bind("<ButtonPress-1>", self._drag_start)

        self.bind("<Button-1>", self._clicked)
        self.title.bind("<Button-1>", self._clicked)
        self.artist.bind("<Button-1>", self._clicked)

    def _clicked(self, event):
        if self.on_click:
            self.on_click(self.song)

    def _drag_start(self, event):
        if self.on_drag_start:
            self.on_drag_start(self.song)
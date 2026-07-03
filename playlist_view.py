import customtkinter as ctk

from playlist_item import PlaylistItem


class PlaylistView(ctk.CTkScrollableFrame):

    def __init__(self, master):
        super().__init__(
            master,
            corner_radius=0,
        )

        self.grid_columnconfigure(0, weight=1)

        self.playlist = []

    def set_playlist(self, playlist):

        self.playlist = playlist

        self._refresh()

    def _refresh(self):

        for child in self.winfo_children():
            child.destroy()

        for row, song in enumerate(self.playlist):

            item = PlaylistItem(
                self,
                song=song,
            )

            item.grid(
                row=row,
                column=0,
                padx=4,
                pady=4,
                sticky="ew",
            )
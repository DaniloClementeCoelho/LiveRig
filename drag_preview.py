import customtkinter as ctk


class DragPreview(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(
            master,
            corner_radius=10,
            border_width=2,
            fg_color="#3B82F6",
            border_color="#2563EB",
        )

        self.place_forget()

        self.label = ctk.CTkLabel(
            self,
            text="",
            anchor="w",
            font=("Arial", 15, "bold"),
        )

        self.label.pack(
            padx=12,
            pady=8,
        )

    def show(self, song, x, y):

        self.label.configure(
            text=song.title
        )

        self.place(
            x=x + 12,
            y=y + 12,
        )

        self.lift()

    def move(self, x, y):

        self.place_configure(
            x=x + 12,
            y=y + 12,
        )

    def hide(self):

        self.place_forget()

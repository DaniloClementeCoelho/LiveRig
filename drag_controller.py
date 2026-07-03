class DragController:

    def __init__(self):

        self.dragging = False
        self.song = None

    def start(self, song):

        self.dragging = True
        self.song = song

        print(f"START DRAG: {song.title}")

    def stop(self):

        if self.dragging:
            print("STOP DRAG")

        self.dragging = False
        self.song = None

    def is_dragging(self):

        return self.dragging
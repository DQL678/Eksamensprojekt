# map.py
import tkinter as tk


class GameMap:
    def __init__(self, canvas):
        self.canvas = canvas
        self.width = 1600
        self.height = 900
        self.walls = []

    def draw(self):
        """Tegner hele mappet."""
        self.canvas.delete("all")
        self.draw_background()
        self.create_walls()
        self.draw_walls()

    def draw_background(self):
        """Tegner baggrunden."""
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill="darkseagreen3", outline=""
        )

    def create_walls(self):
        """
        Laver en simpel liste med vægge.
        Hver væg er en firkant: (x1, y1, x2, y2)
        """
        self.walls = [
            # Yderkant
            (0, 0, 1600, 40),
            (0, 860, 1600, 900),
            (0, 0, 40, 900),
            (1560, 0, 1600, 900),

            # Indre vægge
            (250, 150, 500, 200),
            (700, 100, 750, 350),
            (950, 250, 1300, 300),
            (300, 400, 350, 750),
            (550, 600, 1000, 650),
            (1150, 450, 1200, 800),
        ]

    def draw_walls(self):
        """Tegner alle vægge."""
        for wall in self.walls:
            x1, y1, x2, y2 = wall
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="saddlebrown", outline="black", width=2
            )

    def is_blocked(self, x, y, size=30):
        """
        Tjekker om en spiller rammer en væg.
        x og y er spillerens øverste venstre hjørne.
        """
        player_left = x
        player_top = y
        player_right = x + size
        player_bottom = y + size

        for wall in self.walls:
            wall_left, wall_top, wall_right, wall_bottom = wall

            overlap = (
                player_right > wall_left and
                player_left < wall_right and
                player_bottom > wall_top and
                player_top < wall_bottom
            )

            if overlap:
                return True

        return False
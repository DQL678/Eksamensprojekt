# main.py
import tkinter as tk
from map import GameMap


class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multiplayer Game")

        # Gør vinduet stort
        try:
            self.root.state("zoomed")
        except:
            self.root.geometry("1400x800")

        self.music_volume = 50
        self.sfx_volume = 50

        self.current_frame = None
        self.show_start_menu()

    def clear_frame(self):
        """Fjerner den nuværende frame."""
        if self.current_frame is not None:
            self.current_frame.destroy()

    def show_start_menu(self):
        """Viser startmenuen."""
        self.clear_frame()

        self.current_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.current_frame.pack(fill="both", expand=True)

        title = tk.Label(
            self.current_frame,
            text="Startmenu",
            font=("Arial", 32, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        title.pack(pady=50)

        join_button = tk.Button(
            self.current_frame,
            text="Join Game",
            font=("Arial", 20),
            width=20,
            command=self.start_game
        )
        join_button.pack(pady=20)

        settings_button = tk.Button(
            self.current_frame,
            text="Settings",
            font=("Arial", 20),
            width=20,
            command=self.show_settings
        )
        settings_button.pack(pady=20)

        quit_button = tk.Button(
            self.current_frame,
            text="Quit",
            font=("Arial", 20),
            width=20,
            command=self.root.destroy
        )
        quit_button.pack(pady=20)

    def show_settings(self):
        """Viser settings-menuen."""
        self.clear_frame()

        self.current_frame = tk.Frame(self.root, bg="#2b2b2b")
        self.current_frame.pack(fill="both", expand=True)

        title = tk.Label(
            self.current_frame,
            text="Settings",
            font=("Arial", 30, "bold"),
            fg="white",
            bg="#2b2b2b"
        )
        title.pack(pady=40)

        music_label = tk.Label(
            self.current_frame,
            text="Musik lydstyrke",
            font=("Arial", 18),
            fg="white",
            bg="#2b2b2b"
        )
        music_label.pack(pady=10)

        music_slider = tk.Scale(
            self.current_frame,
            from_=0,
            to=100,
            orient="horizontal",
            length=400,
            font=("Arial", 14),
            command=self.update_music_volume
        )
        music_slider.set(self.music_volume)
        music_slider.pack(pady=10)

        sfx_label = tk.Label(
            self.current_frame,
            text="Lydeffekter lydstyrke",
            font=("Arial", 18),
            fg="white",
            bg="#2b2b2b"
        )
        sfx_label.pack(pady=10)

        sfx_slider = tk.Scale(
            self.current_frame,
            from_=0,
            to=100,
            orient="horizontal",
            length=400,
            font=("Arial", 14),
            command=self.update_sfx_volume
        )
        sfx_slider.set(self.sfx_volume)
        sfx_slider.pack(pady=10)

        back_button = tk.Button(
            self.current_frame,
            text="Tilbage",
            font=("Arial", 18),
            width=15,
            command=self.show_start_menu
        )
        back_button.pack(pady=40)

    def update_music_volume(self, value):
        """Gemmer musik-lydstyrken."""
        self.music_volume = int(value)
        print("Musik volumen:", self.music_volume)

    def update_sfx_volume(self, value):
        """Gemmer lydeffekt-lydstyrken."""
        self.sfx_volume = int(value)
        print("SFX volumen:", self.sfx_volume)

    def start_game(self):
        """Starter spillet."""
        self.clear_frame()

        self.current_frame = tk.Frame(self.root, bg="black")
        self.current_frame.pack(fill="both", expand=True)

        top_bar = tk.Frame(self.current_frame, bg="#222222", height=60)
        top_bar.pack(fill="x")

        back_button = tk.Button(
            top_bar,
            text="Tilbage til menu",
            font=("Arial", 14),
            command=self.show_start_menu
        )
        back_button.pack(side="left", padx=20, pady=10)

        canvas = tk.Canvas(
            self.current_frame,
            width=1600,
            height=900,
            bg="black",
            highlightthickness=0
        )
        canvas.pack(fill="both", expand=True)

        game_map = GameMap(canvas)
        game_map.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
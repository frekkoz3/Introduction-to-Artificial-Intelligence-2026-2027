class GameSetting:

    def __init__(self, difficulty : int =  0):
        if difficulty not in (0, 1):
            raise ValueError(f"Unsupported difficulty {difficulty!r}. Supported levels: 0 and 1.")
        self.difficulty = difficulty
        self.cell_size = 35
        self._load_variable_settings()
        self.width = self.grid_width * self.cell_size
        self.height = self.grid_height * self.cell_size
        self.status_bar = False
        self.bar_height = 2 * self.cell_size if self.status_bar else 0
        self.total_height = self.height + self.bar_height
        self.fps = 30


    def _load_variable_settings(self):

        if self.difficulty == 0:
            self.grid_width = 4
            self.grid_height = 3
            self.n_obstacles = 0
            self.n_dirt = 1

        if self.difficulty == 1:
            self.grid_width = 10
            self.grid_height = 10
            self.n_obstacles = 0
            self.n_dirt = 10

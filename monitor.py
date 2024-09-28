import random

from grid import Grid

class ANTSMonitor:
    def __init__(self, width, height, n_porters, n_cargos, n_dests, min_weight, max_weight):
        self.grid = Grid(width, height)
        self.grid.random_intialize(n_porters, n_cargos, n_dests, min_weight, max_weight)
    
    def run(self, max_steps=5):
        for i in range(max_steps):
            print("*"*10 + f"Step {i}" + "*"*10 + "\n")
            actions = {}
            for porter in self.grid.objects["porter"]:
                bias_x = random.randint(-1, 1)
                bias_y = 0 if bias_x != 0 else random.choice([-1, 1])
                actions[porter.porter_id] = {"type": "move to", "args": {"x": (porter.x + bias_x), "y": (porter.y + bias_y)}}
            self.grid.update(actions)
            print(self.grid.get_state_str())
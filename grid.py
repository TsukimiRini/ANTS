import random
from objects import Porter, Cargo, Destination, GridObjType

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.content = []

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Cell(x, y) for x in range(width)] for y in range(height)]
        self.objects = {
            "porter": [],
            "cargo": [],
            "destination": [],
        }
    
    def random_dests(self, n):
        for i in range(n):
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if len([obj for obj in self.grid[x][y].content if obj.type == GridObjType.DESTINATION]) == 0:
                    self.objects["destination"].append(Destination(self, x, y))
                    break
        return self.objects["destination"]

    def random_cargos(self, n, min_weight, max_weight):
        for i in range(n):
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if len([obj for obj in self.grid[x][y].content if obj.type == GridObjType.DESTINATION]) == 0:
                    self.objects["cargo"].append(Cargo(self, x, y, random.randint(min_weight, max_weight)))
                    break
        return self.objects["cargo"]
    
    def random_porters(self, n):
        for i in range(n):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.objects["porter"].append(Porter(self, i, x, y))
        return self.objects["porter"]
    
    def random_intialize(self, n_porters, n_cargos, n_dests, min_weight, max_weight):
        self.random_porters(n_porters)
        self.random_cargos(n_cargos, min_weight, max_weight)
        self.random_dests(n_dests)
        
    def update(self, actions):
        for porter in self.objects["porter"]:
            action = actions[porter.porter_id]
            porter.operations[action["type"]](**(action["args"]))
        
    def get_state(self):
        state = {}
        for idx, dest in enumerate(self.objects["destination"]):
            state[f"destination {idx}"] = {
                "x": dest.x,
                "y": dest.y,
            }
        
        for porter in self.objects["porter"]:
            state[f"porter {porter.porter_id}"] = {
                "x": porter.x,
                "y": porter.y,
                "state": porter.state,
                "carrying": porter.carrying,
            }
        
        for idx, cargo in enumerate(self.objects["cargo"]):
            state[f"cargo {idx}"] = {
                "x": cargo.x,
                "y": cargo.y,
                "weight": cargo.weight,
            }
        return state

    def get_state_str(self):
        state = self.get_state()
        state_str = ""
        for key, value in state.items():
            state_str += f"{key}: "
            x = value["x"]
            y = value["y"]
            state_str += f"({x}, {y})"
            if "state" in value:
                state_str += f" status: {value['state']}"
            if "weight" in value:
                state_str += f" weight: {value['weight']}"
            state_str += "\n"
        return state_str
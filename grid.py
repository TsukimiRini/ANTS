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
        return dests

    def random_cargos(self, n, min_weight, max_weight):
        for i in range(n):
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if len([obj for obj in self.grid[x][y].content if obj.type == GridObjType.DESTINATION]) == 0:
                    self.objects["cargo"].append(Cargo(self, x, y, random.randint(min_weight, max_weight)))
                    break
        return cargos
    
    def random_porters(self, n):
        for i in range(n):
            self.objects["porter"].append(Porter(self, i, x, y))
        return porters
    
    def random_intialize(self, n_porters, n_cargos, n_dests, min_weight, max_weight):
        self.random_porters(n_porters)
        self.random_cargos(n_cargos, min_weight, max_weight)
        self.random_dests(n_dests)
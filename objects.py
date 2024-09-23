from enum import Enum

class GridObjType(Enum):
    UNDEFINED = "UNDEFINED"
    DESTINATION = "DESTINATION"
    WALL = "WALL"
    CARGO = "CARGO"
    PORTER = "PORTER"

class GridObject:
    def __init__(self, grid, x, y, type_label):
        self.type = type_label
        self.x = x
        self.y = y
        self.grid = grid
        self.grid.grid[x][y].content.append(self)
    
    def move_to(x, y):
        if abs(self.x - x) + abs(self.y - y) == 1 and x >= 0 and x < self.grid.width and y >= 0 and y < self.grid.height:
            self.grid.grid[self.x][self.y].content.remove(self)
            self.x = x
            self.y = y
            self.grid.grid[x][y].content.append(self)
            return True
        return False

class Cargo(GridObject):
    def __init__(self, grid, x, y, weight):
        super().__init__(grid, x, y, GridObjType.CARGO)
        self.weight = weight
    
class Destination(GridObject):
    def __init__(self, grid, x, y):
        super().__init__(grid, x, y, GridObjType.DESTINATION)
    
class Porter(GridObject):
    class PorterState(Enum):
        IDLE = "IDLE"
        READY_FOR_PICKUP = "READY_FOR_PICKUP"
        CARRYING = "CARRYING"
        READY_FOR_DROP = "READY_FOR_DROP"
        
    class OperationResponse(Enum):
        SUCCESS = "Success"
        NOT_READY = "Not ready"
        NO_CARGO = "No cargo to pick up"
        ALREADY_CARRYING = "Already carrying cargo"
        NOT_ENOUGH_CAPACITY = "Not enough capacity"
        NO_PORTER = "No porter to speak to"
    
    def __init__(self, grid, id, x, y):
        super().__init__(grid, x, y, GridObjType.PORTER)
        self.porter_id = id
        self.operations = {
            "speak to": self.speak_to,
            "move to": self.move_to,
            "pick up": self.prepare_pick_up,
            "drop": self.prepare_drop,
            "wait": self.wait,
        }
        self.state = PorterState.IDLE
        self.carrying = None
        self.capacity = 1
    
    def state_to_operation(state):
        if state == PorterState.IDLE:
            return ["move to", "pick up", "wait", "speak to"]
        elif state == PorterState.READY_FOR_PICKUP:
            return []
        elif state == PorterState.CARRYING:
            return ["move to", "drop", "wait", "speak to"]
    
    def speak_to(porters, msg):
        pass
    
    def prepare_pick_up(cargo):
        if self.grid[self.x][self.y].type != GridObjType.CARGO:
            return OperationResponse.NO_CARGO
        self.state = PorterState.READY_FOR_PICKUP
        return OperationResponse.SUCCESS

    def pick_up(cargo):
        if self.state != PorterState.READY_FOR_PICKUP:
            return OperationResponse.NOT_READY
        self.carrying = cargo
        self.state = PorterState.CARRYING
        return OperationResponse.SUCCESS
    
    def prepare_drop(x, y):
        self.carrying = None
        self.state = PorterState.READY_FOR_DROP
        return OperationResponse.SUCCESS
    
    def drop(x, y):
        if self.state != PorterState.READY_FOR_DROP:
            return OperationResponse.NOT_READY
        self.state = PorterState.IDLE
        return OperationResponse.SUCCESS
    
    def wait():
        return OperationResponse.SUCCESS
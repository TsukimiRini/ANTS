import regex as re

from enum import Enum
from openai import OpenAI
from typing import List

operation_mapping = {
    "move to": "move to [point]",
    "pick up": "pick up cargo",
    "drop": "drop currently carried cargo",
    "wait": "wait in place",
    "speak to": "speak to [porterID1], [porterID2], ...: [message]"
}

class RequestAndParse:
    def __init__(self):
        self.models = {}
        
    def request(self, client, prompt=None, context=None):
        messages = []
        if context is not None:
            for role, content in context:
                messages.append({"role": role, "content": content})
        if prompt is not None:
            messages.append({"role": "user", "content": prompt})
        
        if client not in self.models:
            self.models[client] = client.models.list().data[0].id
        try:
            completion = client.completions_create(
                model=self.models[client],
                temperature=0.2,
                messages=messages,
                stream=False)
        except Exception as e:
            return request(client, prompt)
        
        return completion.choices[0].message.content
    
    def extract_point(self, line):
        regex = r"\((\d+), (\d+)\)"
        matches = re.finditer(regex, line)
        for matchNum, match in enumerate(matches, start=1):
            return int(match.group(1)), int(match.group(2))
        return None, None
    
    def parse_action_respponse(self, response):
        actions = []
        lines = response.split("\n")
        for line in lines:
            if "move to" in line:
                x, y = self.extract_point(line)
                actions.append({
                    "type": "move to",
                    "args": {"x": x, "y": y}
                })
            elif "pick up" in line:
                actions.append({
                    "type": "pick up",
                    "args": {}
                })
            elif "drop" in line:
                actions.append({
                    "type": "drop",
                    "args": {}
                })
            elif "wait" in line:
                actions.append({
                    "type": "wait",
                    "args": {}
                })
            elif "speak to" in line:
                actions.append({
                    "type": "speak to",
                    "args": {
                        "porters": [int(s) for s in line.split("speak to ")[-1].split(", ") if s.isdigit()],
                        "msg": line.split(": ")[-1]
                    }
                })
        
        return actions

request_and_parse = RequestAndParse()

class GridObjType(Enum):
    UNDEFINED = "UNDEFINED"
    DESTINATION = "DESTINATION"
    WALL = "WALL"
    CARGO = "CARGO"
    PORTER = "PORTER"

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
    NO_PORTER = "No porter to speak to in the range"

class GridObject:
    def __init__(self, grid, x, y, type_label):
        self.type = type_label
        self.x = x
        self.y = y
        self.grid = grid
        self.grid.grid[x][y].content.append(self)
    
    def get_range(self, distance=2):
        return [(x, y) for x in range(self.x - distance, self.x + distance + 1) for y in range(self.y - distance, self.y + distance + 1) if x >= 0 and x < self.grid.width and y >= 0 and y < self.grid.height]
    
    def within_range(self, obj, distance=1):
        if max(abs(self.x - obj.x), abs(self.y - obj.y)) <= distance:
            return True
        return False
    
    def within_range_point(self, x, y, distance=1):
        if max(abs(self.x - x), abs(self.y - y)) <= distance:
            return True
        return False
    
    def move_to(self, x, y):
        if self.within_range_point(x, y, 1) and x >= 0 and x < self.grid.width and y >= 0 and y < self.grid.height:
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
    def __init__(self, grid, id, x, y, host, port):
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
        request_url = f"http://{host}:{port}/v1"
        self.client = OpenAI(api_key="EMPTY", base_url=request_url)
        self.contexts = {}
    
    def state_to_operation(self, state=self.state):
        if state == PorterState.IDLE:
            return ["move to", "pick up", "wait", "speak to"]
        elif state == PorterState.READY_FOR_PICKUP:
            return []
        elif state == PorterState.CARRYING:
            return ["move to", "drop", "wait", "speak to"]
    
    def get_observation(self, distance=2):
        observations = []
        for x in range(self.x - distance, self.x + distance + 1):
            for y in range(self.y - distance, self.y + distance + 1):
                if x >= 0 and x < self.grid.width and y >= 0 and y < self.grid.height:
                    for obj in self.grid.grid[x][y].content:
                        observations.append(obj)
        
        return observations

    def request_operation(self):
        dest_x, dest_y = self.grid.objects["destination"][0].x, self.grid.objects["destination"][0].y
        observations = self.get_observation()
        observation_str = ""
        for idx, obj in enumerate(observations):
            if obj.type == GridObjType.PORTER:
                observation_str += f" ({idx}) porter {obj.porter_id} at ({obj.x}, {obj.y}),"
            elif obj.type == GridObjType.CARGO:
                observation_str += f" ({idx}) cargo at ({obj.x}, {obj.y}), requiring {obj.weight} porters to transport,"
        observation_str = observation_str[:-1]
        
        available_operations = self.state_to_operation(self.state)
        opeartion_str = ""
        for idx, operation in enumerate(available_operations):
            opeartion_str += f"- {operation_mapping[operation]}\n"
        opeartion_str = opeartion_str[:-1]
        
        prompt = f"""You are a porter, and your ID is {self.porter_id}. Your mission is to search for cargos on a huge ground and carry them back to a truck.
You carry out the mission together with your collegues. On the ground, there are about 10 porters searching and transporting cargos. Most of the cargos require multiple porters to work together to transport.
The ground is a {self.grid.width}*{self.grid.height} square, where the truck is located in the cell ({dest_x}, {dest_y}) and you are now in the point ({self.x}, {self.y}).
Now you see around and find:{observation_str}.
What will you do next?
Your answer should be one action in one of the following format:
{opeartion_str}
You can only speak to a porter when he is nearby, i.e. your distance from the target porter is less than 2.
You can only move to a cell when the cell is next to you, i.e. your distance from the cell is 1.
You can only pick up a cargo when enough porters are in the same cell of the cargo, i.e. there are totally at least n porters whose distance from the cargo is 0 when the cargo requires n porters to transport.
You can drop a cargo you are carrying in the current cell you are in.
*The distance is calculated by the Chebyshev distance.
"""
        self.contexts[self.grid.step] = [("user", prompt)]
        response = request_and_parse.request(self.client, prompt)
        self.contexts[self.grid.step].append(("assistant", response))
        response_actions = request_and_parse.parse_action_respponse(response)
        return response_actions
    
    def request_updated_operation(self):
        response = request_and_parse.request(self.client, context=self.contexts[self.grid.step])
        self.contexts[self.grid.step].append(("assistant", response))
        response_actions = request_and_parse.parse_action_respponse(response)
        return response_actions
    
    def re_request_operation(self, new_obs):
        if new_obs == None or len(new_obs) == 0:
            return None
        new_obs_str = ""
        for obs in new_obs:
            assert obs["type"] in ["move to", "pick up", "drop", "speak to", "wait"]
            if obs["type"] == "move to":
                new_obs_str += f"- porter {obs['porter']} moved to ({obs.x}, {obs.y})\n"
            elif obs["type"] == "pick up":
                new_obs_str += f"- porter {obs['porter']} ready to pick up a cargo\n"
            elif obs["type"] == "drop":
                new_obs_str += f"- porter {obs['porter']} ready to drop a cargo\n"
            elif obs["type"] == "speak to":
                spoken_porters = ", ".join([f"porter {porter}" for porter in obs["args"]["porters"]])
                new_obs_str += f"- porter {obs['porter']} spoke to {spoken_porters}: {obs['args']['msg']}\n"
        if len(new_obs_str) == 0:
            return None
        new_obs_str = new_obs_str[:-1]
        prompt = f"""Before you take any action, other porters nearby have taken some new actions:
{new_obs_str}
What will you do next? You can keep the same action as before or change it.
Your answer should be in the same format as before and include one action you want to take.
You should still follow the rules mentioned before and make sure your action is valid.
"""
        self.contexts[self.grid.step] = [("user", prompt)]
        response = request_and_parse.request(self.client, prompt)
        self.contexts[self.grid.step].append(("assistant", response))
        response_actions = request_and_parse.parse_action_respponse(response)
        return response_actions

    def request_operation_revision(self, errors):
        error_str = ""
        for error in errors:
            error_str += f"- {error}\n"
        error_str = error_str[:-1]
        prompt = f"""The actions you provided are not valid due to the following reasons:
{error_str}
Please provide a new set of actions that are valid.
Your answer should be in the same format as before and include one action you want to take.
You should still follow the rules mentioned before and make sure your action is valid.
"""
        self.contexts[self.grid.step] = [("user", prompt)]
        response = request_and_parse.request(self.client, prompt)
        self.contexts[self.grid.step].append(("assistant", response))
        response_actions = request_and_parse.parse_action_respponse(response)
        return response_actions
    
    def take_actions(self, actions):
        success_actions = []
        errored_actions = []
        for action in actions:
            response = self.operations[action["type"]](**action["args"])
            if response != OperationResponse.SUCCESS:
                errored_actions.append((action, response))
            else:
                success_actions.append(action)
        
        return success_actions, errored_actions
    
    def speak_to(self, porters:List[int], msg:str):
        actual_porters = []
        for porter in porters:
            porter_obj = self.grid.objects["porter"][porter]
            if self.within_range(porter_obj, 2):
                actual_porters.append(porter_obj)
        
        if len(actual_porters) == 0:
            return OperationResponse.NO_PORTER
        
        return OperationResponse.SUCCESS
    
    def prepare_pick_up(self, cargo):
        if self.grid[self.x][self.y].type != GridObjType.CARGO:
            return OperationResponse.NO_CARGO
        self.state = PorterState.READY_FOR_PICKUP
        return OperationResponse.SUCCESS

    def pick_up(self, cargo):
        if self.state != PorterState.READY_FOR_PICKUP:
            return OperationResponse.NOT_READY
        self.carrying = cargo
        self.state = PorterState.CARRYING
        return OperationResponse.SUCCESS
    
    def prepare_drop(self, x, y):
        self.carrying = None
        self.state = PorterState.READY_FOR_DROP
        return OperationResponse.SUCCESS
    
    def drop(self, x, y):
        if self.state != PorterState.READY_FOR_DROP:
            return OperationResponse.NOT_READY
        self.state = PorterState.IDLE
        return OperationResponse.SUCCESS
    
    def wait(self):
        return OperationResponse.SUCCESS
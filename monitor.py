import random

from grid import Grid

class ANTSMonitor:
    def __init__(self, width, height, n_porters, n_cargos, n_dests, min_weight, max_weight):
        self.grid = Grid(width, height)
        self.grid.random_intialize(n_porters, n_cargos, n_dests, min_weight, max_weight)
    
    def run(self, max_steps=5):
        for i in range(max_steps):
            print("*"*10 + f"Step {i}" + "*"*10 + "\n")
            self.step()
            print(self.grid.get_state_str())
            
    def step(self):
        draft_actions = self.request_all_porter_actions()
        sequence = [porter for porter in draft_actions]
        random.shuffle(sequence)
        action_contexts = {}
        for index, porter in enumerate(sequence):
            porter_obj = self.grid.get_porter(porter)
            range_points = porter_obj.get_range()
            observed_new_actions = []
            for range_point in range_points:
                if range_point in action_contexts:
                    observed_new_actions.append(action_contexts[range_point])
            observed_new_actions = list(set(observed_new_actions))
            observed_new_actions = observed_new_actions.sort(key=lambda x: x["timestamp"])
            
            re_requested_operations = porter_obj.re_request_operation(observed_new_actions)
            if re_requested_operations is not None:
                draft_actions[porter] = re_requested_operations
                
            
            before_x, before_y = porter_obj.x, porter_obj.y
            successed, errored = porter_obj.take_actions(draft_actions[porter])
            after_x, after_y = porter_obj.x, porter_obj.y
            
            for action in successed:
                action["porter_id"] = porter
                action["timestamp"] = index
            
            if (before_x, before_y) not in action_contexts:
                action_contexts[(before_x, before_y)] = []
            action_contexts[(before_x, before_y)].extend(successed)
            if (after_x, after_y) not in action_contexts:
                action_contexts[(after_x, after_y)] = []
            action_contexts[(after_x, after_y)].extend(successed)
        
    def request_all_porter_actions(self):
        actions = {}
        for porter in self.grid.objects["porter"]:
            actions[porter.porter_id] = porter.request_operation()
        return actions
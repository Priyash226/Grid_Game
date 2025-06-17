import numpy as np
import random

class GridEnvironment:
    def __init__(self, grid_size=10):
        self.grid_size = grid_size
        self.grid = np.zeros((grid_size, grid_size))
        self.agent_pos = [0, 0]
        self.goal_pos = [grid_size-1, grid_size-1]
        self.visited = set()
        self.reset()
    
    def reset(self):
        self.grid.fill(0)
        self.agent_pos = [0, 0]
        self.goal_pos = [self.grid_size-1, self.grid_size-1]
        self.visited = set()
        self.visited.add(tuple(self.agent_pos))
        
        # Place elements
        self._place_elements(1, 10)  # Obstacles
        self._place_elements(2, 5)    # Rewards
        self._place_elements(3, 5)    # Penalties
        self.grid[self.goal_pos[0]][self.goal_pos[1]] = 4  # Goal
        
    def _place_elements(self, element_type, count):
        placed = 0
        while placed < count:
            # Avoid placing obstacles near start and goal
            x, y = random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)
            start_dist = abs(x - 0) + abs(y - 0)
            goal_dist = abs(x - (self.grid_size-1)) + abs(y - (self.grid_size-1))
            
            if (start_dist < 3 or goal_dist < 3):  # Keep start and goal areas clear
                continue
            if self.grid[x][y] != 0:
                continue
                
            self.grid[x][y] = element_type
            placed += 1
    
    def get_cell_value(self, x, y):
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return self.grid[x][y]
        return None
    
    def is_valid_position(self, x, y):
        return (0 <= x < self.grid_size and 
                0 <= y < self.grid_size and 
                self.grid[x][y] != 1)  # Not an obstacle
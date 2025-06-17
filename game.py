import time

class GridGame:
    def __init__(self, grid_size=10, time_limit=30):
        self.grid_size = grid_size
        self.time_limit = time_limit
        self.score = 0
        self.steps = 0
        self.game_over = False
        self.won = False
        self.start_time = 0
        self.showing_path = False
        self.move_direction = None
        self.move_progress = 0
        self.animation_path = []
        self.animation_index = 0
        self.animation_speed = 1.0
    
    def reset(self):
        self.score = 0
        self.steps = 0
        self.game_over = False
        self.won = False
        self.start_time = time.time()
        self.showing_path = False
        self.move_direction = None
        self.move_progress = 0
        self.animation_path = []
        self.animation_index = 0
    
    def check_time_limit(self):
        elapsed = time.time() - self.start_time
        if elapsed > self.time_limit and not self.game_over:
            self.game_over = True
            self.won = False
            return True
        return False
    
    def update_agent_position(self, new_pos, grid):
        x, y = new_pos
        cell_value = grid[x][y]
        
        if cell_value == 2:  # Reward
            self.score += 15  # Increased from 10
            return 15, False
        elif cell_value == 3:  # Penalty
            self.score -= 5   # Reduced from -10
            return -5, False
        elif cell_value == 4:  # Goal
            self.score += 150  # Increased from 100
            self.game_over = True
            self.won = True
            return 150, True
        else:  # Empty cell
            self.score -= 0.5  # Reduced penalty from -1
            return -0.5, False
    
    def update_animation(self):
        if self.move_progress < 1:
            self.move_progress = min(1, self.move_progress + 0.1)
            return False
        
        if (self.animation_index < len(self.animation_path) - 1 and 
            time.time() - self.last_animation_time > self.animation_speed):
            self.animation_index += 1
            self.last_animation_time = time.time()
            self.move_progress = 0
            return True
        
        return False
import numpy as np
import random

class QLearningAgent:
    def __init__(self, grid_size, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.grid_size = grid_size
        self.learning_rate = learning_rate  # How much new info overrides old
        self.discount_factor = discount_factor  # Importance of future rewards
        self.epsilon = epsilon  # Exploration rate
        
        # Initialize Q-table with zeros
        self.q_table = np.zeros((grid_size, grid_size, 4))  # (x, y, action)
        self.actions = [0, 1, 2, 3]  # Up, Right, Down, Left
        self.visited_counts = np.zeros((grid_size, grid_size))
    
    def get_valid_actions(self, state, grid):
        """Returns list of valid actions from current state"""
        x, y = state
        valid_actions = []
        
        if x > 0 and grid[x-1][y] != 1: valid_actions.append(0)  # Up
        if y < self.grid_size-1 and grid[x][y+1] != 1: valid_actions.append(1)  # Right
        if x < self.grid_size-1 and grid[x+1][y] != 1: valid_actions.append(2)  # Down
        if y > 0 and grid[x][y-1] != 1: valid_actions.append(3)  # Left
        
        return valid_actions
    
    def get_goal_directed_actions(self, state, goal, grid):
        """Prioritize moves that reduce distance to goal"""
        x, y = state
        gx, gy = goal
        preferred_actions = []
        
        # Prefer moves toward goal
        if x > gx and grid[x-1][y] != 1: preferred_actions.append(0)  # Up
        if y < gy and grid[x][y+1] != 1: preferred_actions.append(1)  # Right
        if x < gx and grid[x+1][y] != 1: preferred_actions.append(2)  # Down
        if y > gy and grid[x][y-1] != 1: preferred_actions.append(3)  # Left
        
        return preferred_actions if preferred_actions else self.get_valid_actions(state, grid)
    
    def get_action(self, state, valid_actions):
        """Choose action using ε-greedy policy"""
        if random.random() < self.epsilon:  # Exploration
            return random.choice(valid_actions)
        
        # Exploitation: choose best action from Q-table
        q_values = [self.q_table[state[0]][state[1]][a] if a in valid_actions else -np.inf 
                   for a in self.actions]
        return np.argmax(q_values)
    
    def update_q_table(self, state, action, reward, new_state):
        """Update Q-value using Bellman equation"""
        best_future_q = np.max(self.q_table[new_state[0]][new_state[1]])
        current_q = self.q_table[state[0]][state[1]][action]
        
        # Q-learning formula
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * best_future_q - current_q
        )
        self.q_table[state[0]][state[1]][action] = new_q
    
    def get_optimized_path(self, start_pos, goal_pos, grid):
        """Find path using current Q-table"""
        path = []
        current_pos = list(start_pos)
        visited = set()
        
        for _ in range(self.grid_size * 2):  # Prevent infinite loops
            x, y = current_pos
            visited.add((x, y))
            path.append([x, y])
            
            if (x, y) == tuple(goal_pos):
                break
            
            valid_actions = self.get_goal_directed_actions((x, y), goal_pos, grid)
            if not valid_actions:
                break
                
            # Choose action with highest Q-value
            action = self.get_action((x, y), valid_actions)
            
            # Move according to action
            if action == 0: x -= 1
            elif action == 1: y += 1
            elif action == 2: x += 1
            elif action == 3: y -= 1
            
            current_pos = [x, y]
        
        return path
    
    def reset_visits(self):
        """Reset visit counts"""
        self.visited_counts.fill(0)
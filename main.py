import pygame
import time
import sys
import numpy as np
from environment import GridEnvironment
from agent import QLearningAgent
from game import GridGame
from ui import GameUI

def main():
    # Game configuration for higher win rate
    grid_size = 10
    time_limit = 30  # Double the time limit
    learning_params = {
        'learning_rate': 0.4,    # Faster learning
        'discount_factor': 0.97, # More future reward consideration
        'epsilon': 0.1           # Less random exploration
    }
    
    # Initialize game components
    try:
        print("Creating optimized game environment...")
        environment = GridEnvironment(grid_size)
        
        # Easier game configuration
        environment.obstacle_count = 4           # Reduced obstacles
        environment.reward_count = 10            # More rewards
        environment.penalty_count = 2            # Fewer penalties
        environment.min_goal_distance = 8        # Ensure goal isn't too close
        environment.reset()
        
        print("Creating smarter AI agent...")
        agent = QLearningAgent(grid_size, **learning_params)
        
        print("Initializing game state...")
        game_state = GridGame(grid_size, time_limit)
        game_state.animation_speed = 0.3         # Faster visual feedback
        game_state.reward_value = 15             # Higher reward points
        game_state.penalty_value = -3            # Reduced penalty impact
        game_state.goal_value = 150              # More valuable goal
        
        ui = GameUI()
        print("All components initialized successfully")
    except Exception as e:
        print(f"Initialization failed: {e}")
        return

    # Game loop variables
    running = True
    auto_play = True
    clock = pygame.time.Clock()
    last_move_time = time.time()
    move_interval = 0.4  # seconds between moves

    print("\nGame Controls:")
    print("- SPACE: Toggle AI/Path view")
    print("- R: Reset game")
    print("- +/-: Adjust speed")
    print("\nStarting main game loop...")

    while running:
        current_time = time.time()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_state.game_over:
                    game_state.showing_path = not game_state.showing_path
                    if game_state.showing_path:
                        game_state.animation_path = agent.get_optimized_path(
                            environment.agent_pos,
                            environment.goal_pos,
                            environment.grid
                        )
                        game_state.animation_index = 0
                elif event.key == pygame.K_r:
                    environment.reset()
                    agent = QLearningAgent(grid_size, **learning_params)
                    game_state.reset()
                    last_move_time = current_time
                elif event.key == pygame.K_PLUS:
                    move_interval = min(1.5, move_interval + 0.1)
                elif event.key == pygame.K_MINUS:
                    move_interval = max(0.1, move_interval - 0.1)

        # Game logic
        if not game_state.game_over:
            if current_time - last_move_time > move_interval:
                last_move_time = current_time
                
                if not game_state.showing_path and auto_play:
                    state = environment.agent_pos
                    goal = environment.goal_pos
                    
                    # Get actions prioritized toward goal
                    valid_actions = agent.get_goal_directed_actions(
                        state, 
                        goal, 
                        environment.grid
                    )
                    
                    if valid_actions:
                        action = agent.get_action(state, valid_actions)
                        new_pos = list(state)
                        # Update position based on action
                        if action == 0: new_pos[0] -= 1
                        elif action == 1: new_pos[1] += 1
                        elif action == 2: new_pos[0] += 1
                        elif action == 3: new_pos[1] -= 1
                        
                        if (0 <= new_pos[0] < grid_size and 
                            0 <= new_pos[1] < grid_size and
                            environment.grid[new_pos[0]][new_pos[1]] != 1):
                            
                            environment.agent_pos = new_pos
                            environment.visited.add(tuple(new_pos))
                            
                            # Calculate rewards
                            cell_value = environment.grid[new_pos[0]][new_pos[1]]
                            if cell_value == 2:    # Reward
                                reward = game_state.reward_value
                                environment.grid[new_pos[0]][new_pos[1]] = 0
                            elif cell_value == 3:  # Penalty
                                reward = game_state.penalty_value
                            elif cell_value == 4:  # Goal
                                reward = game_state.goal_value
                                game_state.won = True
                                game_state.game_over = True
                            else:                # Empty
                                reward = 1       # Small reward for exploration
                            
                            agent.update_q_table(state, action, reward, new_pos)
                            game_state.score += reward
                            game_state.steps += 1
                
                elif game_state.showing_path:
                    # Follow the precomputed path
                    if game_state.update_animation():
                        new_pos = game_state.animation_path[game_state.animation_index]
                        environment.agent_pos = new_pos
                        if environment.grid[new_pos[0]][new_pos[1]] == 4:
                            game_state.score += game_state.goal_value
                            game_state.won = True
                            game_state.game_over = True

        # Check time limit
        game_state.check_time_limit()
        
        # Rendering
        try:
            ui.draw(environment, game_state, environment.agent_pos, agent,
                    game_state.move_progress, game_state.move_direction)
        except Exception as e:
            print(f"Rendering error: {e}")
            running = False
        
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    print("Launching Optimized Grid Game...")
    main()
    print("Game session ended")
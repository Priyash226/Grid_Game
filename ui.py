import pygame
import os
import time
from pygame.locals import *

class GameUI:
    def __init__(self, width=900, height=700, grid_size=10, cell_size=60, agent_size=50):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.agent_size = agent_size
        self.margin_x = (width - grid_size * cell_size) // 2
        self.margin_y = 100
        
        # Color definitions
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.DARK_BLUE = (0, 0, 139)
        self.LIGHT_BLUE = (173, 216, 230)
        
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AI Grid Adventure")
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        
        self.images = self._load_images()

    def _load_images(self):
        """Load game images from assets folder"""
        images = {}
        asset_files = {
            'agent': 'agent.png',
            'fire': 'fire.png',
            'goal': 'goal.png',
            'reward': 'reward.png',
            'obstacle': 'obstacle.png'
        }
        
        # Create assets folder if it doesn't exist
        if not os.path.exists('assets'):
            os.makedirs('assets')
            print("Created assets folder - please add your image files there")
        
        for key, filename in asset_files.items():
            try:
                path = os.path.join('assets', filename)
                if key == 'agent':
                    img = pygame.image.load(path).convert_alpha()
                    images[key] = pygame.transform.scale(img, (self.agent_size, self.agent_size))
                else:
                    img = pygame.image.load(path).convert_alpha()
                    images[key] = pygame.transform.scale(img, (self.cell_size-10, self.cell_size-10))
            except:
                print(f"Could not load {filename}, using placeholder")
                images[key] = self._create_placeholder(key)
        
        return images

    def _create_placeholder(self, image_type):
        """Create colored placeholders if images not found"""
        colors = {
            'agent': (255, 165, 0),    # Orange
            'fire': (255, 0, 0),       # Red
            'goal': (0, 0, 255),       # Blue
            'reward': (0, 255, 0),     # Green
            'obstacle': (0, 0, 0)      # Black
        }
        
        size = self.agent_size if image_type == 'agent' else self.cell_size-10
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill(colors[image_type])
        return surf

    def draw(self, environment, game_state, agent_pos, agent, animation_progress=0, move_direction=None):
        """Main drawing method that renders the entire game"""
        self.screen.fill(self.LIGHT_BLUE)
        self._draw_title()
        self._draw_stats(game_state)
        self._draw_grid(environment, agent)
        self._draw_agent(agent_pos, animation_progress, move_direction)
        
        if game_state.game_over:
            self._draw_game_over(game_state.won, game_state.score)
        
        self._draw_instructions()
        pygame.display.flip()

    def _draw_title(self):
        """Draw the game title"""
        title = self.title_font.render("AI Grid Adventure", True, self.DARK_BLUE)
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 20))

    def _draw_stats(self, game_state):
        """Draw game statistics"""
        elapsed = max(0, game_state.time_limit - (time.time() - game_state.start_time))
        timer_text = self.font.render(f"Time: {int(elapsed)}s", True, self.BLACK)
        score_text = self.font.render(f"Score: {game_state.score}", True, self.BLACK)
        steps_text = self.font.render(f"Steps: {game_state.steps}", True, self.BLACK)
        
        self.screen.blit(timer_text, (50, 70))
        self.screen.blit(score_text, (250, 70))
        self.screen.blit(steps_text, (450, 70))

    def _draw_grid(self, environment, agent):
        """Draw the game grid with all elements"""
        grid_rect = pygame.Rect(
            self.margin_x - 5, 
            self.margin_y - 5, 
            self.grid_size * self.cell_size + 10, 
            self.grid_size * self.cell_size + 10
        )
        pygame.draw.rect(self.screen, self.DARK_BLUE, grid_rect)
        
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                rect = pygame.Rect(
                    self.margin_x + y * self.cell_size, 
                    self.margin_y + x * self.cell_size, 
                    self.cell_size, 
                    self.cell_size
                )
                pygame.draw.rect(self.screen, self.WHITE, rect)
                pygame.draw.rect(self.screen, self.BLACK, rect, 1)
                
                cell_value = environment.grid[x][y]
                if cell_value == 1:  # Obstacle
                    self.screen.blit(self.images['obstacle'], 
                                   (rect.x + (self.cell_size - self.images['obstacle'].get_width())//2, 
                                    rect.y + (self.cell_size - self.images['obstacle'].get_height())//2))
                elif cell_value == 2:  # Reward
                    self.screen.blit(self.images['reward'], 
                                   (rect.x + (self.cell_size - self.images['reward'].get_width())//2, 
                                    rect.y + (self.cell_size - self.images['reward'].get_height())//2))
                elif cell_value == 3:  # Penalty
                    self.screen.blit(self.images['fire'], 
                                   (rect.x + (self.cell_size - self.images['fire'].get_width())//2, 
                                    rect.y + (self.cell_size - self.images['fire'].get_height())//2))
                elif cell_value == 4:  # Goal
                    self.screen.blit(self.images['goal'], 
                                   (rect.x + (self.cell_size - self.images['goal'].get_width())//2, 
                                    rect.y + (self.cell_size - self.images['goal'].get_height())//2))
                
                if (x, y) in environment.visited:
                    visited_rect = pygame.Rect(
                        rect.x + 5, 
                        rect.y + 5, 
                        self.cell_size - 10, 
                        self.cell_size - 10
                    )
                    pygame.draw.rect(self.screen, self.YELLOW, visited_rect, 2)

    def _draw_agent(self, agent_pos, progress, direction):
        """Draw the agent with movement animation"""
        x, y = agent_pos
        base_x = self.margin_x + y * self.cell_size + (self.cell_size - self.agent_size) // 2
        base_y = self.margin_y + x * self.cell_size + (self.cell_size - self.agent_size) // 2
        
        offset_x, offset_y = 0, 0
        if progress < 1 and direction is not None:
            move_dist = self.cell_size * progress
            if direction == 0: offset_y = -move_dist  # Up
            elif direction == 1: offset_x = move_dist  # Right
            elif direction == 2: offset_y = move_dist  # Down
            elif direction == 3: offset_x = -move_dist  # Left
        
        self.screen.blit(self.images['agent'], (base_x + offset_x, base_y + offset_y))

    def _draw_game_over(self, won, score):
        """Draw game over screen"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        if won:
            message = f"You Won! Final Score: {score}"
            color = (0, 255, 0)  # Green
        else:
            message = "Time's Up! You Lost."
            color = (255, 0, 0)   # Red
            
        text = self.title_font.render(message, True, color)
        restart_text = self.font.render("Press R to restart", True, self.WHITE)
        
        self.screen.blit(text, (self.width//2 - text.get_width()//2, self.height//2 - 50))
        self.screen.blit(restart_text, (self.width//2 - restart_text.get_width()//2, self.height//2 + 20))

    def _draw_instructions(self):
        """Draw game instructions"""
        instructions = [
            "SPACE: Toggle AI Learning/Path Display",
            "R: Reset Game",
            "Collect rewards (coins) for +10 points",
            "Avoid fire for -10 points",
            "Reach the goal (treasure) within time limit"
        ]
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, self.DARK_BLUE)
            self.screen.blit(text, (self.margin_x, self.margin_y + self.grid_size * self.cell_size + 20 + i * 30))
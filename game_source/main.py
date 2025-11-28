import pygame
import random
import math
import asyncio
import sys
import time
import datetime

# --- CONFIG ---
FPS = 60
WIDTH, HEIGHT = 800, 800 # Keep standard resolution
ROWS, COLS = 4, 4
OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 193, 180)
FONT_COLOR = (119, 110, 101)

pygame.display.init()
pygame.font.init()
pygame.mixer.quit()

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 Web")

# --- ASSETS MANAGEMENT ---
ASSETS = {}
ASSETS_SMALL = {} # For AI Match mode
VALUES = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
ORIGINAL_IMAGES = {} # Cache original images

def load_original_assets():
    # Load raw images once
    try:
        bg_img = pygame.image.load("assets/Tile Background.png")
        ORIGINAL_IMAGES[0] = bg_img
    except:
        ORIGINAL_IMAGES[0] = None
        
    for val in VALUES:
        try:
            img = pygame.image.load(f"assets/{val} Tile.png")
            ORIGINAL_IMAGES[val] = img
        except:
            # print(f"Warning: Missing image for {val}")
            ORIGINAL_IMAGES[val] = None

def scale_assets(tile_width, tile_height, destination_dict):
    # Scale originals to target size
    if 0 in ORIGINAL_IMAGES and ORIGINAL_IMAGES[0]:
         destination_dict[0] = pygame.transform.scale(ORIGINAL_IMAGES[0], (tile_width, tile_height))
    else:
         destination_dict[0] = None
         
    for val in VALUES:
        if val in ORIGINAL_IMAGES and ORIGINAL_IMAGES[val]:
            destination_dict[val] = pygame.transform.scale(ORIGINAL_IMAGES[val], (tile_width, tile_height))
        else:
            destination_dict[val] = None

load_original_assets()

# --- CLASS DEFINITIONS ---

class Button:
    def __init__(self, x, y, width, height, text, color=(143, 122, 102), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.SysFont("comicsans", 40, bold=True)

    def draw(self, window):
        pygame.draw.rect(window, self.color, self.rect, border_radius=10)
        text_surf = self.font.render(self.text, 1, self.text_color)
        window.blit(text_surf, (self.rect.x + (self.rect.width/2 - text_surf.get_width()/2), 
                                self.rect.y + (self.rect.height/2 - text_surf.get_height()/2)))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Tile:
    def __init__(self, value, row, col, rect_width, rect_height):
        self.value = value
        self.row = row
        self.col = col
        self.rect_width = rect_width
        self.rect_height = rect_height
        # Relative position in grid
        self.x = col * rect_width
        self.y = row * rect_height
        self.font = pygame.font.SysFont("comicsans", int(rect_height * 0.4), bold=True)

    def draw(self, window, offset_x, offset_y, asset_dict):
        draw_x = offset_x + self.x
        draw_y = offset_y + self.y
        
        if self.value in asset_dict and asset_dict[self.value]:
            window.blit(asset_dict[self.value], (draw_x, draw_y))
        else:
            pygame.draw.rect(window, (238, 228, 218), (draw_x, draw_y, self.rect_width, self.rect_height))
            text = self.font.render(str(self.value), 1, FONT_COLOR)
            window.blit(
                text,
                (
                    draw_x + (self.rect_width / 2 - text.get_width() / 2),
                    draw_y + (self.rect_height / 2 - text.get_height() / 2),
                ),
            )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / self.rect_height)
            self.col = math.ceil(self.x / self.rect_width)
        else:
            self.row = math.floor(self.y / self.rect_height)
            self.col = math.floor(self.x / self.rect_width)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]

class Game2048:
    def __init__(self, x, y, width, height, is_ai=False, name="Player"):
        self.x_offset = x
        self.y_offset = y
        self.width = width
        self.height = height
        self.tile_width = width // COLS
        self.tile_height = height // ROWS
        self.is_ai = is_ai
        self.name = name
        self.tiles = {}
        self.score = 0
        self.won = False
        self.lost = False
        self.over = False
        self.move_vel = 20 # Speed of animation
        # Scale assets for this instance
        self.assets = {}
        scale_assets(self.tile_width, self.tile_height, self.assets)
        
        self.generate_tiles()
        
        self.font_score = pygame.font.SysFont("comicsans", 30, bold=True)

    def get_random_pos(self):
        row = None
        col = None
        while True:
            row = random.randrange(0, ROWS)
            col = random.randrange(0, COLS)
            if f"{row}{col}" not in self.tiles:
                break
        return row, col

    def generate_tiles(self):
        for _ in range(2):
            row, col = self.get_random_pos()
            self.tiles[f"{row}{col}"] = Tile(2, row, col, self.tile_width, self.tile_height)

    def draw_grid(self, window):
        # Outline
        pygame.draw.rect(window, OUTLINE_COLOR, (self.x_offset, self.y_offset, self.width, self.height), OUTLINE_THICKNESS)
        for row in range(1, ROWS):
            y = self.y_offset + row * self.tile_height
            pygame.draw.line(window, OUTLINE_COLOR, (self.x_offset, y), (self.x_offset + self.width, y), OUTLINE_THICKNESS)
        for col in range(1, COLS):
            x = self.x_offset + col * self.tile_width
            pygame.draw.line(window, OUTLINE_COLOR, (x, self.y_offset), (x, self.y_offset + self.height), OUTLINE_THICKNESS)

    def draw(self, window):
        # Draw background for tiles
        if 0 in self.assets and self.assets[0]:
            for r in range(ROWS):
                for c in range(COLS):
                    window.blit(self.assets[0], (self.x_offset + c * self.tile_width, self.y_offset + r * self.tile_height))
        else:
             pygame.draw.rect(window, BACKGROUND_COLOR, (self.x_offset, self.y_offset, self.width, self.height))

        for tile in self.tiles.values():
            tile.draw(window, self.x_offset, self.y_offset, self.assets)
        
        self.draw_grid(window)
        
        # Draw Name and Score
        label = f"{self.name}: {self.score}"
        text = self.font_score.render(label, 1, FONT_COLOR)
        window.blit(text, (self.x_offset, self.y_offset - 40))

    def move_tiles(self, direction, clock):
        updated = True
        blocks = set()
        
        # Animation loop logic (simplified from original)
        # Note: To keep it smooth in Async loop, we iterate physics here
        # But since this is called inside main loop, we need to be careful not to block too long.
        # However, original code blocked in a while loop with clock.tick.
        
        if direction == "left":
            sort_func = lambda x: x.col
            reverse = False
            delta = (-self.move_vel, 0)
            boundary_check = lambda tile: tile.col == 0
            get_next_tile = lambda tile: self.tiles.get(f"{tile.row}{tile.col - 1}")
            merge_check = lambda tile, next_tile: tile.x > next_tile.x + self.move_vel
            move_check = lambda tile, next_tile: tile.x > next_tile.x + self.tile_width + self.move_vel
            ceil = True
        elif direction == "right":
            sort_func = lambda x: x.col
            reverse = True
            delta = (self.move_vel, 0)
            boundary_check = lambda tile: tile.col == COLS - 1
            get_next_tile = lambda tile: self.tiles.get(f"{tile.row}{tile.col + 1}")
            merge_check = lambda tile, next_tile: tile.x < next_tile.x - self.move_vel
            move_check = lambda tile, next_tile: tile.x + self.tile_width + self.move_vel < next_tile.x
            ceil = False
        elif direction == "up":
            sort_func = lambda x: x.row
            reverse = False
            delta = (0, -self.move_vel)
            boundary_check = lambda tile: tile.row == 0
            get_next_tile = lambda tile: self.tiles.get(f"{tile.row - 1}{tile.col}")
            merge_check = lambda tile, next_tile: tile.y > next_tile.y + self.move_vel
            move_check = lambda tile, next_tile: tile.y > next_tile.y + self.tile_height + self.move_vel
            ceil = True
        elif direction == "down":
            sort_func = lambda x: x.row
            reverse = True
            delta = (0, self.move_vel)
            boundary_check = lambda tile: tile.row == ROWS - 1
            get_next_tile = lambda tile: self.tiles.get(f"{tile.row + 1}{tile.col}")
            merge_check = lambda tile, next_tile: tile.y < next_tile.y - self.move_vel
            move_check = lambda tile, next_tile: tile.y + self.tile_height + self.move_vel < next_tile.y
            ceil = False

        # --- SIMPLIFIED MOVEMENT LOGIC (NO ANIMATION LOOP) ---

        
        moved = False
        merged_flags = set() # Track merged positions in this turn to avoid double merge

        
        if direction == "left":
             for r in range(ROWS):
                 # Get tiles in this row, sorted by col index (0 to 3)
                 row_tiles = sorted([t for t in self.tiles.values() if t.row == r], key=lambda t: t.col)
                 
                 # Compact to left
                 target_col = 0
                 for i, tile in enumerate(row_tiles):
                     # Check for merge with previous tile in this processed row
                     # Note: we need to track the 'current' state of the row being built
                     pass
                     
        # Actually, easier to implement standard 2048 algorithm on a 4x4 grid logic
        # then update the Tile objects to match the new grid.
        
        grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        for t in self.tiles.values():
            grid[t.row][t.col] = t
            
        new_tiles = {}
        
        # Helper to process a line (row or col)
        def process_line(line):
            nonlocal moved
            # Remove Nones
            compact = [t for t in line if t is not None]
            merged = []
            skip = False
            for i in range(len(compact)):
                if skip:
                    skip = False
                    continue
                if i + 1 < len(compact) and compact[i].value == compact[i+1].value:
                    # Merge
                    doubled_val = compact[i].value * 2
                    # Create a new tile object or update one? 
                    # We keep compact[i] and update value
                    compact[i].value = doubled_val
                    merged.append(compact[i])
                    moved = True # Logic moved (merge count as move)
                    skip = True # Skip next one as it is consumed
                else:
                    merged.append(compact[i])
            
            # Pad with Nones
            while len(merged) < len(line):
                merged.append(None)
            return merged

        if direction == "left":
            for r in range(ROWS):
                line = grid[r] # [T, T, None, T]
                new_line = process_line(line)
                # If line changed, moved=True
                if line != new_line: moved = True # Simple check might fail if objects same but pos diff?
                # Actually we rely on process_line to set moved if merge, 
                # but we also need to check if position changed.
                
                for c in range(COLS):
                    if new_line[c]:
                        t = new_line[c]
                        # Update tile position
                        if t.row != r or t.col != c:
                            moved = True
                            t.row = r
                            t.col = c
                            t.x = c * self.tile_width
                            t.y = r * self.tile_height
                        new_tiles[f"{r}{c}"] = t
                        
        elif direction == "right":
            for r in range(ROWS):
                line = grid[r][::-1] # Process from right
                new_line = process_line(line)
                new_line = new_line[::-1] # Reverse back
                
                for c in range(COLS):
                    if new_line[c]:
                        t = new_line[c]
                        if t.row != r or t.col != c:
                            moved = True
                            t.row = r
                            t.col = c
                            t.x = c * self.tile_width
                            t.y = r * self.tile_height
                        new_tiles[f"{r}{c}"] = t

        elif direction == "up":
            for c in range(COLS):
                line = [grid[r][c] for r in range(ROWS)]
                new_line = process_line(line)
                
                for r in range(ROWS):
                    if new_line[r]:
                        t = new_line[r]
                        if t.row != r or t.col != c:
                            moved = True
                            t.row = r
                            t.col = c
                            t.x = c * self.tile_width
                            t.y = r * self.tile_height
                        new_tiles[f"{r}{c}"] = t

        elif direction == "down":
            for c in range(COLS):
                line = [grid[r][c] for r in range(ROWS)][::-1]
                new_line = process_line(line)
                new_line = new_line[::-1]
                
                for r in range(ROWS):
                    if new_line[r]:
                        t = new_line[r]
                        if t.row != r or t.col != c:
                            moved = True
                            t.row = r
                            t.col = c
                            t.x = c * self.tile_width
                            t.y = r * self.tile_height
                        new_tiles[f"{r}{c}"] = t
        
        if moved:
            self.tiles = new_tiles
            self.update_tiles([]) # Argument ignored in new logic
            return self.end_move()
        
        return "continue"

    def update_tiles(self, sorted_tiles):
        # Simplified: Just check for win condition
        for tile in self.tiles.values():
            if tile.value == 2048:
                self.won = True

    def end_move(self):
        self.score = sum(t.value for t in self.tiles.values())
        if len(self.tiles) == 16:
            self.lost = True
            return "lost"
        row, col = self.get_random_pos()
        self.tiles[f"{row}{col}"] = Tile(random.choice([2, 4]), row, col, self.tile_width, self.tile_height)
        return "continue"
    
    def ai_move_logic(self):
        # Simple AI: Try preferred directions
        moves = ["down", "right", "left", "up"]
        # TODO: Add smarter logic (copy grid and simulate?)
        # For now: Random valid move
        return random.choice(moves)

# --- JS COMMUNICATION ---
def send_score_to_web(score, start_time, end_time, game_mode):
    if sys.platform == "emscripten":
        from platform import window
        s_time_iso = datetime.datetime.fromtimestamp(start_time).isoformat()
        e_time_iso = datetime.datetime.fromtimestamp(end_time).isoformat()
        duration = end_time - start_time
        try:
            window.parent.handleGameover(score, s_time_iso, e_time_iso, duration, game_mode)
        except Exception as e:
            print(f"Error calling JS: {e}")
    else:
        print(f"Game Over ({game_mode})! Score: {score}")

# --- MAIN ---

async def main():
    clock = pygame.time.Clock()
    
    # App States
    STATE_MENU = 0
    STATE_PLAYING = 1
    STATE_GAMEOVER = 2
    
    state = STATE_MENU
    game_mode = "EASY" # EASY or AI_MATCH
    
    # UI Elements
    btn_easy = Button(WIDTH//2 - 100, 300, 200, 60, "EASY MODE")
    btn_ai = Button(WIDTH//2 - 100, 400, 200, 60, "AI MATCH")
    
    # User asked: "Start button -> then 2 modes".
    btn_main_start = Button(WIDTH//2 - 100, 350, 200, 80, "START GAME")
    
    menu_phase = 0 # 0: Main Start, 1: Mode Select
    
    # Game Instances
    games = []
    
    start_timestamp = 0
    
    # AI Timer
    ai_move_timer = 0
    AI_DELAY = 500 # ms

    run = True
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if state == STATE_MENU:
                    if menu_phase == 0:
                        if btn_main_start.is_clicked(pos):
                            menu_phase = 1
                    elif menu_phase == 1:
                        if btn_easy.is_clicked(pos):
                            game_mode = "EASY"
                            games = [Game2048(100, 100, 600, 600, is_ai=False, name="Player")]
                            state = STATE_PLAYING
                            start_timestamp = time.time()
                        elif btn_ai.is_clicked(pos):
                            game_mode = "AI_MATCH"

                            games = [
                                Game2048(20, 200, 370, 370, is_ai=False, name="You"),
                                Game2048(410, 200, 370, 370, is_ai=True, name="AI Bot")
                            ]
                            state = STATE_PLAYING
                            start_timestamp = time.time()

            if event.type == pygame.KEYDOWN:
                if state == STATE_PLAYING:
                    # Player Controls
                    player_game = games[0] # Always first
                    if not player_game.over and not player_game.won:
                        move = None
                        if event.key == pygame.K_LEFT: move = "left"
                        elif event.key == pygame.K_RIGHT: move = "right"
                        elif event.key == pygame.K_UP: move = "up"
                        elif event.key == pygame.K_DOWN: move = "down"
                        
                        if move:
                            player_game.move_tiles(move, clock)

        # Logic Update
        if state == STATE_PLAYING:
            # AI Logic
            if game_mode == "AI_MATCH":
                ai_game = games[1]
                current_time = pygame.time.get_ticks()
                if not ai_game.over and not ai_game.won:
                     if current_time - ai_move_timer > AI_DELAY:
                         ai_move = ai_game.ai_move_logic()
                         ai_game.move_tiles(ai_move, clock)
                         ai_move_timer = current_time
            
            # Win/Loss Check
            game_over_condition = False
            winner = None
            
            for g in games:
                if g.won:
                    game_over_condition = True
                    winner = g.name
                    break
                if g.lost:
                    g.over = True
            

            if all(g.lost for g in games):
                game_over_condition = True
                winner = "No One"

            if game_over_condition:
                state = STATE_GAMEOVER
                end_timestamp = time.time()
                # Send score of Player
                send_score_to_web(games[0].score, start_timestamp, end_timestamp, game_mode)
                # Wait and restart
                # logic handled below

        # Draw
        WINDOW.fill(BACKGROUND_COLOR)
        
        if state == STATE_MENU:
            if menu_phase == 0:
                btn_main_start.draw(WINDOW)
            else:
                btn_easy.draw(WINDOW)
                btn_ai.draw(WINDOW)
                
        elif state == STATE_PLAYING or state == STATE_GAMEOVER:
            for g in games:
                g.draw(WINDOW)
                
            if state == STATE_GAMEOVER:
                msg = f"GAME OVER! {winner} Wins!" if winner else "GAME OVER!"
                font = pygame.font.SysFont("comicsans", 50, bold=True)
                text = font.render(msg, 1, (255, 0, 0))
                WINDOW.blit(text, (WIDTH/2 - text.get_width()/2, 50))
                
                inst = pygame.font.SysFont("comicsans", 30).render("Press SPACE to Menu", 1, FONT_COLOR)
                WINDOW.blit(inst, (WIDTH/2 - inst.get_width()/2, 120))
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    state = STATE_MENU
                    menu_phase = 0

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())

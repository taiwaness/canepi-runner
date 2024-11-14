# !/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os
import random
import threading
import json
import pygame.font
import sys
import asyncio
import pygame


try:
    from pyodide import js  # Only available in browser
    IS_BROWSER = True
except ImportError:
    js = NoneIS_BROWSER = False
    #pass  # js won't be used in desktop environment

IS_BROWSER = sys.platform == "emscripten"


pygame.init()

# Global Constants
points = 0
death_count = 0

SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 1500
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Cancer Epigenomic Runner")

Ico = pygame.image.load("assets/DinoWallpaper.png")
pygame.display.set_icon(Ico)

RUNNING = [
    pygame.image.load(os.path.join("assets/Dino", "DinoRun1.png")),
    pygame.image.load(os.path.join("assets/Dino", "DinoRun2.png")),
]
JUMPING = pygame.image.load(os.path.join("assets/Dino", "DinoJump.png"))
DUCKING = [
    pygame.image.load(os.path.join("assets/Dino", "DinoDuck1.png")),
    pygame.image.load(os.path.join("assets/Dino", "DinoDuck2.png")),
]

SMALL_CACTUS = [
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus1.png")),
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus2.png")),
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus3.png")),
]
LARGE_CACTUS = [
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus1.png")),
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus2.png")),
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus3.png")),
]

BIRD = [
    pygame.image.load(os.path.join("assets/Bird", "Bird1.png")),
    pygame.image.load(os.path.join("assets/Bird", "Bird2.png")),
    pygame.image.load(os.path.join("assets/Bird", "Bird3.png")),
    pygame.image.load(os.path.join("assets/Bird", "Bird4.png")),
    pygame.image.load(os.path.join("assets/Bird", "Bird5.png")),
    pygame.image.load(os.path.join("assets/Bird", "Bird6.png")),
    pygame.image.load(os.path.join("assets/Bird", "Bird7.png")),
    pygame.image.load(os.path.join("assets/Bird", "Bird8.png")),
]

CLOUD = pygame.image.load(os.path.join("assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("assets/Other", "Track.png"))

FONT_COLOR=(0,0,0)

INPUT_FONT = pygame.font.Font("freesansbold.ttf", 32)
NAME_MAX_LENGTH = 10

# Add this with other global variables at the top
global_player_name = ""  # Global variable to store player name

class Dinosaur:

    X_POS = 80
    Y_POS = SCREEN_HEIGHT // 2 - 15
    Y_POS_DUCK = SCREEN_HEIGHT // 2 + 30
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if (userInput[pygame.K_UP] or userInput[pygame.K_SPACE]) and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

        # Make collision box slightly smaller
        self.dino_rect.inflate_ip(-1, -1)  # Reduce collision box by 10 pixels on each side

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(100, 200)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH
        # Make collision box slightly smaller
        self.rect.inflate_ip(-1, -1)  # Reduce collision box by 10 pixels on each side

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.remove(self)

    def draw(self, SCREEN):
        # Draw the actual image at the original size
        img_rect = self.image[self.type].get_rect()
        img_rect.center = self.rect.center
        SCREEN.blit(self.image[self.type], img_rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = SCREEN_HEIGHT // 2 + 15
        # Make small cactus collision box even smaller
        self.rect.inflate_ip(-20, -20)  # Reduce collision box by 20 pixels on each side


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = SCREEN_HEIGHT // 2 - 10
        # Make large cactus collision box even smaller
        self.rect.inflate_ip(-20, -20)  # Reduce collision box by 20 pixels on each side


class Bird(Obstacle):
    BIRD_HEIGHTS = [(SCREEN_HEIGHT//2 - 60), (SCREEN_HEIGHT//2 -30), (SCREEN_HEIGHT//2+10)]

    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = random.choice(self.BIRD_HEIGHTS)
        self.index = 0
        # Make bird collision box even smaller
        self.rect.inflate_ip(-50, -50)  # Reduce collision box by 1 pixels on each side

    def draw(self, SCREEN):
        if self.index >= 19:
            self.index = 0
        # Draw the actual image at original size
        img_rect = self.image[self.index // 3].get_rect()
        img_rect.center = self.rect.center
        SCREEN.blit(self.image[self.index // 3], img_rect)
        self.index += 1


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 13
    x_pos_bg = 0
    y_pos_bg = SCREEN_HEIGHT // 2 + 70
    points = 0
    font = pygame.font.Font("freesansbold.ttf", 20)
    obstacles = []
    death_count = 0
    pause = False
    def get_high_score():
        if IS_BROWSER and js is not None:
        # Read high score from local storage
            highscore = js.localStorage.getItem("highscore")
            if highscore is None or highscore == js.undefined:
                return 0
            else:
                return int(highscore)
        else:
            # Read high score from file
            try:
                with open("score.txt", "r") as f:
                    score_ints = [int(x) for x in f.read().split()]  
                    highscore = max(score_ints)
            except (FileNotFoundError, ValueError):
                highscore = 0
            return int(highscore)

    def save_high_score(points):
        if IS_BROWSER and js is not None:
            # Save high score to local storage
            js.localStorage.setItem("highscore", str(points))
        else:
            # Save high score to file
            with open("score.txt", "a") as f:
                f.write(str(points) + "\n")
    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 0.7
    
        highscore = get_high_score()
        
        # Update high score if current points is higher
        if points > highscore:
            highscore = points
            save_high_score(points)
        
        # Render score text
        text = font.render("High Score: " + str(highscore) + "  Points: " + str(points), True, FONT_COLOR)
        textRect = text.get_rect()
        textRect.center = (900, 40)
        SCREEN.blit(text, textRect)


    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    def unpause():
        nonlocal pause, run
        pause = False
        run = True

    def paused():
        nonlocal pause
        pause = True
        font = pygame.font.Font("freesansbold.ttf", 30)
        text = font.render("Game Paused, Press 'u' to Unpause", True, FONT_COLOR)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT  // 3)
        SCREEN.blit(text, textRect)
        pygame.display.update()

        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                    unpause()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    run = False
                    paused()

        current_time = datetime.datetime.now().hour
        if 7 < current_time < 19:
            SCREEN.fill((255, 255, 255))
        else:
            SCREEN.fill((0, 0, 0))
        userInput = pygame.key.get_pressed()

        # Define a list of possible distances
        distances = [650, 880, 999, 1050, 1100, 1150,1200]
        # Adjust the frequency of obstacle generation and limit the number of obstacles
        if len(obstacles) == 0:
            obstacle_type = random.randint(0, 2)
            if obstacle_type == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif obstacle_type == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            else:
                obstacles.append(Bird(BIRD))
        elif len(obstacles) < 3:  
            # Ensure the distance between obstacles is far enough
            if len(obstacles) == 0 or obstacles[-1].rect.x < SCREEN_WIDTH - random.choice(distances):  # Adjust the value 300 as needed
                obstacle_type = random.randint(0, 2)
                if obstacle_type == 0:
                    obstacles.append(SmallCactus(SMALL_CACTUS))
                elif obstacle_type == 1:
                    obstacles.append(LargeCactus(LARGE_CACTUS))
                else:
                    obstacles.append(Bird(BIRD))
        
        
        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(2000)
                death_count += 1
                menu(death_count)
        #Remove obstacles that have moved off the screen
        obstacles = [obstacle for obstacle in obstacles if obstacle.rect.x > -obstacle.rect.width]
        background()

        player.draw(SCREEN)
        player.update(userInput)


        cloud.draw(SCREEN)
        cloud.update()

        score()

        clock.tick(30)
        pygame.display.update()
        #await asyncio.sleep(0)


def get_player_name(screen):
    name = ""
    input_active = True
    
    # Calculate positions
    dino_y = SCREEN_HEIGHT // 2 - 140  # Dinosaur position
    dino_x = SCREEN_WIDTH // 2 - 50  # Dinosaur position
    text_y = SCREEN_HEIGHT // 2        # "Enter your name" text position
    name_y = text_y + 60               # Input name position
    
    # Create input box rect
    input_box_width = 200
    input_box_height = 40
    input_box = pygame.Rect(
        SCREEN_WIDTH//2 - input_box_width//2,
        name_y - input_box_height//2,
        input_box_width,
        input_box_height
    )
    input_box_color = pygame.Color('lightgray')
    
    input_text = INPUT_FONT.render("Enter your name", True, FONT_COLOR)
    input_rect = input_text.get_rect(center=(SCREEN_WIDTH // 2, text_y))
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < NAME_MAX_LENGTH and event.unicode.isalnum():
                        name += event.unicode
        
        if 7 < datetime.datetime.now().hour < 19:
            screen.fill((255, 255, 255))
        else:
            screen.fill((128, 128, 128))
        
        # Draw dinosaur first (above everything)
        screen.blit(RUNNING[0], (dino_x, dino_y))
        
        # Draw "Enter your name" text
        screen.blit(input_text, input_rect)
        
        # Draw input box
        pygame.draw.rect(screen, input_box_color, input_box, 2)
        
        # Draw the name being typed
        name_surface = INPUT_FONT.render(name, True, FONT_COLOR)
        name_rect = name_surface.get_rect(center=(SCREEN_WIDTH // 2, name_y))
        screen.blit(name_surface, name_rect)
        
        # Draw blinking cursor
        if len(name) < NAME_MAX_LENGTH and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = name_rect.right + 2
            pygame.draw.line(screen, FONT_COLOR, 
                           (cursor_x, name_y - 15),
                           (cursor_x, name_y + 15), 2)
        
        pygame.display.flip()
    
    return name

def update_leaderboard(player_name, score):
    if IS_BROWSER and js is not None:
        # Read leaderboard from local storage
        leaderboard_json = js.localStorage.getItem("leaderboard")
        if leaderboard_json is None:
            data = {"leaderboard": []}
        else:
            data = json.loads(leaderboard_json)
        
        # Add new score
        data["leaderboard"].append({"name": player_name, "score": score})
        
        # Sort and keep top 10
        data["leaderboard"] = sorted(data["leaderboard"], key=lambda x: x["score"], reverse=True)[:10]
        
        # Save updated leaderboard
        js.localStorage.setItem("leaderboard", json.dumps(data))
        
        # Write highest score to highscore key
        if len(data["leaderboard"]) > 0:
            highest_score = data["leaderboard"][0]["score"]
            js.localStorage.setItem("highscore", str(highest_score))
        
        # Return True if player made top 10
        return any(entry["name"] == player_name and entry["score"] == score for entry in data["leaderboard"])
    else:
        # Original file-based code
        try:
            with open("leaderboard.json", "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"leaderboard": []}
        
        # Add new score
        data["leaderboard"].append({"name": player_name, "score": score})
        
        # Sort and keep top 10
        data["leaderboard"] = sorted(data["leaderboard"], key=lambda x: x["score"], reverse=True)[:10]
        
        # Save updated leaderboard
        with open("leaderboard.json", "w") as f:
            json.dump(data, f, indent=4)
        
        # Write highest score to score.txt
        if len(data["leaderboard"]) > 0:
            highest_score = data["leaderboard"][0]["score"]
            with open("score.txt", "w") as f:
                f.write(str(highest_score))
        
        # Return True if player made top 10
        return any(entry["name"] == player_name and entry["score"] == score for entry in data["leaderboard"])
   
def menu(death_count):
    global points, FONT_COLOR, global_player_name
    run = True
    font = pygame.font.Font("freesansbold.ttf", 30)
    
    # Get player name only at the very beginning
    if death_count == 0:
        global_player_name = get_player_name(SCREEN)
    
    while run:
        current_time = datetime.datetime.now().hour
        if 7 < current_time < 19:
            FONT_COLOR = (0, 0, 0)
            SCREEN.fill((255, 255, 255))
        else:
            FONT_COLOR = (255, 255, 255)
            SCREEN.fill((128, 128, 128))
        
        if death_count == 0:
            text = font.render("Press any Key to Start", True, FONT_COLOR)
            textRect = text.get_rect()
            textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            SCREEN.blit(text, textRect)
            
            # Move dinosaur to a more central position
            dino_y = SCREEN_HEIGHT // 2 - 140
            dino_x = SCREEN_WIDTH // 2 - 50
            SCREEN.blit(RUNNING[0], (dino_x, dino_y))
            
        elif death_count > 0:
            # Update leaderboard only once
            def update_and_display_leaderboard():
                global points, death_count  # Declare global variables
                made_top_10 = update_leaderboard(global_player_name, points)
                
                # Display appropriate message
                if made_top_10:
                    top_text = font.render("You're such a malignant cancer cell!", True, (255, 0, 0))
                else:
                    top_text = font.render("You're just a benign cancer cell—cured and harmless!", True, (135, 206, 235))
                
                top_rect = top_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6))
                SCREEN.blit(top_text, top_rect)
                
                # Display leaderboard
                leaderboard_text = font.render("Leaderboard:", True, FONT_COLOR)
                leaderboard_rect = leaderboard_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
                SCREEN.blit(leaderboard_text, leaderboard_rect)
                
                # Read leaderboard data
                if IS_BROWSER:
                    leaderboard_json = js.localStorage.getItem("leaderboard")
                    if leaderboard_json is not None:
                        data = json.loads(leaderboard_json)
                        for i, entry in enumerate(data["leaderboard"]):
                            if entry["name"] == global_player_name and entry["score"] == points:
                                score_text = font.render(f"{i+1}. {entry['name']}: {entry['score']}", True, (255, 0, 0))
                            else:
                                score_text = font.render(f"{i+1}. {entry['name']}: {entry['score']}", True, FONT_COLOR)
                            
                            score_rect = score_text.get_rect(
                                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 40 * (i + 1))
                            )
                            SCREEN.blit(score_text, score_rect)
                else:
                    # Original file-based code
                    try:
                        with open("leaderboard.json", "r") as f:
                            data = json.load(f)
                            for i, entry in enumerate(data["leaderboard"]):
                                if entry["name"] == global_player_name and entry["score"] == points:
                                    score_text = font.render(f"{i+1}. {entry['name']}: {entry['score']}", True, (255, 0, 0))
                                else:
                                    score_text = font.render(f"{i+1}. {entry['name']}: {entry['score']}", True, FONT_COLOR)
                                
                                score_rect = score_text.get_rect(
                                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 40 * (i + 1))
                                )
                                SCREEN.blit(score_text, score_rect)
                    except (FileNotFoundError, json.JSONDecodeError):
                        pass
                
                pygame.display.update()
                pygame.time.delay(5000)  # Show leaderboard for 5 seconds
                # Reset death count and points
                death_count = 0
                points = 0
                menu(death_count=0)  # Start fresh
            
            # Run the synchronous leaderboard update and display
            update_and_display_leaderboard()
            return  # Exit this instance of menu
       
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                points = 0
                main()


if __name__ == "__main__":
    menu(death_count=0)
    #asyncio.run(menu(death_count=0))

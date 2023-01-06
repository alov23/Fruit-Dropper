from enum import Enum
import pygame
from pygame.locals import *
import random
import sys

pygame.init()
DISPLAY_SIZE = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print(DISPLAY_SIZE[0]) # print display width
print(DISPLAY_SIZE[1]) # print display height
WINDOW_SIZE = (int((DISPLAY_SIZE[0]*3)/4), int(( ((DISPLAY_SIZE[0]/16)*9) *3)/4)) # makes window 3/4 the width of the users display and keeps it 16:9 aspect ratio
print(WINDOW_SIZE[0]) # print window width
print(WINDOW_SIZE[1]) # print window height

screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

start_game_rect = pygame.Rect(WINDOW_SIZE[0]/10, WINDOW_SIZE[1]/10, (WINDOW_SIZE[0]*8)/10, (WINDOW_SIZE[1]*8)/10)
start_game_rect_color_active = pygame.Color(100, 100, 100)
start_game_rect_color_passive = pygame.Color(50, 50, 50, 0)
start_game_rect_color = start_game_rect_color_passive
pressing_start_game_rect = False

# values that do not change during the program
SPRITE_SIZE = 72 # pixel length of one side of sprites / could have in FruitTypes if end up using different sized sprites
DEFAULT_SPRITE_SPEED = 8
FRAMERATE = 60
SECONDS_OF_PLAYTIME = 15
# fonts for text used in game
STATS_FONT = pygame.font.SysFont("Arial", 12)
GAME_FONT = pygame.font.SysFont("Arial", 96)

fruitOnScreen = [] # will contain fruit currently on screen for ease of access


# have fruit class and fruit enums that define attributes of different fruit types
class FruitTypes(Enum):
    # [SPRITE_IMAGE, IS_DIRECTIONLESS, (MOVE_X_ON_UPDATE, MOVE_Y_ON_UPDATE), SPAWN_AT_BOTTOM, POINT_VALUE]
    APPLE = [pygame.image.load("fruit_sprites/apple.png"), True, (0, DEFAULT_SPRITE_SPEED), False, 50]
    PEAR = [pygame.image.load("fruit_sprites/pear.png"), False, ((DEFAULT_SPRITE_SPEED*3)/4, (DEFAULT_SPRITE_SPEED*3)/4), False, 100]
    CHERRIES = [pygame.image.load("fruit_sprites/cherries.png"), True, (0, -DEFAULT_SPRITE_SPEED), True, 100]
    BLUEBERRIES = [pygame.image.load("fruit_sprites/blueberries.png"), False, ((DEFAULT_SPRITE_SPEED*3)/4, -((DEFAULT_SPRITE_SPEED*3)/4)), True, 150]

class Fruit(pygame.sprite.Sprite):
    # class constructor that allows fruit to be set to a certain pre-made fruit type and use its values
    def __init__(self, fruitType):
        if not isinstance(fruitType, FruitTypes):
            raise TypeError("fruitType not a valid enumerator") # terminates program if someone edits the code and tries to create a fruit of a type that doesn't exist
        self.fruitType = fruitType
        self.image = self.fruitType.value[0]

        if not self.fruitType.value[3]:
            self.position = [random.randint(0, WINDOW_SIZE[0]), SPRITE_SIZE]
        else:
            self.position = [random.randint(0, WINDOW_SIZE[0]), WINDOW_SIZE[1]-SPRITE_SIZE]
        
        self.rect = pygame.Rect((self.position[0], self.position[1]), (SPRITE_SIZE, SPRITE_SIZE))

        if self.position[0] <= WINDOW_SIZE[0]/2: # sets direction fruit is facing based on which half of the screen it is on
            self.facing = 0 # self.facing == 0 means facing right
        else:
            self.facing = 1 # self.facing == 1 means facing left
    
    # moves fruit when frame updates
    # return true if sprite is off screen and should be deleted, false otherwise
    def updatePosition(self):
        if self.fruitType.value[1] == False:
            if self.facing == 0:
                self.rect.centerx += self.fruitType.value[2][0]
            else:
                self.rect.centerx -= self.fruitType.value[2][0]
        
        self.rect.centery += self.fruitType.value[2][1]

        for i in range(2):
            if self.rect.center[i] < 0-SPRITE_SIZE or self.rect.center[i] > WINDOW_SIZE[i]+SPRITE_SIZE:
                return True
        return False


# values used in program
game_started = False
frame = 0
time = -1
score = 0
percentChanceToSpawnFruit = 5
noFruitSpawnStreak = 0 # number of times a frame has passed without a fruit spawning in a row


# shows dictionary of variables on screen
def showStatsDict(statsDict:dict):
    text_position_x = WINDOW_SIZE[0]/200
    text_position_y = WINDOW_SIZE[1]/150
    for entry in statsDict:
        entry_text = STATS_FONT.render(entry + ": " + str(statsDict[entry]), True, (255, 255, 255))
        entry_text_height = STATS_FONT.size(entry + ": " + str(statsDict[entry]))[1]
        screen.blit(entry_text, (text_position_x, text_position_y))
        text_position_y += entry_text_height+(WINDOW_SIZE[1]/200)


# runs every frame
while True:
    frame+=1
    if frame >= FRAMERATE:
        frame = 0
        if game_started and not time <= 0:
            time -= 1
    if time < 10 and not time == -1:
        if frame < 10:
            print("time:  "  + str(time) + " frame:  " + str(frame))
        else:
            print("time:  "  + str(time) + " frame: " + str(frame))
    else:
        if frame < 10:
            print("time: "  + str(time) + " frame:  " + str(frame))
        else:
            print("time: "  + str(time) + " frame: " + str(frame))
    
    mousePos = (-200, -200)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            mousePos = event.pos
            if not game_started: # enables game to be started when mouse button is let go after pressing the start game button
                if start_game_rect.collidepoint(event.pos):
                    start_game_rect_color = start_game_rect_color_active
                    pressing_start_game_rect = True
            if time == 0: # starts a new game when clicking the time up screen
                score = 0
                percentChanceToSpawnFruit = 5
                noFruitSpawnStreak = 0
                time = SECONDS_OF_PLAYTIME
                pygame.time.wait(100)
        if event.type == MOUSEBUTTONUP:
            if not game_started and pressing_start_game_rect: # show game after start button is released
                game_started = True
                pressing_start_game_rect = False
                start_game_rect_color = start_game_rect_color_passive
                time = SECONDS_OF_PLAYTIME
                pygame.time.wait(100)
    
    if game_started:
        if time == 0: # if the timer has ended show final score
            screen.fill((150, 150, 150))
            time_up_text = GAME_FONT.render("Time's Up!", True, (255, 255, 255))
            time_up_text_width, time_up_text_height = GAME_FONT.size("Time's Up!")
            screen.blit(time_up_text, ((WINDOW_SIZE[0]/2)-(time_up_text_width/2), ((WINDOW_SIZE[1]*3)/8)-(time_up_text_height/2)))
            score_text = GAME_FONT.render(f"Final Score: {score}", True, (255, 255, 255))
            score_text_width, score_text_height = GAME_FONT.size(f"Final Score: {score}")
            screen.blit(score_text, ((WINDOW_SIZE[0]/2)-(score_text_width/2), ((WINDOW_SIZE[1]*9)/16)-(score_text_height/2)))
            pygame.display.flip()
            clock.tick(FRAMERATE)
        else: # update game objects
            if random.randint(1, 100) <= percentChanceToSpawnFruit:
                percentChanceToSpawnFruit = 5
                noFruitSpawnStreak = 0
                i = random.randint(0, 3)
                if i == 0:
                    fruitOnScreen.append(Fruit(FruitTypes.APPLE))
                elif i == 1:
                    fruitOnScreen.append(Fruit(FruitTypes.PEAR))
                elif i == 2:
                    fruitOnScreen.append(Fruit(FruitTypes.CHERRIES))
                elif i == 3:
                    fruitOnScreen.append(Fruit(FruitTypes.BLUEBERRIES))
            else:
                noFruitSpawnStreak += 1
                if noFruitSpawnStreak >= 15:
                    percentChanceToSpawnFruit += 1

            screen.fill((150, 150, 150))

            showStatsDict({
                "Time Left" : time,
                "Score" : score,
                "Frame" : frame,
                "Fruit On Screen" : len(fruitOnScreen),
                "No fruit spawn streak" : noFruitSpawnStreak,
                "Percent chance to spawn fruit" : percentChanceToSpawnFruit
            })

            fruitIndex = 0
            for _ in range(len(fruitOnScreen)): # goes through list of fruit on screen and updates them or the list based on certain criteria
                fruit = fruitOnScreen[fruitIndex]
                if fruit.rect.collidepoint(mousePos):
                    score += fruit.fruitType.value[4]
                    fruitOnScreen.pop(fruitIndex)
                elif fruit.updatePosition():
                    fruitOnScreen.pop(fruitIndex)
                else:
                    screen.blit(fruit.image, fruit.rect)
                    fruitIndex += 1
    else: # show start game screen
        screen.fill((150, 150, 150))
        pygame.draw.rect(screen, start_game_rect_color, start_game_rect)
        start_game_text_label = GAME_FONT.render("Start Game", True, (255, 255, 255))
        start_game_text_width, start_game_text_height = GAME_FONT.size("Start Game")
        screen.blit(start_game_text_label, (
            (start_game_rect.x+(start_game_rect.w/2))-(start_game_text_width/2),
            (start_game_rect.y+(start_game_rect.h/2))-(start_game_text_height/2)
        ))

    pygame.display.flip()
    clock.tick(FRAMERATE)
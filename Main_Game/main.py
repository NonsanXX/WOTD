import pygame
import config.config as c
import json
from enemy import Enemy
from world import World
from turret import Turret
from button import Button
from enemy_data import ENEMY_SPAWN_DATA
import os
from random import shuffle
from sfx import SFX
from decimal import Decimal

# Initialize pygame game
pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode((1920,1080), pygame.SCALED | pygame.FULLSCREEN)
pygame.display.set_caption("WOTD")

# game variable
is_fast_forward = False
time_begin = 0
current_fast_forward_type = 1
game_over = False
game_outcome = 0 # -1 lost and 1 is pause
level_started = False
last_enemy_spawn = pygame.time.get_ticks()
placing_turret = False
selected_turret = False
buttoning = False
out_of_menu = False
shuffle(c.CHEERUP_TEXT)
game_paused = False
game_paused_tmp = 1
is_in_credit = False
is_in_options = False
is_show_slot = True
delay_tmp = 10

# load image
map_image = pygame.image.load(os.path.join("Main_Game", "levels", "map.png")).convert_alpha()
cancel_turret_image = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "buttons", "cancel.png")), (99, 99)).convert_alpha()
upgrade_turret_image = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "buttons", "upgrade_turret.png")), (250, 250)).convert_alpha()
demolish_turret_image = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "buttons", "Demolish_button.png")), (100, 100)).convert_alpha()
begin_image = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "buttons", "begin.png")), (250, 250)).convert_alpha()
restart_image = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "buttons", "restart.png")), (100, 100)).convert_alpha()
fast_forward_cancel_image = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "buttons", "FFW_cancel.png")), (99, 99)).convert_alpha()
fast_forward_x3_image = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "buttons", "FFW_X3.png")), (99, 99)).convert_alpha()
fast_forward_x5_image = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "buttons", "FFW_X5.png")), (99, 99)).convert_alpha()
exit_image = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "buttons", "Exit.png")), (100, 100)).convert_alpha()
home_image = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "buttons", "Home.png")), (100, 100)).convert_alpha()
show_slot_image = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "buttons", "show_slot.png")), (64, 64)).convert_alpha()
hide_slot_image = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "buttons", "hide_slot.png")), (64, 64)).convert_alpha()

#load cursor
new_cursor = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "gui", "Cursor Pointer.png")), (40, 40)).convert_alpha()
new_cursor_rect = new_cursor.get_rect()

#hide mouse cursor
pygame.mouse.set_visible(False)

# load gui
coin_gui = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "gui", "coin.png")), (70, 70)).convert_alpha()
coin_gui_up = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "gui", "coin.png")), (100, 100)).convert_alpha()
heart_gui = pygame.transform.scale(pygame.image.load(os.path.join("Main_Game", "assets", "images", "gui", "heart.png")), (60, 60)).convert_alpha()
wallpaper = pygame.image.load(os.path.join("Main_Game", "assets", "images", "gui", "Wallpaper.png")).convert_alpha()
wallpaper_only = pygame.image.load(os.path.join("Main_Game", "assets", "images", "gui", "Wallpaper_only.png")).convert_alpha()


# enemy
enemy_images = {
    "weak" : pygame.image.load(os.path.join("Main_Game", "assets", "images", "enemies", "enemy_1.png")).convert_alpha(),
    "medium" : pygame.image.load(os.path.join("Main_Game", "assets", "images", "enemies", "enemy_2.png")).convert_alpha(),
    "strong" : pygame.image.load(os.path.join("Main_Game", "assets", "images", "enemies", "enemy_3.png")).convert_alpha(),
    "elite" : pygame.image.load(os.path.join("Main_Game", "assets", "images", "enemies", "enemy_4.png")).convert_alpha()
}

witch_frame = lambda x: len(list(os.scandir(os.path.join("Main_Game", "assets", "images", "turrets", "Witch", "Lv%d"%x))))
knight_frame = lambda x: len(list(os.scandir(os.path.join("Main_Game", "assets", "images", "turrets", "Knight", "Lv%d"%x))))
elf_frame = lambda x: len(list(os.scandir(os.path.join("Main_Game", "assets", "images", "turrets", "Elf", "Lv%d"%x))))

# witch tower
witch_spreadsheet = [[pygame.image.load(os.path.join("Main_Game", "assets", "images", "turrets", "Witch", "Lv%d"%level, "Witch%d-%d.png"%(level, frame))).convert_alpha() for frame in range(1, witch_frame(level)+1)] for level in range(1, 4)]

# knight tower
knight_spreadsheet = [[pygame.image.load(os.path.join("Main_Game", "assets", "images", "turrets", "Knight", "Lv%d"%level, "Knight%d-%d.png"%(level, frame))).convert_alpha() for frame in range(1, knight_frame(level)+1)] for level in range(1, 4)]

# elf tower
elf_spreadsheet = [[pygame.image.load(os.path.join("Main_Game", "assets", "images", "turrets", "Elf", "Lv%d"%level, "Elf%d-%d.png"%(level, frame))).convert_alpha() for frame in range(1, elf_frame(level)+1)] for level in range(1, 4)]

selector = {
    "witch" : witch_spreadsheet,
    "knight" : knight_spreadsheet,
    "elf" : elf_spreadsheet
}

# load json data
with open(os.path.join("Main_Game", "levels", "level.tmj")) as file:
    world_data = json.load(file)

# load font for displaing text in screen
def load_font(font, size):
    if font == 'pixel':
        return pygame.font.Font("Main_Game/assets/fonts/PixelAzureBonds-327Z.ttf", size)
    elif font == 'ancient':
        return pygame.font.Font("Main_Game/assets/fonts/AncientModernTales-a7Po.ttf", size)
    elif font == 'thai':
        return pygame.font.Font("Main_Game/assets/fonts/ZF2ndPixelus.ttf", size)

# Load the high score
def load_high_wave():
    if os.path.exists(c.SCORE_FILE):
        with open(c.SCORE_FILE, 'r') as file:
            try:
                high_score = int(file.read())
            except ValueError:
                high_score = 0
    else:
        high_score = 0
    return high_score

# Save the high score
def save_high_wave(score):
    with open(c.SCORE_FILE, 'w') as file:
        file.write(str(score))

#save new volume in config file
#with open('Main_Game/config.py', 'r', encoding='utf-8') as config_file:
    #lines = config_file.readlines()
def load_music_volume():
    if os.path.exists(c.MUSIC_VOLUME_FILE):
        with open(c.MUSIC_VOLUME_FILE, 'r') as file:
            try:
                ms_volume = float(file.read())
            except ValueError:
                ms_volume = 1
    else:
        ms_volume = 1
    return ms_volume

def load_fx_volume():
    if os.path.exists(c.FX_VOLUME_FILE):
        with open(c.FX_VOLUME_FILE, 'r') as file:
            try:
                fx_volume = float(file.read())
            except ValueError:
                fx_volume = 1
    else:
        fx_volume = 1
    return fx_volume


now_music_volume = load_music_volume()
now_fx = load_fx_volume()


def save_music_volume(new_volume):
    with open(c.MUSIC_VOLUME_FILE, 'w') as file:
        file.write(str(new_volume))
    '''for i, line in enumerate(lines):
        if 'MUSIC_VOLUME' in line:
            lines[i] = f'MUSIC_VOLUME = {new_volume}\n'
            break
    with open('Main_Game/config.py', 'w', encoding='utf-8') as config_file:
        config_file.writelines(lines)'''
def save_fx_volume(new_volume):
    with open(c.FX_VOLUME_FILE, 'w') as file:
        file.write(str(new_volume))
    '''for i, line in enumerate(lines):
        if 'EFFECT_VOLUME' in line:
            lines[i] = f'EFFECT_VOLUME = {new_volume}\n'
            break
    with open('Main_Game/config.py', 'w', encoding='utf-8') as config_file:
        config_file.writelines(lines)'''
    

# function for text on screen
def draw_text(text, font, color, coor):
    img = font.render(text, True, color)
    screen.blit(img, coor)
def draw_center_text(text, font, color, eneble, coor):
    img = font.render(text, True, color)
    img_rect = img.get_rect(center=(c.SCREEN_WIDTH/2, c.SCREEN_HEIGHT/2))
    screen.blit(img, (img_rect.x*eneble[0]+coor[0], img_rect.y*eneble[1]+coor[1]))

def display_data(killed, level, difficulty):
    #display data
    screen.blit(heart_gui, (20, c.SCREEN_HEIGHT-90))
    draw_text(str(world.health), load_font('pixel', 50), "grey100", (100, c.SCREEN_HEIGHT-90))
    screen.blit(coin_gui, (10, 40))
    draw_text(str(int(world.money)), load_font('pixel', 50), "grey100", (85, 40))
    draw_center_text("WAVE %s"%(level), load_font('ancient', 60), "grey100", (1, 0), (0, 30))
    draw_center_text("Highest Wave : %s"%(high_wave), load_font('pixel', 30), "grey100", (1, 0), (0, 90))
    draw_center_text("Difficulty : %.1f"%(difficulty), load_font('pixel', 30), "grey100", (1, 0), (0, 125))
    draw_text("ENEMY : %s"%(sum(ENEMY_SPAWN_DATA[(level-1)%c.TOTAL_LEVEL].values())-killed), load_font("pixel", 30), "grey100", (60, 120))
def create_turret(pos, choosing_turret, turret_name):
    mouse_tile_x = pos[0] // c.TILE_SIZE
    mouse_tile_y = pos[1] // c.TILE_SIZE
    # calculate sequence in json tile_map
    mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
    if world.tile_map[mouse_tile_num] == 92:
        # check if already placed
        space_is_free = True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
        if space_is_free:
            new_turret = Turret(choosing_turret, mouse_tile_x, mouse_tile_y, turret_name)
            new_turret.volume = now_fx/4
            turret_group.add(new_turret)

            # losing money
            world.money -= c.BUY_COST

def select_turret(pos):
    mouse_tile_x = pos[0] // c.TILE_SIZE
    mouse_tile_y = pos[1] // c.TILE_SIZE
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret
        
def deselect_turret():
    for turret in turret_group:
        turret.selected = False

def draw_slot(rect):
    pygame.draw.rect(screen, (217, 217, 255, 0), rect, border_radius=25)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2, 25)

def nondeselect(ignore):
    mouse_pos = pygame.mouse.get_pos()
    for button in ignore:
        if button.rect.collidepoint(mouse_pos):
            return True

#create menu
menu_options = ["Start Game", "Options", "Credits", "Quit"]
credit_person = ["ผู้สร้าง", "66070305 ภูริภัทร อรุณไพศาล", "66070162 ภูมิภูริดล วงค์จันทร์", "66070153 ภาคิน ปานสุข", "66070166 มนนทกร ขุนสุวรรณ"]
selected_option = 0

def draw_menu():
    screen.fill("black")
    screen.blit(wallpaper, wallpaper.get_rect())
    for i, option in enumerate(menu_options):
        text = load_font("pixel", 50).render(option, True, "white" if i == selected_option else (150, 150, 150))
        text_rect = text.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 + (i+0.5) * 100))
        screen.blit(text, text_rect)
    draw_center_text("Highest Wave : %s"%(high_wave), load_font("ancient", 80), "grey100", (1, 0), (0, c.SCREEN_WIDTH // 2))

#create credits
def draw_credits():
    screen.fill("black")
    screen.blit(wallpaper_only, wallpaper.get_rect())
    for i, person in enumerate(credit_person):
        text = load_font("thai", 120).render(person, True, "white")
        text_rect = text.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 - 500 + (i+1) * 150))
        screen.blit(text, text_rect)
    draw_text("PRESS ESC TO GO BACK", load_font("pixel", 70), "white", (100, 950))
    
def draw_options():
    screen.fill("black")
    screen.blit(wallpaper_only, wallpaper.get_rect())
    for i, option in enumerate(setting_options):
        text = load_font("pixel", 50).render(option, True, "white" if i == selected_option else (150, 150, 150))
        text_rect = text.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 + (i+0.5) * 100))
        screen.blit(text, text_rect)

#create group
enemy_group = pygame.sprite.Group()
turret_group = pygame.sprite.Group()

#create world
world = World(world_data, map_image)
world.process_data()
world.process_enemy()

waypoint = world.waypoint

# create button
demolish_button = Button(c.SCREEN_WIDTH - 430, c.SCREEN_HEIGHT-150, demolish_turret_image, True,)
demolish_button_past_max = Button(c.SCREEN_WIDTH-120, c.SCREEN_HEIGHT-150, demolish_turret_image, True,)
cancel_button = Button(c.SCREEN_WIDTH/2-250, c.SCREEN_HEIGHT-150, cancel_turret_image, True,)
upgrade_button = Button(c.SCREEN_WIDTH - 300, c.SCREEN_HEIGHT-200, upgrade_turret_image, True,)
begin_button = Button(c.SCREEN_WIDTH - 250, -30, begin_image, True,)
restart_button = Button(820, 500, restart_image, True,)
fast_forward_cancel_button = Button(c.SCREEN_WIDTH/2+610, 10, fast_forward_cancel_image, True,)
fast_forward_x3_button = Button(c.SCREEN_WIDTH/2+730, 10, fast_forward_x3_image, True,)
fast_forward_x5_button = Button(c.SCREEN_WIDTH/2+850, 10, fast_forward_x5_image, True,)

#paused ui
restart_button = Button(760, 550, restart_image, True,)
home_button = Button(910, 545, home_image, True,)
exit_paused_button = Button(1070, 555, exit_image, True,)


# Draw Slot for selector
witch_selector = Button(c.SCREEN_WIDTH/2-150, c.SCREEN_HEIGHT-120, pygame.transform.scale(witch_spreadsheet[0][0], (99, 99)), True)
knight_selector = Button(c.SCREEN_WIDTH/2-50, c.SCREEN_HEIGHT-120, pygame.transform.scale(knight_spreadsheet[0][0], (99, 99)), True)
elf_selector = Button(c.SCREEN_WIDTH/2+50, c.SCREEN_HEIGHT-120, pygame.transform.scale(elf_spreadsheet[0][0], (99, 99)), True)
show_slot_button = Button(c.SCREEN_WIDTH/2 - 30, c.SCREEN_HEIGHT- 60, show_slot_image, True)
hide_slot_button = Button(c.SCREEN_WIDTH/2 - 30, c.SCREEN_HEIGHT - 190, hide_slot_image, True)

# No other action done when mouse is hover over button
ignore = [cancel_button, upgrade_button, demolish_button, begin_button, fast_forward_cancel_button, fast_forward_x3_button, fast_forward_x5_button, witch_selector, knight_selector, elf_selector]

def reset_world():
    global game_over, level_started, placing_turret, selected_turret, game_paused, current_fast_forward_type, game_outcome, game_paused_tmp, last_enemy_spawn, world
    game_over = False
    level_started = False
    placing_turret = False
    selected_turret = None
    game_paused = False
    current_fast_forward_type = 1
    game_outcome = 0
    game_paused_tmp = 1
    last_enemy_spawn = pygame.time.get_ticks()

    # reset world
    world = World(world_data, map_image)
    world.process_data()
    world.process_enemy()

    # empty group
    enemy_group.empty()
    turret_group.empty()

run = True
high_wave = load_high_wave()

#load background music
#### MUST BE 16-bit WAV ####
pygame.mixer.music.load('Main_Game/assets/audio/bg_music.mp3')

#run background music
pygame.mixer.music.set_volume(now_music_volume)
pygame.mixer.music.play(-1) # -1 mean infinite loop

while run:
    clock.tick(c.FPS)
    cursor_pos = pygame.mouse.get_pos()
    #####################
    # UPDATING SECTION
    #####################
    world.game_speed = 0 if game_paused else current_fast_forward_type
    if out_of_menu:
        if not game_over and not game_paused:
            # check if player is lost
            if world.health <= 0:
                game_over = True
                game_outcome = -1 # lost

            enemy_group.update(world)
            turret_group.update(enemy_group, world)

            # Highlight selected turret
            if selected_turret:
                selected_turret.selected = True

    #####################
    # DRAW SECTION
    #####################
    pygame.Surface.fill(screen, "Black")
    world.draw(screen)

    # draw group of enemies
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)

    display_data(world.killed_enemy+world.missed_enemy, world.level, world.difficulty)

    if out_of_menu:
        if not game_over and not game_paused:
            # check if level started
            if not level_started:
                time_begin = pygame.time.get_ticks()
                if begin_button.draw(screen):
                    level_started = True
                    SFX.play_fx("button_fx", now_fx)
                    SFX.play_fx("start_fx", now_fx)
            else:
                # Fast forward option
                if pygame.time.get_ticks() - time_begin > 100: # Check if delta time is greater than 100ms
                    if fast_forward_cancel_button.draw(screen):
                        current_fast_forward_type = 1
                        SFX.play_fx("button_fx", now_fx)
                    if fast_forward_x3_button.draw(screen):
                        current_fast_forward_type = 3
                        SFX.play_fx("button_fx", now_fx)
                    if fast_forward_x5_button.draw(screen):
                        current_fast_forward_type = 5
                        SFX.play_fx("button_fx", now_fx)
                # Spawn enemies
                if pygame.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN / (world.game_speed*world.difficulty):
                    if world.spawned_enemy < len(world.enemy_list):
                        enemy_type = world.enemy_list[world.spawned_enemy]
                        enemy = Enemy(enemy_type, waypoint, enemy_images, world, now_fx)
                        enemy_group.add(enemy)
                        world.spawned_enemy += 1
                        last_enemy_spawn = pygame.time.get_ticks()

            # check if complete wave
            if world.check_level_complete():
                world.money += c.LEVEL_COMPLETE_REWARD
                world.level += 1
                level_started = False
                last_enemy_spawn = pygame.time.get_ticks()
                world.reset_level()
                world.process_enemy()

            # draw button
            # for turret button show cost

            if is_show_slot:
                if delay_tmp >= 5:
                    draw_slot(witch_selector)
                    draw_slot(knight_selector)
                    draw_slot(elf_selector)
                    if witch_selector.draw(screen):
                        SFX.play_fx("select_turret_fx", now_fx)
                        placing_turret = True
                        select = (selector["witch"], "witch")
                    if knight_selector.draw(screen):
                        SFX.play_fx("select_turret_fx", now_fx)
                        placing_turret = True
                        select = (selector["knight"], "knight")
                    if elf_selector.draw(screen):
                        SFX.play_fx("select_turret_fx", now_fx)
                        placing_turret = True
                        select = (selector["elf"], "elf")
                    if hide_slot_button.draw(screen):
                        SFX.play_fx("button_fx", now_fx)
                        is_show_slot = False
                delay_tmp += 1
            else:
                if show_slot_button.draw(screen):
                        SFX.play_fx("button_fx", now_fx)
                        is_show_slot = True
                delay_tmp = 0
            if placing_turret:
                # show cursor
                cursor_turret = pygame.transform.scale(select[0][0][0], (99, 99))
                cursor_rect = cursor_turret.get_rect()
                cursor_rect.center = (cursor_pos[0], cursor_pos[1]-30)
                screen.blit(cursor_turret, cursor_rect)
                if cancel_button.draw(screen):
                    placing_turret = False
                    SFX.play_fx("cancel_fx", now_fx)
            # show upgrade if turret is selected
            if selected_turret:
                # check if turret can be upgraded
                if selected_turret.upgrade_level < c.TURRET_LEVEL:
                    # show cost of an upgrade button
                    draw_text(str(c.UPGRADE_COST), load_font("pixel", 50), "grey100", (c.SCREEN_WIDTH - 200, c.SCREEN_HEIGHT - 200))
                    screen.blit(coin_gui_up, (c.SCREEN_WIDTH - 300, c.SCREEN_HEIGHT - 220))
                    if upgrade_button.draw(screen):
                        if world.money >= c.UPGRADE_COST:
                            selected_turret.upgrade()
                            world.money -= c.UPGRADE_COST
                            SFX.play_fx("upgrade_fx", now_fx)
                    if demolish_button.draw(screen):
                        selected_turret.kill()
                        selected_turret = None
                        SFX.play_fx("kill_fx", now_fx)
                else:
                    if demolish_button_past_max.draw(screen):
                        selected_turret.kill()
                        selected_turret = None
                        SFX.play_fx("kill_fx", now_fx)
        else:
            rect_width = 800
            rect_height = 400
            rect_x = (c.SCREEN_WIDTH - rect_width) // 2
            rect_y = (c.SCREEN_HEIGHT - rect_height) // 2

            pygame.draw.rect(screen, "black", (rect_x, rect_y, rect_width, rect_height), border_radius=30)
            if game_outcome == -1:
                #draw_text("GAME OVER", large_font, "grey0", (rect_x // 2, rect_y // 2))
                draw_center_text("GAME OVER", load_font("ancient", 80), "white", (1, 0), (0, rect_y + 80))
                draw_center_text("%s" %(c.CHEERUP_TEXT[0]), load_font("thai", 50), "white", (1, 0), (0, rect_y + 170))
                if world.level > high_wave:
                    high_wave = world.level
                    save_high_wave(high_wave)
            elif game_outcome == 1:
                draw_center_text("PAUSED", load_font("ancient", 80), "white", (1, 0), (0, rect_y + 80))
                #current_fast_forward_type = 0
            # restart level
            if restart_button.draw(screen):
                SFX.play_fx("button_fx", now_fx)
                reset_world()
            elif home_button.draw(screen):
                SFX.play_fx("button_fx", now_fx)
                reset_world()
                out_of_menu = False
            elif exit_paused_button.draw(screen):
                SFX.play_fx("button_fx", now_fx)
                run = False

    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and out_of_menu:
            if event.key == pygame.K_ESCAPE and game_outcome != -1:
                if game_paused_tmp % 2 == 0:
                    game_outcome = 0
                    game_paused = False
                else:
                    game_outcome = 1
                    game_paused = True
                    if placing_turret:
                        placing_turret = False
                game_paused_tmp += 1
            if pygame.time.get_ticks() - time_begin > 100: # Check if delta time is greater than 100ms
                if event.key == pygame.K_1:
                    current_fast_forward_type = 1
                if event.key == pygame.K_2:
                    current_fast_forward_type = 3
                if event.key == pygame.K_3:
                    current_fast_forward_type = 5
        if nondeselect(ignore):
            buttoning = True
        else:
            buttoning = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not buttoning:
            mouse_pos = pygame.mouse.get_pos()
            #check if mouse in screen
            if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
                selected_turret = None
                deselect_turret()
                if placing_turret:
                    # if have enough money
                    if len(turret_group) > c.LIMIT:
                        SFX.play_fx("denied", now_fx)
                    else:
                        if world.money >= c.BUY_COST and not buttoning:
                            create_turret(mouse_pos, select[0], select[1])
                else:
                    selected_turret = select_turret(mouse_pos)
        if not out_of_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_option = (selected_option - 1) % len(menu_options)
                    if not is_in_credit:
                        SFX.play_fx("menu_select", now_fx)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_option = (selected_option + 1) % len(menu_options)
                    if not is_in_credit:
                        SFX.play_fx("menu_select", now_fx)
                elif event.key == pygame.K_RETURN and not is_in_options:
                    # Perform action based on the selected option
                    if selected_option == 0:
                        out_of_menu = True
                        game_paused_tmp = 1
                    elif selected_option == 1:
                        is_in_options = True
                        selected_option = 0
                    elif selected_option == 2:
                        is_in_credit = True
                    elif selected_option == 3:
                        run = False
                    SFX.play_fx("menu_enter", now_fx)

                #ออกจากหน้าที่เข้าอยู่
                elif event.key == pygame.K_ESCAPE and is_in_credit:
                    is_in_credit = False
                    SFX.play_fx("menu_select", now_fx)
                elif event.key == pygame.K_ESCAPE and is_in_options:
                    is_in_options = False
                    SFX.play_fx("menu_select", now_fx)
                elif event.key == pygame.K_ESCAPE:
                    SFX.play_fx("menu_select", now_fx)
                    run = False
                elif is_in_options:
                    if selected_option == 0:
                        if event.key == pygame.K_RIGHT:
                            if now_music_volume < 1:
                                now_music_volume = Decimal(str(now_music_volume)) + Decimal('0.1')
                                SFX.play_fx("volume_control", now_fx)
                                pygame.mixer.music.set_volume(now_music_volume)
                            else:
                                SFX.play_fx("denied", now_fx)
                        elif event.key == pygame.K_LEFT:
                            if now_music_volume > 0:
                                now_music_volume = Decimal(str(now_music_volume)) - Decimal('0.1')
                                SFX.play_fx("volume_control", now_fx)
                                pygame.mixer.music.set_volume(now_music_volume)
                            else:
                                SFX.play_fx("denied", now_fx)
                    elif selected_option == 1:
                        if event.key == pygame.K_RIGHT:
                            if now_fx < 1:
                                now_fx = Decimal(str(now_fx)) + Decimal('0.1')
                                SFX.play_fx("volume_control", now_fx)
                            else:
                                SFX.play_fx("denied", now_fx)
                        elif event.key == pygame.K_LEFT:
                            if now_fx > 0:
                                now_fx = Decimal(str(now_fx)) - Decimal('0.1')
                                SFX.play_fx("volume_control", now_fx)
                            else:
                                SFX.play_fx("denied", now_fx)
                    elif selected_option == 2:
                        if event.key == pygame.K_RETURN:
                            save_music_volume(now_music_volume)
                            save_fx_volume(now_fx)
                            SFX.play_fx("menu_enter", now_fx)
                    elif selected_option == 3:
                        if event.key == pygame.K_RETURN:
                            is_in_options = False
                            SFX.play_fx("menu_enter", now_fx)
                setting_options = ["Music Volume : %.1f" %now_music_volume, "FX Volume : %.1f" % now_fx, "Save", "Back"]

    if not out_of_menu:
        draw_menu()
        if is_in_credit:
            draw_credits()
        if is_in_options:
            draw_options()
    if not placing_turret:
        new_cursor_rect.center = (cursor_pos[0], cursor_pos[1] + 15)
        screen.blit(new_cursor, new_cursor_rect)
    pygame.display.update()
pygame.quit()
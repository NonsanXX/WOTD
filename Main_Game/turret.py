import pygame
import config.config as c
import os
from turret_data import TURRETS_DATA
import math
class Turret(pygame.sprite.Sprite):
    def __init__(self, sprite_sheets, tile_x, tile_y, name):
        pygame.sprite.Sprite.__init__(self)
        self.upgrade_level = 1
        self.name = name
        self.range = TURRETS_DATA[self.name][self.upgrade_level - 1]["range"]
        self.cooldown = TURRETS_DATA[self.name][self.upgrade_level - 1]["cooldown"]
        self.damage = TURRETS_DATA[self.name][self.upgrade_level - 1]["damage"]
        self.volume = 0.25
        self.shot_fx = pygame.mixer.Sound(os.path.join("Main_Game", "assets", "audio", name, "1.wav"))
        self.last_shot = 0
        self.selected = False
        self.target = None

        # posi var
        self.tile_x = tile_x
        self.tile_y = tile_y
        # calc center coor
        self.x = (tile_x+0.5) * c.TILE_SIZE
        self.y = (tile_y+0.5) * c.TILE_SIZE - 25

        # animation var
        self.sprite_sheets = sprite_sheets
        self.animaion_list = self.load_image(self.sprite_sheets[self.upgrade_level - 1])
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        # Update img section
        self.angle = 90
        self.original_image = self.animaion_list[self.frame_index]
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        # show range
        self.range_image = pygame.Surface((self.range*2, self.range*2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def load_image(self, sprite_sheet):
        # to extract image from spritesheet
        animation_list = [pygame.transform.scale(frame, (130, 130)) for frame in sprite_sheet]
        
        return animation_list
    
    def update(self, enemy_group, world):
        if self.target:
            self.play_animation(world.game_speed)
        else:
            self.original_image = self.animaion_list[0]
            if pygame.time.get_ticks() - self.last_shot > self.cooldown / world.game_speed:
                self.pick_target(enemy_group)
                self.last_shot = pygame.time.get_ticks()

    def pick_target(self, enemy_group):
        # find an enemy to target
        x_dist = 0
        y_dist = 0
        # check distance to each enemy to see if it in range
        for enemy in enemy_group:
            if enemy.health > 0:
                x_dist = enemy.pos[0] - self.x
                y_dist = enemy.pos[1] - self.y
                dist = math.sqrt(x_dist**2 + y_dist**2)
                if dist <= self.range:
                    self.target = enemy
                    self.angle = math.degrees(math.atan2(-y_dist, x_dist))
                    # Play sound

                    self.shot_fx.set_volume(self.volume)
                    self.shot_fx.play()

                    # Damage enemy
                    self.target.health -= self.damage
                    if self.name != "knight": # AOE attack
                        break
    def play_animation(self, game_speed):
        # update
        try:
            self.original_image = self.animaion_list[self.frame_index]
        except IndexError:
            self.frame_index = 0
        # check time
        self.update_time = pygame.time.get_ticks()
        self.frame_index += game_speed
        if self.frame_index >= len(self.animaion_list):
            self.frame_index = 0
            self.target = None

    def upgrade(self):
        self.upgrade_level += 1
        self.range = TURRETS_DATA[self.name][self.upgrade_level - 1]["range"]
        self.cooldown = TURRETS_DATA[self.name][self.upgrade_level - 1]["cooldown"]
        self.damage = TURRETS_DATA[self.name][self.upgrade_level - 1]["damage"]
        self.shot_fx = pygame.mixer.Sound(os.path.join("Main_Game", "assets", "audio", self.name, "%s.wav"%self.upgrade_level))
        # update turret image
        self.animaion_list = self.load_image(self.sprite_sheets[self.upgrade_level - 1])
        self.original_image = self.animaion_list[0]

        # update range circle
        self.range_image = pygame.Surface((self.range*2, self.range*2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)
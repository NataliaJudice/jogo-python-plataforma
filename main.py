import pgzrun
import math
import random
from pygame import Rect

WIDTH = 800
HEIGHT = 600
TITLE = "Shadow Ascent"

scroll_y = 0
stars_bg = [(random.randint(0, WIDTH), random.randint(0, HEIGHT * 5)) for _ in range(100)]
game_state = "MENU"
sound_on = True
falling_enemies = []


class Entity:
    def __init__(self, images, x, y, w, h):
        self.images = images
        self.frame = 0
        self.image = images[0]
        self.rect = Rect(x, y, w, h)
        self.anim_speed = 0.15
        self.timer = 0

    def update_animation(self, dt):
        self.timer += dt
        if self.timer >= self.anim_speed:
            self.timer = 0
            self.frame = (self.frame + 1) % len(self.images)
            self.image = self.images[self.frame]

    def draw(self):
        pos_y = self.rect.bottom - self.rect.height
        pos_x = self.rect.centerx - (self.rect.width // 2)
        screen.blit(self.image, (pos_x, pos_y - scroll_y))


class Player(Entity):
    def __init__(self, x, y):
        self.idle_r = ['hero_idle_r1', 'hero_idle_r2']
        self.idle_l = ['hero_idle_l1', 'hero_idle_l2']
        self.walk_r = ['hero_walk_r1', 'hero_walk_r2', 'hero_walk_r3', 'hero_walk_r4']
        self.walk_l = ['hero_walk_l1', 'hero_walk_l2', 'hero_walk_l3', 'hero_walk_l4']
        super().__init__(self.idle_r, x, y, 50, 70)
        self.vel_y = 0
        self.speed = 5
        self.health = 10
        self.invincible_timer = 0
        self.jumps = 0
        self.facing_left = False

    @property
    def hitbox(self):
        return self.rect.inflate(-20, -10)

    def update_player(self, platforms, dt):
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
        
        dx = 0
        moving = False
        
        if keyboard.left:
            dx = -self.speed
            moving = True
            self.facing_left = True
        elif keyboard.right:
            dx = self.speed
            moving = True
            self.facing_left = False

        if moving:
            self.images = self.walk_l if self.facing_left else self.walk_r
        else:
            self.images = self.idle_l if self.facing_left else self.idle_r
            
        self.update_animation(dt)
        self.vel_y += 0.6
        self.rect.y += self.vel_y
        
        for plat in platforms:
            if self.rect.colliderect(plat) and self.vel_y > 0:
                self.rect.bottom = plat.top
                self.vel_y = 0
                self.jumps = 0
        
        self.rect.x += dx
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

    def jump(self):
        if self.jumps < 2:
            self.vel_y = -14
            self.jumps += 1
            if sound_on:
                try:
                    sounds.jump.play()
                except:
                    pass


class Enemy(Entity):
    def __init__(self, x, y, distance):
        self.walk_r = ['enemy_1', 'enemy_2']
        self.walk_l = ['enemy_1', 'enemy_2']
        super().__init__(self.walk_r, x, y, 45, 60)
        self.start_x = x
        self.distance = distance
        self.direction = 1

    @property
    def hitbox(self):
        return self.rect.inflate(-10, -10)

    def update_enemy(self, dt):
        self.rect.x += 2 * self.direction
        self.images = self.walk_l if self.direction == -1 else self.walk_r
        
        if abs(self.rect.x - self.start_x) > self.distance:
            self.direction *= -1
        self.update_animation(dt)


class FallingStar(Entity):
    def __init__(self, x, y):
        super().__init__(['star_enemy_1', 'star_enemy_2', 'star_enemy_3'], x, y, 60, 60)
        self.speed = random.randint(3, 6)

    def update_star(self, dt):
        self.rect.y += self.speed
        self.update_animation(dt)


player = Player(400, 500)
platforms = [Rect(0, 580, 800, 40)]
for i in range(1, 26):
    px = random.randint(50, 600)
    py = 580 - (i * 160)
    platforms.append(Rect(px, py, 160, 40))

enemies = []
for i in range(3, 25, 4):
    enemies.append(Enemy(platforms[i].x, platforms[i].y - 60, 60))

goal_rect = Rect(platforms[-1].x + 55, platforms[-1].y - 70, 50, 70)
START_Y = 500
FINISH_Y = goal_rect.y

if sound_on:
    try:
        music.play("menu_music")
    except:
        pass


def draw():
    screen.clear()
    if game_state == "MENU":
        screen.draw.text("SHADOW ASCENT", center=(400, 150), fontsize=70, color="white")
        draw_menu_buttons()
    elif game_state == "PLAYING":
        screen.fill((10, 10, 25))
        for s in stars_bg:
            screen.draw.filled_circle((s[0], (s[1] - scroll_y * 0.3) % HEIGHT), 1, "white")
        
        for i in range(len(platforms)):
            plat = platforms[i]
            if i == 0:
                screen.blit("ground_img", (plat.x, plat.y - scroll_y))
            else:
                screen.blit("platform_img", (plat.x, plat.y - scroll_y))
        
        screen.blit("goal", (goal_rect.x, goal_rect.y - scroll_y))
        
        draw_hud()
        if player.invincible_timer <= 0 or int(player.invincible_timer * 10) % 2 == 0:
            player.draw()
        for enemy in enemies:
            enemy.draw()
        for star in falling_enemies:
            star.draw()
            
    elif game_state == "GAMEOVER":
        screen.draw.text("GAME OVER", center=(400, 250), fontsize=80, color="red")
        screen.draw.text("PRESS SPACE TO RETURN TO MENU", center=(400, 400), fontsize=30, color="white")
    elif game_state == "WIN":
        screen.draw.text("VICTORY!", center=(400, 250), fontsize=100, color="gold")
        screen.draw.text("PRESS SPACE TO RETURN TO MENU", center=(400, 450), fontsize=30, color="white")


def update(dt):
    global game_state, scroll_y, falling_enemies
    
    if game_state in ["GAMEOVER", "WIN"]:
        if keyboard.space:
            reset_game()

    if game_state == "PLAYING":
        player.update_player(platforms, dt)
        target_y = player.rect.y - (HEIGHT // 2)
        scroll_y += (target_y - scroll_y) * 0.1

        if random.random() < 0.01:
            spawn_x = random.randint(0, WIDTH - 60)
            falling_enemies.append(FallingStar(spawn_x, scroll_y - 100))

        for star in falling_enemies[:]:
            star.update_star(dt)
            if player.hitbox.colliderect(star.rect) and player.invincible_timer <= 0:
                player.health -= 1
                player.invincible_timer = 1.2
                falling_enemies.remove(star)
                if sound_on:
                    try: sounds.hit.play()
                    except: pass
            elif star.rect.y > scroll_y + HEIGHT:
                falling_enemies.remove(star)

        if player.rect.colliderect(goal_rect):
            game_state = "WIN"
            music.stop()
            if sound_on:
                try: sounds.win.play()
                except: pass

        if player.health <= 0 or player.rect.y > scroll_y + HEIGHT + 100:
            game_state = "GAMEOVER"
            music.stop()
            if sound_on:
                try: sounds.lose.play()
                except: pass

        for enemy in enemies:
            enemy.update_enemy(dt)
            if player.hitbox.colliderect(enemy.hitbox) and player.invincible_timer <= 0:
                player.health -= 1
                player.invincible_timer = 1.2
                


def on_key_down(key):
    if game_state == "PLAYING" and key == keys.UP:
        player.jump()


def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == "MENU":
        if Rect(300, 250, 200, 50).collidepoint(pos):
            game_state = "PLAYING"
            music.stop()
            if sound_on:
                try:
                    music.play("bg_music")
                except:
                    pass
        elif Rect(300, 320, 200, 50).collidepoint(pos):
            sound_on = not sound_on
            if not sound_on:
                music.stop()
            else:
                try:
                    music.play("menu_music")
                except:
                    pass
        elif Rect(300, 390, 200, 50).collidepoint(pos):
            exit()


def draw_hud():
    screen.draw.text(f"LIFE: {player.health}", (20, 20), fontsize=40, color="red")


def draw_menu_buttons():
    screen.draw.filled_rect(Rect(300, 250, 200, 50), "darkgreen")
    screen.draw.text("START", center=(400, 275))
    screen.draw.filled_rect(Rect(300, 320, 200, 50), "blue" if sound_on else "gray")
    screen.draw.text("SOUND", center=(400, 345))
    screen.draw.filled_rect(Rect(300, 390, 200, 50), "darkred")
    screen.draw.text("EXIT", center=(400, 415))


def reset_game():
    global game_state, scroll_y, falling_enemies
    player.health = 10
    player.rect.topleft = (400, 500)
    player.jumps = 0
    scroll_y = 0
    falling_enemies = []
    game_state = "MENU"
    
    
    music.stop()
    
 
    
        
    if sound_on:
        try:
            music.play("menu_music")
        except:
            pass


pgzrun.go()
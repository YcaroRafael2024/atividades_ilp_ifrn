from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1" # Hide Pygame Support Message

import pygame as pg
import pygame.freetype as pgft
from scripts import BASE_RESOLUTION, INITIAL_MAX_FPS, FONT, COLORS, get_file_path, play_random_bg_music, get_music_volume, set_music_volume
from entities import Player, RandomObstaclesManager, LevelObstaclesManager, get_obstacle_list, get_3p_obstacle_list, ButtonGroup, CircularImageButton, PauseButton, ReturnButton, TextButton, Text, ScoreText, Organizer, OrganizerDirection, OrganizerOrientation, LevelsOrganizer, Limiter, Line, GradientLine, BackgroundGetter, CustomEventHandler, CustomEventList, EventPauser, AchievementsGrid, AchievementsDrawer, AchievementsHandler, PerfectionDrawer, MouseHandler
from enum import IntEnum, auto
from time import time
from typing import Any

class DeltaTimeCalculator:
    """Class that calculates automatically the 'deltatime' to the framerate independence."""
    def __init__(self):
        self.set_actual_time()
        self.get_dt()
    
    def set_actual_time(self) -> None:
        """Set actual time."""
        self._last_time = time()
    
    def get_dt(self) -> float:
        """Calculates and Returns the actual dt."""
        self._dt = time() - self._last_time
        self._last_time = time()
        return self._dt

class WindowsKeys(IntEnum):
    """Enum with the Windows Keys."""
    QUIT = auto()
    SETTINGS = auto()
    MAINMENU = auto()
    MAINGAMERANDOM = auto()
    MAINGAMELEVEL = auto()
    SETGAMEMODE = auto()
    SETLEVEL = auto()
    SHOWACHIEVEMENTS = auto()

class Game:
    def __init__(self) -> None:
        pg.init()

        self.__screen: pg.Surface = pg.display.set_mode(BASE_RESOLUTION, pg.RESIZABLE)
        pg.display.set_caption("Duet")
        icon_img = pg.image.load(get_file_path("../images/icon.png")).convert_alpha()
        pg.display.set_icon(icon_img)
        self.__clock: pg.time.Clock = pg.time.Clock()
        self.__MAX_FPS = INITIAL_MAX_FPS
        self.__FONT = FONT
        self.__current_window = WindowsKeys.MAINMENU
        self.__windows = {
            WindowsKeys.MAINMENU : self.main_menu,
            WindowsKeys.MAINGAMERANDOM : self.main_game_random,
            WindowsKeys.MAINGAMELEVEL : self.main_game_level,
            WindowsKeys.SETGAMEMODE : self.set_gamemode,
            WindowsKeys.SETLEVEL : self.set_level,
            WindowsKeys.SETTINGS : self.settings,
            WindowsKeys.SHOWACHIEVEMENTS : self.show_achievements
        }

        self._rnd_mode_settings = [2, [COLORS["RED"], COLORS["BLUE"]], get_obstacle_list]
        self.__start_level = 0
        self.__show_fps = True
        self.__delta_time = DeltaTimeCalculator()
        self.__achievements_drawer = AchievementsDrawer(self.__screen.size, self.__FONT, 20, 16, 10, COLORS["WHITE"], (100, 100, 100))

    def run(self) -> None:
        while self.__current_window != WindowsKeys.QUIT:
            window = self.__windows.get(self.__current_window)

            self.__delta_time.set_actual_time()

            if window == None: break
            else: window()
        
        pg.quit()

    def main_menu(self) -> None:
        def game_bt_func(): self.__current_window = WindowsKeys.SETGAMEMODE # Some "Game" Class function to edit these properties
        def settings_bt_func(): self.__current_window = WindowsKeys.SETTINGS
        game_settings = CircularImageButton((300, 350), "center", "gear.svg", (74, 74), 0, 3, (255, 255, 255), 0.1, (100, 100, 100), settings_bt_func)
        game_start = CircularImageButton((500, 350), "center", "triangle.svg", (60, 60), 10, 3, (255, 255, 255), 0.1, (100, 100, 100), game_bt_func)
        game_title = Text("DUET", self.__FONT, (255, 255, 255), (400, 150), "center", 70)
        fps_text = Text("FPS: ", self.__FONT, (100, 100, 100), (10, 10), size=15)
        player_background = Player((400, 250), 2, 20)
        player_background.set_circle_colors([COLORS["RED"], COLORS["BLUE"]])
        player_background.toggle_gravity()
        player_background.toggle_control()
        background = BackgroundGetter.random_background(self.__screen.get_size())
        
        self._resize_objects((game_title, fps_text, game_start, game_settings, player_background), self.__screen.get_size()) # Maybe try to find a better way later

        while self.__current_window == WindowsKeys.MAINMENU:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.__current_window = WindowsKeys.QUIT
                
                if event.type == pg.KEYDOWN: # Change Later
                    if event.key == pg.K_RETURN:
                        self.__current_window = WindowsKeys.SETGAMEMODE # Open Selected Option
                
                if event.type == pg.VIDEORESIZE:
                    self._resize_objects((game_title, fps_text, background), event.size)

                game_start.update_by_event(event)
                game_settings.update_by_event(event)
                player_background.update_by_event(event)

            self.__clock.tick(self.__MAX_FPS)
            self.__screen.fill(COLORS["BLACK"])

            dt = self.__delta_time.get_dt()

            background.update(dt)
            background.draw(self.__screen)

            player_background.update(dt)
            player_background.draw(self.__screen)

            game_title.draw(self.__screen)
            game_start.update(dt)
            game_settings.update(dt)
            game_start.draw(self.__screen)
            game_settings.draw(self.__screen)

            if self.__show_fps:
                fps_text.set_text(f"FPS: {(dt ** -1):.1f}")
                fps_text.draw(self.__screen)
            
            MouseHandler.update_cursor()
            play_random_bg_music()
            
            pg.display.flip()

    def main_game_random(self) -> None:
        def return_menu_func():
            if pause_button.is_paused:
                self.__current_window = WindowsKeys.MAINMENU
        player = Player([i // 2 for i in BASE_RESOLUTION], self._rnd_mode_settings[0], 20)
        player.set_circle_colors(self._rnd_mode_settings[1])
        pause_button = PauseButton((50, 50), (BASE_RESOLUTION[0] - 10, 10), "topright", EventPauser.toggle_timers, (255, 255, 255), 15)
        return_menu_button = ReturnButton((50, 50), (BASE_RESOLUTION[0] - 70, 10), "topright", return_menu_func, (255, 255, 255))
        obstacle_manager = RandomObstaclesManager(player.get_center(), player.get_normal_distance(), player.get_angular_speed(), 3, self._rnd_mode_settings[2])
        remaining_lives = 0
        heart_img = pg.image.load(get_file_path("../images/heart.svg")).convert_alpha() # Improve this later
        lives_count = Organizer([ heart_img for _ in range(obstacle_manager.get_remaining_lives()) ], [ 40 for _ in range(obstacle_manager.get_remaining_lives()) ], OrganizerDirection.HORIZONTAL, OrganizerOrientation.MIDDLE, 10, "topleft", (10, 10))
        score = 0
        score_text = ScoreText(score, (60, 60, 60), (255, 255, 255), self.__FONT, 20, (10, 55), "topleft", 10)
        fps_text = Text("FPS: ", self.__FONT, (100, 100, 100), (10, 75), size=15)
        best_score_text = Text("Melhor Pontuação: 0", self.__FONT, (0, 0, 0), (400, 275), "center", 30)
        collision_count = Text("Colisões: 0", self.__FONT, (0, 0, 0), (400, 325), "center", 30)
        background = BackgroundGetter.random_background(self.__screen.get_size())
        warn_text = Text("Novos Obstáculos Gerados", self.__FONT, (255, 255, 255), (400, 200), "center", 30)
        show_warn = False
        player_collided = False
        grad_line = GradientLine(
            [
                (255, 255, 255, 0), 
                (255, 255, 255, 255), 
                (255, 255, 255, 255), 
                (255, 255, 255, 255), 
                (255, 255, 255, 0)
            ],
            (0, 300),
            (800, 300),
            300
        )
        game_ended = False
        def restart_btn_event():
            obstacle_manager.reset_manager()
            CustomEventHandler.post_event(CustomEventList.NEWGENERATIONWARNING)
            CustomEventHandler.post_event(CustomEventList.RESETGAME)
        def return_btn_event():
            self.__current_window = WindowsKeys.MAINMENU
        game_end_restart_btn = TextButton((400, 500), "center", restart_btn_event, "Reiniciar", self.__FONT, (255, 255, 255), (60, 60, 60), pgft.STYLE_STRONG, size_font=30, padding_by_size=(140, 40))
        game_end_return_btn = TextButton((400, 550), "center", return_btn_event, "Retornar", self.__FONT, (255, 255, 255), (60, 60, 60), pgft.STYLE_STRONG, size_font=30, padding_by_size=(140, 40))

        self._resize_objects( # Maybe add this to a list
            (pause_button, return_menu_button, score_text, best_score_text, collision_count, fps_text, player, warn_text, lives_count, grad_line, game_end_restart_btn, game_end_return_btn, self.__achievements_drawer), 
            self.__screen.get_size()
        )
        obstacle_manager.resize(self.__screen.get_size(), player.get_center(), player.get_normal_distance())

        while self.__current_window == WindowsKeys.MAINGAMERANDOM:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.__current_window = WindowsKeys.QUIT
                
                pause_button.update_by_event(event)
                return_menu_button.update_by_event(event)
                player.update_by_event(event)
                self.__achievements_drawer.update_by_event(event)

                if event.type == pg.VIDEORESIZE:
                    obstacle_manager.resize(event.size, player.get_center(), player.get_normal_distance())
                    self._resize_objects((score_text, best_score_text, collision_count, fps_text, background, warn_text, lives_count, grad_line, game_end_restart_btn, game_end_return_btn), event.size)
                
                if event.type == CustomEventList.NEWGENERATIONWARNING:
                    remaining_lives = obstacle_manager.get_remaining_lives()
                    lives_count.change_surfaces([heart_img for _ in range(remaining_lives)], [ 40 for _ in range(remaining_lives) ])
                    warn_text.set_text("Novos Obstáculos Gerados")
                    pg.time.set_timer(CustomEventList.DISABLEWARNING, 1000, 1)
                    EventPauser.add_event(CustomEventList.DISABLEWARNING, 1000, 1)
                    show_warn = True
                
                if event.type == CustomEventList.DISABLEWARNING:
                    show_warn = False
                
                if event.type == CustomEventList.PLAYERCOLLISION: # Maybe handle this on the player's class:
                    if obstacle_manager.check_player_lost():
                        pg.time.set_timer(CustomEventList.RANDOMGAMEEND, 500, 1)
                        EventPauser.add_event(CustomEventList.RANDOMGAMEEND, 500, 1)
                        warn_text.set_text("Você perdeu todas as suas Vidas!")
                        show_warn = True
                    else: # THIS REALLY NEED TO BE BETTER
                        pg.time.set_timer(CustomEventList.RESETGAME, 500, 1)
                        EventPauser.add_event(CustomEventList.RESETGAME, 500, 1)

                    player_collided = True
                    player.add_lost_particles(event.indexes)
                    remaining_lives = obstacle_manager.get_remaining_lives()
                    lives_count.change_surfaces([heart_img for _ in range(remaining_lives)], [ 40 for _ in range(remaining_lives) ])
                
                if event.type == CustomEventList.RESETGAME:
                    game_ended = False
                    player_collided = False
                    player.reset_movements()
                    obstacle_manager.reset()
                
                if event.type == CustomEventList.RANDOMGAMEEND:
                    show_warn = False
                    game_ended = True
                    best_score = obstacle_manager.get_best_score()
                    collisions = obstacle_manager.get_player_collision_count()
                    best_score_text.set_text(f"Melhor Pontuação: {best_score}")
                    collision_count.set_text(f"Colisões: {collisions}")
                    if best_score >= 100:
                        if len(self._rnd_mode_settings[1]) == 2:
                            AchievementsHandler.unlock_achievement(3)
                        elif len(self._rnd_mode_settings[1]) == 3:
                            AchievementsHandler.unlock_achievement(4)

                        if best_score >= 1000:
                            if len(self._rnd_mode_settings[1]) == 2:
                                AchievementsHandler.unlock_achievement(5)
                            elif len(self._rnd_mode_settings[1]) == 3:
                                AchievementsHandler.unlock_achievement(6)
                
                if game_ended:
                    game_end_restart_btn.update_by_event(event)
                    game_end_return_btn.update_by_event(event)

            keys = pg.key.get_pressed()

            if keys[pg.K_LSHIFT] and keys[pg.K_ESCAPE]:
                self.__current_window = WindowsKeys.MAINMENU

            self.__clock.tick(self.__MAX_FPS)
            self.__screen.fill(COLORS["BLACK"])

            dt = self.__delta_time.get_dt()

            EventPauser.update(dt)

            background.update(dt)
            background.draw(self.__screen)

            pause_button.draw(self.__screen)

            if pause_button.is_paused:
                return_menu_button.draw(self.__screen)
            elif not game_ended: # Improve this later
                if not player_collided:
                    player.update(dt)
                    obstacle_manager.update(dt)
                    obstacle_manager.check_collision(player)
                else:
                    player.update_lost_particles(dt)

                score = obstacle_manager.get_score()
                
                score_text.set_score(score)

            player.draw(self.__screen) # Improve this draws later
            obstacle_manager.draw(self.__screen)
            lives_count.draw(self.__screen)
            score_text.draw(self.__screen)
            if game_ended: # Improve this later
                grad_line.draw(self.__screen)
                best_score_text.draw(self.__screen)
                collision_count.draw(self.__screen)
                game_end_restart_btn.draw(self.__screen)
                game_end_return_btn.draw(self.__screen)

            if show_warn:
                warn_text.draw(self.__screen)

            if self.__show_fps:
                fps_text.set_text(f"FPS: {(dt ** -1):.1f}")
                fps_text.draw(self.__screen)

            self.__achievements_drawer.update(dt)
            self.__achievements_drawer.draw(self.__screen)
            
            MouseHandler.update_cursor()
            play_random_bg_music()
            
            pg.display.flip()

    def main_game_level(self) -> None:
        def return_menu_func():
            if pause_button.is_paused:
                self.__current_window = WindowsKeys.MAINMENU
        player = Player([i // 2 for i in BASE_RESOLUTION], 2, 20)
        player.set_circle_colors([COLORS["RED"], COLORS["BLUE"]])
        pause_button = PauseButton((50, 50), (BASE_RESOLUTION[0] - 10, 10), "topright", EventPauser.toggle_timers, (255, 255, 255), 15)
        return_menu_button = ReturnButton((50, 50), (BASE_RESOLUTION[0] - 70, 10), "topright", return_menu_func, (255, 255, 255))
        perfection_drawer = PerfectionDrawer((50, 50), 30, COLORS["GREEN"], COLORS["RED"], COLORS["WHITE"], self.__start_level, difference_expansion=5, repetition_time=1)
        obstacle_manager = LevelObstaclesManager(player.get_center(), player.get_normal_distance(), player.get_angular_speed(), self.__start_level, perfection_drawer)
        collision_count = Text("Colisões: 0", self.__FONT, (255, 255, 255), (10, 90), size=20)
        fps_text = Text("FPS: ", self.__FONT, (100, 100, 100), (10, 115), size=15)
        background = BackgroundGetter.random_background(self.__screen.get_size())
        warn_text = Text("Nível: 0", self.__FONT, (255, 255, 255), (400, 200), "center", 30)
        show_warn = False
        player_collided = False

        self._resize_objects((pause_button, return_menu_button, collision_count, fps_text, player, warn_text, perfection_drawer, self.__achievements_drawer), self.__screen.get_size())
        obstacle_manager.resize(self.__screen.get_size(), player.get_center(), player.get_normal_distance())

        while self.__current_window == WindowsKeys.MAINGAMELEVEL:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.__current_window = WindowsKeys.QUIT
                
                pause_button.update_by_event(event)
                return_menu_button.update_by_event(event)
                player.update_by_event(event)
                self.__achievements_drawer.update_by_event(event)

                if event.type == pg.VIDEORESIZE:
                    obstacle_manager.resize(event.size, player.get_center(), player.get_normal_distance())
                    self._resize_objects((collision_count, fps_text, background, warn_text, perfection_drawer), event.size)
                
                if event.type == CustomEventList.NEWLEVELWARNING:
                    warn_text.set_text(f"Nível: {event.level}")
                    pg.time.set_timer(CustomEventList.DISABLEWARNING, 1000, 1)
                    EventPauser.add_event(CustomEventList.DISABLEWARNING, 1000, 1) # Maybe we can get this better with the "EventHandler"
                    show_warn = True
                    perfection_drawer.reset(obstacle_manager.get_actual_level())
                
                if event.type == CustomEventList.DISABLEWARNING:
                    show_warn = False
                
                if event.type == CustomEventList.PLAYERCOLLISION: # Maybe handle this on the player's class
                    pg.time.set_timer(CustomEventList.RESETGAME, 500, 1)
                    EventPauser.add_event(CustomEventList.RESETGAME, 500, 1)
                    player_collided = True
                    player.add_lost_particles(event.indexes)
                
                if event.type == CustomEventList.RESETGAME:
                    player_collided = False
                    player.reset_movements()
                    obstacle_manager.reset()
                    perfection_drawer.reset(obstacle_manager.get_actual_level())
                    perfection_drawer.check_movements()
                
                if event.type == CustomEventList.RANDOMGAMEEND:
                    self.__current_window = WindowsKeys.MAINMENU

                if event.type == pg.KEYDOWN:
                    if event.key in [pg.K_a, pg.K_d, pg.K_SPACE, pg.K_LSHIFT] and not pause_button.is_paused:
                        perfection_drawer.update_movements()
                
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1 and not pause_button.is_paused:
                        perfection_drawer.update_movements()

            keys = pg.key.get_pressed()

            if keys[pg.K_LSHIFT] and keys[pg.K_ESCAPE]:
                self.__current_window = WindowsKeys.MAINMENU

            self.__clock.tick(self.__MAX_FPS)
            self.__screen.fill(COLORS["BLACK"])

            dt = self.__delta_time.get_dt()

            EventPauser.update(dt)

            background.update(dt)
            background.draw(self.__screen)

            pause_button.draw(self.__screen)

            self.__achievements_drawer.update(dt)
            self.__achievements_drawer.draw(self.__screen)
            perfection_drawer.update(dt)
            perfection_drawer.draw(self.__screen)

            if pause_button.is_paused:
                player.draw(self.__screen)
                obstacle_manager.draw(self.__screen)
                return_menu_button.draw(self.__screen)
            else:
                if not player_collided:
                    player.update(dt)
                    obstacle_manager.update(dt)
                    obstacle_manager.check_collision(player)
                else:
                    player.update_lost_particles(dt)

                player.draw(self.__screen)
                obstacle_manager.draw(self.__screen)

                collisions = obstacle_manager.get_player_collision_count()
                collision_count.set_text(f"Colisões: {collisions}")

            collision_count.draw(self.__screen)

            if show_warn:
                warn_text.draw(self.__screen)

            if self.__show_fps:
                fps_text.set_text(f"FPS: {(dt ** -1):.1f}")
                fps_text.draw(self.__screen)
            
            MouseHandler.update_cursor()
            play_random_bg_music()
            
            pg.display.flip()

    def set_gamemode(self) -> None:
        def return_menu_func():
            self.__current_window = WindowsKeys.MAINMENU
        def game_bt_func():
            self._rnd_mode_settings = [2, [COLORS["RED"], COLORS["BLUE"]], get_obstacle_list]
            self.__current_window = WindowsKeys.MAINGAMERANDOM
        def game_bt_func_3p():
            self._rnd_mode_settings = [3, [COLORS["RED"], COLORS["BLUE"], COLORS["GREEN"]], get_3p_obstacle_list]
            self.__current_window = WindowsKeys.MAINGAMERANDOM
        def game_lvl_func(): 
            self.__current_window = WindowsKeys.SETLEVEL
        def show_achievement_func(): 
            self.__current_window = WindowsKeys.SHOWACHIEVEMENTS
        player_background = Player((400, 300), 2, 20)
        player_background.set_circle_colors([COLORS["RED"], COLORS["BLUE"]])
        player_background.toggle_gravity()
        player_background.toggle_control()
        fps_text = Text("FPS: ", self.__FONT, (100, 100, 100), (10, 10), size=15)
        background = BackgroundGetter.random_background(self.__screen.get_size())
        buttongroup = ButtonGroup(
            (400, 300), 
            [
                TextButton((0, 0), "center", game_bt_func, "Geração Aleatória", self.__FONT, (255, 255, 255), style=pgft.STYLE_STRONG, size_font=40),
                TextButton((0, 0), "center", game_lvl_func, "Níveis", self.__FONT, (255, 255, 255), style=pgft.STYLE_STRONG, size_font=40),
                TextButton((0, 0), "center", game_bt_func_3p, "Modo 3 Players", self.__FONT, (0, 255, 0), style=pgft.STYLE_STRONG, size_font=40),
                TextButton((0, 0), "center", show_achievement_func, "Conquistas", self.__FONT, (255, 255, 255), style=pgft.STYLE_STRONG, size_font=40)
            ],
            25,
            False
        )
        return_menu_button = ReturnButton((50, 50), (20, 20), "topleft", return_menu_func, (255, 255, 255)) # This code repeat a lot of times

        self._resize_objects((player_background, fps_text, buttongroup, return_menu_button), self.__screen.get_size())

        while self.__current_window == WindowsKeys.SETGAMEMODE:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.__current_window = WindowsKeys.QUIT
                
                if event.type == pg.KEYDOWN: # Change Later
                    if event.key == pg.K_ESCAPE:
                        self.__current_window = WindowsKeys.MAINMENU
                    
                    if event.key == pg.K_RETURN:
                        self.__current_window = WindowsKeys.MAINGAME # Open Selected Option
                
                if event.type == pg.VIDEORESIZE:
                    self._resize_objects((fps_text, background, return_menu_button), event.size)

                player_background.update_by_event(event)
                buttongroup.update_by_event(event)
                return_menu_button.update_by_event(event)

            self.__clock.tick(self.__MAX_FPS)
            self.__screen.fill(COLORS["BLACK"])

            dt = self.__delta_time.get_dt()

            background.update(dt)
            background.draw(self.__screen)

            player_background.update(dt)
            player_background.draw(self.__screen)

            buttongroup.draw(self.__screen)
            return_menu_button.draw(self.__screen)

            if self.__show_fps:
                fps_text.set_text(f"FPS: {(dt ** -1):.1f}")
                fps_text.draw(self.__screen)
            
            MouseHandler.update_cursor()
            play_random_bg_music()
            
            pg.display.flip()

    def set_level(self) -> None:
        def return_menu_func():
            self.__current_window = WindowsKeys.SETGAMEMODE
        def set_level(n: int): 
            def set_start() -> None:
                self.__current_window = WindowsKeys.MAINGAMELEVEL
                self.__start_level = n
            return set_start
        player_background = Player((200, 300), 2, 20)
        player_background.set_circle_colors([COLORS["RED"], COLORS["BLUE"]])
        player_background.toggle_gravity()
        player_background.toggle_control()
        fps_text = Text("FPS: ", self.__FONT, (100, 100, 100), (10, 10), size=15)
        background = BackgroundGetter.random_background(self.__screen.get_size())
        levels_organizer = LevelsOrganizer(400, (600, 0), 75, 3, set_level, self.__FONT)
        division_line = Line((400, 0), (400, 600), 5, 5, COLORS["WHITE"])
        level_text = Text("Seletor - Niveis", self.__FONT, COLORS["WHITE"], (200, 300), "center", 50)
        return_menu_button = ReturnButton((50, 50), (20, 20), "topleft", return_menu_func, (255, 255, 255)) # This code repeat a lot of times

        self._resize_objects((player_background, fps_text, levels_organizer, division_line, level_text, return_menu_button), self.__screen.get_size())

        while self.__current_window == WindowsKeys.SETLEVEL:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.__current_window = WindowsKeys.QUIT
                
                if event.type == pg.KEYDOWN: # Change Later
                    if event.key == pg.K_ESCAPE:
                        self.__current_window = WindowsKeys.SETGAMEMODE
                    
                    if event.key == pg.K_RETURN:
                        self.__current_window = WindowsKeys.MAINGAME # Open Selected Option
                
                if event.type == pg.VIDEORESIZE:
                    self._resize_objects((fps_text, background, division_line, level_text, return_menu_button), event.size)

                player_background.update_by_event(event)
                levels_organizer.update_by_event(event)
                return_menu_button.update_by_event(event)

            self.__clock.tick(self.__MAX_FPS)
            self.__screen.fill(COLORS["BLACK"])

            dt = self.__delta_time.get_dt()

            background.update(dt)
            background.draw(self.__screen)

            player_background.update(dt)
            player_background.draw(self.__screen)

            levels_organizer.draw(self.__screen)
            level_text.draw(self.__screen)
            division_line.draw(self.__screen)
            return_menu_button.draw(self.__screen)

            if self.__show_fps:
                fps_text.set_text(f"FPS: {(dt ** -1):.1f}")
                fps_text.draw(self.__screen)
            
            MouseHandler.update_cursor()
            play_random_bg_music()

            pg.display.flip()

    def show_achievements(self) -> None:
        def return_menu_func():
            self.__current_window = WindowsKeys.SETGAMEMODE
        fps_text = Text("FPS: ", self.__FONT, (100, 100, 100), (10, 10), size=15)
        background = BackgroundGetter.random_background(self.__screen.get_size())
        achievement_grid = AchievementsGrid(self.__screen.get_size(), COLORS["WHITE"], (120, 120, 120), (30, 30, 30), 20, 1.5, 10)
        return_menu_button = ReturnButton((50, 50), (BASE_RESOLUTION[0] - 20, 20), "topright", return_menu_func, (255, 255, 255))
        
        self._resize_objects((fps_text, achievement_grid, return_menu_button), self.__screen.get_size()) # Maybe try to find a better way later

        while self.__current_window == WindowsKeys.SHOWACHIEVEMENTS:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.__current_window = WindowsKeys.QUIT
                
                if event.type == pg.KEYDOWN: # Change Later
                    if event.key == pg.K_RETURN:
                        self.__current_window = WindowsKeys.SETGAMEMODE # Open Selected Option
                
                if event.type == pg.VIDEORESIZE:
                    self._resize_objects((fps_text, background, achievement_grid, return_menu_button), event.size)
                
                achievement_grid.update_by_event(event)
                return_menu_button.update_by_event(event)

            keys = pg.key.get_pressed()

            if keys[pg.K_LSHIFT] and keys[pg.K_ESCAPE]:
                self.__current_window = WindowsKeys.SETGAMEMODE

            self.__clock.tick(self.__MAX_FPS)
            self.__screen.fill(COLORS["BLACK"])

            dt = self.__delta_time.get_dt()

            background.update(dt)
            background.draw(self.__screen)

            achievement_grid.draw(self.__screen)
            return_menu_button.draw(self.__screen)

            if self.__show_fps:
                fps_text.set_text(f"FPS: {(dt ** -1):.1f}")
                fps_text.draw(self.__screen)
            
            MouseHandler.update_cursor()
            play_random_bg_music()
            
            pg.display.flip()

    def settings(self) -> None:
        def return_menu_func():
            self.__current_window = WindowsKeys.MAINMENU
        def toggle_fps_visibility():
            self.__show_fps = not self.__show_fps
        def set_max_fps(amount: float):
            if amount == 300:
                self.__MAX_FPS = 0
                limiter_fps_text.set_text(f"FPS Ilimitado")
            else:
                self.__MAX_FPS = amount
                limiter_fps_text.set_text(f"Máx. FPS: {self.__MAX_FPS:.1f}")
        def set_volume_all(volume: float):
            set_music_volume(volume)
            volume_text.set_text(f"Volume: {round(volume * 100)}%")
        fps_text = Text("FPS: ", self.__FONT, (100, 100, 100), (10, 10), size=15)
        background = BackgroundGetter.random_background(self.__screen.get_size())
        toggle_fps_vsblt_btn = TextButton((200, 200), "topleft", toggle_fps_visibility, "Mostrar FPS", self.__FONT, COLORS["WHITE"], (80, 80, 80), size_font=20, padding=(15, 15))
        limiter_fps = Limiter((165, 50), (225, 300), "topleft", (50, 50, 50), COLORS["WHITE"], 1, 300, 300 if self.__MAX_FPS == 0 else self.__MAX_FPS, set_max_fps)
        limiter_fps_text = Text("Máx. FPS: ", self.__FONT, COLORS["WHITE"], (425, 325), "midleft", 30)
        volume_limiter = Limiter((165, 50), (225, 400), "topleft", (50, 50, 50), COLORS["WHITE"], 0.0, 1.0, get_music_volume(), set_volume_all)
        volume_text = Text("", self.__FONT, COLORS["WHITE"], (425, 425), "midleft", 30)
        return_menu_button = ReturnButton((50, 50), (BASE_RESOLUTION[0] - 20, 20), "topright", return_menu_func, (255, 255, 255))
        set_max_fps(limiter_fps.get_actual_value())
        set_volume_all(volume_limiter.get_actual_value())
        
        self._resize_objects((fps_text, toggle_fps_vsblt_btn, limiter_fps, limiter_fps_text, volume_limiter, volume_text, return_menu_button), self.__screen.get_size())

        while self.__current_window == WindowsKeys.SETTINGS:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.__current_window = WindowsKeys.QUIT
                
                if event.type == pg.KEYDOWN: # Change Later
                    if event.key == pg.K_ESCAPE:
                        self.__current_window = WindowsKeys.MAINMENU
                
                if event.type == pg.VIDEORESIZE:
                    self._resize_objects((fps_text, background, limiter_fps, limiter_fps_text, volume_limiter, volume_text, return_menu_button), event.size)
                    
                toggle_fps_vsblt_btn.update_by_event(event)
                limiter_fps.update_by_event(event)
                volume_limiter.update_by_event(event)
                return_menu_button.update_by_event(event)

            self.__clock.tick(self.__MAX_FPS)
            self.__screen.fill(COLORS["BLACK"])

            dt = self.__delta_time.get_dt()

            background.update(dt)
            background.draw(self.__screen)

            toggle_fps_vsblt_btn.draw(self.__screen)

            limiter_fps_text.draw(self.__screen)
            volume_text.draw(self.__screen)

            limiter_fps.update(dt)
            limiter_fps.draw(self.__screen)
            volume_limiter.update(dt)
            volume_limiter.draw(self.__screen)
            return_menu_button.draw(self.__screen)

            if self.__show_fps:
                fps_text.set_text(f"FPS: {(dt ** -1):.1f}")
                fps_text.draw(self.__screen)
            
            MouseHandler.update_cursor()
            play_random_bg_music()
            
            pg.display.flip()

    @staticmethod
    def _resize_objects(objects: list[Any], resolution: tuple[int, int]) -> None:
        for obj in objects:
            obj.resize(resolution)

if __name__ == '__main__':
    Game().run()

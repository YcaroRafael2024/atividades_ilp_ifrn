from . import BaseObstaclesManager
from ..eventhandler import CustomEventHandler, CustomEventList
from scripts import get_file_path
from copy import deepcopy
from json import load as json_load

class LevelObstaclesManager(BaseObstaclesManager):
    """An Obstacle Manager that generates pre-defined obstacles (levels)."""
    def __init__(self, player_center: tuple[int, int], player_normal_distance: int, player_angular_speed: float, actual_level: int = 1) -> None:
        super().__init__(player_center, player_normal_distance, player_angular_speed)
        self._actual_level = max(1, actual_level)

    def _generate_obstacles(self) -> None:
        """Load Current Level Obstacles."""
        self._total_score += self._actual_score
        self._actual_score = 0
        self._obstacles.clear()
        # Basically to convert the "standard" obstacles to the new resolution
        self._speed = self._base_obstacles_attrs[2]
        actual_center = self._player_center
        actual_distance = self._player_normal_distance
        self._player_center = self._base_obstacles_attrs[0]
        self._player_normal_distance = self._base_obstacles_attrs[1]

        with open(get_file_path("../data/levels.json")) as file:
            levels: dict[str, list[int]] = json_load(file)

        indexes_lvl = levels.get(f"{self._actual_level}")

        if indexes_lvl is None:
            # Raise custom event
            self._actual_level = 1
            indexes_lvl = levels.get(f"{self._actual_level}")

        CustomEventHandler.post_event(CustomEventList.NEWLEVELWARNING, {"level" : self._actual_level})
        self._actual_level += 1

        for i in indexes_lvl:
            self._obstacles.append(deepcopy(self._possibles_obstacles[i]))
        
        self._amount_obstacles = len(self._obstacles)
        self._set_base_y()
        self._last_obstacle = self._obstacles[self._amount_obstacles-1]
        self.resize(self._actual_resolution, actual_center, actual_distance)

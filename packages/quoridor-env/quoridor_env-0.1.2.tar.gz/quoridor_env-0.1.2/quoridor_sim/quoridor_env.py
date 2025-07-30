import gymnasium as gym
from gymnasium import spaces
import numpy as np

from .core import QuoridorGame

class QuoridorEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 5}

    def __init__(self, num_players=2, max_walls=10):
        super().__init__()
        self.game = QuoridorGame(num_players=num_players, max_walls=max_walls)
        self.num_players = num_players
        self.board_size = self.game.board_size

        # Define action space: move (4) + wall placements (2 * 64) max
        self.action_space = spaces.Discrete(4 + 2 * (self.board_size - 1) ** 2)

        # Observation: C x H x W (channels: players, walls, goals)
        self.observation_space = spaces.Box(
            low=0, high=1,
            shape=(6, self.board_size, self.board_size),
            dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game.reset()
        obs = self._get_obs()
        return obs, {}

    def step(self, action):
        legal_actions = self.game.legal_moves()
        action_obj = self._decode_action(action)

        if action_obj not in legal_actions:
            # Invalid action => no-op and penalty
            reward = -1.0
            terminated = False
            truncated = False
            info = {"invalid_action": True}
            obs = self._get_obs()
            return obs, reward, terminated, truncated, info

        self.game.step(action_obj)

        obs = self._get_obs()
        reward = 1.0 if self.game.winner == self.game.turn else 0.0
        terminated = self.game.winner is not None
        truncated = False
        info = {}

        return obs, reward, terminated, truncated, info

    def render(self):
        print("Positions:", self.game.positions)
        print("Horizontal walls:", self.game.horiz_walls)
        print("Vertical walls:", self.game.vert_walls)

    def _get_obs(self):
        state = self.game.get_state()
        obs = np.zeros((6, self.board_size, self.board_size), dtype=np.float32)

        for idx, (x, y) in enumerate(state["positions"]):
            obs[idx, x, y] = 1.0

        for x, y in state["horiz_walls"]:
            obs[4, x, y] = 1.0

        for x, y in state["vert_walls"]:
            obs[5, x, y] = 1.0

        return obs

    def _decode_action(self, action):
        if action < 4:
            # 0: up, 1: down, 2: left, 3: right
            dx, dy = [(0, -1), (0, 1), (-1, 0), (1, 0)][action]
            x, y = self.game.positions[self.game.turn]
            return ("move", x + dx, y + dy)
        else:
            i = action - 4
            n = (self.board_size - 1) ** 2
            if i < n:
                x, y = divmod(i, self.board_size - 1)
                return ("wall", x, y, "h")
            else:
                i -= n
                x, y = divmod(i, self.board_size - 1)
                return ("wall", x, y, "v")

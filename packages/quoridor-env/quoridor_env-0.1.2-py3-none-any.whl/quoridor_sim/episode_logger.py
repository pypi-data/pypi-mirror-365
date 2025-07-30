import json
import os
from datetime import datetime

class EpisodeLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.episode = []

    def log_step(self, observation, action, reward, next_observation, done):
        self.episode.append({
            "observation": observation.tolist(),
            "action": action,
            "reward": reward,
            "next_observation": next_observation.tolist(),
            "done": done
        })

    def save(self, tag=None):
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"episode_{tag + '_' if tag else ''}{timestamp}.json"
        path = os.path.join(self.log_dir, filename)
        with open(path, "w") as f:
            json.dump(self.episode, f)
        self.episode.clear()
        return path

    def load(self, filepath):
        with open(filepath, "r") as f:
            return json.load(f)

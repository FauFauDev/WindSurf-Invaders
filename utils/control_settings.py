import json
import os
import pygame

DEFAULT_BINDINGS = {
    "move_left": pygame.K_LEFT,
    "move_right": pygame.K_RIGHT,
    "move_up": pygame.K_UP,
    "move_down": pygame.K_DOWN,
    "fire": pygame.K_SPACE,
}

ACTION_DEFINITIONS = [
    ("move_left", "Move Left"),
    ("move_right", "Move Right"),
    ("move_up", "Move Up"),
    ("move_down", "Move Down"),
    ("fire", "Fire"),
]


class ControlSettings:
    """Manage configurable key bindings and persistence."""

    FILE_PATH = os.path.join("data", "controls.json")
    DEFAULT_BINDINGS = DEFAULT_BINDINGS
    ACTIONS = ACTION_DEFINITIONS

    def __init__(self):
        self.bindings = {action: DEFAULT_BINDINGS[action] for action, _ in self.ACTIONS}
        self.load()

    def load(self):
        if not os.path.exists(self.FILE_PATH):
            return
        try:
            with open(self.FILE_PATH, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            for action, key_code in data.items():
                if action in self.bindings and isinstance(key_code, int):
                    self.bindings[action] = key_code
        except (OSError, ValueError, json.JSONDecodeError):
            # Keep defaults on failure
            pass

    def save(self):
        os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        with open(self.FILE_PATH, "w", encoding="utf-8") as handle:
            json.dump(self.bindings, handle, indent=2)

    def reset_defaults(self):
        for action, default_key in DEFAULT_BINDINGS.items():
            self.bindings[action] = default_key
        self.save()

    def get(self, action):
        return self.bindings.get(action, DEFAULT_BINDINGS[action])

    def set_binding(self, action, key):
        if action not in self.bindings:
            return
        previous_key = self.bindings[action]
        if previous_key == key:
            return
        # Ensure uniqueness by swapping keys if necessary
        for other_action, other_key in self.bindings.items():
            if other_action != action and other_key == key:
                self.bindings[other_action] = previous_key
        self.bindings[action] = key
        self.save()

    def key_label(self, action):
        return self.format_key(self.get(action))

    @staticmethod
    def format_key(key):
        try:
            name = pygame.key.name(key)
        except pygame.error:
            name = str(key)
        return name.upper()

    def iter_bindings(self):
        for action, label in self.ACTIONS:
            yield action, label, self.get(action)

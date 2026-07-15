"""Optional sound effects (soft, kid-friendly)."""

import pygame


class AudioSystem:
    """Simple procedural bleeps — no external files needed."""

    def __init__(self):
        self.enabled = False
        self._initialized = False

    def init(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self._initialized = True
        except pygame.error:
            self._initialized = False

    def _beep(self, frequency: int, duration_ms: int):
        if not self.enabled or not self._initialized:
            return
        try:
            import math
            import array
            sample_rate = 22050
            n_samples = int(sample_rate * duration_ms / 1000)
            buf = array.array("h")
            for i in range(n_samples):
                t = i / sample_rate
                envelope = 1.0 - (i / n_samples)
                val = int(3000 * envelope * math.sin(2 * math.pi * frequency * t))
                buf.append(val)
                buf.append(val)
            sound = pygame.mixer.Sound(buffer=buf)
            sound.play()
        except (pygame.error, ImportError):
            pass

    def play_splash(self):
        self._beep(440, 80)

    def play_collect(self):
        self._beep(660, 100)

    def play_hurt(self):
        self._beep(220, 200)

    def play_plastic(self):
        self._beep(330, 120)

    def play_happy(self):
        self._beep(784, 120)
        self._beep(988, 100)

    def play_wave(self):
        self._beep(523, 80)
        self._beep(659, 80)

    def play_treasure(self):
        self._beep(440, 80)
        self._beep(554, 80)
        self._beep(659, 120)

    def play_milestone(self):
        self._beep(523, 100)
        self._beep(659, 100)
        self._beep(784, 140)

    def play_powerup(self):
        self._beep(600, 90)
        self._beep(800, 110)

    def toggle(self):
        self.enabled = not self.enabled

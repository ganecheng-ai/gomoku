# -*- coding: utf-8 -*-
"""
五子棋游戏音效模块
"""

import pygame
import os
from enum import Enum


class SoundType(Enum):
    """音效类型"""
    MOVE = "move"           # 落子音效
    WIN = "win"             # 获胜音效
    UNDO = "undo"           # 悔棋音效
    CLICK = "click"         # 按钮点击音效
    START = "start"         # 游戏开始音效


class SoundManager:
    """音效管理器"""

    def __init__(self, enabled: bool = True):
        """
        初始化音效管理器

        Args:
            enabled: 是否启用音效
        """
        self.enabled = enabled
        self.sounds = {}
        self.music_playing = False

        if self.enabled:
            self._init_sounds()

    def _init_sounds(self):
        """初始化音效"""
        # 使用 pygame 的合成器生成简单音效
        # 落子音效 - 短促的敲击声
        self.sounds[SoundType.MOVE] = self._create_move_sound()

        # 获胜音效 - 欢快的音效
        self.sounds[SoundType.WIN] = self._create_win_sound()

        # 悔棋音效
        self.sounds[SoundType.UNDO] = self._create_undo_sound()

        # 点击音效
        self.sounds[SoundType.CLICK] = self._create_click_sound()

        # 开始音效
        self.sounds[SoundType.START] = self._create_start_sound()

    def _create_move_sound(self) -> pygame.mixer.Sound:
        """创建落子音效"""
        sample_rate = 22050
        duration = 0.1
        n_samples = int(sample_rate * duration)

        # 生成一个简单的敲击音
        import array
        buf = array.array('h', [0] * n_samples)

        # 衰减的正弦波
        import math
        freq = 800
        for i in range(n_samples):
            t = i / sample_rate
            envelope = 1.0 - (t / duration)
            value = int(10000 * envelope * math.sin(2 * math.pi * freq * t))
            buf[i] = max(-32768, min(32767, value))

        return pygame.mixer.Sound(buffer=buf)

    def _create_win_sound(self) -> pygame.mixer.Sound:
        """创建获胜音效"""
        sample_rate = 22050
        duration = 0.5
        n_samples = int(sample_rate * duration)

        import array
        buf = array.array('h', [0] * n_samples)

        import math
        # 播放一个上行的音阶
        notes = [523, 659, 784, 1047]  # C5, E5, G5, C6
        note_duration = duration / len(notes)

        for i in range(n_samples):
            t = i / sample_rate
            note_idx = int(t / note_duration)
            if note_idx < len(notes):
                note_t = t - note_idx * note_duration
                envelope = 1.0 - (note_t / note_duration)
                freq = notes[note_idx]
                value = int(8000 * envelope * math.sin(2 * math.pi * freq * t))
                buf[i] = max(-32768, min(32767, value))

        return pygame.mixer.Sound(buffer=buf)

    def _create_undo_sound(self) -> pygame.mixer.Sound:
        """创建悔棋音效"""
        sample_rate = 22050
        duration = 0.15
        n_samples = int(sample_rate * duration)

        import array
        buf = array.array('h', [0] * n_samples)

        import math
        # 向下的滑音
        for i in range(n_samples):
            t = i / sample_rate
            freq = 600 - (t / duration) * 200
            envelope = 1.0 - (t / duration)
            value = int(8000 * envelope * math.sin(2 * math.pi * freq * t))
            buf[i] = max(-32768, min(32767, value))

        return pygame.mixer.Sound(buffer=buf)

    def _create_click_sound(self) -> pygame.mixer.Sound:
        """创建按钮点击音效"""
        sample_rate = 22050
        duration = 0.05
        n_samples = int(sample_rate * duration)

        import array
        buf = array.array('h', [0] * n_samples)

        import math
        freq = 1200
        for i in range(n_samples):
            t = i / sample_rate
            value = int(5000 * math.sin(2 * math.pi * freq * t))
            buf[i] = max(-32768, min(32767, value))

        return pygame.mixer.Sound(buffer=buf)

    def _create_start_sound(self) -> pygame.mixer.Sound:
        """创建游戏开始音效"""
        sample_rate = 22050
        duration = 0.3
        n_samples = int(sample_rate * duration)

        import array
        buf = array.array('h', [0] * n_samples)

        import math
        # 一个清脆的开始音
        notes = [392, 523]  # G4, C5
        note_duration = duration / len(notes)

        for i in range(n_samples):
            t = i / sample_rate
            note_idx = int(t / note_duration)
            if note_idx < len(notes):
                note_t = t - note_idx * note_duration
                freq = notes[note_idx]
                value = int(7000 * math.sin(2 * math.pi * freq * t))
                buf[i] = max(-32768, min(32767, value))

        return pygame.mixer.Sound(buffer=buf)

    def play(self, sound_type: SoundType):
        """
        播放音效

        Args:
            sound_type: 音效类型
        """
        if not self.enabled:
            return

        if sound_type in self.sounds:
            self.sounds[sound_type].play()

    def toggle(self) -> bool:
        """
        切换音效开关

        Returns:
            新的音效状态
        """
        self.enabled = not self.enabled
        return self.enabled

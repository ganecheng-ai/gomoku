# -*- coding: utf-8 -*-
"""
五子棋游戏主程序
"""

import sys
from typing import Tuple

import pygame
from pygame.locals import *

import tkinter as tk
from tkinter import filedialog

from config import *
from game import GomokuGame, Stone, GameState
from ai import GomokuAI
from sound import SoundManager, SoundType


class Button:
    """按钮类"""

    def __init__(self, x: int, y: int, width: int, height: int, text: str, font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hovered = False

    def draw(self, screen: pygame.Surface):
        """绘制按钮"""
        color = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON_BG
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_TEXT, self.rect, 2, border_radius=8)

        text_surface = self.font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件，返回是否被点击"""
        if event.type == MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class GomokuUI:
    """五子棋游戏界面"""

    def __init__(self):
        """初始化游戏 UI"""
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # 初始化字体 (尝试使用中文字体)
        self._init_fonts()

        # 游戏实例
        self.game = GomokuGame()
        self.ai = GomokuAI(difficulty=2)

        # 游戏状态
        self.state = STATE_MENU
        self.game_mode = None  # "pvp" = 双人对战，"pve" = 人机对战
        self.ai_thinking = False
        self.ai_move_timer = 0

        # 游戏设置
        self.forbidden_rules = FORBIDDEN_RULES_ENABLED
        self.time_limit = DEFAULT_TIME_LIMIT
        self.first_player = Stone.BLACK

        # 创建按钮
        self._create_buttons()

        # 最后落子位置
        self.last_move = None

        # 音效管理器
        self.sound_manager = SoundManager(enabled=True)
        self.sound_toggle_button = None

    def _init_fonts(self):
        """初始化字体"""
        # 尝试加载中文字体
        font_names = [
            'SimHei',      # 黑体 (Windows)
            'Microsoft YaHei',  # 微软雅黑 (Windows)
            'PingFang SC',      # 苹方 (macOS)
            'Heiti SC',         # 黑体 (macOS)
            'WenQuanYi Zen Hei', # 文泉驿 (Linux)
            'Noto Sans CJK SC',  # 思源黑体
            'Arial Unicode MS',
        ]

        self.font_title = None
        self.font_text = None
        self.font_small = None

        for font_name in font_names:
            try:
                self.font_title = pygame.font.SysFont(font_name, FONT_SIZE_TITLE)
                self.font_text = pygame.font.SysFont(font_name, FONT_SIZE_TEXT)
                self.font_small = pygame.font.SysFont(font_name, FONT_SIZE_SMALL)
                break
            except:
                continue

        # 如果所有中文字体都加载失败，使用默认字体
        if self.font_title is None:
            self.font_title = pygame.font.Font(None, FONT_SIZE_TITLE * 2)
            self.font_text = pygame.font.Font(None, FONT_SIZE_TEXT * 2)
            self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL * 2)

    def _create_buttons(self):
        """创建菜单按钮"""
        button_width = 200
        button_height = 50
        start_x = (WINDOW_WIDTH - button_width) // 2

        self.btn_pvp = Button(
            start_x, 250, button_width, button_height,
            "双人对战", self.font_text
        )
        self.btn_pve = Button(
            start_x, 320, button_width, button_height,
            "人机对战", self.font_text
        )
        self.btn_settings = Button(
            start_x, 390, button_width, button_height,
            "游戏设置", self.font_text
        )
        self.btn_back = Button(
            start_x, 390, button_width, button_height,
            "返回菜单", self.font_text
        )
        self.btn_restart = Button(
            start_x, 390, button_width, button_height,
            "重新开始", self.font_text
        )
        self.btn_undo = Button(
            280, 580, 100, 40,
            "悔棋", self.font_small
        )
        self.btn_menu = Button(
            420, 580, 100, 40,
            "菜单", self.font_small
        )
        self.btn_sound = Button(
            560, 580, 100, 40,
            "音效：开", self.font_small
        )
        self.btn_save = Button(
            280, 630, 100, 40,
            "保存棋谱", self.font_small
        )
        self.btn_load = Button(
            420, 630, 100, 40,
            "加载棋谱", self.font_small
        )
        self.btn_settings_back = Button(
            start_x, 520, button_width, button_height,
            "返回菜单", self.font_text
        )
        # 设置选项按钮
        self.btn_forbidden = Button(
            start_x, 200, button_width, button_height,
            "禁手规则：关", self.font_text
        )
        self.btn_time_limit = Button(
            start_x, 270, button_width, button_height,
            "时限：不限时", self.font_text
        )
        self.btn_first_player = Button(
            start_x, 340, button_width, button_height,
            "先手：黑棋", self.font_text
        )

    def _draw_board(self):
        """绘制棋盘"""
        # 绘制背景
        self.screen.fill(COLOR_BG)

        # 绘制棋盘区域
        board_rect = (
            BOARD_MARGIN - CELL_SIZE // 2,
            BOARD_MARGIN - CELL_SIZE // 2,
            (self.game.board_size - 1) * CELL_SIZE + CELL_SIZE,
            (self.game.board_size - 1) * CELL_SIZE + CELL_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_BOARD, board_rect, border_radius=10)

        # 绘制棋盘线
        for i in range(self.game.board_size):
            # 横线
            start_x = BOARD_MARGIN
            end_x = BOARD_MARGIN + (self.game.board_size - 1) * CELL_SIZE
            y = BOARD_MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_LINE, (start_x, y), (end_x, y), 1)

            # 竖线
            start_y = BOARD_MARGIN
            end_y = BOARD_MARGIN + (self.game.board_size - 1) * CELL_SIZE
            x = BOARD_MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_LINE, (x, start_y), (x, end_y), 1)

        # 绘制天元和星位
        star_points = []
        if self.game.board_size == 15:
            star_points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]

        for row, col in star_points:
            x = BOARD_MARGIN + col * CELL_SIZE
            y = BOARD_MARGIN + row * CELL_SIZE
            pygame.draw.circle(self.screen, COLOR_LINE, (x, y), 5)

    def _draw_stones(self):
        """绘制棋子"""
        board = self.game.get_board()

        for row in range(self.game.board_size):
            for col in range(self.game.board_size):
                stone = board[row][col]
                if stone != Stone.NONE:
                    x = BOARD_MARGIN + col * CELL_SIZE
                    y = BOARD_MARGIN + row * CELL_SIZE

                    # 绘制棋子阴影
                    shadow_offset = 2
                    pygame.draw.circle(
                        self.screen, (50, 50, 50),
                        (x + shadow_offset, y + shadow_offset),
                        CELL_SIZE // 2 - 2
                    )

                    # 绘制棋子
                    color = COLOR_BLACK if stone == Stone.BLACK else COLOR_WHITE
                    pygame.draw.circle(self.screen, color, (x, y), CELL_SIZE // 2 - 2)

                    # 给棋子添加渐变效果
                    if stone == Stone.BLACK:
                        # 黑棋高光
                        highlight_pos = (x - CELL_SIZE // 6, y - CELL_SIZE // 6)
                        pygame.draw.circle(self.screen, (60, 60, 60), highlight_pos, 4)
                    else:
                        # 白棋高光
                        highlight_pos = (x - CELL_SIZE // 6, y - CELL_SIZE // 6)
                        pygame.draw.circle(self.screen, (255, 255, 255), highlight_pos, 4)

        # 高亮显示最后一步
        if self.last_move:
            row, col = self.last_move
            x = BOARD_MARGIN + col * CELL_SIZE
            y = BOARD_MARGIN + row * CELL_SIZE
            pygame.draw.circle(self.screen, COLOR_HIGHLIGHT, (x, y), 5)

    def _draw_ui(self):
        """绘制 UI 元素"""
        if self.state == STATE_MENU:
            self._draw_menu()
        elif self.state == STATE_PLAYING:
            self._draw_game_ui()
        elif self.state == STATE_GAME_OVER:
            self._draw_game_over()
        elif self.state == STATE_SETTINGS:
            self._draw_settings()

    def _draw_menu(self):
        """绘制菜单界面"""
        self.screen.fill(COLOR_BG)

        # 标题
        title = self.font_title.render("五子棋", True, COLOR_TEXT)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # 绘制装饰性棋盘
        self._draw_mini_board()

        # 按钮
        self.btn_pvp.draw(self.screen)
        self.btn_pve.draw(self.screen)
        self.btn_settings.draw(self.screen)

    def _draw_mini_board(self):
        """绘制装饰性小棋盘"""
        mini_board_size = 7
        mini_cell_size = 15
        mini_margin = 20
        start_x = WINDOW_WIDTH - mini_board_size * mini_cell_size - mini_margin
        start_y = mini_margin

        # 背景
        pygame.draw.rect(
            self.screen, COLOR_BOARD,
            (start_x, start_y, (mini_board_size - 1) * mini_cell_size,
             (mini_board_size - 1) * mini_cell_size),
            border_radius=5
        )

        # 线
        for i in range(mini_board_size):
            pygame.draw.line(
                self.screen, COLOR_LINE,
                (start_x, start_y + i * mini_cell_size),
                (start_x + (mini_board_size - 1) * mini_cell_size, start_y + i * mini_cell_size),
                1
            )
            pygame.draw.line(
                self.screen, COLOR_LINE,
                (start_x + i * mini_cell_size, start_y),
                (start_x + i * mini_cell_size, start_y + (mini_board_size - 1) * mini_cell_size),
                1
            )

    def _draw_game_ui(self):
        """绘制游戏界面"""
        self._draw_board()
        self._draw_stones()

        # 当前玩家提示
        player_text = "黑方回合" if self.game.current_player == Stone.BLACK else "白方回合"
        text_surface = self.font_text.render(player_text, True, COLOR_TEXT)
        self.screen.blit(text_surface, (20, 20))

        # 显示计时器
        if self.game.time_limit > 0:
            self._draw_timer()

        # 按钮
        self.btn_undo.draw(self.screen)
        self.btn_menu.draw(self.screen)
        self.btn_sound.draw(self.screen)
        self.btn_save.draw(self.screen)
        self.btn_load.draw(self.screen)

        # AI 思考中提示
        if self.ai_thinking:
            thinking_text = self.font_small.render("AI 思考中...", True, COLOR_TEXT)
            self.screen.blit(thinking_text, (20, 60))

    def _draw_timer(self):
        """绘制计时器"""
        # 更新计时器显示
        black_time = self.game.get_time_left(Stone.BLACK)
        white_time = self.game.get_time_left(Stone.WHITE)

        if black_time is not None:
            black_min = int(black_time) // 60
            black_sec = int(black_time) % 60
            black_color = COLOR_WARNING if black_time < 60 else COLOR_TEXT
            black_text = f"黑方：{black_min}:{black_sec:02d}"
            text_surface = self.font_small.render(black_text, True, black_color)
            self.screen.blit(text_surface, (20, 55))

        if white_time is not None:
            white_min = int(white_time) // 60
            white_sec = int(white_time) % 60
            white_color = COLOR_WARNING if white_time < 60 else COLOR_TEXT
            white_text = f"白方：{white_min}:{white_sec:02d}"
            text_surface = self.font_small.render(white_text, True, white_color)
            self.screen.blit(text_surface, (20, 80))

    def _draw_game_over(self):
        """绘制游戏结束界面"""
        self._draw_board()
        self._draw_stones()

        # 半透明遮罩
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((255, 255, 255))
        self.screen.blit(overlay, (0, 0))

        # 游戏结束文字
        if self.game.state == GameState.BLACK_WIN:
            result_text = "黑方获胜！"
        elif self.game.state == GameState.WHITE_WIN:
            result_text = "白方获胜！"
        else:
            result_text = "平局！"

        text_surface = self.font_title.render(result_text, True, COLOR_TEXT)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(text_surface, text_rect)

        # 按钮
        self.btn_restart.draw(self.screen)
        self.btn_back.draw(self.screen)

    def _draw_settings(self):
        """绘制设置界面"""
        self.screen.fill(COLOR_BG)

        # 标题
        title = self.font_title.render("游戏设置", True, COLOR_TEXT)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # 设置选项说明
        desc_text = self.font_small.render("请选择合适的游戏规则", True, COLOR_TEXT)
        desc_rect = desc_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(desc_text, desc_rect)

        # 设置选项按钮
        self.btn_forbidden.draw(self.screen)
        self.btn_time_limit.draw(self.screen)
        self.btn_first_player.draw(self.screen)
        self.btn_settings_back.draw(self.screen)

        # 当前设置状态说明
        y_offset = 260
        settings_info = [
            f"禁手规则：{'启用' if self.forbidden_rules else '禁用'}",
            f"时限：{self._get_time_limit_text()}",
            f"先手：{'黑棋' if self.first_player == Stone.BLACK else '白棋'}"
        ]
        for info in settings_info:
            info_surface = self.font_small.render(info, True, COLOR_TEXT)
            self.screen.blit(info_surface, (WINDOW_WIDTH // 2 - 100, y_offset))
            y_offset += 30

    def _get_time_limit_text(self) -> str:
        """获取时限文字描述"""
        if self.time_limit == 0:
            return "不限时"
        elif self.time_limit < 60:
            return f"{self.time_limit}秒"
        elif self.time_limit < 3600:
            return f"{self.time_limit // 60}分钟"
        else:
            return f"{self.time_limit // 3600}小时"

    def _get_board_position(self, mouse_pos: Tuple[int, int]) -> Tuple[int, int]:
        """将鼠标位置转换为棋盘坐标"""
        x, y = mouse_pos

        # 找到最近的交叉点
        col = round((x - BOARD_MARGIN) / CELL_SIZE)
        row = round((y - BOARD_MARGIN) / CELL_SIZE)

        return row, col

    def _start_game(self, mode: str):
        """开始新游戏"""
        self.game_mode = mode
        # 应用设置
        self.game.apply_settings(
            forbidden_rules=self.forbidden_rules,
            time_limit=self.time_limit,
            first_player=self.first_player
        )
        # 同步游戏模式到 game 实例
        self.game.game_mode = mode
        self.last_move = None
        self.state = STATE_PLAYING
        self.ai_thinking = False
        self.game.start_timer()

        # 设置 AI 棋子
        if mode == "pve":
            self.ai.set_stones(Stone.WHITE, Stone.BLACK)

    def _handle_menu_event(self, event: pygame.event.Event) -> bool:
        """处理菜单事件"""
        if self.btn_pvp.handle_event(event):
            self.sound_manager.play(SoundType.START)
            self._start_game("pvp")
            return True
        elif self.btn_pve.handle_event(event):
            self.sound_manager.play(SoundType.START)
            self._start_game("pve")
            return True
        elif self.btn_settings.handle_event(event):
            self.sound_manager.play(SoundType.CLICK)
            self.state = STATE_SETTINGS
            return True
        return False

    def _handle_game_event(self, event: pygame.event.Event) -> bool:
        """处理游戏事件"""
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            # 检查是否点击棋盘
            pos = event.pos
            if (BOARD_MARGIN - CELL_SIZE <= pos[0] <= BOARD_MARGIN + (self.game.board_size - 1) * CELL_SIZE + CELL_SIZE and
                BOARD_MARGIN - CELL_SIZE <= pos[1] <= BOARD_MARGIN + (self.game.board_size - 1) * CELL_SIZE + CELL_SIZE):

                if not self.ai_thinking:
                    row, col = self._get_board_position(pos)

                    if self.game.is_valid_move(row, col):
                        # 人类玩家落子
                        self.game.make_move(row, col)
                        self.last_move = (row, col)
                        # 播放落子音效
                        self.sound_manager.play(SoundType.MOVE)

                        # 检查游戏是否结束
                        if self.game.state != GameState.PLAYING:
                            self.state = STATE_GAME_OVER
                        elif self.game_mode == "pve" and self.game.current_player == Stone.WHITE:
                            # AI 回合
                            self.ai_thinking = True
                            self.ai_move_timer = pygame.time.get_ticks()

            # 检查按钮点击
            if self.btn_undo.handle_event(event):
                if len(self.game.move_history) >= (2 if self.game_mode == "pvp" else 1):
                    # 悔棋
                    if self.game_mode == "pve":
                        # 人机模式悔两步
                        self.game.undo_move()
                    self.game.undo_move()
                    self.last_move = self.game.move_history[-1] if self.game.move_history else None
                    # 播放悔棋音效
                    self.sound_manager.play(SoundType.UNDO)

            elif self.btn_menu.handle_event(event):
                self.sound_manager.play(SoundType.CLICK)
                self.state = STATE_MENU

            elif self.btn_sound.handle_event(event):
                # 切换音效开关
                enabled = self.sound_manager.toggle()
                self.btn_sound.text = "音效：开" if enabled else "音效：关"
                self.sound_manager.play(SoundType.CLICK)

            elif self.btn_save.handle_event(event):
                # 保存棋谱
                root = tk.Tk()
                root.withdraw()
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")],
                    title="保存棋谱"
                )
                if filepath:
                    if self.game.save_game_record(filepath):
                        print(f"棋谱已保存到：{filepath}")
                    else:
                        print("保存棋谱失败")
                root.destroy()
                self.sound_manager.play(SoundType.CLICK)

            elif self.btn_load.handle_event(event):
                # 加载棋谱
                root = tk.Tk()
                root.withdraw()
                filepath = filedialog.askopenfilename(
                    defaultextension=".json",
                    filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")],
                    title="加载棋谱"
                )
                if filepath:
                    if self.game.load_game_record(filepath):
                        self.last_move = self.game.move_history[-1] if self.game.move_history else None
                        print(f"棋谱已从 {filepath} 加载")
                    else:
                        print("加载棋谱失败")
                root.destroy()
                self.sound_manager.play(SoundType.CLICK)

            return True

        return False

    def _handle_game_over_event(self, event: pygame.event.Event) -> bool:
        """处理游戏结束事件"""
        if self.btn_restart.handle_event(event):
            self.sound_manager.play(SoundType.START)
            self._start_game(self.game_mode)
            return True
        elif self.btn_back.handle_event(event):
            self.sound_manager.play(SoundType.CLICK)
            self.state = STATE_MENU
            return True
        return False

    def _handle_settings_event(self, event: pygame.event.Event) -> bool:
        """处理设置界面事件"""
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            # 返回菜单按钮
            if self.btn_settings_back.handle_event(event):
                self.sound_manager.play(SoundType.CLICK)
                self.state = STATE_MENU
                return True

            # 禁手规则切换
            if self.btn_forbidden.handle_event(event):
                self.forbidden_rules = not self.forbidden_rules
                self.btn_forbidden.text = f"禁手规则：{'开' if self.forbidden_rules else '关'}"
                self.sound_manager.play(SoundType.CLICK)
                return True

            # 时限切换
            if self.btn_time_limit.handle_event(event):
                # 循环切换时限选项
                time_indices = TIME_LIMIT_OPTIONS.index(self.time_limit)
                self.time_limit = TIME_LIMIT_OPTIONS[(time_indices + 1) % len(TIME_LIMIT_OPTIONS)]
                self.btn_time_limit.text = f"时限：{self._get_time_limit_text()}"
                self.sound_manager.play(SoundType.CLICK)
                return True

            # 先手切换
            if self.btn_first_player.handle_event(event):
                self.first_player = Stone.WHITE if self.first_player == Stone.BLACK else Stone.BLACK
                self.btn_first_player.text = f"先手：{'黑棋' if self.first_player == Stone.BLACK else '白棋'}"
                self.sound_manager.play(SoundType.CLICK)
                return True

        return False

    def _update_ai(self):
        """更新 AI"""
        if self.ai_thinking:
            current_time = pygame.time.get_ticks()
            if current_time - self.ai_move_timer >= AI_THINK_DELAY:
                # AI 落子
                row, col = self.ai.get_move(self.game)
                if row >= 0:
                    self.game.make_move(row, col)
                    self.last_move = (row, col)
                    # 播放落子音效
                    self.sound_manager.play(SoundType.MOVE)

                    # 检查游戏是否结束
                    if self.game.state != GameState.PLAYING:
                        self.state = STATE_GAME_OVER
                        # 播放获胜音效
                        self.sound_manager.play(SoundType.WIN)

                self.ai_thinking = False

    def run(self):
        """运行游戏主循环"""
        running = True

        while running:
            self.clock.tick(60)

            # 事件处理
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    break

                if self.state == STATE_MENU:
                    self._handle_menu_event(event)
                elif self.state == STATE_PLAYING:
                    self._handle_game_event(event)
                elif self.state == STATE_GAME_OVER:
                    self._handle_game_over_event(event)
                elif self.state == STATE_SETTINGS:
                    self._handle_settings_event(event)

            # AI 更新
            if self.state == STATE_PLAYING:
                self._update_ai()

            # 绘制
            self._draw_ui()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    ui = GomokuUI()
    ui.run()


if __name__ == "__main__":
    main()

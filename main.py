# -*- coding: utf-8 -*-
"""
五子棋游戏主程序
"""

import sys
import pygame
from pygame.locals import *

from config import *
from game import GomokuGame, Stone, GameState
from ai import GomokuAI


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

        # 创建按钮
        self._create_buttons()

        # 最后落子位置
        self.last_move = None

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

        # 按钮
        self.btn_undo.draw(self.screen)
        self.btn_menu.draw(self.screen)

        # AI 思考中提示
        if self.ai_thinking:
            thinking_text = self.font_small.render("AI 思考中...", True, COLOR_TEXT)
            self.screen.blit(thinking_text, (20, 60))

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
        self.game.reset()
        self.last_move = None
        self.state = STATE_PLAYING
        self.ai_thinking = False

        # 设置 AI 棋子
        if mode == "pve":
            self.ai.set_stones(Stone.WHITE, Stone.BLACK)

    def _handle_menu_event(self, event: pygame.event.Event) -> bool:
        """处理菜单事件"""
        if self.btn_pvp.handle_event(event):
            self._start_game("pvp")
            return True
        elif self.btn_pve.handle_event(event):
            self._start_game("pve")
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

            elif self.btn_menu.handle_event(event):
                self.state = STATE_MENU

            return True

        return False

    def _handle_game_over_event(self, event: pygame.event.Event) -> bool:
        """处理游戏结束事件"""
        if self.btn_restart.handle_event(event):
            self._start_game(self.game_mode)
            return True
        elif self.btn_back.handle_event(event):
            self.state = STATE_MENU
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

                    # 检查游戏是否结束
                    if self.game.state != GameState.PLAYING:
                        self.state = STATE_GAME_OVER

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

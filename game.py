# -*- coding: utf-8 -*-
"""
五子棋游戏核心逻辑
"""

from enum import Enum
from typing import List, Tuple, Optional


class Stone(Enum):
    """棋子类型"""
    NONE = 0
    BLACK = 1
    WHITE = 2


class GameState(Enum):
    """游戏状态"""
    PLAYING = 0
    BLACK_WIN = 1
    WHITE_WIN = 2
    DRAW = 3


class GomokuGame:
    """五子棋游戏类"""

    def __init__(self, board_size: int = 15):
        """初始化游戏"""
        self.board_size = board_size
        self.reset()

    def reset(self):
        """重置游戏"""
        # 初始化空棋盘
        self.board = [[Stone.NONE for _ in range(self.board_size)]
                      for _ in range(self.board_size)]
        self.current_player = Stone.BLACK
        self.move_history: List[Tuple[int, int]] = []
        self.state = GameState.PLAYING
        self.winner = None

    def get_current_player(self) -> Stone:
        """获取当前玩家"""
        return self.current_player

    def is_valid_move(self, row: int, col: int) -> bool:
        """检查落子是否有效"""
        # 检查是否在棋盘范围内
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return False
        # 检查位置是否为空
        return self.board[row][col] == Stone.NONE

    def make_move(self, row: int, col: int) -> bool:
        """落子"""
        if not self.is_valid_move(row, col) or self.state != GameState.PLAYING:
            return False

        # 落子
        self.board[row][col] = self.current_player
        self.move_history.append((row, col))

        # 检查是否获胜
        if self.check_win(row, col):
            self.state = (GameState.BLACK_WIN if self.current_player == Stone.BLACK
                         else GameState.WHITE_WIN)
            self.winner = self.current_player
        elif self.check_draw():
            self.state = GameState.DRAW

        # 切换玩家
        self.current_player = (Stone.WHITE if self.current_player == Stone.BLACK
                               else Stone.BLACK)

        return True

    def undo_move(self) -> Optional[Tuple[int, int]]:
        """悔棋"""
        if not self.move_history:
            return None

        row, col = self.move_history.pop()
        self.board[row][col] = Stone.NONE

        # 切换回上一个玩家
        self.current_player = (Stone.WHITE if self.current_player == Stone.BLACK
                               else Stone.BLACK)

        # 重置游戏状态
        self.state = GameState.PLAYING
        self.winner = None

        return (row, col)

    def check_win(self, row: int, col: int) -> bool:
        """检查是否获胜"""
        stone = self.board[row][col]
        if stone == Stone.NONE:
            return False

        # 四个方向：水平、垂直、两个对角线
        directions = [
            (0, 1),   # 水平
            (1, 0),   # 垂直
            (1, 1),   # 主对角线
            (1, -1)   # 副对角线
        ]

        for dr, dc in directions:
            count = 1  # 当前落子

            # 正方向计数
            r, c = row + dr, col + dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size
                   and self.board[r][c] == stone):
                count += 1
                r += dr
                c += dc

            # 反方向计数
            r, c = row - dr, col - dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size
                   and self.board[r][c] == stone):
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                return True

        return False

    def check_draw(self) -> bool:
        """检查是否平局"""
        for row in self.board:
            for cell in row:
                if cell == Stone.NONE:
                    return False
        return True

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """获取所有有效落子位置"""
        moves = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == Stone.NONE:
                    moves.append((row, col))
        return moves

    def get_board(self) -> List[List[Stone]]:
        """获取棋盘状态"""
        return self.board

    def get_move_history(self) -> List[Tuple[int, int]]:
        """获取落子历史"""
        return self.move_history.copy()

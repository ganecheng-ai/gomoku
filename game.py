# -*- coding: utf-8 -*-
"""
五子棋游戏核心逻辑
"""

from enum import Enum
from typing import List, Tuple, Optional
import time
import json
import os


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
    BLACK_FORBIDDEN = 4  # 黑棋禁手判负
    WHITE_FORBIDDEN = 5  # 白棋禁手判负 (理论上白棋无禁手)


class GomokuGame:
    """五子棋游戏类"""

    def __init__(self, board_size: int = 15, forbidden_rules: bool = False, time_limit: int = 0):
        """
        初始化游戏

        Args:
            board_size: 棋盘大小
            forbidden_rules: 是否启用禁手规则
            time_limit: 每方时限 (秒), 0 表示不限时
        """
        self.board_size = board_size
        self.forbidden_rules = forbidden_rules
        self.time_limit = time_limit
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

        # 计时器初始化
        self.black_time_left = self.time_limit if self.time_limit > 0 else None
        self.white_time_left = self.time_limit if self.time_limit > 0 else None
        self.last_move_time = time.time()

        # 游戏设置
        self.first_player = Stone.BLACK  # 先手玩家
        self.game_mode = 'pvp'  # 游戏模式：pvp 或 pve

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

        # 更新计时器
        self._update_timer()

        # 检查禁手规则 (仅对黑棋)
        if self.forbidden_rules and self.current_player == Stone.BLACK:
            forbidden_type = self.check_forbidden(row, col)
            if forbidden_type:
                # 黑棋禁手判负
                self.state = GameState.WHITE_WIN
                self.winner = Stone.WHITE
                self.board[row][col] = self.current_player
                self.move_history.append((row, col))
                return False

        # 落子
        self.board[row][col] = self.current_player
        self.move_history.append((row, col))

        # 检查是否获胜 (长连也判胜)
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
        prev_player = self.current_player
        self.current_player = (Stone.WHITE if self.current_player == Stone.BLACK
                               else Stone.BLACK)

        # 重置游戏状态
        self.state = GameState.PLAYING
        self.winner = None

        # 回退计时器 (简单处理：不加回时间)
        self.last_move_time = time.time()

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

    def _update_timer(self):
        """更新计时器"""
        if self.time_limit <= 0:
            return

        current_time = time.time()
        elapsed = current_time - self.last_move_time
        self.last_move_time = current_time

        # 扣除当前玩家的时间
        if self.current_player == Stone.BLACK:
            if self.black_time_left is not None:
                self.black_time_left = max(0, self.black_time_left - elapsed)
                if self.black_time_left <= 0:
                    self.state = GameState.WHITE_WIN
                    self.winner = Stone.WHITE
        else:
            if self.white_time_left is not None:
                self.white_time_left = max(0, self.white_time_left - elapsed)
                if self.white_time_left <= 0:
                    self.state = GameState.BLACK_WIN
                    self.winner = Stone.BLACK

    def get_time_left(self, player: Stone) -> Optional[float]:
        """获取玩家剩余时间"""
        if self.time_limit <= 0:
            return None
        return self.black_time_left if player == Stone.BLACK else self.white_time_left

    def start_timer(self):
        """开始计时器"""
        self.last_move_time = time.time()

    def pause_timer(self):
        """暂停计时器"""
        current_time = time.time()
        elapsed = current_time - self.last_move_time
        if self.current_player == Stone.BLACK:
            if self.black_time_left is not None:
                self.black_time_left = max(0, self.black_time_left - elapsed)
        else:
            if self.white_time_left is not None:
                self.white_time_left = max(0, self.white_time_left - elapsed)

    def check_forbidden(self, row: int, col: int) -> Optional[str]:
        """
        检查禁手 (仅适用于黑棋)

        禁手类型:
        - 三三禁手：同时形成两个或更多活三
        - 四四禁手：同时形成两个或更多冲四或活四
        - 长连禁手：形成超过 5 子的连线

        Returns:
            禁手类型字符串，如果没有禁手则返回 None
        """
        if not self.forbidden_rules:
            return None

        # 检查长连禁手 (超过 5 子)
        if self._count_connected(row, col) > 5:
            return "long_line"  # 长连禁手

        # 检查三三禁手和四四禁手
        threes, fours = self._count_open_threes_and_fours(row, col)

        if fours >= 2:
            return "four_four"  # 四四禁手

        if threes >= 2:
            return "three_three"  # 三三禁手

        return None

    def _count_connected(self, row: int, col: int) -> int:
        """统计某位置上棋子在四个方向上的连子数"""
        stone = self.board[row][col]
        if stone == Stone.NONE:
            return 0

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        max_count = 0

        for dr, dc in directions:
            count = 1

            # 正方向
            r, c = row + dr, col + dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size
                   and self.board[r][c] == stone):
                count += 1
                r += dr
                c += dc

            # 反方向
            r, c = row - dr, col - dc
            while (0 <= r < self.board_size and 0 <= c < self.board_size
                   and self.board[r][c] == stone):
                count += 1
                r -= dr
                c -= dc

            max_count = max(max_count, count)

        return max_count

    def _count_open_threes_and_fours(self, row: int, col: int) -> Tuple[int, int]:
        """
        统计某位置上棋子形成的活三/冲四数量

        Returns:
            (活三数量，四的数量)
        """
        stone = self.board[row][col]
        if stone == Stone.NONE:
            return (0, 0)

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        three_count = 0
        four_count = 0

        for dr, dc in directions:
            # 统计该方向上的连子数和开放端
            count, open_ends = self._analyze_direction(row, col, dr, dc, stone)

            # 判断棋型
            if count >= 4:
                if open_ends >= 1:
                    four_count += 1  # 活四或冲四
            elif count == 3:
                if open_ends == 2:
                    three_count += 1  # 活三
                elif open_ends == 1:
                    # 眠三可能形成冲四
                    pass
            elif count == 2:
                if open_ends == 2:
                    # 活二可能形成活三
                    pass

        return (three_count, four_count)

    def _analyze_direction(self, row: int, col: int, dr: int, dc: int, stone: Stone) -> Tuple[int, int]:
        """
        分析某方向上的棋型

        Returns:
            (连子数，开放端数量)
        """
        count = 1
        open_ends = 0

        # 正方向
        r, c = row + dr, col + dc
        while (0 <= r < self.board_size and 0 <= c < self.board_size
               and self.board[r][c] == stone):
            count += 1
            r += dr
            c += dc

        # 检查正方向是否开放
        if (0 <= r < self.board_size and 0 <= c < self.board_size
                and self.board[r][c] == Stone.NONE):
            open_ends += 1

        # 反方向
        r, c = row - dr, col - dc
        while (0 <= r < self.board_size and 0 <= c < self.board_size
               and self.board[r][c] == stone):
            count += 1
            r -= dr
            c -= dc

        # 检查反方向是否开放
        if (0 <= r < self.board_size and 0 <= c < self.board_size
                and self.board[r][c] == Stone.NONE):
            open_ends += 1

        return (count, open_ends)

    def set_first_player(self, player: Stone):
        """设置先手玩家"""
        self.first_player = player

    def get_settings(self) -> dict:
        """获取游戏设置"""
        return {
            'board_size': self.board_size,
            'forbidden_rules': self.forbidden_rules,
            'time_limit': self.time_limit,
            'first_player': self.first_player
        }

    def apply_settings(self, board_size: int = None, forbidden_rules: bool = None,
                       time_limit: int = None, first_player: Stone = None):
        """应用游戏设置"""
        if board_size is not None:
            self.board_size = board_size
        if forbidden_rules is not None:
            self.forbidden_rules = forbidden_rules
        if time_limit is not None:
            self.time_limit = time_limit
        if first_player is not None:
            self.first_player = first_player
        self.reset()

    def save_game_record(self, filepath: str) -> bool:
        """
        保存棋谱记录到文件

        Args:
            filepath: 保存文件路径

        Returns:
            是否保存成功
        """
        try:
            record = {
                'board_size': self.board_size,
                'move_history': [(r, c) for r, c in self.move_history],
                'game_mode': 'pve' if self.game_mode == 'pve' else 'pvp',
                'forbidden_rules': self.forbidden_rules,
                'time_limit': self.time_limit,
                'first_player': self.first_player.value,
                'winner': self.winner.value if self.winner else None,
                'state': self.state.value
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存棋谱失败：{e}")
            return False

    def load_game_record(self, filepath: str) -> bool:
        """
        从文件加载棋谱记录

        Args:
            filepath: 加载文件路径

        Returns:
            是否加载成功
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                record = json.load(f)

            # 重置游戏
            self.board_size = record.get('board_size', 15)
            self.forbidden_rules = record.get('forbidden_rules', False)
            self.time_limit = record.get('time_limit', 0)
            self.first_player = Stone(record.get('first_player', 1))
            self.game_mode = record.get('game_mode', 'pvp')

            # 重置棋盘
            self.reset()

            # 恢复落子历史
            for r, c in record.get('move_history', []):
                if self.is_valid_move(r, c):
                    self.board[r][c] = self.current_player
                    self.move_history.append((r, c))
                    if self.check_win(r, c):
                        self.state = (GameState.BLACK_WIN if self.current_player == Stone.BLACK
                                     else GameState.WHITE_WIN)
                        self.winner = self.current_player
                        break
                    elif self.check_draw():
                        self.state = GameState.DRAW
                        break
                    self.current_player = (Stone.WHITE if self.current_player == Stone.BLACK
                                           else Stone.BLACK)

            return True
        except Exception as e:
            print(f"加载棋谱失败：{e}")
            return False

    def export_to_sgf(self, filepath: str) -> bool:
        """
        导出为 SGF (Smart Game Format) 格式棋谱

        Args:
            filepath: 保存文件路径

        Returns:
            是否保存成功
        """
        try:
            # SGF 格式基础结构
            sgf = ['(']
            sgf.append(';FF[4]CA[UTF-8]AP[GomokuPython]GM[1]')
            sgf.append(f'SZ[{self.board_size}]')

            # 添加游戏属性
            if self.forbidden_rules:
                sgf.append('RB[黑棋 (禁手)]')
            else:
                sgf.append('PB[黑棋]')
            sgf.append('PW[白棋]')

            # 添加棋步
            for i, (row, col) in enumerate(self.move_history):
                stone = 'B' if i % 2 == 0 else 'W'  # 黑棋先手
                # SGF 坐标使用字母表示 (a=0, b=1, ...)
                col_char = chr(ord('a') + col)
                row_char = chr(ord('a') + row)
                sgf.append(f';{stone}[{col_char}{row_char}]')

            sgf.append(')')

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(''.join(sgf))
            return True
        except Exception as e:
            print(f"导出 SGF 失败：{e}")
            return False

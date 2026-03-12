# -*- coding: utf-8 -*-
"""
五子棋 AI 对手
"""

import random
from typing import List, Tuple
from game import GomokuGame, Stone


class GomokuAI:
    """五子棋 AI"""

    def __init__(self, difficulty: int = 2):
        """
        初始化 AI

        Args:
            difficulty: 难度级别 (1=简单，2=中等，3=困难)
        """
        self.difficulty = difficulty
        self.ai_stone = Stone.WHITE
        self.player_stone = Stone.BLACK

    def set_stones(self, ai_stone: Stone, player_stone: Stone):
        """设置 AI 和玩家的棋子类型"""
        self.ai_stone = ai_stone
        self.player_stone = player_stone

    def get_move(self, game: GomokuGame) -> Tuple[int, int]:
        """
        获取 AI 的落子位置

        Args:
            game: 游戏实例

        Returns:
            (row, col): 落子位置
        """
        board = game.get_board()
        board_size = game.board_size

        # 获取所有空位
        empty_positions = []
        for row in range(board_size):
            for col in range(board_size):
                if board[row][col] == Stone.NONE:
                    empty_positions.append((row, col))

        if not empty_positions:
            return (-1, -1)

        # 简单难度：随机选择一个有威胁的位置
        if self.difficulty == 1:
            # 优先选择靠近中心的位置
            center = board_size // 2
            empty_positions.sort(key=lambda p: abs(p[0] - center) + abs(p[1] - center))
            # 从前 20% 的位置中随机选择
            count = max(1, len(empty_positions) // 5)
            return random.choice(empty_positions[:count])

        # 中等和困难难度：使用评分系统
        scores = self._evaluate_positions(game, empty_positions)

        # 困难难度会选择最高分的位置
        # 中等难度会有一定概率选择次优位置
        if self.difficulty == 3:
            best_idx = scores.index(max(scores))
            return empty_positions[best_idx]
        else:
            # 中等难度：80% 选择最优，20% 随机
            if random.random() < 0.8:
                best_idx = scores.index(max(scores))
                return empty_positions[best_idx]
            else:
                return random.choice(empty_positions)

    def _evaluate_positions(self, game: GomokuGame, positions: List[Tuple[int, int]]) -> List[int]:
        """评估所有位置的分数"""
        scores = []
        for row, col in positions:
            score = self._evaluate_position(game, row, col)
            scores.append(score)
        return scores

    def _evaluate_position(self, game: GomokuGame, row: int, col: int) -> int:
        """评估单个位置的分数"""
        score = 0

        # 尝试落子并评分
        for stone, is_ai in [(self.ai_stone, True), (self.player_stone, False)]:
            # 临时落子
            game.board[row][col] = stone

            # 检查是否获胜
            if game.check_win(row, col):
                if is_ai:
                    score += 100000  # AI 获胜，最高分
                else:
                    score += 50000  # 阻止玩家获胜，高分

            # 评估棋型
            score += self._evaluate_pattern(game, row, col, stone)

            # 撤销落子
            game.board[row][col] = Stone.NONE

        # 位置偏好：中心位置加分
        board_size = game.board_size
        center = board_size // 2
        distance = abs(row - center) + abs(col - center)
        score += max(0, 10 - distance)

        return score

    def _evaluate_pattern(self, game: GomokuGame, row: int, col: int, stone: Stone) -> int:
        """评估棋型的分数"""
        score = 0
        board = game.board
        board_size = game.board_size

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            # 统计该方向上的连子数
            count = 1
            open_ends = 0

            # 正方向
            r, c = row + dr, col + dc
            while 0 <= r < board_size and 0 <= c < board_size and board[r][c] == stone:
                count += 1
                r += dr
                c += dc

            # 检查正方向是否开放
            if 0 <= r < board_size and 0 <= c < board_size and board[r][c] == Stone.NONE:
                open_ends += 1

            # 反方向
            r, c = row - dr, col - dc
            while 0 <= r < board_size and 0 <= c < board_size and board[r][c] == stone:
                count += 1
                r -= dr
                c -= dc

            # 检查反方向是否开放
            if 0 <= r < board_size and 0 <= c < board_size and board[r][c] == Stone.NONE:
                open_ends += 1

            # 根据连子数和开放端数评分
            if count >= 5:
                score += 10000
            elif count == 4:
                if open_ends == 2:
                    score += 5000  # 活四
                elif open_ends == 1:
                    score += 1000  # 冲四
            elif count == 3:
                if open_ends == 2:
                    score += 1000  # 活三
                elif open_ends == 1:
                    score += 100  # 眠三
            elif count == 2:
                if open_ends == 2:
                    score += 100  # 活二
                elif open_ends == 1:
                    score += 10  # 眠二

        return score

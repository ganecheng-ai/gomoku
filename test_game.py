# -*- coding: utf-8 -*-
"""
五子棋游戏测试
"""

import unittest
from game import GomokuGame, Stone, GameState


class TestGomokuGame(unittest.TestCase):
    """测试五子棋游戏逻辑"""

    def setUp(self):
        """测试前准备"""
        self.game = GomokuGame()

    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.game.current_player, Stone.BLACK)
        self.assertEqual(self.game.state, GameState.PLAYING)
        self.assertIsNone(self.game.winner)

    def test_valid_move(self):
        """测试有效落子"""
        self.assertTrue(self.game.is_valid_move(7, 7))
        self.assertTrue(self.game.make_move(7, 7))
        self.assertEqual(self.game.board[7][7], Stone.BLACK)

    def test_invalid_move(self):
        """测试无效落子"""
        # 超出范围
        self.assertFalse(self.game.is_valid_move(-1, 0))
        self.assertFalse(self.game.is_valid_move(15, 15))

        # 重复落子
        self.game.make_move(7, 7)
        self.assertFalse(self.game.is_valid_move(7, 7))
        self.assertFalse(self.game.make_move(7, 7))

    def test_player_switch(self):
        """测试玩家切换"""
        self.game.make_move(7, 7)
        self.assertEqual(self.game.current_player, Stone.WHITE)

        self.game.make_move(7, 8)
        self.assertEqual(self.game.current_player, Stone.BLACK)

    def test_undo_move(self):
        """测试悔棋"""
        self.game.make_move(7, 7)
        self.game.make_move(7, 8)

        result = self.game.undo_move()
        self.assertEqual(result, (7, 8))
        self.assertEqual(self.game.board[7][8], Stone.NONE)
        self.assertEqual(self.game.current_player, Stone.WHITE)

    def test_horizontal_win(self):
        """测试水平五连"""
        # 黑棋水平五连
        for i in range(5):
            self.game.make_move(7, i)
            if i < 4:
                self.game.make_move(0, i)  # 白棋随便下

        self.assertEqual(self.game.state, GameState.BLACK_WIN)
        self.assertEqual(self.game.winner, Stone.BLACK)

    def test_vertical_win(self):
        """测试垂直五连"""
        # 黑棋垂直五连
        for i in range(5):
            self.game.make_move(i, 7)
            if i < 4:
                self.game.make_move(0, i)  # 白棋随便下

        self.assertEqual(self.game.state, GameState.BLACK_WIN)

    def test_diagonal_win(self):
        """测试对角线五连"""
        # 黑棋主对角线五连
        for i in range(5):
            self.game.make_move(i, i)
            if i < 4:
                self.game.make_move(0, i + 5)

        self.assertEqual(self.game.state, GameState.BLACK_WIN)

        # 重置测试副对角线
        self.game.reset()

        # 黑棋副对角线五连
        for i in range(5):
            self.game.make_move(i, 4 - i)
            if i < 4:
                self.game.make_move(0, i + 5)

        self.assertEqual(self.game.state, GameState.BLACK_WIN)

    def test_no_win_with_four(self):
        """测试四子不获胜"""
        for i in range(4):
            self.game.make_move(7, i)
            if i < 3:
                self.game.make_move(0, i)

        self.assertEqual(self.game.state, GameState.PLAYING)

    def test_move_history(self):
        """测试落子历史"""
        self.game.make_move(7, 7)
        self.game.make_move(7, 8)

        history = self.game.get_move_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], (7, 7))
        self.assertEqual(history[1], (7, 8))


class TestAIBasic(unittest.TestCase):
    """测试 AI 基本功能"""

    def test_ai_get_move(self):
        """测试 AI 获取落子"""
        from ai import GomokuAI

        game = GomokuGame()
        ai = GomokuAI(difficulty=2)

        # AI 应该能返回一个有效位置
        row, col = ai.get_move(game)
        self.assertTrue(game.is_valid_move(row, col) or (row == -1 and col == -1))


if __name__ == "__main__":
    unittest.main()

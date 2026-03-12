# -*- coding: utf-8 -*-
"""
五子棋游戏配置
"""

# 窗口设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 650
TITLE = "五子棋"

# 棋盘设置
BOARD_SIZE = 15  # 15x15 的棋盘
CELL_SIZE = 40   # 每个格子的大小
BOARD_MARGIN = 50  # 棋盘边缘留白

# 颜色定义 (RGB)
COLOR_BG = (220, 179, 92)       # 木质背景色
COLOR_BOARD = (218, 170, 80)    # 棋盘颜色
COLOR_LINE = (30, 30, 30)       # 棋盘线颜色
COLOR_BLACK = (10, 10, 10)      # 黑棋颜色
COLOR_WHITE = (250, 250, 250)   # 白棋颜色
COLOR_TEXT = (30, 30, 30)       # 文字颜色
COLOR_HIGHLIGHT = (255, 100, 100)  # 高亮颜色
COLOR_BUTTON_BG = (70, 130, 180)   # 按钮背景色
COLOR_BUTTON_HOVER = (100, 160, 210)  # 按钮悬停色

# 字体设置
FONT_SIZE_TITLE = 36
FONT_SIZE_TEXT = 24
FONT_SIZE_SMALL = 18

# 游戏状态
STATE_MENU = 0      # 菜单界面
STATE_PLAYING = 1   # 游戏中
STATE_GAME_OVER = 2 # 游戏结束

# AI 设置
AI_THINK_DELAY = 500  # AI 思考延迟 (毫秒)

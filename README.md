# 五子棋 (Gomoku)

经典的五子棋游戏，使用 Python 和 Pygame 开发。支持双人对战和人机对战模式。

## 功能特性

- **双人对战模式**: 本地两名玩家轮流落子
- **人机对战模式**: 与 AI 对弈，支持三种难度级别
- **简体中文界面**: 完整的中文化支持
- **精美的游戏画面**: 木质纹理棋盘、逼真的棋子效果
- **智能 AI 对手**: 基于评分系统的 AI，具备进攻和防守能力
- **游戏音效**: 落子、获胜、悔棋等音效，支持开关控制
- **悔棋功能**: 支持撤销上一步落子
- **胜负判定**: 自动检测五子连线并判定胜负

## 游戏截图

![游戏界面](screenshots/game.png)

## 快速开始

### 系统要求

- Python 3.10 或更高版本
- 支持 Windows、macOS、Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行游戏

```bash
python main.py
```

### 游戏操作

1. 启动游戏后选择游戏模式（双人对战或人机对战）
2. 黑棋先行，轮流落子
3. 点击棋盘上的交叉点放置棋子
4. 先连成五子一线者获胜
5. 可使用「悔棋」按钮撤销上一步
6. 可使用「菜单」按钮返回主界面
7. 可使用「音效：开/关」按钮切换音效

## 项目结构

```
gomoku/
├── main.py          # 游戏主入口
├── game.py          # 游戏核心逻辑
├── ai.py            # AI 对手
├── config.py        # 游戏配置
├── sound.py         # 音效管理器
├── test_game.py     # 单元测试
├── requirements.txt # 依赖列表
├── README.md        # 项目说明
├── plan.md          # 开发计划
└── prompt.md        # 指令文件
```

## 开发计划

- v0.1.0: 基础双人对战 - 已完成
- v0.2.0: 添加人机对战 - 已完成
- v0.3.0: 完善 UI 和音效 - 已完成
- v1.0.0: 首次正式发布 - 计划中

## 测试

运行单元测试：

```bash
python -m unittest discover -v
```

当前测试状态：11 个测试全部通过

## 编译二进制文件

使用 PyInstaller 打包为可执行文件：

```bash
pyinstaller --onefile --windowed --name "五子棋" main.py
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

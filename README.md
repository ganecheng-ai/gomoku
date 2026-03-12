# 五子棋 (Gomoku)

经典的五子棋游戏，使用 Python 和 Pygame 开发。支持双人对战和人机对战模式。

![GitHub License](https://img.shields.io/github/license/ganecheng-ai/gomoku)
![GitHub Tag](https://img.shields.io/github/v/tag/ganecheng-ai/gomoku)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)

## 功能特性

- **双人对战模式**: 本地两名玩家轮流落子，经典五子棋规则
- **人机对战模式**: 与 AI 对弈，支持三种难度级别（简单/中等/困难）
- **简体中文界面**: 完整的中文化支持，字体自适应多平台
- **精美的游戏画面**:
  - 木质纹理棋盘背景
  - 逼真的棋子立体效果和高光
  - 天元和星位标记
  - 最后落子位置高亮提示
- **智能 AI 对手**:
  - 基于评分系统的 AI 算法
  - 具备进攻和防守能力
  - 可识别活四、冲四、活三、眠三等棋型
- **游戏音效**:
  - 落子音效
  - 获胜音效
  - 悔棋音效
  - 按钮点击音效
  - 支持开关控制
- **便捷功能**:
  - 悔棋功能（人机模式支持悔两步）
  - 重新开始
  - 返回主菜单
  - 游戏设置界面
- **胜负判定**: 自动检测五子连线并判定胜负
- **禁手规则** (v1.1.0):
  - 支持三三禁手、四四禁手、长连禁手
  - 符合专业五子棋规则
- **计时器功能** (v1.1.0):
  - 支持不限时、1 分钟、2 分钟、5 分钟、10 分钟
  - 超时自动判负
  - 剩余时间显示
- **棋谱记录** (v1.1.0):
  - JSON 格式保存/加载对局
  - SGF 格式导出支持

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

主要依赖：
- `pygame` >= 2.0.0 - 游戏引擎
- `pyinstaller` >= 6.0.0 - 打包工具

### 运行游戏

```bash
python main.py
```

### 游戏操作

1. 启动游戏后选择游戏模式（双人对战或人机对战）
2. 黑棋先行，轮流落子
3. 点击棋盘上的交叉点放置棋子
4. 先连成五子一线者获胜
5. 可使用「悔棋」按钮撤销上一步落子
6. 可使用「菜单」按钮返回主界面
7. 可使用「音效：开/关」按钮切换音效

### 游戏规则

- 棋盘大小：15×15
- 黑棋先手，白棋后手
- 双方轮流落子
- 先在水平、垂直或对角线方向连成五子者获胜

## 项目结构

```
gomoku/
├── main.py          # 游戏主入口，UI 控制逻辑
├── game.py          # 游戏核心逻辑（棋盘、落子、胜负判定）
├── ai.py            # AI 对手（评分系统、棋型识别）
├── config.py        # 游戏配置（窗口大小、颜色、字体）
├── sound.py         # 音效管理器（程序生成音效）
├── test_game.py     # 单元测试
├── requirements.txt # 依赖列表
├── README.md        # 项目说明
├── plan.md          # 开发计划
├── prompt.md        # 指令文件
└── .github/
    └── workflows/
        └── release.yml  # GitHub Actions 自动发布流程
```

## 开发计划

- v0.1.0: 基础双人对战 - 已完成
- v0.2.0: 添加人机对战 - 已完成
- v0.3.0: 完善 UI 和音效 - 已完成
- v0.3.1: 修复 GitHub Actions 发布配置 - 已完成
- v1.0.0: 首次正式发布 - 已完成
- v1.0.1: 修复 macOS 构建问题 - 已完成
- v1.1.0: 功能增强版本 - 已完成
  - 添加禁手规则、计时器、棋谱记录和设置界面

## 构建发布

### 本地打包

使用 PyInstaller 打包为可执行文件：

```bash
# Windows
pyinstaller --onefile --windowed --name "五子棋" main.py

# macOS
pyinstaller --onefile --windowed --name "Gomoku" main.py

# Linux
pyinstaller --onefile --windowed --name "Gomoku" main.py
```

### 自动发布

创建 Git Tag 时自动通过 GitHub Actions 构建并发布：

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions 将自动：
1. 在 Windows、macOS、Linux 三个平台构建
2. 运行单元测试验证
3. 生成可执行文件
4. 创建 GitHub Release 并上传构建产物
5. 生成 SHA256 校验和文件

#### 构建产物命名规范

| 平台 | 文件名 | 格式 |
|------|--------|------|
| Windows | `gomoku-windows-x86_64.exe` | .exe |
| macOS | `gomoku-macos.dmg` | .dmg |
| Linux | `gomoku-linux-x86_64.tar.gz` | .tar.gz |
| 校验和 | `checksums.txt` | .txt |

## 测试

运行单元测试：

```bash
python -m unittest discover -v
```

当前测试覆盖：
- 游戏初始状态
- 有效/无效落子
- 玩家切换
- 悔棋功能
- 胜负判定（水平、垂直、对角线）
- 落子历史
- AI 落子逻辑

## 技术栈

- **语言**: Python 3.10+
- **GUI 框架**: Pygame 2.x
- **AI 算法**: 基于评分系统的启发式评估
- **打包工具**: PyInstaller 6.x
- **CI/CD**: GitHub Actions

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**享受五子棋游戏的乐趣！**

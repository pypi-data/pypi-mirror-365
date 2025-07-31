# ClaudeWarp - Claude API 代理管理工具

一个用于管理和切换Claude API代理服务器的命令行工具，专为需要频繁切换代理的开发者设计。

## ✨ 特性

- 🚀 **多代理管理** - 添加、删除、编辑多个Claude API代理服务器
- 🔄 **一键切换** - 快速在不同代理间切换，自动更新Claude Code配置
- 📦 **环境变量导出** - 支持Bash/Zsh/Fish/PowerShell等多种Shell格式
- 🔧 **Claude Code集成** - 自动同步代理配置到Claude Code，无需手动修改
- 🏷️ **标签管理** - 为代理添加标签，方便分类和搜索
- 💾 **配置备份** - 自动备份配置文件，支持恢复
- 🔐 **多种认证** - 支持API Key和Auth Token两种认证方式

## 🚀 安装

### 方式一：pip安装 (推荐)

```bash
# 直接安装
pip install claudewarp

# 立即可用
cw --help
```

### 方式二：本地开发安装

克隆项目后使用conda创建虚拟环境：

```bash
# 创建虚拟环境
conda create --name cwenv python=3.11 -y
conda activate cwenv

# 开发模式安装
pip install -e .

# 或者安装依赖后使用
pip install -r requirements.txt
python main.py --help
```

### 基本使用

```bash
# 查看帮助
cw --help

# 添加代理服务器
cw add my-proxy https://api.example.com your-api-key --desc "我的代理"

# 查看代理列表
cw list

# 切换代理 (会自动更新Claude Code配置)
cw use my-proxy

# 查看当前代理
cw current

# 导出环境变量
cw export --format bash
```

## 📖 详细用法

### 代理管理

#### 添加代理
```bash
# 交互式添加
cw add

# 命令行添加 (API Key)
cw add proxy1 https://api.proxy1.com sk-xxx --desc "代理1" --tags "fast,stable"

# 使用Auth Token
cw add proxy2 https://api.proxy2.com --auth-token your-token --desc "代理2"

# 配置模型
cw add proxy3 https://api.proxy3.com sk-xxx --bigmodel "claude-3-opus" --smallmodel "claude-3-haiku"
```

#### 查看代理
```bash
# 查看所有代理
cw list

# 查看特定代理详情
cw info proxy1

# 查看当前代理
cw current
```

#### 编辑代理
```bash
# 编辑代理信息
cw edit proxy1 --desc "更新的描述" --tags "updated,fast"

# 更新API密钥
cw edit proxy1 --key new-api-key

# 切换认证方式
cw edit proxy1 --auth-token new-token  # 会清空API Key
```

#### 删除代理
```bash
# 删除代理
cw remove proxy1
```

### 代理切换

#### 切换代理
```bash
# 切换到指定代理 (会自动更新Claude Code配置)
cw use proxy1

# 查看当前使用的代理
cw current
```

**⚠️ 重要提醒：** 切换代理会直接修改 `~/.claude/settings.json` 文件，建议先备份：
```bash
cp ~/.claude/settings.json ~/.claude/settings.json.backup
```

### 搜索和过滤

#### 搜索代理
```bash
# 按名称搜索
cw search proxy

# 按标签搜索
cw search fast

# 按描述搜索
cw search "测试"
```

### 环境变量导出

#### 导出不同格式
```bash
# Bash/Zsh格式
cw export --format bash

# PowerShell格式
cw export --format powershell

# Fish Shell格式
cw export --format fish

# 导出到文件
cw export --format bash > proxy-env.sh
source proxy-env.sh
```

#### 自定义导出
```bash
# 导出指定代理
cw export proxy1 --format bash

# 包含注释
cw export --format bash --comments

# 导出所有代理
cw export --format bash --all
```

## 🏗️ 项目结构

```
claudewarp/
├── claudewarp/                 # 主应用包
│   ├── cli/                   # 命令行界面层
│   │   ├── commands.py        # CLI命令处理器
│   │   ├── formatters.py      # 输出格式化器
│   │   └── main.py           # CLI应用入口
│   └── core/                  # 核心业务逻辑层
│       ├── config.py         # 配置文件管理器
│       ├── exceptions.py     # 自定义异常类
│       ├── manager.py        # 代理服务器管理器
│       ├── models.py         # Pydantic数据模型
│       └── utils.py          # 工具函数库
├── tests/                     # 测试套件
├── docs/                      # 项目文档
├── main.py                    # 应用程序主入口
├── requirements.txt           # 运行时依赖
├── requirements-dev.txt       # 开发依赖
└── README.md                 # 项目说明
```

## 🔧 技术架构

### 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface Layer                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │               CLI Commands (Typer)                      ││
│  │                                                         ││
│  │ • 代理管理命令 (add, remove, list, use)                ││
│  │ • Rich输出格式化和美化                                  ││
│  │ • 交互式命令行界面                                      ││
│  │ • 彩色日志和错误处理                                    ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                     │
│  ┌─────────────────────────────────────────────────────────┐│
│  │               ProxyManager                              ││
│  │                                                         ││
│  │ • 代理服务器生命周期管理 (CRUD)                         ││
│  │ • 智能代理切换与状态管理                                ││
│  │ • Claude Code 自动配置集成                              ││
│  │ • 多格式环境变量导出                                    ││
│  │ • 搜索、过滤、标签管理                                  ││
│  │ • 连接验证与健康检查                                    ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                              │
│┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
││ ConfigManager   │  │  Data Models    │  │   Utilities     ││
││                 │  │                 │  │                 ││
││ • JSON配置持久化│  │ • ProxyServer   │  │ • 文件操作      ││
││ • 自动备份机制  │  │ • ProxyConfig   │  │ • 原子写入      ││
││ • 版本管理      │  │ • ExportFormat  │  │ • 路径管理      ││
││ • 配置验证      │  │ • Pydantic验证  │  │ • 异常处理      ││
│└─────────────────┘  └─────────────────┘  └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 核心特性

#### 1. 纯CLI体验
- **Typer框架**: 现代化CLI命令处理
- **Rich输出**: 美化的终端输出和表格显示
- **交互式界面**: 支持用户友好的命令交互

#### 2. 智能配置管理
- **自动备份**: 配置变更前自动创建备份
- **原子操作**: 确保配置文件操作的原子性和一致性
- **版本控制**: 配置文件版本管理和兼容性检查

#### 3. Claude Code 集成
- **无缝集成**: 自动生成和更新 Claude Code 配置文件
- **智能合并**: 保留用户现有配置，只更新代理相关设置
- **环境变量**: 支持多种 Shell 格式的环境变量导出

#### 4. 数据验证与安全
- **Pydantic模型**: 全面的数据验证和类型安全
- **输入验证**: URL格式、API密钥格式、名称合规性检查
- **错误处理**: 结构化异常体系和详细错误信息

## 🛠️ 开发

### 技术栈

- **Python 3.8+** - 核心开发语言
- **Typer** - CLI命令处理框架
- **Rich** - 终端输出美化
- **Pydantic** - 数据验证和序列化
- **TOML** - 配置文件格式
- **Colorlog** - 彩色日志输出

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_cli.py

# 生成覆盖率报告
pytest --cov=claudewarp tests/
```

### 代码格式化
```bash
# 格式化代码
ruff format .

# 检查代码风格
ruff check .

# 类型检查
pyright
```

## 📂 配置文件

### ClaudeWarp 配置
配置文件位置: `~/.config/claudewarp/config.toml` (Linux/macOS) 或 `%APPDATA%\claudewarp\config.toml` (Windows)

### Claude Code 配置
ClaudeWarp 会自动修改 `~/.claude/settings.json` 文件，格式参考：

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "your-api-key",
    "ANTHROPIC_BASE_URL": "https://your-proxy.com",
    "ANTHROPIC_MODEL": "claude-3-opus",
    "ANTHROPIC_SMALL_FAST_MODEL": "claude-3-haiku",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": 1
  },
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

## ⚠️ 重要提醒

1. **备份配置**: 首次使用前建议备份 Claude Code 配置：
   ```bash
   cp ~/.claude/settings.json ~/.claude/settings.json.backup
   ```

2. **权限要求**: 确保对 `~/.claude/` 目录有读写权限

3. **配置冲突**: 如果手动修改了 Claude Code 配置，切换代理时可能会覆盖自定义设置

## 🐛 故障排除

### 常见问题

**Q: 切换代理后 Claude Code 无法连接**
A: 检查代理 URL 和 API 密钥是否正确，确认代理服务器可访问

**Q: 配置文件损坏怎么办？**
A: ClaudeWarp 会自动创建备份，可以从 `~/.config/claudewarp/backups/` 恢复

**Q: 权限错误**
A: 确保对配置目录有读写权限：`chmod 755 ~/.config/claudewarp`

**Q: 依赖安装失败**
A: 使用 pip 安装： `pip install -r requirements.txt`

## 📜 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系

如有问题或建议，请提交 GitHub Issue。

---

**ClaudeWarp** - 让 Claude API 代理管理变得简单高效！
# AI Agent 开发环境指南

## 功能特性
- **Zephyr编译管理**：完整开发环境初始化、仓库克隆、PR切换、多板型编译
- **Twister测试框架**：支持参数化测试执行与结果分析
- **Cody智能查询**：提供单次查询和交互式会话两种模式
- **环境自检机制**：自动验证CMake/ninja/gcc等编译工具链完整性
- **异常处理**：统一错误捕获与友好提示机制

## 使用示例

## 环境要求
- Node.js 18+
- Python 3.10+

## 依赖管理

### Node.js 依赖
```bash
npm install
```

使用 [uv](https://github.com/astral-sh/uv) 工具进行依赖管理：

```bash
# 安装uv
pipx install uv

# 初始化虚拟环境
uv venv .venv

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 安装依赖
uv pip install -r requirements.txt

# 生成锁定文件（可选）
uv pip compile requirements.txt -o requirements.lock
```

## 开发运行

```bash
python cli.py "你的查询内容"
```

## 使用示例

### Zephyr编译管理
```bash
# 初始化开发环境（中文环境）
LANG=zh_CN python cli.py zephyr init --path ./test_project

# 克隆Zephyr仓库
python cli.py zephyr clone https://github.com/zephyrproject/your-repo.git

# 切换指定PR
python cli.py zephyr pr 1234

# 编译项目(native_posix板型)
python cli.py zephyr compile -b native_posix

# 执行Twister测试（附加参数示例）
python cli.py zephyr test -a "-p native_posix -T tests/kernel"

# Cody单次查询
example-cli query "如何清理编译缓存"

# 进入交互模式
example-cli interactive
```
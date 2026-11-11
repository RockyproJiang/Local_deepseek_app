# AI Chat Assistant

AI Chat Assistant——基于 Ollama + DeepSeek 模型的本地 Tkinter 聊天助手，类 macOS 现代界面，实时流式输出、多对话管理与持久化记忆，完全离线保护隐私。

## 功能特性

- **流式逐字输出**：通过本地 Ollama HTTP 接口逐块读取模型响应，实时显示生成内容，并可随时停止生成。
- **多对话管理**：新建、切换多个独立会话，切换与关闭窗口时自动保存当前会话历史（进程内保存，重启后无法恢复）。
- **持久化长期记忆**：每个会话的问答以 JSON 文件落盘（`chat_memories/`），后续对话自动注入最近记忆作为上下文。
- **macOS 风格界面**：浅色系配色、圆角气泡、侧边栏会话列表，基于 Tkinter 手工绘制，无额外 GUI 依赖。
- **思考标签清理**：对 DeepSeek-R1 的 `<think>` 推理内容做过滤，只呈现最终回答。

## 技术栈 / 依赖

- Python 3.x、Tkinter（标准库，随 Python 提供）
- `requests>=2.28.0`（见 `requirements.txt`）
- 本机 [Ollama](https://ollama.com/) 服务及 DeepSeek 模型（默认 `deepseek-r1:8b`，定义于 `config.py` 的 `MODEL_NAME`）

> `requirements.txt` 仅保留 Python 依赖；原先误混入的 `pip install`、`ollama serve` 等 shell 命令已清理，环境准备请按下方「快速开始」手动执行。

## 目录结构

```text
Local_deepseek_app/
├── main.py               # 程序入口，创建 Tk 窗口并启动 ChatApplication
├── chat_app.py           # 主应用类：会话管理、流式请求、界面组装
├── config.py             # Ollama 地址、模型名、界面样式、记忆路径等配置
├── memory_manager.py     # 长期记忆的读写、追加与清空
├── ui_components.py      # 聊天气泡显示区与输入区组件
├── utils.py              # 时间格式化、JSON 存取、think 标签清理等工具
├── requirements.txt      # Python 依赖
├── .gitignore            # 忽略 __pycache__、chat_memories/、日志等
└── README.md
```

## 快速开始

1. 安装并启动 Ollama，拉取模型：

```bash
git clone https://github.com/RockyproJiang/Local_deepseek_app.git
cd Local_deepseek_app

ollama serve
ollama pull deepseek-r1:8b
```

> 若 `config.py` 中 `MODEL_NAME` 改为其他模型，请拉取对应模型名。`ollama serve` 建议保持在单独的终端窗口中运行。

2. 安装 Python 依赖并启动应用：

```bash
pip install -r requirements.txt
python main.py
```

## 配置与安全说明

- **无 API Key、无密钥、无需联网、数据全部本地存储**：本项目不调用任何云端大模型，也不读取任何凭据；对话与记忆仅写入本机 `chat_memories/`（已由 `.gitignore` 忽略）。
- 模型能力通过本地 Ollama HTTP 接口（`http://localhost:11434`，见 `config.py` 的 `OLLAMA_URL`）获得，须自行确保本机 Ollama 已启动且模型已拉取；未启动时会连接失败。
- Ollama 地址、模型、温度、界面尺寸与记忆上限（`MAX_HISTORY`、`MAX_MEMORY_ITEMS`）均可在 `config.py` 中调整。
- 所有数据只在本机处理，适合离线与隐私敏感场景；请勿把 `chat_memories/` 中的对话记录随仓库公开提交。

## 许可证

本项目采用 MIT License，详见 [LICENSE](LICENSE)。

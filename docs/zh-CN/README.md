# llm-wiki-installer 中文指南

`llm-wiki-installer` 用一条命令生成一个适合 LLM 和 Obsidian 使用的
Markdown 知识库仓库。生成后的 vault 使用 Git 审核变更，用 `raw/` 保存经
用户确认的原始证据，用 `wiki/` 保存长期维护的结构化知识。

本仓库不是知识库本身，而是安装器。安装器会把固定目录、AGENTS 策略、辅助
脚本和可选上游 Skills 写入另一个目标仓库。

## Quick Start

进入你想作为 vault 根目录的空目录，然后运行一行安装命令：

```bash
curl -fsSL https://raw.githubusercontent.com/exhank/llm-wiki-installer/main/install.sh | /bin/bash
```

默认流程是交互式的。安装器会显示依赖工具和上游 Skills 的选择器：工具
（rg、fzf）默认全选，上游 Skills 默认只选 `kepano/obsidian-skills`
（`Ar9av/obsidian-wiki` 面向它自己的 vault 布局，属于可选项）。没有传入目
标路径时，安装器会把 vault 生成到当前目录；目标目录非空或位于其他 Git 仓
库内部时会拒绝，除非传入 `--force`。

需要 Python 3.10+ 与 Git。安装器不会替你安装 rg/fzf：缺少已选择的工具时
会给出可执行的报错提示。

如果你使用 `uv`，也可以运行已经发布到 PyPI 的入口：

```bash
uvx llm-wiki-installer
```

需要固定版本时：

```bash
uvx llm-wiki-installer==<version> --no-interactive /path/to/knowledge-vault
```

## 生成的目录

```text
inbox/      待处理输入
raw/        用户确认过的原始证据
attachments/ Obsidian 默认附件目录
wiki/       长期维护的 Markdown 知识
wiki/tags.md 扁平 kebab-case 标签注册表
outputs/    当前交付物
archives/    不活跃的旧交付物
AGENTS.md   跨工具的规范 agent 策略（Codex/Gemini/OpenCode 读取）
CLAUDE.md   为 Claude Code 引入 AGENTS.md（@AGENTS.md import）
.agents/    上游 Skills（.claude/skills 为指向它的软链）
.codex/     Codex 适配配置与 Stop hook（信任项目后生效）
.scripts/   校验脚本
```

空目录内含 `.gitkeep` 占位文件，保证 commit/push/clone 后目录结构不丢失。
内置的 obsidian-git 插件配置为手动 commit（不自动提交/拉取/推送），Git
审查门才真实存在。

核心工作流：

```text
inbox -> raw -> wiki -> query -> fileback -> review -> export/archive
```

## 常用安装参数

```text
--force              覆盖生成文件，并允许非空目录 / 嵌套 Git 仓库目标
--no-interactive     不显示交互选择器，使用默认选择
--yes                --no-interactive 的别名
--tools LIST         选择 rg,fzf, all 或 none（默认 all）
--skills LIST        选择 Ar9av,kepano, all 或 none（默认 kepano）
--offline            禁止网络 bootstrap 操作
--dry-run            只打印安装计划，不写文件
--json               用 JSON 输出 dry-run 或最终摘要
```

示例：

```bash
bash install.sh --dry-run --json /path/to/knowledge-vault
bash install.sh --tools rg --skills kepano /path/to/knowledge-vault
bash install.sh --offline --tools rg --skills none /path/to/knowledge-vault
```

## 隐私与网络边界

安装器不包含遥测。它只会写入目标 vault 根目录下面的路径，并会拒绝把生成
内容写进安装器仓库本身或其子目录。

可能发生的网络操作只有三类：

- streamed install 克隆本安装器的指定 release ref；
- 克隆用户选择的、已 pin commit 的上游 Skill 来源。

使用 `--dry-run` 可以先查看计划；使用 `--offline` 可以关闭网络 bootstrap
操作。

## 开发

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
make verify
```

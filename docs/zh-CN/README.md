# llm-wiki-installer 中文指南

`llm-wiki-installer` 用一条命令生成一个适合 LLM 和 Obsidian 使用的
Markdown 知识库仓库。生成后的 vault 使用 Git 审核变更，用 `raw/` 保存经
用户确认的原始证据，用 `wiki/` 保存长期维护的结构化知识。

本仓库不是知识库本身，而是安装器。安装器会把固定目录、AGENTS 策略、辅助
脚本、qmd 配置和可选上游 Skills 写入另一个目标仓库。

## 30 秒开始

推荐使用已经发布到 PyPI 的入口：

```bash
mkdir knowledge-vault
cd knowledge-vault
uvx --python 3.13 llm-wiki-installer --no-interactive .
bash .scripts/postrun.sh
git status --short
```

先预览计划，不写文件、不联网：

```bash
uvx --python 3.13 llm-wiki-installer --dry-run --json .
```

需要固定版本时：

```bash
uvx --python 3.13 llm-wiki-installer==0.1.0 --dry-run --json /path/to/knowledge-vault
```

如果目标机器不用 `uv`，也可以使用 release-pinned shell bootstrap：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/exhank/llm-wiki-installer/v0.1.0/install.sh)" -- --no-interactive
```

## 生成的目录

```text
inbox/      待处理输入
raw/        用户确认过的原始证据
wiki/       长期维护的 Markdown 知识
outputs/    当前交付物
archive/    不活跃的旧交付物
.agents/    上游 Skills 与 manifest
.codex/     Codex 适配配置
.scripts/   校验脚本
```

核心工作流：

```text
inbox -> raw -> wiki -> query -> fileback -> review -> export/archive
```

## 常用安装参数

```text
--force              覆盖目标 vault 中的生成文件
--no-interactive     不显示交互选择器，使用默认全选
--yes                --no-interactive 的别名
--tools LIST         选择 qmd,rg,fzf, all 或 none
--skills LIST        选择 Ar9av,kepano, all 或 none
--no-install-tools   缺少已选择工具时直接失败，不自动安装
--offline            禁止网络 bootstrap 操作
--dry-run            只打印安装计划，不写文件
--json               用 JSON 输出 dry-run 或最终摘要
```

示例：

```bash
bash install.sh --dry-run --json /path/to/knowledge-vault
bash install.sh --tools qmd,rg --skills kepano /path/to/knowledge-vault
bash install.sh --offline --tools rg --skills none /path/to/knowledge-vault
```

## 隐私与网络边界

安装器不包含遥测。它只会写入目标 vault 根目录下面的路径，并会拒绝把生成
内容写进安装器仓库本身或其子目录。

可能发生的网络操作只有三类：

- streamed install 克隆本安装器的指定 release ref；
- 克隆用户选择的、已 pin commit 的上游 Skill 来源；
- 当选择 qmd 且本机缺少 qmd 时，通过 npm 安装 `@tobilu/qmd`。

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

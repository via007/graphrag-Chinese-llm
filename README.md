---

# GraphRAG 中文优化版

本项目基于微软的 [GraphRAG](https://github.com/microsoft/graphrag) 进行改进，旨在更好地适配中文语料环境，优化国内用户的使用体验。通过调整提示词输出语言、集成国内主流大语言模型 (LLM) 接口以及提供详细的中文配置说明，本项目大幅降低了中文用户的使用门槛，同时保留了原项目的核心功能和灵活性。

## 项目亮点

- **中文友好**：将提示词的输出语言从英文改为中文，便于国内用户理解和使用。
- **支持国内 LLM**：集成了 DeepSeek、阿里云、腾讯云等国内主流大语言模型接口，方便国内用户调用。
- **详细中文文档**：提供全面的中文版配置文件说明（参考 `yml参数配置详细说明-中文版.md`），降低学习成本。
- **优化开发体验**：通过 Poetry 管理依赖，推荐 Python 3.11/3.12，提供缓存机制和调试模式，减少资源浪费。
- **知识图谱可视化**：支持基于 Parquet 文件的知识图谱可视化，参考 `KnowledgeGraph.py`。

## 快速开始

### 环境要求

- **Python 版本**：3.11 或 3.12（强烈建议使用最新版本以确保兼容性）。
- **依赖管理**：使用 [Poetry](https://python-poetry.org/) 管理项目依赖，避免在 Conda 环境中配置以减少潜在冲突。

### 安装步骤

1. 克隆本项目：
   ```bash
   git clone https://github.com/your-username/graphrag-chinese.git
   cd graphrag-chinese
   ```

2. 安装 Poetry（如果尚未安装）：
   ```bash
   pip install poetry
   ```

3. 安装项目依赖：
   ```bash
   poetry install
   ```

4. 配置国内 LLM 接口：
   - 编辑 `my_pkb/settings.yml`，根据需求配置 DeepSeek、阿里云、腾讯云等 LLM 接口。
   - 具体参数说明请参考 `yml参数配置详细说明-中文版.md`。

### 建立索引

为了避免资源浪费，建议先使用调试模式验证配置：

```bash
poetry run poe index --root ./my_pkb --dry-run --verbose
```

- `--dry-run`：仅验证配置，不实际执行索引操作。
- `--verbose`：启用详细日志，便于排查问题。

正式建立索引：

```bash
poetry run poe index --root ./my_pkb --verbose
```

如果索引过程因网络或其他原因中断，可启用缓存以节省时间：

```bash
poetry run poe index --root ./my_pkb --cache --verbose
```

### 查询知识图谱

索引建立完成后，可通过以下命令进行查询：

```bash
poetry run poe query --root ./my_pkb --method local --query "你好"
```

- `--method local`：使用本地索引进行查询。
- `--query`：输入您的查询内容（支持中文）。

### 可视化知识图谱

本项目生成的知识图谱以 Parquet 文件形式存储，您可以通过 Python 脚本进行可视化。参考以下代码：

可视化方法请参考 `KnowledgeGraph.py`。

## 注意事项

在项目落地过程中，我们总结了以下关键问题和解决方案，帮助您更高效地使用本项目：

1. **Python 版本兼容性**：
   - 请确保使用 Python 3.11 或 3.12。较低版本可能导致依赖冲突或功能异常。

2. **依赖管理**：
   - 推荐使用 Poetry 管理环境，避免在 Conda 中配置，以减少环境冲突的可能性。
   - 运行 `poetry install` 后，可通过 `poetry shell` 进入虚拟环境。

3. **调试模式**：
   - 建立索引前，使用 `--dry-run` 和 `--verbose` 检查配置文件和环境是否正确，避免浪费 LLM API 的 tokens。

4. **缓存机制**：
   - 如果索引过程中断，第二次运行时加上 `--cache` 参数，可复用之前的计算结果，节省时间和成本。

5. **日志记录**：
   - 始终启用 `--verbose` 参数，详细日志有助于快速定位问题。

6. **国内 LLM 配置**：
   - 请确保在 `settings.yml` 中正确填写 API Key 和 Endpoint。国内 LLM 的调用频率和配额可能有限，请提前确认。

## 配置文件说明

所有配置参数的详细说明请参考以下文档：
- **`yml参数配置详细说明-中文版.md`**：包含 `settings.yml` 中每个字段的中文解释和推荐值。
- 示例配置文件位于 `my_pkb/settings.yml`，包括 DeepSeek、阿里云、腾讯云等 LLM 的配置模板。

## 许可证

本项目遵循原 GraphRAG 项目的 [MIT 许可证](https://github.com/microsoft/graphrag/blob/main/LICENSE)。请确保在使用本项目时遵守相关条款。

## 致谢

感谢微软 GraphRAG 团队提供的优秀开源项目，以及国内 LLM 提供商（DeepSeek、阿里云、腾讯云等）对本项目的支持。


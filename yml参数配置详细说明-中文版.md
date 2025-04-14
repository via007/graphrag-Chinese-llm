<DOCUMENT>
# 默认配置模式（使用 YAML/JSON）

默认配置模式可以通过在数据项目根目录中使用 `settings.yml` 或 `settings.json` 文件进行配置。如果同时存在一个 `.env` 文件，则它将被加载，其中定义的环境变量将可用于配置文档中的标记替换，使用 `${ENV_VAR}` 语法。我们在 `graphrag init` 中默认初始化为 YML，但如果您愿意，也可以使用等效的 JSON 格式。

许多这些配置值都有默认值。为了避免在此重复说明，请直接参考代码中的 [constants](https://github.com/microsoft/graphrag/blob/main/graphrag/config/defaults.py)。

例如：

```
# .env
GRAPHRAG_API_KEY=some_api_key

# settings.yml
llm: 
  api_key: ${GRAPHRAG_API_KEY}
```

# 配置部分

## 语言模型设置

### models

这是一个模型配置的字典。字典的键用于在需要模型实例时在其他地方引用此配置。通过这种方式，您可以根据需要指定多个不同的模型，并在工作流程步骤中分别引用它们。

例如：
```yml
models:
  default_chat_model:
    api_key: ${GRAPHRAG_API_KEY}
    type: openai_chat
    model: gpt-4o
    model_supports_json: true
  default_embedding_model:
    api_key: ${GRAPHRAG_API_KEY}
    type: openai_embedding
    model: text-embedding-ada-002
```

#### 字段

- `api_key` **str** - 要使用的 OpenAI API 密钥。
- `auth_type` **api_key|managed_identity** - 指示您希望如何验证请求。
- `type` **openai_chat|azure_openai_chat|openai_embedding|azure_openai_embedding|mock_chat|mock_embeddings** - 要使用的 LLM 类型。
- `model` **str** - 模型名称。
- `encoding_model` **str** - 要使用的文本编码模型。默认使用与语言模型对齐的编码模型（即如果未设置，则从 tiktoken 中检索）。
- `api_base` **str** - 要使用的 API 基础 URL。
- `api_version` **str** - API 版本。
- `deployment_name` **str** - 要使用的部署名称（Azure）。
- `organization` **str** - 客户端组织。
- `proxy` **str** - 要使用的代理 URL。
- `audience` **str** - （仅限 Azure OpenAI）请求托管身份令牌的目标 Azure 资源/服务的 URI。如果未定义 `api_key`，则使用此字段。默认值=`https://cognitiveservices.azure.com/.default`
- `model_supports_json` **bool** - 模型是否支持 JSON 模式输出。
- `request_timeout` **float** - 每个请求的超时时间。
- `tokens_per_minute` **int** - 设置每分钟令牌的漏桶限制。
- `requests_per_minute` **int** - 设置每分钟请求的漏桶限制。
- `retry_strategy` **str** - 要使用的重试策略，默认值为 "native"，使用 OpenAI SDK 内置的策略。其他允许的值包括 "exponential_backoff"、"random_wait" 和 "incremental_wait"。
- `max_retries` **int** - 最大重试次数。
- `max_retry_wait` **float** - 最大回退时间。
- `concurrent_requests` **int** - 允许同时打开的请求数。
- `async_mode` **asyncio|threaded** - 要使用的异步模式。可以是 `asyncio` 或 `threaded`。
- `responses` **list[str]** - 如果此模型类型是模拟的，则这是要返回的响应字符串列表。
- `max_tokens` **int** - 输出令牌的最大数量。
- `temperature` **float** - 要使用的温度。
- `top_p` **float** - 要使用的 top-p 值。
- `n` **int** - 要生成的完成数量。
- `frequency_penalty` **float** - 令牌生成的频率惩罚。
- `presence_penalty` **float** - 令牌生成的出现惩罚。

## 输入文件和分块

### input

我们的管道可以从输入文件夹中摄取 .csv、.txt 或 .json 数据。请参阅 [inputs 页面](../index/inputs.md) 了解更多详情和示例。

#### 字段

- `type` **file|blob** - 要使用的输入类型。默认值=`file`
- `file_type` **text|csv|json** - 要加载的输入数据类型。默认值是 `text`
- `base_dir` **str** - 从根目录相对读取输入的基础目录。
- `connection_string` **str** - （仅限 blob）Azure 存储连接字符串。
- `storage_account_blob_url` **str** - 要使用的存储账户 blob URL。
- `container_name` **str** - （仅限 blob）Azure 存储容器名称。
- `encoding` **str** - 输入文件的编码。默认值是 `utf-8`
- `file_pattern` **str** - 匹配输入文件的正则表达式。根据指定的 `file_type`，默认值是 `.*\.csv$`、`.*\.txt$` 或 `.*\.json$`，但您可以根据需要自定义。
- `file_filter` **dict** - 用于过滤的键/值对。默认值是 None。
- `text_column` **str** - （仅限 CSV/JSON）文本列名称。如果未设置，我们期望有一个名为 `text` 的列。
- `title_column` **str** - （仅限 CSV/JSON）标题列名称，如果未设置，将使用文件名。
- `metadata` **list[str]** - （仅限 CSV/JSON）要保留的附加文档属性字段。

### chunks

这些设置配置我们如何将文档解析成文本块。这是必要的，因为非常大的文档可能无法适应单个上下文窗口，并且图提取的准确性可以被调整。另请注意输入文档配置中的 `metadata` 设置，它会将文档元数据复制到每个块中。

#### 字段

- `size` **int** - 块的最大大小（以令牌为单位）。
- `overlap` **int** - 块的重叠（以令牌为单位）。
- `group_by_columns` **list[str]** - 在分块前按这些字段对文档进行分组。
- `strategy` **str**[tokens|sentences] - 如何分块文本。
- `encoding_model` **str** - 用于按令牌边界分割的文本编码模型。
- `prepend_metadata` **bool** - 确定是否应在每个块的开头添加元数据值。默认值=`False`。
- `chunk_size_includes_metadata` **bool** - 指定块大小计算是否应包括元数据令牌。默认值=`False`。

## 输出和存储

### output

此部分控制管道用于导出输出表的存储机制。

#### 字段

- `type` **file|memory|blob|cosmosdb** - 要使用的存储类型。默认值=`file`
- `base_dir` **str** - 相对于根目录写入输出工件的基础目录。
- `connection_string` **str** - （仅限 blob/cosmosdb）Azure 存储连接字符串。
- `container_name` **str** - （仅限 blob/cosmosdb）Azure 存储容器名称。
- `storage_account_blob_url` **str** - （仅限 blob）要使用的存储账户 blob URL。
- `cosmosdb_account_blob_url` **str** - （仅限 cosmosdb）CosmosDB 账户 blob URL。

### update_index_output

此部分定义了用于运行增量索引的二级存储位置，以保留您的原始输出。

#### 字段

- `type` **file|memory|blob|cosmosdb** - 要使用的存储类型。默认值=`file`
- `base_dir` **str** - 相对于根目录写入输出工件的基础目录。
- `connection_string` **str** - （仅限 blob/cosmosdb）Azure 存储连接字符串。
- `container_name` **str** - （仅限 blob/cosmosdb）Azure 存储容器名称。
- `storage_account_blob_url` **str** - （仅限 blob）要使用的存储账户 blob URL。
- `cosmosdb_account_blob_url` **str** - （仅限 cosmosdb）CosmosDB 账户 blob URL。

### cache

此部分控制管道使用的缓存机制。这用于缓存 LLM 调用结果，以便在重新运行索引过程时获得更快的性能。

#### 字段

- `type` **file|memory|blob|cosmosdb** - 要使用的存储类型。默认值=`file`
- `base_dir` **str** - 相对于根目录写入输出工件的基础目录。
- `connection_string` **str** - （仅限 blob/cosmosdb）Azure 存储连接字符串。
- `container_name` **str** - （仅限 blob/cosmosdb）Azure 存储容器名称。
- `storage_account_blob_url` **str** - （仅限 blob）要使用的存储账户 blob URL。
- `cosmosdb_account_blob_url` **str** - （仅限 cosmosdb）CosmosDB 账户 blob URL。

### reporting

此部分控制管道使用的报告机制，用于常见事件和错误消息。默认值是将报告写入输出目录中的文件。但是，您也可以选择将报告写入控制台或 Azure Blob 存储容器。

#### 字段

- `type` **file|console|blob** - 要使用的报告类型。默认值=`file`
- `base_dir` **str** - 相对于根目录写入报告的基础目录。
- `connection_string` **str** - （仅限 blob）Azure 存储连接字符串。
- `container_name` **str** - （仅限 blob）Azure 存储容器名称。
- `storage_account_blob_url` **str** - 要使用的存储账户 blob URL。

### vector_store

系统所有向量的存储位置。默认配置为 lancedb。这是一个字典，其键用于标识各个存储参数（例如，用于文本嵌入）。

#### 字段

- `type` **lancedb|azure_ai_search|cosmosdb** - 向量存储的类型。默认值=`lancedb`
- `db_uri` **str** （仅限 lancedb）- 数据库 URI。默认值=`storage.base_dir/lancedb`
- `url` **str** （仅限 AI Search）- AI Search 端点
- `api_key` **str** （可选 - 仅限 AI Search）- 要使用的 AI Search API 密钥。
- `audience` **str** （仅限 AI Search）- 如果使用托管身份验证，则为托管身份令牌的受众。
- `container_name` **str** - 向量容器的名称。这存储给定数据集摄取的所有索引（表）。默认值=`default`
- `database_name` **str** - （仅限 cosmosdb）数据库名称。
- `overwrite` **bool** （仅在索引创建时使用）- 如果集合存在则覆盖。默认值=`True`

## 工作流程配置

这些设置控制每个单独的工作流程的执行。

### workflows

**list[str]** - 这是要按顺序运行的工作流程名称列表。GraphRAG 内置了管道来配置此项，但您可以通过在此指定列表来精确运行您想要的内容。如果您自己完成了部分处理，这将非常有用。

### embed_text

默认情况下，GraphRAG 索引器只会导出我们的查询方法所需的嵌入。然而，该模型为所有纯文本字段定义了嵌入，这些嵌入可以通过设置 `target` 和 `names` 字段进行自定义。

支持的嵌入名称包括：

- `text_unit.text`
- `document.text`
- `entity.title`
- `entity.description`
- `relationship.description`
- `community.title`
- `community.summary`
- `community.full_content`

#### 字段

- `model_id` **str** - 用于文本嵌入的模型定义名称。
- `vector_store_id` **str** - 要写入的向量存储定义名称。
- `batch_size` **int** - 要使用的最大批处理大小。
- `batch_max_tokens` **int** - 批处理的最大令牌数。
- `target` **required|all|selected|none** - 确定要导出的嵌入集。
- `names` **list[str]** - 如果 target=selected，则应明确列出我们支持的嵌入名称。

### extract_graph

调整基于语言模型的图提取过程。

#### 字段

- `model_id` **str** - 用于 API 调用的模型定义名称。
- `prompt` **str** - 要使用的提示文件。
- `entity_types` **list[str]** - 要识别的实体类型。
- `max_gleanings` **int** - 要使用的最大收集循环次数。
- `encoding_model` **str** - 要使用的文本编码模型。默认使用与语言模型对齐的编码模型（即如果未设置，则从 tiktoken 中检索）。这仅在 logit_bias 检查期间用于收集。

### summarize_descriptions

#### 字段

- `model_id` **str** - 用于 API 调用的模型定义名称。
- `prompt` **str** - 要使用的提示文件。
- `max_length` **int** - 每次总结的输出令牌最大数量。

### extract_graph_nlp

定义 NLP 基于图提取方法的设置。

#### 字段

- `normalize_edge_weights` **bool** - 在图构建期间是否标准化边权重。默认值=`True`。
- `text_analyzer` **dict** - NLP 模型的参数。
  - extractor_type **regex_english|syntactic_parser|cfg** - 默认值=`regex_english`。
  - model_name **str** - NLP 模型的名称（适用于基于 SpaCy 的模型）
  - max_word_length **int** - 允许的最长单词。默认值=`15`。
  - word_delimiter **str** - 分割单词的分隔符。默认值 ' '。
  - include_named_entities **bool** - 是否在名词短语中包含命名实体。默认值=`True`。
  - exclude_nouns **list[str] | None** - 要排除的名词列表。如果为 `None`，我们使用内部停用词列表。
  - exclude_entity_tags **list[str]** - 要忽略的实体标签列表。
  - exclude_pos_tags **list[str]** - 要忽略的词性标签列表。
  - noun_phrase_tags **list[str]** - 要忽略的名词短语标签列表。
  - noun_phrase_grammars **dict[str, str]** - 模型的名词短语语法（仅限 cfg）。

### prune_graph

手动图修剪的参数。这可以用来优化图簇的模块化，通过移除过度连接或稀有节点。

#### 字段

- min_node_freq **int** - 允许的最小节点频率。
- max_node_freq_std **float | None** - 允许的节点频率最大标准差。
- min_node_degree **int** - 允许的最小节点度。
- max_node_degree_std **float | None** - 允许的节点度最大标准差。
- min_edge_weight_pct **int** - 允许的最小边权重百分位。
- remove_ego_nodes **bool** - 移除自我节点。
- lcc_only **bool** - 仅使用最大连接组件。

### cluster_graph

这些是用于图的 Leiden 层次聚类以创建社区的设置。

#### 字段

- `max_cluster_size` **int** - 要导出的最大簇大小。
- `use_lcc` **bool** - 是否仅使用最大连接组件。
- `seed` **int** - 如果希望运行结果一致，则提供的随机化种子。我们确实提供了默认值以保证聚类稳定性。

### extract_claims

#### 字段

- `enabled` **bool** - 是否启用声明提取。默认关闭，因为声明提示确实需要用户调整。
- `model_id` **str** - 用于 API 调用的模型定义名称。
- `prompt` **str** - 要使用的提示文件。
- `description` **str** - 描述我们想要提取的声明类型。
- `max_gleanings` **int** - 要使用的最大收集循环次数。
- `encoding_model` **str** - 要使用的文本编码模型。默认使用与语言模型对齐的编码模型（即如果未设置，则从 tiktoken 中检索）。这仅在 logit_bias 检查期间用于收集。

### community_reports

#### 字段

- `model_id` **str** - 用于 API 调用的模型定义名称。
- `prompt` **str** - 要使用的提示文件。
- `max_length` **int** - 每个报告的输出令牌最大数量。
- `max_input_length` **int** - 生成报告时使用的输入令牌最大数量。

### embed_graph

我们使用 node2vec 来嵌入图。这主要用于可视化，因此默认未启用。

#### 字段

- `enabled` **bool** - 是否启用图嵌入。
- `dimensions` **int** - 要生成的向量维度数。
- `num_walks` **int** - node2vec 的漫步次数。
- `walk_length` **int** - node2vec 的漫步长度。
- `window_size` **int** - node2vec 的窗口大小。
- `iterations` **int** - node2vec 的迭代次数。
- `random_seed` **int** - node2vec 的随机种子。
- `strategy` **dict** - 完全覆盖嵌入图策略。

### umap

指示我们是否应运行 UMAP 降维。这用于为每个图节点提供适合可视化的 x/y 坐标。如果未启用此功能，节点将收到 0/0 x/y 坐标。如果启用此功能，您 *必须* 同时启用图嵌入。

#### 字段

- `enabled` **bool** - 是否启用 UMAP 布局。

### snapshots

#### 字段

- `embeddings` **bool** - 将嵌入快照导出到 parquet。
- `graphml` **bool** - 将图快照导出到 GraphML。

## 查询

### local_search

#### 字段

- `chat_model_id` **str** - 用于聊天完成调用的模型定义名称。
- `embedding_model_id` **str** - 用于嵌入调用的模型定义名称。
- `prompt` **str** - 要使用的提示文件。
- `text_unit_prop` **float** - 文本单元比例。
- `community_prop` **float** - 社区比例。
- `conversation_history_max_turns` **int** - 对话历史最大轮次。
- `top_k_entities` **int** - 映射的顶级 k 个实体。
- `top_k_relationships` **int** - 映射的顶级 k 个关系。
- `temperature` **float | None** - 用于令牌生成的温度。
- `top_p` **float | None** - 用于令牌生成的 top-p 值。
- `n` **int | None** - 要生成的完成数量。
- `max_tokens` **int** - 最大令牌数。
- `llm_max_tokens` **int** - LLM 最大令牌数。

### global_search

#### 字段

- `chat_model_id` **str** - 用于聊天完成调用的模型定义名称。
- `map_prompt` **str** - 要使用的映射器提示文件。
- `reduce_prompt` **str** - 要使用的归约器提示文件。
- `knowledge_prompt` **str** - 要使用的知识提示文件。
- `map_prompt` **str | None** - 全局搜索映射器提示。
- `reduce_prompt` **str | None** - 全局搜索归约器。
- `knowledge_prompt` **str | None** - 全局搜索通用提示。
- `temperature` **float | None** - 用于令牌生成的温度。
- `top_p` **float | None** - 用于令牌生成的 top-p 值。
- `n` **int | None** - 要生成的完成数量。
- `max_tokens` **int** - 最大上下文大小（以令牌为单位）。
- `data_max_tokens` **int** - 数据 LLM 最大令牌数。
- `map_max_tokens` **int** - 映射 LLM 最大令牌数。
- `reduce_max_tokens` **int** - 归约 LLM 最大令牌数。
- `concurrency` **int** - 并发请求数。
- `dynamic_search_llm` **str** - 用于动态社区选择的 LLM 模型。
- `dynamic_search_threshold` **int** - 包含社区报告的评分阈值。
- `dynamic_search_keep_parent` **bool** - 如果任何子社区相关，则保留父社区。
- `dynamic_search_num_repeats` **int** - 对同一社区报告评分的次数。
- `dynamic_search_use_summary` **bool** - 使用社区摘要而不是完整上下文。
- `dynamic_search_concurrent_coroutines` **int** - 并发协程数，用于评分社区报告。
- `dynamic_search_max_level` **int** - 如果处理的社区都不相关，则考虑的社区层次最大级别。

### drift_search

#### 字段

- `chat_model_id` **str** - 用于聊天完成调用的模型定义名称。
- `embedding_model_id` **str** - 用于嵌入调用的模型定义名称。
- `prompt` **str** - 要使用的提示文件。
- `reduce_prompt` **str** - 要使用的归约器提示文件。
- `temperature` **float** - 用于令牌生成的温度。
- `top_p` **float** - 用于令牌生成的 top-p 值。
- `n` **int** - 要生成的完成数量。
- `max_tokens` **int** - 最大上下文大小（以令牌为单位）。
- `data_max_tokens` **int** - 数据 LLM 最大令牌数。
- `concurrency` **int** - 并发请求数。
- `drift_k_followups` **int** - 要检索的顶级全局结果数量。
- `primer_folds` **int** - 搜索启动的折叠次数。
- `primer_llm_max_tokens` **int** - 启动中 LLM 的最大令牌数。
- `n_depth` **int** - 漂移搜索的步数。
- `local_search_text_unit_prop` **float** - 搜索中分配给文本单元的比例。
- `local_search_community_prop` **float** - 搜索中分配给社区属性的比例。
- `local_search_top_k_mapped_entities` **int** - 本地搜索期间映射的顶级 K 个实体数。
- `local_search_top_k_relationships` **int** - 本地搜索期间映射的顶级 K 个关系数。
- `local_search_max_data_tokens` **int** - 本地搜索的最大上下文大小（以令牌为单位）。
- `local_search_temperature` **float** - 本地搜索中用于令牌生成的温度。
- `local_search_top_p` **float** - 本地搜索中用于令牌生成的 top-p 值。
- `local_search_n` **int** - 本地搜索中要生成的完成数量。
- `local_search_llm_max_gen_tokens` **int** - 本地搜索中 LLM 的最大生成令牌数。

### basic_search

#### 字段

- `chat_model_id` **str** - 用于聊天完成调用的模型定义名称。
- `embedding_model_id` **str** - 用于嵌入调用的模型定义名称。
- `prompt` **str** - 要使用的提示文件。
- `text_unit_prop` **float** - 文本单元比例。
- `community_prop` **float** - 社区比例。
- `conversation_history_max_turns` **int** - 对话历史最大轮次。
- `top_k_entities` **int** - 映射的顶级 k 个实体。
- `top_k_relationships` **int** - 映射的顶级 k 个关系。
- `temperature` **float | None** - 用于令牌生成的温度。
- `top_p` **float | None** - 用于令牌生成的 top-p 值。
- `n` **int | None** - 要生成的完成数量。
- `max_tokens` **int** - 最大令牌数。
- `llm_max_tokens` **int** - LLM 最大令牌数。
</DOCUMENT>
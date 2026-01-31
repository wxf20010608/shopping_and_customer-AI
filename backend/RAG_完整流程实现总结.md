# RAG 完整流程实现总结

## ✅ 已完整实现的 RAG 功能

### 一、数据准备与索引构建（离线阶段）

#### 1. 文档上传/导入 ✅
- **手动创建**：`POST /knowledge-base/documents`
- **文件上传**：`POST /knowledge-base/documents/upload`（支持 PDF、Word、Excel、文本、图片）
- **从URL导入**：`POST /knowledge-base/documents/from-url`
- **从数据库导入**：`POST /knowledge-base/documents/from-database` ✅ **新增功能**

#### 2. 文本预处理（5个步骤）✅
**实现位置**：`backend/app/services/text_cleaner.py`

- **(1) 文本规范化** (`normalize_text`)
  - 统一编码（UTF-8）
  - 正则表达式去除特殊字符、乱码
  - 标准化日期、货币格式

- **(2) 结构化处理** (`extract_structure`)
  - 提取标题、段落、列表
  - 处理表格数据（转为Markdown）
  - 代码块分离和格式化

- **(3) 内容清理** (`clean_content`)
  - 去除广告、导航栏、页脚等噪音
  - 过滤低质量文本
  - 去重（完全重复）
  - 质量评分计算

- **(4) 分块优化** (`chunk_text_optimized`)
  - 按语义边界分块（段落、章节）
  - 重叠分块避免信息割裂
  - 控制分块大小（可配置）

- **(5) 元数据提取** (`extract_metadata`)
  - 提取来源、作者、时间等信息
  - 添加文档结构标签
  - 质量评分标注
  - 统计信息

#### 3. 向量化与索引 ✅
**实现位置**：`backend/app/services/rag_service.py` - `add_document()`

**流程**：
1. 使用嵌入模型将文本块转换为向量（`embed_texts`）
2. 存储到 FAISS 向量索引（`vector_index.add(embeddings)`）
3. 存储到数据库：
   - `knowledge_documents` 表：文档元数据、内容、质量评分
   - `knowledge_chunks` 表：文档块、向量ID映射、块元数据
4. 保存向量索引到文件（`_save_vector_index()`）

**代码位置**：
```python
# backend/app/services/rag_service.py:205-311
def add_document(...):
    # 步骤1：文本预处理（5个子步骤）
    # 步骤2：存储文档到数据库
    # 步骤3：向量化与索引构建
    #   3.1 批量向量化
    #   3.2 添加到FAISS向量索引
    #   3.3 创建块记录并存储到数据库
    #   3.4 提交数据库事务
    #   3.5 保存向量索引到文件
```

### 二、检索-增强（Retrieval-Augmented）（在线阶段）

#### 1. 查询向量化 ✅
**实现位置**：`backend/app/services/rag_service.py` - `search()`

- 使用与文档相同的嵌入模型将用户查询转换为向量
- 向量归一化以便计算余弦相似度

#### 2. 相似度检索 ✅
**实现位置**：`backend/app/services/rag_service.py` - `search()`

**流程**：
1. 在 FAISS 向量索引中搜索（使用 L2 距离）
2. 转换为相似度分数：`similarity = 1 / (1 + distance)`
3. 应用相似度阈值过滤（默认 0.3）
4. 按相似度降序排序
5. 返回 Top-K 结果

**代码位置**：
```python
# backend/app/services/rag_service.py:313-371
def search(...):
    # 步骤1：向量化查询
    # 步骤2：在向量索引中搜索
    # 步骤3：计算相似度并过滤
    # 步骤4：按相似度排序
```

#### 3. 上下文构建 ✅
**实现位置**：`backend/app/services/rag_service.py` - `retrieve_context()`

**流程**：
1. 调用 `search()` 获取检索结果
2. 从数据库获取文档块内容
3. 按相似度排序并组合成上下文文本
4. 返回上下文和结果详情

**代码位置**：
```python
# backend/app/services/rag_service.py:373-440
def retrieve_context(...):
    # 步骤1：向量化查询并检索
    # 步骤2：从数据库获取块内容
    # 步骤3：按相似度排序并组合上下文
```

### 三、生成（Generation）

#### 1. 提示词增强 ✅
**实现位置**：`backend/app/services/customer_service.py` - `chat()`

**流程**：
1. 调用 `rag_service.retrieve_context()` 检索知识库
2. 如果找到相关内容（相似度 >= 阈值）：
   - 将知识库内容注入系统提示词
   - **明确指示AI优先使用知识库内容回答**
   - 如果知识库内容完全回答了问题，直接使用知识库内容
   - 如果知识库内容部分相关，结合知识库和系统信息回答
3. 如果没有找到相关内容（相似度 < 阈值）：
   - 使用常规系统提示词
   - 直接调用大模型回答

**代码位置**：
```python
# backend/app/services/customer_service.py:328-395
def chat(...):
    # RAG 知识库检索增强（完整流程）
    # 步骤1：向量化用户查询
    # 步骤2：在向量数据库中检索最相关的文档块（余弦相似度计算）
    # 步骤3：获取检索结果并构建上下文
    # 如果找到相关内容：优先使用知识库内容
    # 如果没有找到：使用大模型直接回答
```

#### 2. 大模型生成 ✅
- 将增强后的提示词发送给 Qwen 模型
- 生成最终回复
- 保存对话记录

## 完整流程串联

### 管理员上传文档流程

```
管理员界面 → 上传文件/创建文档/从数据库导入
  ↓
后端API接收 (knowledge_base_route.py)
  ↓
rag_service.add_document()
  ↓
【数据准备阶段】
  ├─ (1) 文本规范化
  ├─ (2) 结构化处理
  ├─ (3) 内容清理
  ├─ (4) 分块优化
  └─ (5) 元数据提取
  ↓
【向量化与索引】
  ├─ 向量化（embed_texts）
  ├─ 存储到FAISS索引
  ├─ 存储到数据库（knowledge_documents, knowledge_chunks）
  └─ 保存索引文件
  ↓
文档列表显示（管理员界面）
```

### 用户对话时的RAG流程

```
用户提交问题
  ↓
customer_service.chat()
  ↓
【检索增强阶段】
  ├─ 向量化查询（embed_text）
  ├─ 在FAISS中搜索（L2距离）
  ├─ 转换为相似度分数（余弦相似度）
  ├─ 阈值过滤
  └─ 获取文档块内容
  ↓
【生成阶段】
  ├─ 如果找到相关内容（相似度 >= 阈值）
  │   └─ 注入知识库内容到提示词 → 优先使用知识库内容
  └─ 如果没有找到相关内容（相似度 < 阈值）
      └─ 使用常规提示词 → 调用大模型直接回答
  ↓
生成回复并保存
```

## 关键配置

### 环境变量

```bash
# 嵌入模型配置
RAG_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5  # 或通过 RAG_LANGUAGE 自动选择
RAG_LANGUAGE=zh  # zh/chinese, en/english, multilingual/multi

# 分块配置
RAG_CHUNK_SIZE=500          # 块大小（字符）
RAG_CHUNK_OVERLAP=50        # 重叠大小（字符）
RAG_MIN_CHUNK_LENGTH=20     # 最小块长度
RAG_MAX_CHUNK_LENGTH=2000   # 最大块长度

# 检索配置
RAG_TOP_K=3                 # 检索 Top-K 相关文档
RAG_SIMILARITY_THRESHOLD=0.3  # 相似度阈值（0-1），低于此值不使用知识库

# 质量过滤
RAG_QUALITY_THRESHOLD=0.3   # 质量评分阈值
```

## 管理员界面功能

### 知识库管理标签页 ✅

1. **创建文档**：手动输入文本创建文档
2. **从数据库导入**：从数据库表导入数据 ✅ **新增**
3. **从URL导入**：从网页URL导入内容
4. **上传文件**：上传PDF、Word、Excel、文本、图片等文件
5. **文档列表**：查看所有文档，支持分类和状态筛选 ✅ **已实现**
6. **搜索测试**：测试知识库检索功能
7. **重建索引**：重建向量索引

### 文档列表显示 ✅

- 文档ID和标题
- 分类
- 来源类型
- 块数量
- 质量评分
- 状态（有效/无效）
- 操作按钮（查看、删除）

## 客服对话中的RAG使用 ✅

### 自动检索流程

当用户进行客服对话时，系统会自动：

1. **向量化用户查询**
   - 使用与文档相同的嵌入模型
   - 将查询文本转换为向量

2. **在向量数据库中检索**
   - 使用 FAISS 进行 L2 距离搜索
   - 转换为相似度分数（余弦相似度）
   - 应用阈值过滤

3. **优先使用知识库内容**
   - 如果找到相关内容（相似度 >= 阈值）：
     - 将知识库内容注入系统提示词
     - **明确指示AI优先使用知识库内容回答**
     - 如果知识库内容完全回答了问题，直接使用知识库内容
   - 如果没有找到相关内容（相似度 < 阈值）：
     - 使用常规系统提示词
     - 调用大模型直接回答

### 日志输出

系统会输出详细的RAG检索日志：
- `✓ RAG检索成功：找到 N 条相关内容，最高相似度 X.XX`
- `⚠ RAG检索结果相似度较低（X.XX < 阈值），不使用知识库内容`
- `ℹ RAG检索未找到相关内容，将使用大模型直接回答`
- `⚠ RAG 检索失败: 错误信息`

## 数据存储

### 数据库表

1. **knowledge_documents** 表
   - 存储文档元数据、内容、质量评分
   - 字段：id, title, content, source_type, source_url, category, tags, active, chunk_count, document_metadata, quality_score

2. **knowledge_chunks** 表
   - 存储文档块、向量ID映射、块元数据
   - 字段：id, document_id, chunk_index, content, chunk_metadata, vector_id

### 向量索引文件

- **位置**：`backend/knowledge_base_index.faiss`
- **类型**：FAISS IndexFlatL2（L2距离索引）
- **持久化**：每次添加/删除文档后自动保存

## 完整示例

### 示例1：上传文档并检索

1. **管理员上传文档**：
   ```
   管理员界面 → 知识库标签页 → 上传文件
   选择文件：policy.pdf
   分类：售后政策
   ```
   - 系统自动执行：
     - 解析PDF → 清洗 → 分块 → 向量化 → 存储
     - 文档显示在列表中

2. **用户提问**：
   ```
   用户："退换货政策是什么？"
   ```
   - 系统自动执行：
     - 向量化查询 → 检索知识库 → 找到相关内容（相似度 0.85）
     - 使用知识库内容回答

### 示例2：从数据库导入

1. **管理员从数据库导入**：
   ```
   管理员界面 → 知识库标签页 → 从数据库表导入
   表名：products
   分类：商品信息
   ```
   - 系统自动执行：
     - 提取表数据 → 清洗 → 分块 → 向量化 → 存储
     - 文档显示在列表中

2. **用户提问**：
   ```
   用户："这个商品有什么特点？"
   ```
   - 系统自动执行：
     - 检索知识库 → 找到商品信息 → 使用知识库内容回答

## 性能优化

1. **模型选择**：
   - 中文内容：`BAAI/bge-large-zh-v1.5`
   - 中英文混合：`intfloat/multilingual-e5-large`

2. **相似度阈值**：
   - 严格模式：0.5-0.7
   - 平衡模式：0.3（默认）
   - 宽松模式：0.1-0.2

3. **Top-K 数量**：
   - 精确回答：1-2
   - 平衡模式：3（默认）
   - 全面回答：5-10

## ✅ 功能完整性确认

- ✅ 数据准备（文本预处理、分块、向量化）
- ✅ 索引构建（FAISS向量索引、数据库存储）
- ✅ 检索增强（向量化查询、相似度计算、阈值过滤）
- ✅ 生成增强（知识库内容注入、优先使用策略）
- ✅ 管理员界面（上传、查看、管理文档）
- ✅ 客服集成（自动检索、优先使用知识库）

**RAG 完整流程已实现，系统会自动在客服对话中优先使用知识库内容回答用户问题！**

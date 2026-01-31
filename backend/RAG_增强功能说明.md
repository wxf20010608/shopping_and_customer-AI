# RAG 知识库增强功能说明

## 新增功能概述

已实现完整的文本清洗、预处理、多语言模型支持等功能，大幅提升知识库质量和检索效果。

## 一、文本清洗功能（5个步骤）

### (1) 文本规范化

**功能**：
- ✅ 统一编码（UTF-8）
- ✅ 正则表达式去除特殊字符、乱码
- ✅ 标准化日期格式（如：2024/01/11 → 2024年1月11日）
- ✅ 标准化货币格式（如：¥100, 100元, RMB100 → ￥100）
- ✅ 去除控制字符和不可见字符
- ✅ 标准化空白字符

**实现位置**：`backend/app/services/text_cleaner.py` - `normalize_text()` 方法

### (2) 结构化处理

**功能**：
- ✅ 提取标题（支持 Markdown 格式 #、##、### 等）
- ✅ 提取段落（按双换行分割）
- ✅ 提取列表项（支持 -、*、+、数字列表）
- ✅ 处理表格数据（转换为 Markdown 表格格式）
- ✅ 代码块分离和格式化（识别 ``` 代码块）

**实现位置**：`backend/app/services/text_cleaner.py` - `extract_structure()` 方法

**输出结构**：
```python
{
    "text": "处理后的文本",
    "structure": {
        "titles": [{"level": 1, "text": "标题", "line": 0}],
        "paragraphs": ["段落1", "段落2"],
        "lists": [{"text": "列表项", "line": 5}],
        "tables": [{"row": 0, "cells": ["列1", "列2"]}],
        "code_blocks": [{"index": 0, "content": "代码", "language": "python"}]
    }
}
```

### (3) 内容清理

**功能**：
- ✅ 去除广告、导航栏、页脚等噪音内容
  - 匹配模式：首页、关于我们、Copyright、广告、关注我们等
- ✅ 过滤低质量文本
  - 过短内容（少于最小长度）
  - 无意义内容（纯数字、纯符号）
- ✅ 去重处理
  - 完全重复的行自动去除
  - 基于哈希值快速去重
- ✅ 质量评分
  - 综合长度、中文比例、信息密度、结构完整性评分
  - 低于阈值的文档自动过滤

**实现位置**：`backend/app/services/text_cleaner.py` - `clean_content()` 方法

**质量评分维度**：
- 长度评分（30%）：适中长度得分更高
- 中文内容比例（30%）：合理的中文比例
- 信息密度（20%）：非空白字符比例
- 结构完整性（20%）：包含标点和结构

### (4) 分块优化

**功能**：
- ✅ 按语义边界分块
  - 优先按标题分块（章节级别）
  - 其次按段落分块
  - 最后按句子分块
- ✅ 重叠分块
  - 避免信息割裂
  - 可配置重叠大小
- ✅ 控制分块大小
  - 最小块长度：20 字符（可配置）
  - 最大块长度：2000 字符（可配置）
  - 默认块大小：500 字符（可配置）

**实现位置**：`backend/app/services/text_cleaner.py` - `chunk_text_optimized()` 方法

**分块策略**：
1. 如果有标题，按标题分块（保留章节结构）
2. 如果没有标题，按段落分块
3. 如果段落太长，按句子分割
4. 应用重叠处理，避免信息割裂

### (5) 元数据提取

**功能**：
- ✅ 提取来源信息（URL、文件路径、数据库表名）
- ✅ 提取作者信息（从文档中识别）
- ✅ 提取时间信息（发布时间、更新时间）
- ✅ 添加文档结构标签
  - `has_titles` - 包含标题
  - `has_lists` - 包含列表
  - `has_tables` - 包含表格
  - `has_code` - 包含代码块
- ✅ 质量评分标注
- ✅ 统计信息
  - 总长度、字符数、中文字符数
  - 英文单词数、段落数、标题数等

**实现位置**：`backend/app/services/text_cleaner.py` - `extract_metadata()` 方法

**元数据示例**：
```json
{
    "source_url": "https://example.com",
    "extracted_at": "2024-01-11T12:00:00",
    "extracted_time": "2024-01-11",
    "author": "张三",
    "source_type": "web",
    "structure_tags": ["has_titles", "has_lists"],
    "quality_score": 0.85,
    "statistics": {
        "total_length": 5000,
        "chinese_char_count": 3000,
        "paragraph_count": 10
    }
}
```

## 二、多语言嵌入模型选择

### 支持的模型

**中文模型**（推荐用于中文内容）：
- `BAAI/bge-large-zh-v1.5` - 百度 BGE 大模型（中文效果最佳）
- `moka-ai/m3e-large` - M3E 大模型（中文专用）

**多语言模型**（推荐用于中英文混合）：
- `intfloat/multilingual-e5-large` - 多语言 E5 大模型
- `text-embedding-3-large` - OpenAI 兼容模型

**英文模型**（推荐用于英文内容）：
- `text-embedding-ada-002` - OpenAI Ada 模型
- `intfloat/e5-large-v2` - E5 大模型（英文专用）

### 配置方式

**方式一：通过语言类型自动选择**
```bash
# .env 文件
RAG_LANGUAGE=zh  # 可选: zh/chinese, en/english, multilingual/multi
```

系统会根据语言类型自动选择对应的模型列表，优先使用列表中的第一个模型。

**方式二：直接指定模型**
```bash
# .env 文件
RAG_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
```

**容错机制**：
- 如果指定的模型加载失败，会自动尝试备用模型
- 如果所有模型都失败，RAG 功能会降级但不影响主系统

### 实现位置

`backend/app/services/rag_service.py` - `_initialize_embedding_model()` 方法

## 三、数据库模型更新

### 新增字段

**KnowledgeDocument 表**：
- `metadata` (TEXT) - JSON 格式的元数据
- `quality_score` (FLOAT) - 文档质量评分（0-1）

**KnowledgeChunk 表**：
- `metadata` (TEXT) - JSON 格式的块元数据（已存在，现在会填充更多信息）

### 自动迁移

系统启动时会自动检查并添加新字段，无需手动迁移。

## 四、使用示例

### 添加文档（自动应用所有清洗步骤）

```python
# 通过 API 添加文档
POST /knowledge-base/documents
{
    "title": "商品退换货政策",
    "content": "支持7天无理由退换货...",
    "category": "售后政策"
}
```

系统会自动执行：
1. 文本规范化
2. 结构化处理
3. 内容清理
4. 分块优化
5. 元数据提取
6. 向量化和索引

### 查看文档元数据

```python
GET /knowledge-base/documents/{document_id}
```

返回结果包含：
- `metadata` - 完整的元数据 JSON
- `quality_score` - 质量评分

### 配置中文模型

```bash
# .env 文件
RAG_LANGUAGE=zh
# 或
RAG_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
```

## 五、环境变量配置

```bash
# RAG 基础配置
RAG_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5  # 嵌入模型名称
RAG_LANGUAGE=zh                              # 语言类型（自动选择模型）
RAG_CHUNK_SIZE=500                           # 块大小（字符）
RAG_CHUNK_OVERLAP=50                         # 重叠大小（字符）
RAG_TOP_K=3                                  # 检索 Top-K

# 文本清洗配置
RAG_MIN_CHUNK_LENGTH=20                      # 最小块长度
RAG_MAX_CHUNK_LENGTH=2000                    # 最大块长度
RAG_QUALITY_THRESHOLD=0.3                    # 质量评分阈值

# PDF 解析配置
PDF_MAX_PAGES=50                             # PDF 最大页数
PDF_MAX_CHARS=50000                          # PDF 最大字符数
```

## 六、性能优化建议

1. **模型选择**：
   - 中文内容优先使用 `BAAI/bge-large-zh-v1.5`
   - 中英文混合使用 `intfloat/multilingual-e5-large`
   - 英文内容使用 `intfloat/e5-large-v2`

2. **分块大小**：
   - 短文档（< 1000 字）：chunk_size = 300-500
   - 中等文档（1000-5000 字）：chunk_size = 500-800
   - 长文档（> 5000 字）：chunk_size = 800-1200

3. **质量阈值**：
   - 严格过滤：quality_threshold = 0.5
   - 中等过滤：quality_threshold = 0.3（默认）
   - 宽松过滤：quality_threshold = 0.1

## 七、技术实现细节

### 文本清洗流程

```
原始文本
  ↓
(1) 文本规范化（编码、格式、特殊字符）
  ↓
(2) 结构化处理（标题、段落、列表、表格、代码）
  ↓
(3) 内容清理（去噪音、去重、质量评分）
  ↓
(4) 分块优化（语义边界、重叠、大小控制）
  ↓
(5) 元数据提取（来源、作者、时间、标签、统计）
  ↓
清洗后的文档块 + 元数据
```

### 模型选择逻辑

```
检查 RAG_EMBEDDING_MODEL 环境变量
  ↓
如果未设置，根据 RAG_LANGUAGE 选择模型列表
  ↓
尝试加载第一个模型
  ↓
如果失败，尝试备用模型
  ↓
如果都失败，RAG 功能降级（不影响主系统）
```

## 八、注意事项

1. **首次下载模型**：首次使用特定模型时会自动下载（可能需要几分钟到几十分钟）
2. **内存占用**：大模型（如 bge-large）需要更多内存（建议 4GB+）
3. **质量过滤**：低质量文档会被自动过滤，可通过调整阈值控制
4. **分块大小**：建议根据实际文档类型调整，过小会丢失上下文，过大会影响检索精度

## 九、故障排除

### 问题：模型下载失败

**解决方案**：
1. 检查网络连接
2. 使用国内镜像（如果可用）
3. 手动下载模型到本地

### 问题：质量评分过低导致文档被过滤

**解决方案**：
1. 降低 `RAG_QUALITY_THRESHOLD` 阈值
2. 检查文档内容是否确实有意义
3. 优化文档格式（添加标题、段落等）

### 问题：分块效果不理想

**解决方案**：
1. 调整 `RAG_CHUNK_SIZE` 和 `RAG_CHUNK_OVERLAP`
2. 优化文档格式（使用标题、段落分隔）
3. 检查文档是否包含足够的语义边界

---

所有功能已完整实现并集成到系统中，安装依赖后即可使用。

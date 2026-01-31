# RAG 知识库功能使用说明

## 功能概述

RAG (Retrieval-Augmented Generation) 知识库功能已集成到智慧商城系统中，可以为客服系统提供知识库增强，提升回答准确性和专业性。

## 功能特性

### 1. 数据准备与索引构建（离线阶段）

- ✅ **文档加载**：支持从多种来源加载数据
  - 手动输入文本
  - **PDF 文件** (.pdf) - 使用 pdfplumber，可保留表格结构
  - **Word 文档** (.docx) - 使用 python-docx，提取文本和表格
  - **Excel 文件** (.xlsx, .xls) - 使用 pandas，提取所有工作表
  - **文本文件** (.txt, .md, .csv, .log) - 直接读取
  - **图片文件** (.jpg, .jpeg, .png, .bmp, .gif, .webp) - 使用 PaddleOCR 或 pytesseract 进行 OCR
  - **网页内容** - 使用 trafilatura 专业提取
  - **数据库表** - 从 SQLite 数据库表提取数据

- ✅ **文本预处理**（增强版）：
  - **(1) 文本规范化**：
    - 统一编码（UTF-8）
    - 正则表达式去除特殊字符、乱码
    - 标准化日期、货币等格式
  - **(2) 结构化处理**：
    - 提取标题、段落、列表
    - 处理表格数据（转为Markdown或结构化文本）
    - 代码块分离和格式化
  - **(3) 内容清理**：
    - 去除广告、导航栏、页脚等噪音内容
    - 过滤低质量文本（过短、无意义内容）
    - 去重（完全重复和近似重复）
  - **(4) 分块优化**：
    - 按语义边界分块（段落、章节）
    - 重叠分块避免信息割裂
    - 控制分块大小（通常128-512 tokens，可配置）
  - **(5) 元数据提取**：
    - 提取来源、作者、时间等信息
    - 添加文档结构标签
    - 质量评分标注

- ✅ **向量化与索引**：
  - 使用 sentence-transformers 嵌入模型将文本转换为向量
  - **支持多语言模型选择**：
    - 中文：BGE-large-zh, m3e-large
    - 多语言：multilingual-e5, text-embedding-3
    - 英文：text-embedding-ada-002, e5-large
  - 存储至 FAISS 向量数据库，建立高效检索结构
  - 支持索引重建和增量更新

### 2. 检索-增强（Retrieval-Augmented）

- ✅ **查询向量化**：使用与文档相同的嵌入模型将查询转换为向量
- ✅ **相似度检索**：从向量数据库中召回 Top-K 最相关文档块（基于余弦相似度）
- ✅ **上下文注入**：将检索到的文档块作为附加上下文插入 Prompt 模板

### 3. 生成（Generation）

- ✅ **增强生成**：将增强后的 Prompt 注入 Qwen 生成模型，生成最终响应
- ✅ **生成控制**：添加指令约束（"仅基于提供的信息回答"），确保回答准确性

### 4. 管理员管理功能

- ✅ 添加、删除、更新知识库文档
- ✅ 文档分类和标签管理
- ✅ 文档搜索和测试
- ✅ 向量索引重建

## 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

新增依赖：
- `faiss-cpu==1.7.4` - 向量数据库
- `sentence-transformers==2.2.2` - 文本嵌入模型
- `numpy==1.24.3` - 数值计算
- `pdfplumber==0.10.3` - PDF 解析（保留表格）
- `python-docx==1.1.0` - Word 文档解析
- `pandas==2.0.3` - Excel 文件处理
- `openpyxl==3.1.2` - Excel .xlsx 格式支持
- `xlrd==2.0.1` - Excel .xls 格式支持
- `trafilatura==1.6.3` - 网页内容提取
- `paddlepaddle==2.5.2` - PaddleOCR 引擎
- `paddleocr==2.7.0.3` - 图片 OCR 识别

## 环境配置

在 `.env` 文件中添加以下配置（可选）：

```bash
# RAG 配置
RAG_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2  # 或指定具体模型
RAG_LANGUAGE=multilingual   # 语言类型: zh/chinese, en/english, multilingual/multi
RAG_CHUNK_SIZE=500          # 每个块的最大字符数
RAG_CHUNK_OVERLAP=50        # 块之间的重叠字符数
RAG_TOP_K=3                 # 检索 Top-K 相关文档
RAG_MIN_CHUNK_LENGTH=20     # 最小块长度（字符）
RAG_MAX_CHUNK_LENGTH=2000   # 最大块长度（字符）
RAG_QUALITY_THRESHOLD=0.3   # 质量评分阈值（低于此值的文档会被过滤）
```

## API 接口

### 管理员接口（需要 Basic 认证）

#### 1. 创建文档

```http
POST /knowledge-base/documents
Content-Type: application/json
Authorization: Basic <base64(admin:password)>

{
  "title": "商品退换货政策",
  "content": "商品支持7天无理由退换货...",
  "source_type": "manual",
  "category": "售后政策",
  "tags": "退换货,政策"
}
```

#### 2. 上传文档文件

```http
POST /knowledge-base/documents/upload
Content-Type: multipart/form-data
Authorization: Basic <base64(admin:password)>

file: <文件>
title: 可选标题
category: 可选分类
tags: 可选标签
```

**支持的文件格式**：
- **PDF** (.pdf) - 使用 pdfplumber，可保留表格结构
- **Word** (.docx) - 使用 python-docx，提取文本和表格
- **Excel** (.xlsx, .xls) - 使用 pandas，提取所有工作表数据
- **文本** (.txt, .md, .csv, .log) - 直接读取
- **图片** (.jpg, .jpeg, .png, .bmp, .gif, .webp) - 使用 PaddleOCR 或 pytesseract 进行 OCR 识别

#### 2.1. 从网页 URL 导入

```http
POST /knowledge-base/documents/from-url
Content-Type: application/json
Authorization: Basic <base64(admin:password)>

{
  "url": "https://example.com/article",
  "title": "可选标题",
  "category": "可选分类",
  "tags": "可选标签"
}
```

使用 trafilatura 专业网页提取工具，自动提取网页正文内容。

#### 2.2. 从数据库表导入

```http
POST /knowledge-base/documents/from-database
Content-Type: application/json
Authorization: Basic <base64(admin:password)>

{
  "table_name": "products",
  "columns": ["name", "description", "price"],  // 可选，不指定则提取所有列
  "limit": 1000,  // 可选，默认1000行
  "title": "可选标题",
  "category": "可选分类",
  "tags": "可选标签"
}
```

从数据库表中提取数据并转换为文本格式。

#### 3. 获取文档列表

```http
GET /knowledge-base/documents?category=售后政策&active=true
Authorization: Basic <base64(admin:password)>
```

#### 4. 更新文档

```http
PUT /knowledge-base/documents/{document_id}
Content-Type: application/json
Authorization: Basic <base64(admin:password)>

{
  "title": "更新后的标题",
  "content": "更新后的内容...",
  "active": true
}
```

#### 5. 删除文档

```http
DELETE /knowledge-base/documents/{document_id}
Authorization: Basic <base64(admin:password)>
```

#### 6. 搜索知识库（测试）

```http
POST /knowledge-base/search?query=退换货政策&top_k=5
Authorization: Basic <base64(admin:password)>
```

#### 7. 重建向量索引

```http
POST /knowledge-base/rebuild-index
Authorization: Basic <base64(admin:password)>
```

## 使用流程

### 步骤 1：添加知识库文档

1. 登录管理员后台：`http://localhost:5173/admin`
2. 访问知识库管理界面（需要前端支持）
3. 或直接使用 API 添加文档：

```bash
curl -X POST "http://localhost:8000/knowledge-base/documents" \
  -H "Authorization: Basic YWRtaW46MTIzNDU2" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "商品退换货政策",
    "content": "本商城支持7天无理由退换货。商品需保持原包装完好，不影响二次销售。",
    "category": "售后政策",
    "tags": "退换货,政策"
  }'
```

### 步骤 2：自动集成到客服系统

RAG 功能已自动集成到客服系统中。当用户提问时：

1. 系统自动从知识库检索相关文档
2. 将检索到的内容作为上下文注入到 Qwen 模型
3. 模型基于知识库信息生成回答

### 步骤 3：测试效果

1. 在客服聊天界面提问相关问题
2. 系统会自动检索知识库并基于知识库信息回答
3. 在管理员界面可以测试搜索功能

## 技术架构

### 数据模型

- `KnowledgeDocument` - 知识库文档表
- `KnowledgeChunk` - 文档块表（用于向量化存储）

### 服务模块

- `RAGService` - RAG 核心服务类
  - 文档预处理和分块
  - 文本向量化
  - 向量索引管理
  - 相似度检索

### 集成点

- `customer_service.py` - 在 `chat()` 函数中集成 RAG 检索
- `knowledge_base_route.py` - 知识库管理 API 路由

## 性能优化建议

1. **索引优化**：
   - 定期重建索引（删除文档后）
   - 使用更高效的 FAISS 索引类型（如 IVF）

2. **检索优化**：
   - 调整 `RAG_TOP_K` 参数（默认 3）
   - 使用分类筛选减少检索范围

3. **分块优化**：
   - 根据文档类型调整 `RAG_CHUNK_SIZE`
   - 长文档使用较小的块，短文档使用较大的块

## 故障排除

### 问题 1：RAG 功能不工作

**检查项**：
1. 确认已安装依赖：`pip install faiss-cpu sentence-transformers`
2. 检查嵌入模型是否加载成功（查看启动日志）
3. 确认知识库中有文档

### 问题 2：检索结果不准确

**解决方案**：
1. 增加知识库文档数量
2. 优化文档内容（更清晰、更具体）
3. 调整检索 Top-K 数量
4. 使用分类筛选

### 问题 3：向量索引损坏

**解决方案**：
```bash
# 调用重建索引接口
POST /knowledge-base/rebuild-index
```

## 扩展功能

### 未来可扩展的功能

1. **混合检索**：结合关键词检索（BM25）提升召回率
2. **多模态支持**：支持图片、表格等多媒体内容
3. **增量更新**：支持文档增量更新而不重建整个索引
4. **版本管理**：文档版本控制和历史记录
5. **统计分析**：检索命中率、用户反馈等统计

## 嵌入模型选择

系统支持根据语言类型自动选择最适合的嵌入模型：

### 中文模型
- `BAAI/bge-large-zh-v1.5` - 百度 BGE 大模型（推荐，中文效果最佳）
- `moka-ai/m3e-large` - M3E 大模型（中文专用）

### 多语言模型
- `intfloat/multilingual-e5-large` - 多语言 E5 大模型（推荐）
- `text-embedding-3-large` - OpenAI 兼容模型

### 英文模型
- `text-embedding-ada-002` - OpenAI Ada 模型
- `intfloat/e5-large-v2` - E5 大模型（英文专用）

### 配置方式

**方式一：通过环境变量指定语言类型（自动选择模型）**
```bash
RAG_LANGUAGE=zh  # 或 chinese, en, english, multilingual, multi
```

**方式二：直接指定模型名称**
```bash
RAG_EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
```

系统会优先使用指定的模型，如果加载失败会自动尝试备用模型。

## 注意事项

1. **首次使用**：首次启动时会自动下载嵌入模型（约 400MB-2GB 取决于模型），需要网络连接
2. **内存占用**：向量索引和模型会占用一定内存，建议服务器至少 4GB 内存（大模型需要更多）
3. **索引文件**：向量索引保存在 `backend/knowledge_base_index.faiss`，请定期备份
4. **模型选择**：根据主要使用语言选择模型，中文内容推荐使用 BGE-large-zh
5. **质量过滤**：质量评分低于阈值的文档会被自动过滤，可通过 `RAG_QUALITY_THRESHOLD` 调整

## 示例场景

### 场景 1：添加商品政策文档

```json
{
  "title": "商品退换货政策",
  "content": "1. 支持7天无理由退换货\n2. 商品需保持原包装\n3. 退换货流程：...",
  "category": "售后政策",
  "tags": "退换货,政策,售后"
}
```

### 场景 2：上传产品手册 PDF

使用文件上传接口上传 PDF 文件，系统会自动提取文本并建立索引。

### 场景 3：用户提问

用户：`"你们的退换货政策是什么？"`

系统自动：
1. 检索知识库中关于"退换货政策"的文档
2. 将检索到的内容注入到 Qwen 模型
3. 生成基于知识库的准确回答

---

如有问题，请查看日志或联系技术支持。

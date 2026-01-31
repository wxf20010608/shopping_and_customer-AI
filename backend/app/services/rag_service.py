"""
RAG (Retrieval-Augmented Generation) 知识库服务
实现文档加载、预处理、向量化、检索和生成增强功能
"""
from __future__ import annotations

import os
import json
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
from sqlalchemy.orm import Session

from ..models import KnowledgeDocument, KnowledgeChunk
from ..utils import load_env
from .text_cleaner import get_text_cleaner

# 向量数据库和嵌入模型
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

# BM25 关键词检索
try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    BM25Okapi = None

# 中文分词
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    jieba = None


class RAGService:
    """RAG 知识库服务类"""
    
    def __init__(self):
        load_env()
        self.embedding_model = None
        self.vector_index = None
        self.vector_dim = 384  # 默认向量维度
        self.index_path = Path(__file__).resolve().parent.parent.parent / "knowledge_base_index.faiss"
        self.chunk_size = int(os.environ.get("RAG_CHUNK_SIZE", "500"))  # 每个块的最大字符数
        self.chunk_overlap = int(os.environ.get("RAG_CHUNK_OVERLAP", "50"))  # 块之间的重叠字符数
        self.top_k = int(os.environ.get("RAG_TOP_K", "5"))  # 检索 Top-K 相关文档（增加到5以提高召回率）
        self.text_cleaner = get_text_cleaner()
        # BM25相关
        self.bm25_index = None  # BM25索引
        self.bm25_chunk_texts = []  # 存储所有块的文本（用于BM25检索）
        self.bm25_chunk_map = {}  # 映射：BM25索引 -> vector_id
        self.use_hybrid_search = os.environ.get("RAG_USE_HYBRID_SEARCH", "true").lower() == "true"  # 是否使用混合检索
        self.hybrid_weight_vector = float(os.environ.get("RAG_HYBRID_WEIGHT_VECTOR", "0.7"))  # 向量检索权重
        self.hybrid_weight_bm25 = float(os.environ.get("RAG_HYBRID_WEIGHT_BM25", "0.3"))  # BM25检索权重
        self._initialize_embedding_model()
        self._load_vector_index()
    
    def _initialize_embedding_model(self, language: Optional[str] = None):
        """
        初始化嵌入模型
        支持根据语言类型选择不同的模型
        
        参数:
        - language: 语言类型 ('zh'/'chinese', 'en'/'english', 'multilingual'/'multi')
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            print("警告: sentence-transformers 未安装，RAG 功能将受限")
            return
        
        # 嵌入模型映射
        models = {
            'zh': ['BAAI/bge-large-zh-v1.5', 'moka-ai/m3e-large'],
            'chinese': ['BAAI/bge-large-zh-v1.5', 'moka-ai/m3e-large'],
            'multilingual': ['intfloat/multilingual-e5-large', 'text-embedding-3-large'],
            'multi': ['intfloat/multilingual-e5-large', 'text-embedding-3-large'],
            'en': ['text-embedding-ada-002', 'intfloat/e5-large-v2'],
            'english': ['text-embedding-ada-002', 'intfloat/e5-large-v2']
        }
        
        # 确定语言类型
        if not language:
            language = os.environ.get("RAG_LANGUAGE", "multilingual").lower()
        
        # 获取模型列表
        model_list = models.get(language, models['multilingual'])
        
        # 从环境变量或模型列表中选择模型
        model_name = os.environ.get("RAG_EMBEDDING_MODEL")
        if not model_name:
            # 使用列表中的第一个模型
            model_name = model_list[0]
        
        # 如果模型已经加载，跳过重新加载
        if self.embedding_model is not None:
            print(f"ℹ️ 嵌入模型已存在，跳过重新加载: {model_name}")
            return
        
        try:
            print(f"📥 开始加载嵌入模型: {model_name}...")
            self.embedding_model = SentenceTransformer(model_name)
            # 获取模型维度
            test_embedding = self.embedding_model.encode(["test"])
            self.vector_dim = test_embedding.shape[1]
            print(f"✓ 嵌入模型已加载: {model_name}, 维度: {self.vector_dim}, 语言: {language}")
        except Exception as e:
            print(f"⚠ 加载嵌入模型失败: {e}")
            # 尝试使用备用模型
            if len(model_list) > 1:
                try:
                    model_name = model_list[1]
                    self.embedding_model = SentenceTransformer(model_name)
                    test_embedding = self.embedding_model.encode(["test"])
                    self.vector_dim = test_embedding.shape[1]
                    print(f"✓ 使用备用嵌入模型: {model_name}, 维度: {self.vector_dim}")
                except Exception as e2:
                    print(f"⚠ 备用模型也加载失败: {e2}")
                    self.embedding_model = None
            else:
                self.embedding_model = None
    
    def _load_vector_index(self):
        """加载或创建向量索引"""
        if not FAISS_AVAILABLE:
            print("警告: FAISS 未安装，向量索引功能将不可用")
            return
        
        try:
            if self.index_path.exists():
                self.vector_index = faiss.read_index(str(self.index_path))
                print(f"✓ 向量索引已加载: {self.vector_index.ntotal} 个向量")
            else:
                # 创建新的索引
                self.vector_index = faiss.IndexFlatL2(self.vector_dim)
                print("✓ 创建新的向量索引")
        except Exception as e:
            print(f"⚠ 加载向量索引失败: {e}")
            if self.vector_index is None:
                self.vector_index = faiss.IndexFlatL2(self.vector_dim)
    
    def _save_vector_index(self):
        """保存向量索引到文件"""
        if not FAISS_AVAILABLE or self.vector_index is None:
            return
        
        try:
            faiss.write_index(self.vector_index, str(self.index_path))
        except Exception as e:
            print(f"⚠ 保存向量索引失败: {e}")
    
    def _tokenize_chinese(self, text: str) -> List[str]:
        """中文分词（用于BM25）"""
        if not text:
            return []
        
        if JIEBA_AVAILABLE:
            # 使用jieba分词
            return list(jieba.cut(text))
        else:
            # 简单的中文分词：按字符分割（对于中文，每个字符通常是一个词）
            # 同时保留英文单词
            import re
            # 分离中文字符和英文单词
            chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
            english_words = re.findall(r'[a-zA-Z]+', text)
            return chinese_chars + english_words
    
    def _build_bm25_index(self, db: Optional[Session] = None):
        """构建BM25索引（从数据库加载所有块）"""
        if not BM25_AVAILABLE:
            return
        
        if db is None:
            # 延迟构建，需要时再构建
            return
        
        try:
            # 从数据库加载所有活跃的块（使用明确的join条件）
            chunks = db.query(KnowledgeChunk).join(
                KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id
            ).filter(
                KnowledgeDocument.active == True
            ).order_by(KnowledgeChunk.vector_id.asc()).all()
            
            if not chunks:
                self.bm25_index = None
                self.bm25_chunk_texts = []
                self.bm25_chunk_map = {}
                return
            
            # 构建BM25索引
            self.bm25_chunk_texts = []
            self.bm25_chunk_map = {}
            
            for chunk in chunks:
                if chunk.vector_id is not None:
                    # 分词处理
                    tokenized = self._tokenize_chinese(chunk.content)
                    self.bm25_chunk_texts.append(tokenized)
                    self.bm25_chunk_map[len(self.bm25_chunk_texts) - 1] = chunk.vector_id
            
            if self.bm25_chunk_texts:
                self.bm25_index = BM25Okapi(self.bm25_chunk_texts)
                print(f"✓ BM25索引已构建: {len(self.bm25_chunk_texts)} 个文档块")
            else:
                self.bm25_index = None
        except Exception as e:
            print(f"⚠ 构建BM25索引失败: {e}")
            import traceback
            traceback.print_exc()
            self.bm25_index = None
    
    def search_bm25(self, query: str, top_k: Optional[int] = None, category: Optional[str] = None) -> List[Dict]:
        """
        BM25关键词检索
        
        参数:
        - query: 查询文本
        - top_k: 返回的Top-K结果数量
        - category: 分类筛选（可选，需要在后续步骤中处理）
        
        返回:
        - List[Dict]: 包含 vector_id, bm25_score 的结果列表，按BM25分数降序排列
        """
        if not BM25_AVAILABLE or self.bm25_index is None:
            return []
        
        if not query or not query.strip():
            return []
        
        top_k = top_k or self.top_k
        
        try:
            # 对查询文本进行分词
            query_tokens = self._tokenize_chinese(query.strip())
            if not query_tokens:
                return []
            
            # BM25检索
            scores = self.bm25_index.get_scores(query_tokens)
            
            # 构建结果列表
            results = []
            for idx, score in enumerate(scores):
                vector_id = self.bm25_chunk_map.get(idx)
                if vector_id is not None and score > 0:  # 只保留分数大于0的结果
                    results.append({
                        "vector_id": int(vector_id),
                        "bm25_score": float(score)
                    })
            
            # 按BM25分数降序排序
            results.sort(key=lambda x: x["bm25_score"], reverse=True)
            
            # 返回Top-K
            return results[:top_k * 2]  # 返回更多候选，用于混合检索
            
        except Exception as e:
            print(f"⚠ BM25检索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def preprocess_text(self, text: str) -> str:
        """
        文本预处理：使用增强的文本清洗器
        (1) 文本规范化
        (2) 结构化处理
        (3) 内容清理
        """
        if not text:
            return ""
        
        # 使用文本清洗器进行规范化
        normalized = self.text_cleaner.normalize_text(text)
        
        # 结构化处理
        structured = self.text_cleaner.extract_structure(normalized)
        
        # 内容清理
        cleaned, quality_info = self.text_cleaner.clean_content(structured["text"])
        
        return cleaned
    
    def chunk_text(self, text: str, chunk_size: Optional[int] = None, overlap: Optional[int] = None) -> List[Dict[str, any]]:
        """
        将文本分块处理（使用优化的分块策略）
        (4) 分块优化：按语义边界分块、重叠分块、控制大小
        """
        if not text:
            return []
        
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap
        
        # 使用优化的分块方法
        chunks = self.text_cleaner.chunk_text_optimized(text, chunk_size, overlap)
        
        return chunks
    
    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """将文本转换为向量"""
        if not self.embedding_model or not text:
            return None
        
        try:
            embedding = self.embedding_model.encode([text], normalize_embeddings=True)[0]
            return embedding.astype('float32')
        except Exception as e:
            print(f"⚠ 文本向量化失败: {e}")
            return None
    
    def embed_texts(self, texts: List[str]) -> Optional[np.ndarray]:
        """
        批量将文本转换为向量
        支持字符串列表或字典列表（从字典中提取 content）
        """
        if not self.embedding_model or not texts:
            return None
        
        # 如果是字典列表，提取 content 字段
        if texts and isinstance(texts[0], dict):
            texts = [item.get("content", "") if isinstance(item, dict) else str(item) for item in texts]
        
        try:
            embeddings = self.embedding_model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return embeddings.astype('float32')
        except Exception as e:
            print(f"⚠ 批量文本向量化失败: {e}")
            return None
    
    def add_document(self, db: Session, title: str, content: str, source_type: str = "manual", 
                     source_url: Optional[str] = None, category: Optional[str] = None,
                     tags: Optional[str] = None) -> KnowledgeDocument:
        """
        添加文档到知识库（数据准备阶段）
        
        完整流程：
        1. 文本预处理（规范化、结构化、清理、分块、元数据提取）
        2. 向量化（使用嵌入模型将文本块转换为向量）
        3. 存储到向量数据库（FAISS）
        4. 存储到关系数据库（SQLite）
        
        参数:
        - db: 数据库会话
        - title: 文档标题
        - content: 文档内容
        - source_type: 来源类型（manual, pdf, web, api, database）
        - source_url: 来源URL
        - category: 分类
        - tags: 标签
        
        返回:
        - KnowledgeDocument: 创建的文档对象
        """
        # ========== 步骤1：文本预处理（5个子步骤）==========
        
        # (1) 文本规范化
        normalized_content = self.text_cleaner.normalize_text(content)
        if not normalized_content:
            raise ValueError("文档内容为空或清洗后为空")
        
        # (2) 结构化处理
        structured = self.text_cleaner.extract_structure(normalized_content)
        
        # (3) 内容清理
        cleaned_content, quality_info = self.text_cleaner.clean_content(structured["text"])
        if not cleaned_content:
            raise ValueError(f"文档质量评分过低 ({quality_info.get('quality_score', 0):.2f})，已过滤")
        
        # (5) 元数据提取
        metadata = self.text_cleaner.extract_metadata(cleaned_content, source_url)
        metadata["quality_score"] = quality_info.get("quality_score", 0.0)
        metadata_json = json.dumps(metadata, ensure_ascii=False)
        
        # (4) 分块优化
        chunk_data = self.chunk_text(cleaned_content)
        if not chunk_data:
            raise ValueError("文档分块失败")
        
        # 提取块内容列表（用于向量化）
        chunk_contents = [chunk["content"] for chunk in chunk_data]
        
        # ========== 步骤2：存储文档到数据库 ==========
        # 创建文档记录
        doc = KnowledgeDocument(
            title=title,
            content=cleaned_content,  # 存储清洗后的内容
            source_type=source_type,
            source_url=source_url,
            category=category,
            tags=tags,
            chunk_count=len(chunk_data),
            document_metadata=metadata_json,  # 存储元数据
            quality_score=metadata["quality_score"]  # 存储质量评分
        )
        db.add(doc)
        db.flush()
        
        # ========== 步骤3：向量化与索引构建 ==========
        SYNTHETIC_OFFSET = 1000000  # 向量化失败时使用的合成 ID 前缀，避免与 FAISS 冲突
        chunks_created = False
        
        if self.embedding_model and FAISS_AVAILABLE and self.vector_index is not None:
            # 3.1 批量向量化（使用嵌入模型将文本块转换为向量）
            embeddings = self.embed_texts(chunk_contents)
            if embeddings is not None:
                start_id = self.vector_index.ntotal
                
                # 3.2 添加到FAISS向量索引（用于快速相似度检索）
                self.vector_index.add(embeddings)
                
                # 3.3 创建块记录并存储到数据库（包含向量ID映射）
                for i, (chunk_info, embedding) in enumerate(zip(chunk_data, embeddings)):
                    # 块元数据
                    chunk_metadata = {
                        "title": chunk_info.get("title"),
                        "type": chunk_info.get("type", "paragraph"),
                        "chunk_index": chunk_info.get("chunk_index", i)
                    }
                    
                    chunk_record = KnowledgeChunk(
                        document_id=doc.id,
                        chunk_index=i,
                        content=chunk_info["content"],
                        chunk_metadata=json.dumps(chunk_metadata, ensure_ascii=False),
                        vector_id=start_id + i  # 存储向量ID，用于检索时映射
                    )
                    db.add(chunk_record)
                    chunks_created = True
                
                print(f"  → 已向量化并存储到FAISS索引（向量ID: {start_id}-{start_id + len(chunk_data) - 1}）")
            else:
                print(f"  → 向量化失败，将仅创建 chunks 供 BM25 检索")
        
        # 向量化失败或无嵌入模型时：仍创建 chunks，使用合成 vector_id 供 BM25 检索
        if not chunks_created:
            for i, chunk_info in enumerate(chunk_data):
                chunk_metadata = {
                    "title": chunk_info.get("title"),
                    "type": chunk_info.get("type", "paragraph"),
                    "chunk_index": chunk_info.get("chunk_index", i)
                }
                synthetic_id = SYNTHETIC_OFFSET + doc.id * 10000 + i
                chunk_record = KnowledgeChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    content=chunk_info["content"],
                    chunk_metadata=json.dumps(chunk_metadata, ensure_ascii=False),
                    vector_id=synthetic_id  # 合成 ID，仅用于 BM25 检索
                )
                db.add(chunk_record)
        
        # 3.4 提交数据库事务
        db.commit()
        db.refresh(doc)
        
        # 3.5 保存向量索引到文件（持久化）
        self._save_vector_index()
        
        # 3.6 重建BM25索引（如果启用混合检索）
        if self.use_hybrid_search and BM25_AVAILABLE:
            self._build_bm25_index(db)
        
        print(f"✓ 文档已添加: {title}, 块数: {len(chunk_data)}, 质量评分: {metadata['quality_score']:.2f}")
        
        return doc
    
    def search(self, query: str, top_k: Optional[int] = None, category: Optional[str] = None, 
               similarity_threshold: float = 0.15) -> List[Dict]:  # 降低默认阈值以提高召回率
        """
        检索相关文档块（使用余弦相似度）
        
        参数:
        - query: 查询文本
        - top_k: 返回的Top-K结果数量
        - category: 分类筛选（可选）
        - similarity_threshold: 相似度阈值（0-1），低于此值的结果会被过滤
        
        返回:
        - List[Dict]: 包含 vector_id, distance, similarity 的结果列表，按相似度降序排列
        """
        if not self.embedding_model or not FAISS_AVAILABLE or self.vector_index is None:
            return []
        
        if not query or not query.strip():
            return []
        
        top_k = top_k or self.top_k
        
        # 向量化查询（使用与文档相同的嵌入模型）
        query_embedding = self.embed_text(query.strip())
        if query_embedding is None:
            return []
        
        # 向量索引为空时直接返回，避免 FAISS 的 assert k > 0 报错
        if self.vector_index.ntotal == 0:
            return []
        
        # 检查维度是否匹配（旧索引可能由不同嵌入模型创建）
        if self.vector_index.d != query_embedding.shape[0]:
            print(f"⚠ 向量维度不匹配：索引 {self.vector_index.d} vs 查询 {query_embedding.shape[0]}，跳过向量检索")
            return []
        
        # 搜索向量索引（使用L2距离，后续转换为余弦相似度）
        query_embedding = query_embedding.reshape(1, -1)
        max_results = min(top_k * 3, self.vector_index.ntotal)  # 多检索一些，用于后续筛选（从2倍增加到3倍以提高召回率）
        distances, indices = self.vector_index.search(query_embedding, max_results)
        
        # 计算余弦相似度（FAISS使用L2距离，需要转换为余弦相似度）
        # 对于归一化的向量，L2距离和余弦距离的关系：cosine_sim = 1 - (L2_distance^2 / 2)
        # 或者使用：similarity = 1 / (1 + distance)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0:  # FAISS 返回 -1 表示无效
                continue
            
            # 转换为相似度分数（0-1，1表示最相似）
            # 对于L2距离，使用更精确的转换：对于归一化向量，cosine_sim ≈ 1 - distance^2/2
            # 但考虑到实际使用，使用更宽松的转换以提高召回率
            if dist <= 0:
                similarity = 1.0
            else:
                # 使用更宽松的转换公式，降低阈值要求
                similarity = float(1 / (1 + dist * 0.5))  # 调整系数以提高相似度分数
            
            # 应用相似度阈值过滤
            if similarity < similarity_threshold:
                continue
            
            results.append({
                "vector_id": int(idx),
                "distance": float(dist),
                "similarity": similarity
            })
        
        # 按相似度降序排序（最相似的在前面）
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # 返回Top-K
        return results[:top_k]
    
    def retrieve_context(self, db: Session, query: str, top_k: Optional[int] = None, 
                        category: Optional[str] = None, similarity_threshold: float = 0.3) -> Tuple[str, List[Dict]]:
        """
        检索并返回上下文文本（RAG检索增强的核心方法）
        
        参数:
        - db: 数据库会话
        - query: 用户查询文本
        - top_k: 返回的Top-K相关块
        - category: 分类筛选（可选）
        - similarity_threshold: 相似度阈值，低于此值的结果会被过滤
        
        返回:
        - Tuple[str, List[Dict]]: (上下文文本, 检索结果详情)
        """
        # 步骤1：混合检索（向量检索 + BM25关键词检索）
        # 确保BM25索引已构建（如果启用混合检索）
        if self.use_hybrid_search and BM25_AVAILABLE and self.bm25_index is None:
            self._build_bm25_index(db)
        
        # 1.1 向量检索（语义相似度）
        initial_threshold = max(0.1, similarity_threshold * 0.6)  # 使用更低的初始阈值
        expanded_top_k = top_k * 3  # 检索更多候选结果
        
        vector_results = self.search(query, expanded_top_k, category, initial_threshold)
        
        if not vector_results:
            # 如果初始检索没有结果，尝试进一步降低阈值
            vector_results = self.search(query, expanded_top_k, category, 0.05)
        
        # 1.2 BM25关键词检索（如果启用混合检索）
        bm25_results = []
        if self.use_hybrid_search and BM25_AVAILABLE:
            # 确保BM25索引已构建
            if self.bm25_index is None:
                self._build_bm25_index(db)
            
            if self.bm25_index is not None:
                bm25_results = self.search_bm25(query, expanded_top_k, category)
                print(f"✓ BM25检索: 找到 {len(bm25_results)} 个候选结果")
        
        # 1.3 合并和重排序结果
        if not vector_results and not bm25_results:
            return "", []
        
        # 归一化分数并合并结果
        combined_results = {}
        # 保存原始向量检索结果，用于后续获取distance字段
        vector_results_map = {r["vector_id"]: r for r in vector_results}
        
        # 处理向量检索结果
        if vector_results:
            # 归一化相似度分数到0-1范围
            max_sim = max([r["similarity"] for r in vector_results], default=1.0)
            min_sim = min([r["similarity"] for r in vector_results], default=0.0)
            sim_range = max_sim - min_sim if max_sim > min_sim else 1.0
            
            for r in vector_results:
                vector_id = r["vector_id"]
                # 归一化相似度
                normalized_sim = (r["similarity"] - min_sim) / sim_range if sim_range > 0 else r["similarity"]
                combined_results[vector_id] = {
                    "vector_id": vector_id,
                    "vector_score": normalized_sim * self.hybrid_weight_vector,
                    "bm25_score": 0.0,
                    "combined_score": normalized_sim * self.hybrid_weight_vector,
                    "distance": r.get("distance", 0.0)  # 保留原始distance字段
                }
        
        # 处理BM25检索结果
        if bm25_results:
            # 归一化BM25分数到0-1范围
            max_bm25 = max([r["bm25_score"] for r in bm25_results], default=1.0)
            min_bm25 = min([r["bm25_score"] for r in bm25_results], default=0.0)
            bm25_range = max_bm25 - min_bm25 if max_bm25 > min_bm25 else 1.0
            
            for r in bm25_results:
                vector_id = r["vector_id"]
                # 归一化BM25分数
                normalized_bm25 = (r["bm25_score"] - min_bm25) / bm25_range if bm25_range > 0 else r["bm25_score"]
                
                if vector_id in combined_results:
                    # 合并分数
                    combined_results[vector_id]["bm25_score"] = normalized_bm25 * self.hybrid_weight_bm25
                    combined_results[vector_id]["combined_score"] += normalized_bm25 * self.hybrid_weight_bm25
                else:
                    # 新结果（从BM25检索中获取，可能没有distance字段）
                    original_vector_result = vector_results_map.get(vector_id, {})
                    combined_results[vector_id] = {
                        "vector_id": vector_id,
                        "vector_score": 0.0,
                        "bm25_score": normalized_bm25 * self.hybrid_weight_bm25,
                        "combined_score": normalized_bm25 * self.hybrid_weight_bm25,
                        "distance": original_vector_result.get("distance", 0.0)  # 如果向量检索中有，则使用
                    }
        
        # 按综合分数排序
        search_results = sorted(combined_results.values(), key=lambda x: x["combined_score"], reverse=True)
        
        # 取top_k个结果
        search_results = search_results[:top_k]
        
        # 转换为原有格式（兼容性）
        final_results = []
        for r in search_results:
            final_results.append({
                "vector_id": r["vector_id"],
                "similarity": r["combined_score"],  # 使用综合分数作为相似度
                "vector_score": r["vector_score"],
                "bm25_score": r["bm25_score"],
                "distance": r.get("distance", 0.0)  # 保留distance字段（如果存在）
            })
        
        search_results = final_results
        
        if search_results:
            print(f"✓ 混合检索完成: 向量检索 {len(vector_results)} 个，BM25检索 {len(bm25_results)} 个，合并后 {len(search_results)} 个")
        
        # 步骤2：从数据库获取块内容
        vector_ids = [r["vector_id"] for r in search_results]
        chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.vector_id.in_(vector_ids),
            KnowledgeChunk.document_id.in_(
                db.query(KnowledgeDocument.id).filter(KnowledgeDocument.active == True)
            )
        ).all()
        
        # 如果指定了分类，进一步筛选
        if category:
            doc_ids = [d.id for d in db.query(KnowledgeDocument.id).filter(
                KnowledgeDocument.category == category,
                KnowledgeDocument.active == True
            ).all()]
            chunks = [c for c in chunks if c.document_id in doc_ids]
        
        # 步骤3：按相似度排序并组合上下文
        chunk_dict = {c.vector_id: c for c in chunks}
        context_parts = []
        result_details = []
        
        for result in search_results:
            chunk = chunk_dict.get(result["vector_id"])
            if chunk:
                # 获取文档信息
                doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == chunk.document_id).first()
                doc_title = doc.title if doc else f"文档#{chunk.document_id}"
                
                # 构建上下文片段（移除相似度标注，避免干扰AI判断）
                context_parts.append(chunk.content)
                
                # 保存结果详情
                result_details.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_title": doc_title,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "similarity": result["similarity"],
                    "distance": result.get("distance", 0.0),  # 混合检索可能没有distance字段
                    "vector_score": result.get("vector_score", 0.0),
                    "bm25_score": result.get("bm25_score", 0.0)
                })
        
        context_text = "\n\n".join(context_parts)
        return context_text, result_details
    
    def delete_document(self, db: Session, document_id: int):
        """删除文档（需要重建索引）"""
        doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()
        if not doc:
            return
        
        # 获取所有块的向量 ID
        chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == document_id).all()
        vector_ids = [c.vector_id for c in chunks if c.vector_id is not None]
        
        # 删除块记录
        db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == document_id).delete()
        
        # 删除文档
        db.delete(doc)
        db.commit()
        
        # 重建索引（删除操作较复杂，这里简化处理：重建整个索引）
        self._rebuild_index(db)
        
        # 重建BM25索引
        if self.use_hybrid_search and BM25_AVAILABLE:
            self._build_bm25_index(db)
    
    def _rebuild_index(self, db: Session):
        """重建向量索引"""
        if not FAISS_AVAILABLE or not self.embedding_model:
            return
        
        # 获取所有活跃文档的块（使用明确的join条件）
        chunks = db.query(KnowledgeChunk).join(
            KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id
        ).filter(
            KnowledgeDocument.active == True
        ).order_by(KnowledgeChunk.document_id, KnowledgeChunk.chunk_index).all()
        
        if not chunks:
            self.vector_index = faiss.IndexFlatL2(self.vector_dim)
            self._save_vector_index()
            return
        
        # 重新向量化（chunks 是字符串列表）
        texts = [c.content for c in chunks]
        embeddings = self.embed_texts(texts)
        
        if embeddings is not None:
            # 创建新索引
            self.vector_index = faiss.IndexFlatL2(self.vector_dim)
            self.vector_index.add(embeddings)
            
            # 更新向量 ID
            for i, chunk in enumerate(chunks):
                chunk.vector_id = i
            db.commit()
            
            self._save_vector_index()
            print(f"✓ 向量索引已重建: {len(chunks)} 个块")
            
            # 重建BM25索引
            if self.use_hybrid_search and BM25_AVAILABLE:
                self._build_bm25_index(db)
    
    def rebuild_chunks_for_documents_without_chunks(self, db: Session) -> int:
        """
        为没有 chunks 的文档重建 chunks（向量化失败时仍创建 chunks 供 BM25 检索）
        返回处理的文档数量
        """
        SYNTHETIC_OFFSET = 1000000
        docs = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.active == True,
            KnowledgeDocument.content.isnot(None),
            KnowledgeDocument.content != ""
        ).all()
        count = 0
        for doc in docs:
            chunk_count = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == doc.id).count()
            if chunk_count > 0:
                continue
            try:
                chunk_data = self.chunk_text(doc.content)
                if not chunk_data:
                    continue
                for i, chunk_info in enumerate(chunk_data):
                    synthetic_id = SYNTHETIC_OFFSET + doc.id * 10000 + i
                    chunk_record = KnowledgeChunk(
                        document_id=doc.id,
                        chunk_index=i,
                        content=chunk_info["content"],
                        chunk_metadata=json.dumps({
                            "title": chunk_info.get("title"),
                            "type": chunk_info.get("type", "paragraph"),
                            "chunk_index": chunk_info.get("chunk_index", i)
                        }, ensure_ascii=False),
                        vector_id=synthetic_id
                    )
                    db.add(chunk_record)
                doc.chunk_count = len(chunk_data)
                count += 1
                print(f"  → 已为文档 #{doc.id}《{doc.title}》重建 {len(chunk_data)} 个 chunks")
            except Exception as e:
                print(f"⚠ 文档 #{doc.id} 重建 chunks 失败: {e}")
        if count > 0:
            db.commit()
            if self.use_hybrid_search and BM25_AVAILABLE:
                self._build_bm25_index(db)
            print(f"✓ 已为 {count} 个文档重建 chunks")
        return count


# 全局 RAG 服务实例
_rag_service: Optional[RAGService] = None


def is_rag_ready() -> bool:
    """检查 RAG 服务是否已准备好（模型已加载）"""
    global _rag_service
    if _rag_service is None:
        return False
    return _rag_service.embedding_model is not None


def get_rag_service() -> RAGService:
    """获取 RAG 服务实例（单例模式）"""
    global _rag_service
    if _rag_service is None:
        print("🔄 创建新的 RAG 服务实例（首次初始化）")
        _rag_service = RAGService()
    else:
        print("♻️ 使用现有的 RAG 服务实例（单例模式）")
    return _rag_service

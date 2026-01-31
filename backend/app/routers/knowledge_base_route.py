"""
知识库管理路由（管理员接口）
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import os
import secrets

from ..database import get_db
from .. import schemas
from ..services.rag_service import get_rag_service
from ..models import KnowledgeDocument, KnowledgeChunk
from ..admin_router import verify_admin

router = APIRouter(prefix="/admin/knowledge-base", tags=["knowledge-base"])


@router.post("/documents", response_model=schemas.KnowledgeDocumentRead, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: schemas.KnowledgeDocumentCreate,
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """创建知识库文档"""
    try:
        rag_service = get_rag_service()
        doc = rag_service.add_document(
            db=db,
            title=payload.title,
            content=payload.content,
            source_type=payload.source_type,
            source_url=payload.source_url,
            category=payload.category,
            tags=payload.tags
        )
        return doc
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建文档失败: {str(e)}")


@router.get("/documents", response_model=List[schemas.KnowledgeDocumentRead])
def list_documents(
    category: Optional[str] = Query(None, description="分类筛选"),
    active: Optional[bool] = Query(None, description="筛选状态：true=有效，false=无效，不传=全部"),
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """获取知识库文档列表"""
    query = db.query(KnowledgeDocument)
    if category and category.strip():
        query = query.filter(KnowledgeDocument.category == category.strip())
    # 只有当 active 是明确的布尔值时才筛选
    if active is not None:
        query = query.filter(KnowledgeDocument.active == active)
    return query.order_by(KnowledgeDocument.id.desc()).all()


@router.get("/documents/{document_id}", response_model=schemas.KnowledgeDocumentRead)
def get_document(
    document_id: int,
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """获取单个文档"""
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return doc


@router.put("/documents/{document_id}", response_model=schemas.KnowledgeDocumentRead)
def update_document(
    document_id: int,
    payload: schemas.KnowledgeDocumentUpdate,
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """更新文档（更新内容会触发重新向量化）"""
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 如果内容或标题更新，需要重新向量化
    need_reindex = False
    if payload.content is not None or payload.title is not None:
        need_reindex = True
    
    # 更新字段
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(doc, key, value)
    
    db.commit()
    
    # 如果内容更新，重新向量化
    if need_reindex and payload.content is not None:
        try:
            rag_service = get_rag_service()
            # 删除旧块
            db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == document_id).delete()
            db.commit()
            
            # 重新添加文档（会重新分块和向量化）
            doc = rag_service.add_document(
                db=db,
                title=doc.title,
                content=doc.content,
                source_type=doc.source_type,
                source_url=doc.source_url,
                category=doc.category,
                tags=doc.tags
            )
        except Exception as e:
            print(f"⚠ 重新向量化失败: {e}")
    
    db.refresh(doc)
    return doc


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """删除文档"""
    try:
        rag_service = get_rag_service()
        rag_service.delete_document(db, document_id)
        return {"status": "ok", "message": "文档已删除"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除文档失败: {str(e)}")


@router.post("/documents/upload", response_model=schemas.KnowledgeDocumentRead, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    上传文档文件
    支持格式：
    - PDF (.pdf) - 使用 pdfplumber，可保留表格
    - Word (.docx) - 使用 python-docx
    - Excel (.xlsx, .xls) - 使用 pandas
    - 文本 (.txt, .md, .csv, .log) - 直接读取
    - 图片 (.jpg, .jpeg, .png, .bmp, .gif, .webp) - 使用 PaddleOCR 或 pytesseract
    """
    from ..services.document_parser import parse_document
    
    # 读取文件内容
    file_data = file.file.read()
    
    # 获取文件类型
    file_type = file.content_type
    filename = file.filename or ""
    
    try:
        # 使用文档解析器解析文件
        print(f"📄 开始解析文件: {filename} (类型: {file_type}, 大小: {len(file_data)} bytes)")
        parse_result = parse_document(file_data, filename=filename, file_type=file_type)
        
        content = parse_result.get("content", "")
        source_type = parse_result.get("source_type", "file")
        metadata = parse_result.get("metadata", {})
        
        if not content.strip():
            raise HTTPException(
                status_code=400, 
                detail=f"文件内容为空或无法提取文本。解析器: {metadata.get('parser', 'unknown')}"
            )
        
        print(f"✓ 文件解析完成，提取文本长度: {len(content)} 字符")
        
        # 使用文件名作为标题（如果没有提供）
        doc_title = title or (filename or "未命名文档")
        
        # 如果文件名没有扩展名，从 metadata 中获取信息
        if not doc_title or doc_title == "未命名文档":
            parser_info = metadata.get("parser", "")
            if parser_info:
                doc_title = f"文档 ({parser_info})"
        
        # 添加文档到知识库（包含向量化）
        print(f"🔄 开始处理文档: {doc_title} (内容长度: {len(content)} 字符)")
        rag_service = get_rag_service()
        doc = rag_service.add_document(
            db=db,
            title=doc_title,
            content=content,
            source_type=source_type,
            source_url=filename,
            category=category,
            tags=tags
        )
        print(f"✓ 文档已成功添加到知识库: {doc_title} (ID: {doc.id}, 块数: {doc.chunk_count})")
        return doc
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"❌ 上传文档失败: {error_detail}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"上传文档失败: {error_detail}\n\n可能原因：\n1. 文件格式不支持或损坏\n2. 文档解析失败\n3. 向量化处理失败\n4. 数据库操作失败"
        )


@router.get("/documents/{document_id}/chunks", response_model=List[schemas.KnowledgeChunkRead])
def get_document_chunks(
    document_id: int,
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """获取文档的所有块"""
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    chunks = db.query(KnowledgeChunk).filter(
        KnowledgeChunk.document_id == document_id
    ).order_by(KnowledgeChunk.chunk_index).all()
    return chunks


@router.post("/search", response_model=List[schemas.KnowledgeChunkRead])
def search_knowledge(
    query: str,
    top_k: Optional[int] = 5,
    category: Optional[str] = None,
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """搜索知识库（测试检索功能）"""
    try:
        rag_service = get_rag_service()
        search_results = rag_service.search(query, top_k=top_k, category=category)
        
        if not search_results:
            return []
        
        vector_ids = [r["vector_id"] for r in search_results]
        chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.vector_id.in_(vector_ids)
        ).all()
        
        # 按相似度排序
        chunk_dict = {c.vector_id: c for c in chunks}
        result_chunks = []
        for result in search_results:
            chunk = chunk_dict.get(result["vector_id"])
            if chunk:
                result_chunks.append(chunk)
        
        return result_chunks
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"搜索失败: {str(e)}")


@router.post("/rebuild-index")
def rebuild_index(
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """重建向量索引和BM25索引（含为无chunks的文档补建chunks）"""
    try:
        rag_service = get_rag_service()
        # 先为没有 chunks 的文档补建 chunks（供 BM25 检索）
        rebuilt_count = rag_service.rebuild_chunks_for_documents_without_chunks(db)
        rag_service._rebuild_index(db)
        # 重建BM25索引（如果启用混合检索）
        if rag_service.use_hybrid_search:
            rag_service._build_bm25_index(db)
        msg = "向量索引和BM25索引已重建"
        if rebuilt_count > 0:
            msg += f"，已为 {rebuilt_count} 个文档补建 chunks"
        return {"status": "ok", "message": msg}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"重建索引失败: {str(e)}")


@router.post("/documents/from-url", response_model=schemas.KnowledgeDocumentRead, status_code=status.HTTP_201_CREATED)
def import_from_url(
    payload: schemas.KnowledgeDocumentFromUrl,
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """从网页 URL 导入文档（使用 trafilatura 提取）"""
    from ..services.document_parser import parse_webpage
    
    url = payload.url
    if not url or not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="无效的 URL，必须以 http:// 或 https:// 开头")
    
    try:
        content = parse_webpage(url)
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="无法从网页提取内容，请检查 URL 是否可访问")
        
        doc_title = payload.title or f"网页: {url}"
        
        rag_service = get_rag_service()
        doc = rag_service.add_document(
            db=db,
            title=doc_title,
            content=content,
            source_type="web",
            source_url=url,
            category=payload.category,
            tags=payload.tags
        )
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"从网页导入失败: {str(e)}")


@router.post("/documents/from-database", response_model=schemas.KnowledgeDocumentRead, status_code=status.HTTP_201_CREATED)
def import_from_database(
    payload: schemas.KnowledgeDocumentFromDatabase,
    _: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """从数据库表导入数据"""
    from ..services.document_parser import parse_from_database
    
    table_name = payload.table_name
    if not table_name:
        raise HTTPException(status_code=400, detail="表名不能为空")
    
    try:
        content = parse_from_database(db, table_name, columns=payload.columns, limit=payload.limit)
        
        if not content.strip():
            raise HTTPException(status_code=400, detail=f"表 '{table_name}' 为空或不存在")
        
        doc_title = payload.title or f"数据库表: {table_name}"
        
        rag_service = get_rag_service()
        doc = rag_service.add_document(
            db=db,
            title=doc_title,
            content=content,
            source_type="database",
            source_url=f"table:{table_name}",
            category=payload.category,
            tags=payload.tags
        )
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"从数据库导入失败: {str(e)}")

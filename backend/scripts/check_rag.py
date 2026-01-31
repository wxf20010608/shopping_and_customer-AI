#!/usr/bin/env python
"""
RAG 知识库功能验证脚本
用于检查知识库功能是否正常
"""
import sys
from pathlib import Path

# 添加项目路径
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

def check_imports():
    """检查必要的导入"""
    print("=" * 60)
    print("1. 检查依赖导入...")
    print("=" * 60)
    
    errors = []
    
    # 检查 FAISS
    try:
        import faiss
        print("✓ faiss-cpu 已安装")
    except ImportError:
        errors.append("✗ faiss-cpu 未安装")
        print("✗ faiss-cpu 未安装")
    
    # 检查 sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ sentence-transformers 已安装")
    except ImportError:
        errors.append("✗ sentence-transformers 未安装")
        print("✗ sentence-transformers 未安装")
    
    # 检查 numpy
    try:
        import numpy as np
        print(f"✓ numpy 已安装 (版本: {np.__version__})")
    except ImportError:
        errors.append("✗ numpy 未安装")
        print("✗ numpy 未安装")
    
    # 检查项目模块
    try:
        from app.models import KnowledgeDocument, KnowledgeChunk
        print("✓ 知识库模型导入成功")
    except ImportError as e:
        errors.append(f"✗ 知识库模型导入失败: {e}")
        print(f"✗ 知识库模型导入失败: {e}")
    
    try:
        from app.services.rag_service import get_rag_service
        print("✓ RAG 服务导入成功")
    except ImportError as e:
        errors.append(f"✗ RAG 服务导入失败: {e}")
        print(f"✗ RAG 服务导入失败: {e}")
    
    try:
        from app.services.text_cleaner import get_text_cleaner
        print("✓ 文本清洗服务导入成功")
    except ImportError as e:
        errors.append(f"✗ 文本清洗服务导入失败: {e}")
        print(f"✗ 文本清洗服务导入失败: {e}")
    
    return len(errors) == 0, errors


def check_database():
    """检查数据库"""
    print("\n" + "=" * 60)
    print("2. 检查数据库...")
    print("=" * 60)
    
    try:
        from app.database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if "knowledge_documents" in tables:
            print("✓ knowledge_documents 表存在")
            
            # 检查字段
            columns = [col['name'] for col in inspector.get_columns("knowledge_documents")]
            required_fields = ['id', 'title', 'content', 'metadata', 'quality_score']
            missing_fields = [f for f in required_fields if f not in columns]
            
            if missing_fields:
                print(f"⚠ 缺少字段: {missing_fields}")
            else:
                print("✓ 所有必需字段都存在")
        else:
            print("✗ knowledge_documents 表不存在")
            return False
        
        if "knowledge_chunks" in tables:
            print("✓ knowledge_chunks 表存在")
        else:
            print("✗ knowledge_chunks 表不存在")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 数据库检查失败: {e}")
        return False


def check_rag_service():
    """检查 RAG 服务"""
    print("\n" + "=" * 60)
    print("3. 检查 RAG 服务...")
    print("=" * 60)
    
    try:
        from app.services.rag_service import get_rag_service
        
        rag_service = get_rag_service()
        
        if rag_service.embedding_model:
            print(f"✓ 嵌入模型已加载: {rag_service.embedding_model}")
            print(f"  向量维度: {rag_service.vector_dim}")
        else:
            print("⚠ 嵌入模型未加载（可能是首次使用，需要下载模型）")
        
        if rag_service.vector_index:
            print(f"✓ 向量索引已加载: {rag_service.vector_index.ntotal} 个向量")
        else:
            print("⚠ 向量索引未创建（知识库为空）")
        
        print(f"✓ 块大小: {rag_service.chunk_size}")
        print(f"✓ 重叠大小: {rag_service.chunk_overlap}")
        print(f"✓ Top-K: {rag_service.top_k}")
        
        return True
    except Exception as e:
        print(f"✗ RAG 服务检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_text_cleaner():
    """检查文本清洗服务"""
    print("\n" + "=" * 60)
    print("4. 检查文本清洗服务...")
    print("=" * 60)
    
    try:
        from app.services.text_cleaner import get_text_cleaner
        
        cleaner = get_text_cleaner()
        
        # 测试文本规范化
        test_text = "测试文本 2024/01/11 价格：¥100"
        normalized = cleaner.normalize_text(test_text)
        if normalized:
            print("✓ 文本规范化功能正常")
        else:
            print("✗ 文本规范化功能异常")
            return False
        
        # 测试结构化处理
        structured = cleaner.extract_structure(test_text)
        if structured and "text" in structured:
            print("✓ 结构化处理功能正常")
        else:
            print("✗ 结构化处理功能异常")
            return False
        
        # 测试内容清理
        cleaned, quality_info = cleaner.clean_content(test_text)
        if cleaned:
            print(f"✓ 内容清理功能正常 (质量评分: {quality_info.get('quality_score', 0):.2f})")
        else:
            print("✗ 内容清理功能异常")
            return False
        
        # 测试分块
        chunks = cleaner.chunk_text_optimized(test_text * 10, chunk_size=50)
        if chunks:
            print(f"✓ 分块功能正常 (生成了 {len(chunks)} 个块)")
        else:
            print("✗ 分块功能异常")
            return False
        
        # 测试元数据提取
        metadata = cleaner.extract_metadata(test_text)
        if metadata:
            print("✓ 元数据提取功能正常")
        else:
            print("✗ 元数据提取功能异常")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 文本清洗服务检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_api_routes():
    """检查 API 路由"""
    print("\n" + "=" * 60)
    print("5. 检查 API 路由...")
    print("=" * 60)
    
    try:
        from app.main import create_app
        
        app = create_app()
        
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        knowledge_routes = [r for r in routes if 'knowledge' in r.lower()]
        
        if knowledge_routes:
            print(f"✓ 找到 {len(knowledge_routes)} 个知识库相关路由:")
            for route in knowledge_routes[:10]:  # 只显示前10个
                print(f"  - {route}")
            if len(knowledge_routes) > 10:
                print(f"  ... 还有 {len(knowledge_routes) - 10} 个路由")
            return True
        else:
            print("✗ 未找到知识库相关路由")
            return False
    except Exception as e:
        print(f"✗ API 路由检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("RAG 知识库功能验证")
    print("=" * 60 + "\n")
    
    results = []
    
    # 1. 检查导入
    success, errors = check_imports()
    results.append(("依赖导入", success))
    
    if not success:
        print("\n⚠ 存在导入错误，请先解决依赖问题")
        print("\n建议运行: pip install -r requirements.txt")
        return
    
    # 2. 检查数据库
    db_ok = check_database()
    results.append(("数据库", db_ok))
    
    # 3. 检查 RAG 服务
    rag_ok = check_rag_service()
    results.append(("RAG 服务", rag_ok))
    
    # 4. 检查文本清洗
    cleaner_ok = check_text_cleaner()
    results.append(("文本清洗", cleaner_ok))
    
    # 5. 检查 API 路由
    api_ok = check_api_routes()
    results.append(("API 路由", api_ok))
    
    # 总结
    print("\n" + "=" * 60)
    print("验证结果总结")
    print("=" * 60)
    
    all_ok = True
    for name, ok in results:
        status = "✓ 通过" if ok else "✗ 失败"
        print(f"{name:20s} {status}")
        if not ok:
            all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ 所有检查通过！知识库功能正常")
    else:
        print("✗ 部分检查失败，请查看上面的错误信息")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

from __future__ import annotations

import os
import json
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import time
from pathlib import Path
import io
from PIL import Image
import pytesseract
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
try:
    import requests
except ImportError:
    requests = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

paddle_ocr = None  # PaddleOCR有依赖问题，暂时禁用

from ..models import ChatMessage, Product, Order, ShippingInfo, User
from ..utils import load_env


def extract_text_from_image(image_data: bytes) -> str:
    try:
        load_env()
        img = Image.open(io.BytesIO(image_data))
        if pytesseract:
            try:
                cmd = os.environ.get("TESSERACT_CMD")
                if cmd:
                    import pytesseract as _pt
                    _pt.pytesseract.tesseract_cmd = cmd
            except Exception:
                pass
            txt = pytesseract.image_to_string(img)
            txt = (txt or "").strip()
            return txt
        return ""
    except Exception:
        return ""


def extract_text_from_pdf(pdf_data: bytes) -> str:
    try:
        load_env()
        max_pages = int(os.environ.get("PDF_MAX_PAGES", "20"))
        max_chars = int(os.environ.get("PDF_MAX_CHARS", "20000"))
        txt = ""
        if fitz:
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            n = min(getattr(doc, "page_count", len(doc)), max_pages)
            for i in range(n):
                try:
                    page = doc.load_page(i)
                    t = page.get_text() or ""
                    if t:
                        txt += t + "\n"
                    if len(txt) >= max_chars:
                        break
                except Exception:
                    continue
            try:
                doc.close()
            except Exception:
                pass
        txt = (txt or "").strip()
        if len(txt) > max_chars:
            txt = txt[:max_chars]
        return txt
    except Exception:
        return ""


def transcribe_audio(audio_data: bytes, filename: str | None = None, mime: str | None = None) -> str:
    try:
        load_env()
        key = os.environ.get("MODEL_API_KEY") or os.environ.get("DASHSCOPE_API_KEY")
        base_url = os.environ.get("MODEL_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        model_stt = os.environ.get("MODEL_NAME_STT", "qwen-audio")
        if not key or not requests:
            return ""
        url = f"{base_url}/audio/transcriptions"
        files = {"file": (filename or "audio.webm", audio_data, mime or "application/octet-stream")}
        data = {"model": model_stt, "language": os.environ.get("STT_LANGUAGE", "zh")}
        headers = {"Authorization": f"Bearer {key}"}
        try:
            resp = requests.post(url, files=files, data=data, headers=headers, timeout=60)
            resp.raise_for_status()
            j = resp.json()
        except Exception:
            return ""
        try:
            txt = j.get("text") or j.get("output", {}).get("text") or j.get("result", {}).get("text")
            if not txt:
                # 兼容部分服务返回 choices 或 data 字段
                txt = (j.get("choices", [{}])[0].get("text") or j.get("data", {}).get("text") or "").strip()
        except Exception:
            txt = ""
        return (txt or "").strip()
    except Exception:
        return ""
def _call_qwen(prompt: str, history: List[dict], model_override: Optional[str] = None) -> str:
    load_env()
    key = os.environ.get("MODEL_API_KEY") or os.environ.get("DASHSCOPE_API_KEY")
    # 去除可能的引号
    if key:
        key = key.strip().strip('"').strip("'")
    model = os.environ.get("MODEL_NAME", "qwen-turbo")
    vl_model = os.environ.get("MODEL_NAME_VL") or ("qwen-vl-plus" if "vl" not in (model or "") else model)
    text_model = os.environ.get("MODEL_NAME_TEXT") or model
    temperature = float(os.environ.get("MODEL_TEMPERATURE", "0.7"))
    max_tokens = int(os.environ.get("MODEL_MAX_LENGTH", "2048"))
    base_url = os.environ.get("MODEL_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
    if not key:
        return "当前未配置AI密钥，已根据系统信息给出基础回复。"
    
    # 检查密钥格式是否正确（简单的格式验证）
    if not key.startswith("sk-"):
        return "AI密钥格式错误：密钥应以'sk-'开头。请检查您的API密钥格式。"

    def normalize_message(m: dict) -> dict:
        role = m.get("role") or "user"
        content = m.get("content")
        if isinstance(content, list):
            return {"role": role, "content": content}
        else:
            s = content if isinstance(content, str) else ""
            return {"role": role, "content": [{"type":"text","text": s}]}

    def _fallback_reply() -> str:
        return ""

    try:
        import urllib.request
        import urllib.error
        url = f"{base_url}/chat/completions"
        try:
            has_img = any(any(isinstance(seg, dict) and (seg.get("type") == "image_url") for seg in (m.get("content") or [])) for m in history)
        except Exception:
            has_img = False
        chosen_model = vl_model if has_img else text_model
        if model_override:
            chosen_model = model_override
        def prepare_messages(chosen: str):
            is_vl = ("vl" in (chosen or "")) or ("vision" in (chosen or ""))
            if is_vl:
                return [{"role": "system", "content": [{"type":"text","text": prompt}]}] + [normalize_message(m) for m in history]
            else:
                msgs = [{"role": "system", "content": prompt}]
                for m in history:
                    role = m.get("role") or "user"
                    content = m.get("content")
                    if isinstance(content, list):
                        text_parts = [seg.get("text") for seg in content if isinstance(seg, dict) and seg.get("text")]
                        s = "\n".join(text_parts)
                    else:
                        s = content if isinstance(content, str) else ""
                    msgs.append({"role": role, "content": s})
                return msgs
        payload_mm = {"model": chosen_model, "messages": prepare_messages(chosen_model), "temperature": temperature, "max_tokens": max_tokens}
        def do_request(payload: dict):
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"))
            req.add_header("Content-Type", "application/json")
            # DashScope API认证头
            req.add_header("Authorization", f"Bearer {key}")
            # 对于DashScope服务，如果支持异步调用可以添加此头部
            # 但某些账户可能不支持异步调用，暂时注释掉
            # if "dashscope" in base_url:
            #     req.add_header("X-DashScope-Async", "enable")
            
            # 调试信息：打印请求URL和头部
            print(f"Request URL: {url}")
            print(f"Authorization: Bearer {key[:10]}...")
            print(f"Model: {chosen_model}")
            
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        def do_request_requests(payload: dict):
            if not requests:
                raise RuntimeError("requests not available")
            headers = {"Content-Type":"application/json","Authorization":f"Bearer {key}"}
            r = requests.post(url, json=payload, headers=headers, timeout=60)
            r.raise_for_status()
            return r.json()
        try:
            data = do_request(payload_mm)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8") if hasattr(e, "read") else ""
            print(f"API Error {e.code}: {body}")
            if e.code == 401:
                raise HTTPException(status_code=401, detail="AI密钥无效或未授权，请检查密钥设置。")
            if e.code in (400, 404, 422):
                try:
                    msg = ""
                    code = ""
                    import json as _json
                    jd = _json.loads(body or "{}")
                    err = jd.get("error") or {}
                    msg = (err.get("message") or "").strip()
                    code = (err.get("code") or "").strip()
                    if ("overdue" in msg.lower()) or (code.lower() == "arrearage"):
                        raise HTTPException(status_code=402, detail="模型账户欠费或未开通权限，请在控制台结算或更换有效密钥。")
                except HTTPException:
                    raise
                except Exception:
                    pass
                alt_model = model_override or text_model
                payload_tx = {"model": alt_model, "messages": prepare_messages(alt_model), "temperature": temperature, "max_tokens": max_tokens}
                try:
                    data = do_request(payload_tx)
                except Exception:
                    try:
                        data = do_request_requests(payload_tx)
                    except Exception:
                        raise HTTPException(status_code=e.code, detail=(msg or f"AI服务错误 {e.code}"))
            else:
                raise HTTPException(status_code=e.code, detail=f"AI服务错误 {e.code}")

        except urllib.error.URLError as e:
            # 网络错误时降级为纯文本对话再试一次
            try:
                msg = getattr(e, "reason", None) or getattr(e, "args", None)
                print(f"Network Error: {msg}")
            except Exception:
                pass
            try:
                alt_model = model_override or text_model
                payload_tx = {"model": alt_model, "messages": prepare_messages(alt_model), "temperature": temperature, "max_tokens": max_tokens}
                data = do_request(payload_tx)
            except Exception:
                try:
                    data = do_request_requests(payload_tx)
                except Exception:
                    raise HTTPException(status_code=503, detail="AI网络错误或服务不可用，请稍后再试")

        try:
            # DashScope响应格式
            msg = data["output"]["choices"][0]["message"]["content"]
        except Exception:
            try:
                # OpenAI兼容格式
                msg = data["choices"][0]["message"]["content"]
            except Exception:
                print(f"⚠ 无法解析API响应: {json.dumps(data)[:500]}")
                msg = json.dumps(data)[:400]
        
        # 确保返回的消息不为空
        if not msg or not str(msg).strip():
            print("⚠ API返回了空消息")
            raise HTTPException(status_code=503, detail="AI服务返回了空回复，请稍后再试")
        
        return str(msg).strip()
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(status_code=503, detail="AI服务不可用")


def chat(user_id: int, product_id: Optional[int], text: str, db: Session, model_override: Optional[str] = None, extra_segments: Optional[List[dict]] = None) -> ChatMessage:
    print(f"📞 收到聊天请求: user_id={user_id}, product_id={product_id}, text={text[:50] if text else ''}...")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("用户不存在")
    product: Optional[Product] = None
    if product_id:
        product = db.query(Product).filter(Product.id == product_id).first()

    # Build context from recent messages
    recent = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id, ChatMessage.product_id == product_id)
        .order_by(ChatMessage.id.desc())
        .limit(20)
        .all()
    )[::-1]

    def msg_to_segments(m: ChatMessage):
        c = (m.content or "")
        if c.startswith("image:"):
            url = c.split("image:",1)[1]
            try:
                from base64 import b64encode
                p = Path(__file__).resolve().parent.parent / url.lstrip("/")
                data = b""
                try:
                    with open(p, "rb") as fp:
                        data = fp.read()
                except Exception:
                    data = b""
                mime = "image/jpeg"
                ext = Path(p).suffix.lower()
                if ext in (".png",):
                    mime = "image/png"
                elif ext in (".webp",):
                    mime = "image/webp"
                elif ext in (".gif",):
                    mime = "image/gif"
                data_url = f"data:{mime};base64,{b64encode(data).decode('ascii')}" if data else url
                return {"role": m.role, "content": [{"type":"text","text":"[图片]"},{"type":"image_url","image_url":{"url": data_url}}]}
            except Exception:
                return {"role": m.role, "content": [{"type":"text","text":"[图片]"},{"type":"image_url","image_url":{"url": url}}]}
        elif c.startswith("file:"):
            url = c.split("file:",1)[1]
            return {"role": m.role, "content": [{"type":"text","text":f"[文件]{url}"}]}
        elif c.startswith("audio:"):
            url = c.split("audio:",1)[1]
            return {"role": m.role, "content": [{"type":"text","text":f"[音频]{url}"}]}
        else:
            return {"role": m.role, "content": [{"type":"text","text": c}]}

    history = [msg_to_segments(m) for m in recent]

    # System prompt with available info
    product_info = (
        f"商品：{product.name}，分类：{product.category}，价格￥{product.price:.2f}，库存{product.stock}。" if product else ""
    )

    # last order and logistics summary for user
    order = db.query(Order).filter(Order.user_id == user_id).order_by(Order.id.desc()).first()
    logistics = None
    if order:
        logistics = db.query(ShippingInfo).filter(ShippingInfo.order_id == order.id).first()
    logistics_info = ""
    if logistics:
        logistics_info = f"最近订单#{order.id} 物流状态：{logistics.status.value}，运单号：{logistics.tracking_number or '-'}。"

    # RAG 知识库检索增强（完整流程）
    rag_context = ""
    rag_used = False
    rag_similarity = 0.0
    
    try:
        from ..services.rag_service import get_rag_service
        
        rag_service = get_rag_service()
        # 有嵌入模型时用向量+BM25 混合检索，无嵌入模型或向量为空时仅用 BM25
        if rag_service:
            # RAG完整流程：
            # 步骤1：向量化用户查询（使用与文档相同的嵌入模型）
            # 步骤2：在向量数据库中检索最相关的文档块（使用余弦相似度计算）
            # 步骤3：获取检索结果并构建上下文
            # 降低相似度阈值以提高召回率（从0.3降到0.2）
            similarity_threshold = float(os.environ.get("RAG_SIMILARITY_THRESHOLD", "0.2"))
            # 增加top_k以提高召回率（从3增加到5）
            top_k = int(os.environ.get("RAG_TOP_K", "5"))
            context_text, result_details = rag_service.retrieve_context(
                db, text, top_k=top_k, similarity_threshold=similarity_threshold
            )
            
            if context_text and result_details:
                # 计算最高相似度
                rag_similarity = max([r["similarity"] for r in result_details], default=0.0)
                
                # 如果相似度足够高，优先使用知识库内容
                if rag_similarity >= similarity_threshold:
                    rag_used = True
                    # 构建增强的提示词，指示AI使用检索到的内容（但不暴露来源）
                    rag_context = (
                        f"\n\n【参考信息】\n"
                        f"{context_text}\n"
                        f"【参考信息结束】\n\n"
                        f"请优先使用以上参考信息回答用户问题。如果参考信息完全回答了用户问题，"
                        f"请直接使用参考信息回答，无需调用其他信息。如果参考信息部分相关，"
                        f"请结合参考信息和系统信息回答。如果参考信息不相关，再使用系统信息回答。"
                        f"回答时不要提及信息来源，直接自然地回答问题即可。"
                    )
                    print(f"✓ RAG检索成功：找到 {len(result_details)} 条相关内容，最高相似度 {rag_similarity:.2f}")
                else:
                    print(f"⚠ RAG检索结果相似度较低（{rag_similarity:.2f} < {similarity_threshold}），不使用知识库内容")
            else:
                print("ℹ RAG检索未找到相关内容，将使用大模型直接回答")
    except Exception as e:
        # RAG 功能失败不影响主流程
        import traceback
        print(f"⚠ RAG 检索失败: {e}")
        traceback.print_exc()
        rag_context = ""

    # 构建系统提示词
    if rag_used:
        # 如果使用了知识库，优先使用检索到的内容（但不暴露来源）
        system_prompt = (
            "你是电商客服，使用简洁中文回复，支持售前/售后、物流查询、商品推荐。"
            "请优先使用系统提供的参考信息回答用户问题。"
            "如果参考信息完全回答了问题，直接使用参考信息；"
            "如果参考信息部分相关，结合参考信息和系统信息回答；"
            "如果参考信息不相关，再使用系统信息回答。"
            "回答时不要提及信息来源，直接自然地回答问题即可。"
            + product_info + logistics_info + rag_context
        )
    else:
        # 如果没有使用知识库，使用常规提示词
        system_prompt = (
            "你是电商客服，使用简洁中文回复，支持售前/售后、物流查询、商品推荐。"
            "优先结合系统提供的信息进行回答，无法确定时要礼貌引导。"
            + product_info + logistics_info
        )

    # persist user message
    umsg = None
    if (text or "").strip():
        umsg = ChatMessage(user_id=user_id, product_id=product_id, role="user", content=text)
        db.add(umsg)
        db.commit(); db.refresh(umsg)

    user_content = []
    if (text or "").strip():
        user_content = [{"type":"text","text": text}]
    if extra_segments:
        try:
            max_seg_len = int(os.environ.get("EXTRA_SEGMENT_MAX_LEN", "4000"))
            max_seg_count = int(os.environ.get("EXTRA_SEGMENT_MAX_COUNT", "6"))
        except Exception:
            max_seg_len = 4000
            max_seg_count = 6
        cleaned = []
        try:
            for s in extra_segments:
                if not isinstance(s, dict):
                    continue
                t = s.get("text") or ""
                if not t:
                    continue
                if len(t) > max_seg_len:
                    t = t[:max_seg_len]
                cleaned.append({"type":"text","text": t})
                if len(cleaned) >= max_seg_count:
                    break
        except Exception:
            cleaned = []
        user_content = user_content + cleaned
    try:
        print(f"🤖 开始调用AI服务...")
        reply = _call_qwen(system_prompt, history + [{"role": "user", "content": user_content}], model_override)
        print(f"✅ AI服务返回回复: {reply[:100] if reply else 'None'}...")
    except HTTPException as he:
        print(f"❌ HTTPException: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        import traceback
        print(f"❌ 调用AI服务时发生异常: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=503, detail=f"AI服务调用失败: {str(e)}")

    if not reply or not str(reply).strip():
        print("⚠ AI服务返回了空回复")
        raise HTTPException(status_code=503, detail="AI服务暂不可用，请稍后再试或联系人工客服")
    amsg = ChatMessage(user_id=user_id, product_id=product_id, role="assistant", content=reply)
    db.add(amsg)
    db.commit(); db.refresh(amsg)
    return amsg


def history(user_id: int, product_id: Optional[int], db: Session, start: Optional[str] = None, end: Optional[str] = None, limit: int = 100) -> List[ChatMessage]:
    q = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id, ChatMessage.product_id == product_id)
    )
    from datetime import datetime
    def parse_dt(s: Optional[str]) -> Optional[datetime]:
        if not s:
            return None
        try:
            # 处理 ISO 格式（包括带 Z 的 UTC 时间）
            ts = s.strip()
            if ts.endswith('Z'):
                ts = ts[:-1]  # 移除 Z 后缀
            # 处理带时区偏移的格式
            if '+' in ts:
                ts = ts.split('+')[0]
            elif ts.count('-') > 2:  # 有负时区偏移，如 2024-01-01T12:00:00-08:00
                # 找到最后一个 - 并检查是否是时区偏移
                parts = ts.rsplit('-', 1)
                if len(parts) == 2 and ':' in parts[1] and len(parts[1]) <= 6:
                    ts = parts[0]
            # 尝试解析
            return datetime.fromisoformat(ts)
        except Exception as e:
            print(f"解析时间失败: {s}, 错误: {e}")
            return None
    sdt = parse_dt(start)
    edt = parse_dt(end)
    if sdt:
        q = q.filter(ChatMessage.created_at >= sdt)
    if edt:
        q = q.filter(ChatMessage.created_at <= edt)
    try:
        cap = int(os.environ.get("CHAT_HISTORY_LIMIT_MAX", "5000"))
    except Exception:
        cap = 5000
    items = q.order_by(ChatMessage.id.desc()).limit(max(1, min(limit, cap))).all()
    return items[::-1]

def delete_conversation(user_id: int, product_id: Optional[int], db: Session) -> int:
    q = db.query(ChatMessage).filter(ChatMessage.user_id == user_id, ChatMessage.product_id == product_id)
    deleted = q.delete(synchronize_session=False)
    db.commit()
    return int(deleted)

def retract_message(message_id: int, user_id: int, db: Session) -> bool:
    m = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not m:
        return False
    if m.user_id != user_id or m.role != "user":
        return False
    try:
        from datetime import timedelta
        try:
            th_ms = int(os.environ.get("CHAT_GROUP_THRESHOLD_MS", "15000"))
        except Exception:
            th_ms = 15000
        start = m.created_at - timedelta(milliseconds=th_ms)
        end = m.created_at + timedelta(milliseconds=th_ms)
        q = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == user_id,
                ChatMessage.product_id == m.product_id,
                ChatMessage.role == "user",
                ChatMessage.created_at >= start,
                ChatMessage.created_at <= end,
            )
            .order_by(ChatMessage.id.asc())
        )
        items = q.all()
        changed = False
        for x in items:
            c = x.content or ""
            if x.id == m.id or c.startswith("image:") or c.startswith("file:") or c.startswith("audio:"):
                x.content = "此消息已撤回"
                db.add(x)
                changed = True
        if not changed:
            m.content = "此消息已撤回"
            db.add(m)
        db.commit()
        return True
    except Exception:
        try:
            m.content = "此消息已撤回"
            db.add(m)
            db.commit()
            return True
        except Exception:
            return False


def chat_with_upload(user_id: int, product_id: Optional[int], text: str, images: List[UploadFile] | None, files: List[UploadFile] | None, audios: List[UploadFile] | None, db: Session, model_override: Optional[str] = None) -> ChatMessage:
    base = Path(__file__).resolve().parent.parent / "static" / "uploads" / "chat"
    base.mkdir(parents=True, exist_ok=True)
    
    # persist attachments as individual user messages
    def save(f: UploadFile, prefix: str) -> str:
        ext = Path(f.filename or "").suffix or ".bin"
        name = f"{prefix}_{int(time.time())}_{os.urandom(4).hex()}{ext}"
        dest = base / name
        with open(dest, "wb") as fp:
            fp.write(f.file.read())
        return f"/static/uploads/chat/{name}"

    urls: List[tuple[str,str]] = []
    file_contents = []  # 存储文件内容用于AI分析
    
    # 处理图片 - 进行OCR识别
    image_contents = []  # 存储图片OCR识别内容
    for f in images or []:
        # 首先读取图片内容进行OCR识别
        try:
            image_data = f.file.read()
            ocr_text = extract_text_from_image(image_data)
            if ocr_text:
                image_contents.append(f"图片 {f.filename} 识别内容:\n{ocr_text}")
            f.file.seek(0)  # 重置文件指针
        except:
            pass  # 如果无法读取图片内容，忽略
        
        # 然后保存图片
        url = save(f, "img")
        urls.append(("image", url))
        db.add(ChatMessage(user_id=user_id, product_id=product_id, role="user", content=f"image:{url}"))
    
    # 处理文件 - 读取文本文件内容，其它类型仅摘要
    for f in files or []:
        file_bytes = b""
        try:
            file_bytes = f.file.read()
        except Exception:
            file_bytes = b""
        finally:
            try:
                f.file.seek(0)
            except Exception:
                pass

        ext = Path(f.filename or "").suffix.lower()
        size = len(file_bytes)
        text_exts = {".txt", ".md", ".csv", ".json", ".log"}
        if ext in text_exts:
            try:
                max_bytes = 1024 * 1024
                if len(file_bytes) > max_bytes:
                    file_bytes = file_bytes[:max_bytes]
                text_content = file_bytes.decode("utf-8", errors="ignore")
                if text_content:
                    max_chars = 10000
                    if len(text_content) > max_chars:
                        text_content = text_content[:max_chars]
                    file_contents.append(f"文件 {f.filename} 内容:\n{text_content}")
            except Exception:
                pass
        elif ext == ".pdf":
            try:
                pdf_text = extract_text_from_pdf(file_bytes)
                if pdf_text:
                    file_contents.append(f"文件 {f.filename} 内容:\n{pdf_text}")
                else:
                    info = f"文件 {f.filename} 类型 {ext or '-'} 大小 {size} 字节"
                    file_contents.append(info)
            except Exception:
                try:
                    info = f"文件 {f.filename} 类型 {ext or '-'} 大小 {size} 字节"
                    file_contents.append(info)
                except Exception:
                    pass
        else:
            try:
                info = f"文件 {f.filename} 类型 {ext or '-'} 大小 {size} 字节"
                file_contents.append(info)
            except Exception:
                pass

        url = save(f, "file")
        urls.append(("file", url))
        db.add(ChatMessage(user_id=user_id, product_id=product_id, role="user", content=f"file:{url}"))
    
    # 处理音频 - 服务端识别并保存附件消息
    audio_texts = []
    for f in audios or []:
        try:
            b = f.file.read()
            f.file.seek(0)
        except Exception:
            b = b""
        if not b:
            continue
        ext = Path(f.filename or "").suffix.lower()
        mime = "audio/webm"
        if ext in (".mp3",):
            mime = "audio/mpeg"
        elif ext in (".wav",):
            mime = "audio/wav"
        elif ext in (".m4a", ".aac"):
            mime = "audio/aac"
        txt = transcribe_audio(b, f.filename or "audio", mime)
        if txt:
            audio_texts.append(f"语音 {f.filename} 识别内容:\n{txt}")
        url = save(f, "audio")
        urls.append(("audio", url))
        db.add(ChatMessage(user_id=user_id, product_id=product_id, role="user", content=f"audio:{url}"))
    
    db.commit()

    # 构建额外上下文片段（仅用于AI，不进入可见文本）
    extra_segments: List[dict] = []
    for s in image_contents:
        extra_segments.append({"type":"text","text": s})
    for s in file_contents:
        extra_segments.append({"type":"text","text": s})
    for s in audio_texts:
        extra_segments.append({"type":"text","text": s})
    # 如果有媒体文件或文本内容，调用AI处理（文本仅为用户输入，不包含识别内容）
    if urls or (text or "").strip():
        return chat(user_id, product_id, text or "", db, model_override, extra_segments)
    
    # 如果只有媒体文件但没有文本内容，返回最后一个媒体消息
    if urls:
        return db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.product_id == product_id,
            ChatMessage.role == "user"
        ).order_by(ChatMessage.id.desc()).first()
    
    # 回退到普通聊天
    return chat(user_id, product_id, text or "", db, model_override)
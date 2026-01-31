"""
文本清洗和预处理服务
实现文本规范化、结构化处理、内容清理、分块优化和元数据提取
"""
from __future__ import annotations

import os
import re
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import Counter

from ..utils import load_env


class TextCleaner:
    """文本清洗和预处理类"""
    
    def __init__(self):
        load_env()
        self.min_chunk_length = int(os.environ.get("RAG_MIN_CHUNK_LENGTH", "20"))  # 最小块长度
        self.max_chunk_length = int(os.environ.get("RAG_MAX_CHUNK_LENGTH", "2000"))  # 最大块长度
        self.quality_threshold = float(os.environ.get("RAG_QUALITY_THRESHOLD", "0.3"))  # 质量评分阈值
        self.chunk_size = int(os.environ.get("RAG_CHUNK_SIZE", "500"))  # 默认块大小
        self.chunk_overlap = int(os.environ.get("RAG_CHUNK_OVERLAP", "50"))  # 默认重叠大小
    
    def normalize_text(self, text: str) -> str:
        """
        (1) 文本规范化
        - 统一编码（UTF-8）
        - 采用正则表达式去除特殊字符、乱码
        - 标准化日期、货币等格式
        """
        if not text:
            return ""
        
        # 确保 UTF-8 编码
        if isinstance(text, bytes):
            try:
                text = text.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text = text.decode('gbk', errors='ignore')
                except:
                    text = text.decode('latin-1', errors='ignore')
        
        # 去除控制字符和不可见字符（保留换行和制表符）
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # 标准化空白字符（多个空格/换行合并）
        text = re.sub(r'[ \t]+', ' ', text)  # 多个空格/制表符合并为一个空格
        text = re.sub(r'\n{3,}', '\n\n', text)  # 多个换行合并为两个
        
        # 标准化日期格式
        # 匹配各种日期格式并统一
        date_patterns = [
            (r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', r'\1年\2月\3日'),  # 2024/01/11 -> 2024年1月11日
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', r'\3年\1月\2日'),  # 01/11/2024 -> 2024年1月11日
        ]
        for pattern, replacement in date_patterns:
            text = re.sub(pattern, replacement, text)
        
        # 标准化货币格式
        # 匹配各种货币表示并统一
        currency_patterns = [
            (r'¥\s*(\d+(?:\.\d+)?)', r'￥\1'),  # ¥100 -> ￥100
            (r'(\d+(?:\.\d+)?)\s*元', r'￥\1'),  # 100元 -> ￥100
            (r'RMB\s*(\d+(?:\.\d+)?)', r'￥\1'),  # RMB100 -> ￥100
            (r'CNY\s*(\d+(?:\.\d+)?)', r'￥\1'),  # CNY100 -> ￥100
        ]
        for pattern, replacement in currency_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # 去除特殊字符和乱码（保留中文、英文、数字、基本标点、换行）
        # 保留的字符：中文、英文、数字、基本标点、连字符（用于 3-5、7-10 等范围）、换行、制表符
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s.,!?;:()（）【】《》「」『』、。，！？；：\n\t\-]', '', text)
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    def extract_structure(self, text: str) -> Dict[str, any]:
        """
        (2) 结构化处理
        - 提取标题、段落、列表
        - 处理表格数据（转为Markdown或结构化文本）
        - 代码块分离和格式化
        """
        if not text:
            return {"text": "", "structure": {}}
        
        structure = {
            "titles": [],
            "paragraphs": [],
            "lists": [],
            "tables": [],
            "code_blocks": []
        }
        
        lines = text.split('\n')
        processed_lines = []
        current_code_block = []
        in_code_block = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                processed_lines.append("")
                continue
            
            # 检测代码块
            if line.startswith('```') or line.startswith('~~~'):
                if in_code_block:
                    # 结束代码块
                    code_content = '\n'.join(current_code_block)
                    structure["code_blocks"].append({
                        "index": len(structure["code_blocks"]),
                        "content": code_content,
                        "language": current_code_block[0] if current_code_block else "text"
                    })
                    processed_lines.append(f"[代码块 {len(structure['code_blocks'])}]")
                    current_code_block = []
                    in_code_block = False
                else:
                    # 开始代码块
                    in_code_block = True
                    if len(line) > 3:
                        current_code_block.append(line[3:].strip())  # 语言标识
                continue
            
            if in_code_block:
                current_code_block.append(line)
                continue
            
            # 检测标题（以 # 开头或全大写短行）
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title_text = line.lstrip('#').strip()
                structure["titles"].append({
                    "level": level,
                    "text": title_text,
                    "line": i
                })
                processed_lines.append(f"【标题{level}】{title_text}")
            # 检测列表项
            elif re.match(r'^[-*+]\s+', line) or re.match(r'^\d+[.)]\s+', line):
                list_item = re.sub(r'^[-*+\d.)]\s+', '', line)
                structure["lists"].append({
                    "text": list_item,
                    "line": i
                })
                processed_lines.append(f"• {list_item}")
            # 检测表格行（包含多个 | 分隔符）
            elif '|' in line and line.count('|') >= 2:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if cells:
                    structure["tables"].append({
                        "row": len(structure["tables"]),
                        "cells": cells
                    })
                    processed_lines.append("| " + " | ".join(cells) + " |")
            else:
                # 普通段落
                processed_lines.append(line)
        
        # 处理剩余的代码块
        if in_code_block and current_code_block:
            code_content = '\n'.join(current_code_block)
            structure["code_blocks"].append({
                "index": len(structure["code_blocks"]),
                "content": code_content,
                "language": "text"
            })
            processed_lines.append(f"[代码块 {len(structure['code_blocks'])}]")
        
        # 提取段落（非空行序列）
        paragraphs = []
        current_para = []
        for line in processed_lines:
            if line.strip():
                current_para.append(line)
            else:
                if current_para:
                    paragraphs.append('\n'.join(current_para))
                    current_para = []
        if current_para:
            paragraphs.append('\n'.join(current_para))
        
        structure["paragraphs"] = paragraphs
        
        return {
            "text": '\n'.join(processed_lines),
            "structure": structure
        }
    
    def clean_content(self, text: str) -> Tuple[str, Dict]:
        """
        (3) 内容清理
        - 去除广告、导航栏、页脚等噪音内容
        - 过滤低质量文本（过短、无意义内容）
        - 去重（完全重复和近似重复）
        """
        if not text:
            return "", {"removed": 0, "quality_score": 0.0}
        
        lines = text.split('\n')
        cleaned_lines = []
        removed_count = 0
        
        # 噪音模式（广告、导航、页脚等）
        noise_patterns = [
            r'^(首页|关于我们|联系我们|隐私政策|使用条款|网站地图|返回顶部)',
            r'^(Copyright|©|版权所有)',
            r'^(广告|Advertisement|AD)',
            r'^(关注我们|Follow us|订阅)',
            r'^(分享到|Share to)',
            r'^(Cookie|Cookies)',
            r'^[\d\s\-]+$',  # 纯数字和分隔符
            r'^[^\u4e00-\u9fa5a-zA-Z]{0,5}$',  # 过短且无意义
        ]
        
        seen_lines = set()  # 用于去重
        
        for line in lines:
            line = line.strip()
            if not line:
                cleaned_lines.append("")
                continue
            
            # 检查是否为噪音
            is_noise = False
            for pattern in noise_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_noise = True
                    break
            
            if is_noise:
                removed_count += 1
                continue
            
            # 检查长度（过短的内容可能是噪音）
            if len(line) < self.min_chunk_length:
                # 检查是否包含有意义的内容
                has_meaning = bool(re.search(r'[\u4e00-\u9fa5a-zA-Z]{3,}', line))
                if not has_meaning:
                    removed_count += 1
                    continue
            
            # 去重（完全重复）
            line_hash = hash(line)
            if line_hash in seen_lines:
                removed_count += 1
                continue
            seen_lines.add(line_hash)
            
            cleaned_lines.append(line)
        
        cleaned_text = '\n'.join(cleaned_lines)
        
        # 计算质量评分
        quality_score = self._calculate_quality_score(cleaned_text)
        
        # 过滤低质量文本
        if quality_score < self.quality_threshold:
            return "", {"removed": len(lines), "quality_score": quality_score}
        
        return cleaned_text, {"removed": removed_count, "quality_score": quality_score}
    
    def _calculate_quality_score(self, text: str) -> float:
        """计算文本质量评分（0-1）"""
        if not text:
            return 0.0
        
        score = 0.0
        
        # 长度评分（适中长度得分更高）
        length = len(text)
        if 100 <= length <= 5000:
            score += 0.3
        elif 50 <= length < 100 or 5000 < length <= 10000:
            score += 0.2
        else:
            score += 0.1
        
        # 中文内容比例
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
        total_chars = len(re.findall(r'[\u4e00-\u9fa5a-zA-Z]', text))
        if total_chars > 0:
            chinese_ratio = chinese_chars / total_chars
            if 0.3 <= chinese_ratio <= 0.9:  # 合理的中文比例
                score += 0.3
            else:
                score += 0.1
        
        # 信息密度（非空白字符比例）
        non_whitespace = len(re.sub(r'\s', '', text))
        if len(text) > 0:
            density = non_whitespace / len(text)
            if density > 0.5:
                score += 0.2
            else:
                score += 0.1
        
        # 结构完整性（包含标点、换行等）
        has_punctuation = bool(re.search(r'[。，！？；：]', text))
        has_structure = bool(re.search(r'\n', text)) or bool(re.search(r'[。！？]', text))
        if has_punctuation and has_structure:
            score += 0.2
        
        return min(score, 1.0)
    def _try_faq_split(self, text: str) -> Optional[List[str]]:
        """
        尝试按 FAQ 格式分块（问/答、Q/A、编号问题等）
        适用于"常见问题"类文档，每个问答单独成块便于精准检索
        
        支持格式示例：
        - 9. Q: 问题 A: 回答
        - 问：xxx 答：xxx
        - 一、问：xxx 答：xxx
        """
        if not text or len(text) < 100:
            return None
        
        # 优先按「数字. Q:」或「数字. 」分段（如 9. Q: ... 10. Q: ...），每段为完整 Q&A
        numbered_qa = re.split(r'(?m)^\s*(\d+[.．、]\s+)', text)
        if len(numbered_qa) >= 3:  # 至少有 1 个编号 + 2 段内容
            segments = []
            for i in range(1, len(numbered_qa), 2):
                prefix = numbered_qa[i] if i < len(numbered_qa) else ""
                content = numbered_qa[i + 1] if i + 1 < len(numbered_qa) else ""
                seg = (prefix + content).strip()
                if seg and len(seg) >= self.min_chunk_length:
                    segments.append(seg)
            if len(segments) >= 3:
                return segments
        
        # 备选：按 问/答、Q/A、中文序号 分段
        faq_pattern = re.compile(
            r'(?m)^\s*((?:问|Q|问题)\d*[：:]\s*|(?:答|A|回答)[：:]\s*|'
            r'[一二三四五六七八九十]+[、．.]\s*)',
            re.IGNORECASE
        )
        parts = faq_pattern.split(text)
        segments = []
        i = 1
        while i < len(parts):
            prefix = parts[i] if i < len(parts) else ""
            content = parts[i + 1] if i + 1 < len(parts) else ""
            if prefix.strip() and content.strip():
                segments.append((prefix + content).strip())
            elif content.strip():
                segments.append(content.strip())
            i += 2
        if len(segments) >= 3:
            return [s for s in segments if s and len(s) >= self.min_chunk_length]
        return None
    
    def chunk_text_optimized(self, text: str, chunk_size: Optional[int] = None, 
                            overlap: Optional[int] = None) -> List[Dict[str, any]]:
        """
        (4) 分块优化
        - FAQ 文档：按问答对分块，提高检索精准度
        - 一般文档：按语义边界分块（段落、章节）
        - 重叠分块避免信息割裂
        """
        if not text:
            return []

        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap

        # 优先尝试 FAQ 分块（常见问题类文档）
        faq_segments = self._try_faq_split(text)
        if faq_segments:
            chunks = []
            current = ""
            for seg in faq_segments:
                seg = seg.strip()
                if not seg or len(seg) < self.min_chunk_length:
                    continue
                # 单个问答过长则单独成块，否则可合并相邻小段
                if len(seg) > chunk_size:
                    if current:
                        chunks.append({"content": current.strip(), "type": "faq"})
                        current = ""
                    chunks.append({"content": seg[:self.max_chunk_length], "type": "faq"})
                elif len(current) + len(seg) + 2 <= chunk_size:
                    current = (current + "\n\n" + seg) if current else seg
                else:
                    if current:
                        chunks.append({"content": current.strip(), "type": "faq"})
                    current = seg
            if current:
                chunks.append({"content": current.strip(), "type": "faq"})
            # 应用最小长度过滤并添加 chunk_index
            final = []
            for i, c in enumerate(chunks):
                content = c["content"].strip()
                if len(content) >= self.min_chunk_length:
                    content = self.normalize_text(content)
                    if content:
                        final.append({
                            "content": content[:self.max_chunk_length],
                            "type": "faq",
                            "chunk_index": len(final)
                        })
            if final:
                return final
            # 若 FAQ 分块过滤后为空，继续下面的通用分块

        # 首先进行结构化处理
        structured = self.extract_structure(text)
        text = structured["text"]
        structure_info = structured["structure"]

        # 按语义边界分块（优先按段落、章节）
        chunks = []

        # 如果有标题，按标题分块
        if structure_info.get("titles"):
            current_section = []
            current_title = None
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                # 检查是否是标题行
                is_title = any(t["line"] == i for t in structure_info["titles"])
                
                if is_title:
                    # 保存之前的章节
                    if current_section and current_title:
                        section_text = '\n'.join(current_section)
                        if section_text.strip():
                            chunks.append({
                                "content": section_text,
                                "title": current_title,
                                "type": "section"
                            })
                    
                    # 开始新章节
                    title_obj = next((t for t in structure_info["titles"] if t["line"] == i), None)
                    current_title = title_obj["text"] if title_obj else None
                    current_section = [line]
                else:
                    current_section.append(line)
            
            # 添加最后一个章节
            if current_section and current_title:
                section_text = '\n'.join(current_section)
                if section_text.strip():
                    chunks.append({
                        "content": section_text,
                        "title": current_title,
                        "type": "section"
                    })
        
        # 如果没有标题或分块失败，按段落分块
        if not chunks:
            paragraphs = structure_info.get("paragraphs", [])
            if not paragraphs:
                # 按双换行分割段落
                paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            
            current_chunk = ""
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                # 如果段落本身很长，需要进一步分割
                if len(para) > chunk_size:
                    # 先保存当前块
                    if current_chunk:
                        chunks.append({
                            "content": current_chunk,
                            "type": "paragraph"
                        })
                        current_chunk = ""
                    
                    # 按句子分割长段落
                    sentences = re.split(r'[。！？\n]', para)
                    for sent in sentences:
                        sent = sent.strip()
                        if not sent:
                            continue
                        
                        if len(current_chunk) + len(sent) <= chunk_size:
                            current_chunk += sent + "。"
                        else:
                            if current_chunk:
                                chunks.append({
                                    "content": current_chunk,
                                    "type": "paragraph"
                                })
                            current_chunk = sent + "。"
                else:
                    # 段落可以加入当前块
                    if len(current_chunk) + len(para) <= chunk_size:
                        current_chunk += para + "\n\n"
                    else:
                        if current_chunk:
                            chunks.append({
                                "content": current_chunk,
                                "type": "paragraph"
                            })
                        current_chunk = para + "\n\n"
            
            # 添加最后一个块
            if current_chunk:
                chunks.append({
                    "content": current_chunk,
                    "type": "paragraph"
                })
        
        # 应用重叠分块（避免信息割裂）
        overlapped_chunks = []
        for i, chunk in enumerate(chunks):
            content = chunk["content"]
            
            # 如果块太大，需要分割
            if len(content) > chunk_size:
                # 按句子分割
                sentences = re.split(r'[。！？\n]', content)
                current_subchunk = ""
                
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    
                    if len(current_subchunk) + len(sent) <= chunk_size:
                        current_subchunk += sent + "。"
                    else:
                        if current_subchunk:
                            overlapped_chunks.append({
                                "content": current_subchunk,
                                "title": chunk.get("title"),
                                "type": chunk.get("type", "paragraph"),
                                "chunk_index": len(overlapped_chunks)
                            })
                        
                        # 重叠处理：保留前一个块的最后部分
                        if overlap > 0 and current_subchunk:
                            overlap_text = current_subchunk[-overlap:] if len(current_subchunk) > overlap else current_subchunk
                            current_subchunk = overlap_text + sent + "。"
                        else:
                            current_subchunk = sent + "。"
                
                if current_subchunk:
                    overlapped_chunks.append({
                        "content": current_subchunk,
                        "title": chunk.get("title"),
                        "type": chunk.get("type", "paragraph"),
                        "chunk_index": len(overlapped_chunks)
                    })
            else:
                # 正常大小的块，添加重叠
                if overlap > 0 and i > 0:
                    prev_chunk = overlapped_chunks[-1]["content"] if overlapped_chunks else ""
                    if len(prev_chunk) > overlap:
                        overlap_text = prev_chunk[-overlap:]
                        content = overlap_text + content
                
                overlapped_chunks.append({
                    "content": content,
                    "title": chunk.get("title"),
                    "type": chunk.get("type", "paragraph"),
                    "chunk_index": len(overlapped_chunks)
                })
        
        # 过滤和清理块
        final_chunks = []
        for chunk in overlapped_chunks:
            content = chunk["content"].strip()
            if not content:
                continue
            
            # 控制块大小
            if len(content) > self.max_chunk_length:
                content = content[:self.max_chunk_length]
            
            if len(content) < self.min_chunk_length:
                continue
            
            # 规范化文本
            content = self.normalize_text(content)
            if content:
                chunk["content"] = content
                final_chunks.append(chunk)
        
        return final_chunks
    
    def extract_metadata(self, text: str, source_url: Optional[str] = None) -> Dict[str, any]:
        """
        (5) 元数据提取
        - 提取来源、作者、时间等信息
        - 添加文档结构标签
        - 质量评分标注
        """
        metadata = {
            "source_url": source_url,
            "extracted_at": datetime.utcnow().isoformat(),
            "structure_tags": [],
            "quality_score": 0.0,
            "statistics": {}
        }
        
        if not text:
            return metadata
        
        # 提取时间信息
        time_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
            r'发布时间[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'更新时间[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            if matches:
                metadata["extracted_time"] = matches[0] if isinstance(matches[0], str) else '-'.join(matches[0])
                break
        
        # 提取作者信息
        author_patterns = [
            r'作者[：:]\s*([^\n]+)',
            r'Author[：:]\s*([^\n]+)',
            r'来源[：:]\s*([^\n]+)',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["author"] = match.group(1).strip()
                break
        
        # 提取来源信息
        if source_url:
            if source_url.startswith('http'):
                metadata["source_type"] = "web"
            elif source_url.endswith('.pdf'):
                metadata["source_type"] = "pdf"
            elif source_url.endswith(('.docx', '.doc')):
                metadata["source_type"] = "word"
            elif source_url.startswith('table:'):
                metadata["source_type"] = "database"
        
        # 结构化处理以获取结构标签
        structured = self.extract_structure(text)
        structure_info = structured["structure"]
        
        if structure_info.get("titles"):
            metadata["structure_tags"].append("has_titles")
        if structure_info.get("lists"):
            metadata["structure_tags"].append("has_lists")
        if structure_info.get("tables"):
            metadata["structure_tags"].append("has_tables")
        if structure_info.get("code_blocks"):
            metadata["structure_tags"].append("has_code")
        
        # 质量评分
        _, quality_info = self.clean_content(text)
        metadata["quality_score"] = quality_info.get("quality_score", 0.0)
        
        # 统计信息
        metadata["statistics"] = {
            "total_length": len(text),
            "char_count": len(re.sub(r'\s', '', text)),
            "chinese_char_count": len(re.findall(r'[\u4e00-\u9fa5]', text)),
            "english_word_count": len(re.findall(r'[a-zA-Z]+', text)),
            "paragraph_count": len(structure_info.get("paragraphs", [])),
            "title_count": len(structure_info.get("titles", [])),
            "list_count": len(structure_info.get("lists", [])),
            "table_count": len(structure_info.get("tables", [])),
            "code_block_count": len(structure_info.get("code_blocks", []))
        }
        
        return metadata


# 全局文本清洗器实例
_text_cleaner: Optional[TextCleaner] = None


def get_text_cleaner() -> TextCleaner:
    """获取文本清洗器实例（单例模式）"""
    global _text_cleaner
    if _text_cleaner is None:
        _text_cleaner = TextCleaner()
    return _text_cleaner

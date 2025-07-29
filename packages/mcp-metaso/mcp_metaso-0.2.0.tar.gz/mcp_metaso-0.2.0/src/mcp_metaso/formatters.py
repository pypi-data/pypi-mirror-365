"""搜索结果格式化器

提供各种搜索类型的结果格式化功能，将API返回的原始数据转换为用户友好的格式。
"""
from typing import Dict, Callable, Any


def format_webpage_result(item: Dict[str, Any], index: int) -> str:
    """格式化网页搜索结果
    
    Args:
        item: 网页搜索结果项
        index: 结果序号
        
    Returns:
        str: 格式化后的结果字符串
    """
    formatted = f"## 结果 {index}\n"
    formatted += f"**标题**: {item.get('title', 'N/A')}\n"
    formatted += f"**URL**: {item.get('link', 'N/A')}\n"
    formatted += f"**摘要**: {item.get('snippet', 'N/A')}\n"
    
    if item.get('displayDate'):
        formatted += f"**发布时间**: {item['displayDate']}\n"
    
    return formatted + "\n"


def format_document_result(item: Dict[str, Any], index: int) -> str:
    """格式化文库搜索结果
    
    Args:
        item: 文库搜索结果项
        index: 结果序号
        
    Returns:
        str: 格式化后的结果字符串
    """
    formatted = f"## 文库结果 {index}\n"
    formatted += f"**标题**: {item.get('title', 'N/A')}\n"
    
    # 处理作者信息 - 可能是数组或字符串
    authors = item.get('authors', item.get('author', 'N/A'))
    if isinstance(authors, list):
        authors_str = ', '.join(authors)
    else:
        authors_str = str(authors) if authors != 'N/A' else 'N/A'
    formatted += f"**作者/来源**: {authors_str}\n"
    
    formatted += f"**文档链接**: {item.get('link', item.get('url', 'N/A'))}\n"
    formatted += f"**摘要**: {item.get('snippet', item.get('abstract', 'N/A'))}\n"
    
    # 显示相关度和位置信息
    if item.get('score'):
        formatted += f"**相关度**: {item['score']}\n"
    if item.get('position'):
        formatted += f"**排序位置**: {item['position']}\n"
    
    # 兼容其他可能的字段
    if item.get('source'):
        formatted += f"**文档来源**: {item['source']}\n"
    if item.get('publishDate'):
        formatted += f"**发布时间**: {item['publishDate']}\n"
    
    return formatted + "\n"


def format_scholar_result(item: Dict[str, Any], index: int) -> str:
    """格式化学术搜索结果
    
    Args:
        item: 学术搜索结果项
        index: 结果序号
        
    Returns:
        str: 格式化后的结果字符串
    """
    formatted = f"## 学术结果 {index}\n"
    formatted += f"**标题**: {item.get('title', 'N/A')}\n"
    
    # 处理作者信息 - 可能是数组或字符串
    authors = item.get('authors', item.get('author', 'N/A'))
    if isinstance(authors, list):
        authors_str = ', '.join(authors)
    else:
        authors_str = str(authors) if authors != 'N/A' else 'N/A'
    formatted += f"**作者**: {authors_str}\n"
    
    formatted += f"**URL**: {item.get('link', item.get('url', 'N/A'))}\n"
    formatted += f"**摘要**: {item.get('snippet', item.get('abstract', 'N/A'))}\n"
    
    # 显示发表日期
    if item.get('date'):
        formatted += f"**发表日期**: {item['date']}\n"
    elif item.get('year'):
        formatted += f"**发表年份**: {item['year']}\n"
    
    # 显示相关度和位置信息
    if item.get('score'):
        formatted += f"**相关度**: {item['score']}\n"
    if item.get('position'):
        formatted += f"**排序位置**: {item['position']}\n"
    
    # 显示期刊/会议信息
    if item.get('venue', item.get('journal')):
        formatted += f"**期刊/会议**: {item.get('venue', item.get('journal'))}\n"
    
    # 显示引用和DOI信息
    if item.get('citationCount'):
        formatted += f"**引用次数**: {item['citationCount']}\n"
    if item.get('doi'):
        formatted += f"**DOI**: {item['doi']}\n"
    
    return formatted + "\n"


def format_image_result(item: Dict[str, Any], index: int) -> str:
    """格式化图片搜索结果
    
    Args:
        item: 图片搜索结果项
        index: 结果序号
        
    Returns:
        str: 格式化后的结果字符串
    """
    formatted = f"## 图片结果 {index}\n"
    formatted += f"**标题**: {item.get('title', 'N/A')}\n"
    formatted += f"**图片URL**: {item.get('imageUrl', 'N/A')}\n"
    
    # 显示图片尺寸信息
    if item.get('imageWidth') and item.get('imageHeight'):
        formatted += f"**尺寸**: {item['imageWidth']} x {item['imageHeight']}\n"
    
    # 显示评分和位置信息
    if item.get('score'):
        formatted += f"**相关度**: {item['score']}\n"
    if item.get('position'):
        formatted += f"**排序位置**: {item['position']}\n"
    
    # 兼容其他可能的字段
    if item.get('sourceUrl', item.get('link')):
        formatted += f"**来源页面**: {item.get('sourceUrl', item.get('link'))}\n"
    if item.get('description'):
        formatted += f"**描述**: {item['description']}\n"
    
    return formatted + "\n"


def format_video_result(item: Dict[str, Any], index: int) -> str:
    """格式化视频搜索结果
    
    Args:
        item: 视频搜索结果项
        index: 结果序号
        
    Returns:
        str: 格式化后的结果字符串
    """
    formatted = f"## 视频结果 {index}\n"
    formatted += f"**标题**: {item.get('title', 'N/A')}\n"
    
    # 处理作者/频道信息 - 可能是数组或字符串
    authors = item.get('authors', item.get('channel', 'N/A'))
    if isinstance(authors, list):
        authors_str = ', '.join(authors)
    else:
        authors_str = str(authors) if authors != 'N/A' else 'N/A'
    formatted += f"**创作者/频道**: {authors_str}\n"
    
    formatted += f"**视频链接**: {item.get('link', item.get('url', 'N/A'))}\n"
    formatted += f"**描述**: {item.get('snippet', item.get('description', 'N/A'))}\n"
    
    # 显示时长信息
    if item.get('duration'):
        try:
            duration_sec = int(item['duration'])
            minutes = duration_sec // 60
            seconds = duration_sec % 60
            formatted += f"**时长**: {minutes}分{seconds}秒 ({duration_sec}秒)\n"
        except (ValueError, TypeError):
            formatted += f"**时长**: {item['duration']}\n"
    
    # 显示发布时间
    if item.get('date'):
        formatted += f"**发布时间**: {item['date']}\n"
    elif item.get('publishDate'):
        formatted += f"**发布时间**: {item['publishDate']}\n"
    
    # 显示相关度和位置信息
    if item.get('score'):
        formatted += f"**相关度**: {item['score']}\n"
    if item.get('position'):
        formatted += f"**排序位置**: {item['position']}\n"
    
    # 显示封面图片
    if item.get('coverImage'):
        formatted += f"**封面图片**: {item['coverImage']}\n"
    elif item.get('thumbnail'):
        formatted += f"**缩略图**: {item['thumbnail']}\n"
    
    # 兼容其他字段
    if item.get('viewCount'):
        formatted += f"**观看次数**: {item['viewCount']}\n"
    
    return formatted + "\n"


def format_podcast_result(item: Dict[str, Any], index: int) -> str:
    """格式化播客搜索结果
    
    Args:
        item: 播客搜索结果项
        index: 结果序号
        
    Returns:
        str: 格式化后的结果字符串
    """
    formatted = f"## 播客结果 {index}\n"
    formatted += f"**标题**: {item.get('title', 'N/A')}\n"
    
    # 处理作者/主持人信息 - 可能是数组或字符串
    authors = item.get('authors', item.get('host', 'N/A'))
    if isinstance(authors, list):
        authors_str = ', '.join(authors)
    else:
        authors_str = str(authors) if authors != 'N/A' else 'N/A'
    formatted += f"**主持人/嘉宾**: {authors_str}\n"
    
    formatted += f"**播客链接**: {item.get('link', item.get('url', 'N/A'))}\n"
    formatted += f"**内容简介**: {item.get('snippet', item.get('description', 'N/A'))}\n"
    
    # 显示时长信息
    if item.get('duration'):
        try:
            duration_sec = int(item['duration'])
            hours = duration_sec // 3600
            minutes = (duration_sec % 3600) // 60
            seconds = duration_sec % 60
            if hours > 0:
                formatted += f"**时长**: {hours}小时{minutes}分{seconds}秒 ({duration_sec}秒)\n"
            else:
                formatted += f"**时长**: {minutes}分{seconds}秒 ({duration_sec}秒)\n"
        except (ValueError, TypeError):
            formatted += f"**时长**: {item['duration']}\n"
    
    # 显示发布时间
    if item.get('date'):
        formatted += f"**发布时间**: {item['date']}\n"
    elif item.get('publishDate'):
        formatted += f"**发布时间**: {item['publishDate']}\n"
    
    # 显示相关度和位置信息
    if item.get('score'):
        formatted += f"**相关度**: {item['score']}\n"
    if item.get('position'):
        formatted += f"**排序位置**: {item['position']}\n"
    
    # 兼容其他字段
    if item.get('podcastName', item.get('show')):
        formatted += f"**播客节目**: {item.get('podcastName', item.get('show'))}\n"
    if item.get('audioUrl'):
        formatted += f"**音频链接**: {item['audioUrl']}\n"
    
    return formatted + "\n"


# 格式化函数映射
RESULT_FORMATTERS: Dict[str, Callable[[Dict[str, Any], int], str]] = {
    "webpage": format_webpage_result,
    "document": format_document_result,
    "scholar": format_scholar_result, 
    "image": format_image_result,
    "video": format_video_result,
    "podcast": format_podcast_result
}

# 定义scope到结果key的映射
SCOPE_RESULT_MAPPING: Dict[str, str] = {
    "webpage": "webpages",
    "document": "documents", 
    "scholar": "scholars",
    "image": "images",
    "video": "videos",
    "podcast": "podcasts"
}

# 搜索类型中文名称映射
SCOPE_CN_MAPPING: Dict[str, str] = {
    "webpage": "网页",
    "document": "文库", 
    "scholar": "学术",
    "image": "图片",
    "video": "视频",
    "podcast": "播客"
}
"""
将普通关键词转换为正则表达式格式的工具函数
支持中英文关键词，自动处理大小写、单词边界、空格等
"""

import re


def keyword_to_regex(keyword, case_insensitive=True, word_boundary=True, plural_optional=False):
    """
    将普通关键词转换为正则表达式格式
    
    Args:
        keyword (str): 原始关键词，如 "Data Engineer" 或 "数据开发工程师"
        case_insensitive (bool): 是否大小写不敏感，默认 True
        word_boundary (bool): 是否使用单词边界，默认 True
        plural_optional (bool): 是否自动处理复数形式（仅英文），默认 False
    
    Returns:
        str: 正则表达式字符串
    
    Examples:
        >>> keyword_to_regex("Data Engineer")
        '(?i)\\bData\\s+Engineer\\b'
        
        >>> keyword_to_regex("数据开发工程师")
        '(?i)\\b数据开发工程师\\b'
        
        >>> keyword_to_regex("ETL Developer", plural_optional=True)
        '(?i)\\bETL\\s+Developer(s)?\\b'
    """
    if not keyword or not keyword.strip():
        return ""
    
    # 转义正则表达式特殊字符（但保留空格，因为我们要特殊处理）
    # 需要转义的字符：. ^ $ * + ? { } [ ] \\ | ( )
    special_chars = r'.^$*+?{}[]\\|()'
    
    # 判断是否包含中文字符
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', keyword))
    
    # 转义特殊字符（除了空格）
    escaped_keyword = ""
    for char in keyword:
        if char in special_chars:
            escaped_keyword += "\\" + char
        elif char == " ":
            # 空格转换为 \s+（匹配一个或多个空格）
            escaped_keyword += "\\s+"
        else:
            escaped_keyword += char
    
    # 处理复数形式（仅英文，且仅处理常见复数规则）
    if plural_optional and not has_chinese:
        # 检查最后一个单词是否适合添加复数
        words = keyword.split()
        if words:
            last_word = words[-1]
            # 常见需要复数的词：Engineer, Developer, Architect, Table, Pipeline 等
            plural_words = ['Engineer', 'Developer', 'Architect', 'Table', 'Pipeline', 
                          'Warehouse', 'Lake', 'Lakehouse', 'Platform', 'Metric', 
                          'Indicator', 'Layer', 'KPI']
            
            # 如果最后一个词在列表中，添加可选的复数形式
            if any(last_word.endswith(word) for word in plural_words):
                # 找到最后一个词的位置并替换
                pattern = re.escape(last_word)
                if last_word.endswith('y'):
                    # 如 Metrics -> Metrics? 或 Metric -> Metrics?
                    escaped_keyword = escaped_keyword.replace(
                        re.escape(last_word), 
                        f"{re.escape(last_word[:-1])}ies?|{re.escape(last_word)}(s)?"
                    )
                else:
                    escaped_keyword = escaped_keyword.replace(
                        re.escape(last_word), 
                        f"{re.escape(last_word)}(s)?"
                
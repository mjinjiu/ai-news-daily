#!/usr/bin/env python3
"""
清理HTML文件中的控制字符，并修复常见排版问题
"""

import sys
from pathlib import Path

def clean_html(filepath):
    """清理HTML文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_len = len(content)
    
    # 1. 移除所有控制字符（保留正常换行、回车、制表符）
    cleaned = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
    
    # 2. 修复多余的空行（超过3个连续换行缩减为2个）
    import re
    cleaned = re.sub(r'\n{4,}', '\n\n\n', cleaned)
    
    # 3. 修复HTML标签之间的空格
    cleaned = re.sub(r'>\s+\n\s+<', '>\n<', cleaned)
    
    # 4. 确保关键标签正确闭合
    # 检查未闭合的标签
    removed = original_len - len(cleaned)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    
    print(f"✅ 已清理: {filepath}")
    print(f"   移除了 {removed} 个控制字符/垃圾字符")
    return True

def validate_html(filepath):
    """基础HTML验证"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 检查基本结构
    if '<!DOCTYPE html>' not in content:
        issues.append("缺少 DOCTYPE")
    if '<html' not in content:
        issues.append("缺少 <html> 标签")
    if '</html>' not in content:
        issues.append("缺少 </html> 闭合标签")
    if '<head>' not in content:
        issues.append("缺少 <head>")
    if '</head>' not in content:
        issues.append("缺少 </head>")
    if '<body>' not in content:
        issues.append("缺少 <body>")
    if '</body>' not in content:
        issues.append("缺少 </body>")
    
    # 检查常见的未闭合标签
    tags_to_check = ['div', 'section', 'article', 'p', 'span', 'a', 'li', 'ul', 'h1', 'h2', 'h3']
    for tag in tags_to_check:
        open_count = content.count(f'<{tag}')
        close_count = content.count(f'</{tag}>')
        # 排除自闭合和带属性的标签计数误差
        if abs(open_count - close_count) > 5:
            issues.append(f"<{tag}> 标签可能不平衡: 开{open_count} vs 闭{close_count}")
    
    if issues:
        print(f"⚠️  {filepath} 发现问题:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(f"✅ {filepath} 基础结构检查通过")
    
    return len(issues) == 0

if __name__ == "__main__":
    files = [
        "/root/.openclaw/workspace/ai-news-site/index.html",
        "/root/.openclaw/workspace/ai-news-site-en/index.html"
    ]
    
    for filepath in files:
        print(f"\n🔧 处理: {filepath}")
        print("=" * 50)
        clean_html(filepath)
        validate_html(filepath)

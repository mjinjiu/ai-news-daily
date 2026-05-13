#!/usr/bin/env python3
import json
import re

# 读取 content.json
with open('/root/.openclaw/workspace/ai-news-site/data/content.json', 'r', encoding='utf-8') as f:
    raw = f.read()

# 策略：找到所有字符串值中的中文引号对 "..." 并替换为「...」
# 逐行处理，更精确
lines = raw.split('\n')
fixed_lines = []
for line in lines:
    # 匹配 JSON 字符串值行："key": "..."
    match = re.match(r'^(\s*"[^"]+": )"(.*)"(,?\s*)$', line)
    if match:
        prefix = match.group(1)
        value = match.group(2)
        suffix = match.group(3)
        # 修复中文引号对（需要成对出现）
        # 简单方法：把所有中文引号替换为书名号
        # 先检查是否有不成对的中文引号
        cn_quotes = value.count('"')
        if cn_quotes > 0:
            # 替换中文引号为书名号
            value = value.replace('"', '「').replace('"', '」')
            # 如果数量为奇数，可能有未闭合的，全部替换
            if value.count('「') != value.count('」'):
                # 全部统一为书名号
                value = value.replace('"', '「').replace('"', '」')
        fixed_lines.append(prefix + '"' + value + '"' + suffix)
    else:
        fixed_lines.append(line)

fixed_content = '\n'.join(fixed_lines)

# 验证
try:
    data = json.loads(fixed_content)
    print("✅ JSON 验证通过！")
    
    with open('/root/.openclaw/workspace/ai-news-site/data/content.json', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    print("✅ content.json 已修复")
    
except json.JSONDecodeError as e:
    print(f"❌ JSON 仍有问题: {e}")
    print(f"错误位置: 行 {e.lineno}, 列 {e.colno}")
    err_lines = fixed_content.split('\n')
    if e.lineno <= len(err_lines):
        print(f"内容: {err_lines[e.lineno-1]}")

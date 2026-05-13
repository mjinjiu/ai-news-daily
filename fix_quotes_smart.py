#!/usr/bin/env python3
import json

with open('/root/.openclaw/workspace/ai-news-site/data/content.json', 'r', encoding='utf-8') as f:
    raw = f.read()

# 状态机：只替换字符串值内部的中文引号
result = []
in_string = False
escape_next = False

for ch in raw:
    if escape_next:
        result.append(ch)
        escape_next = False
        continue
    
    if ch == '\\':
        result.append(ch)
        escape_next = True
        continue
    
    if not in_string:
        if ch == '"':
            in_string = True
        result.append(ch)
    else:
        # 在字符串内部
        if ch == '"':
            in_string = False
            result.append(ch)
        elif ch == '"':
            result.append('「')
        elif ch == '"':
            result.append('」')
        else:
            result.append(ch)

fixed = ''.join(result)

# 验证
try:
    data = json.loads(fixed)
    print('✅ JSON 验证通过！')
    with open('/root/.openclaw/workspace/ai-news-site/data/content.json', 'w', encoding='utf-8') as f:
        f.write(fixed)
    print('✅ content.json 已修复')
except json.JSONDecodeError as e:
    print(f'❌ 仍然失败: {e}')
    print(f'行 {e.lineno}')
    err_lines = fixed.split('\n')
    if e.lineno <= len(err_lines):
        print(f'内容: {err_lines[e.lineno-1]}')
        
    # 保存以便调试
    with open('/root/.openclaw/workspace/ai-news-site/data/content_debug.json', 'w', encoding='utf-8') as f:
        f.write(fixed)
    print('调试文件已保存到 content_debug.json')

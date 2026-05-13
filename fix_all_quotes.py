#!/usr/bin/env python3
import json

with open('/root/.openclaw/workspace/ai-news-site/data/content.json', 'r', encoding='utf-8') as f:
    raw = f.read()

# 方法：用更简单的方式——读取整个文件，逐行修复
lines = raw.split('\n')
fixed_lines = []
for line in lines:
    # 对于每一行，如果包含中文引号
    if '"' in line or '"' in line:
        # 替换所有中文引号为书名号
        line = line.replace('"', '「').replace('"', '」')
    fixed_lines.append(line)

fixed = '\n'.join(fixed_lines)

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

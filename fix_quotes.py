#!/usr/bin/env python3
import json
import re

# 读取 content.json，修复中文引号问题
with open('/root/.openclaw/workspace/ai-news-site/data/content.json', 'r', encoding='utf-8') as f:
    raw = f.read()

# 查找所有包含中文引号的行并修复
# 策略：把中文内容里的 "替换成「」
# 但只修复 value 中的，不修复 key 中的

# 简单方法：逐行处理
lines = raw.split('\n')
fixed_lines = []
for line in lines:
    # 如果是 JSON 字符串行（包含": "），修复其中文引号
    if '"' in line and ': "' in line:
        # 分离 key 和 value
        # 找到第一个": "后面的内容
        parts = line.split(': "', 1)
        if len(parts) == 2:
            key_part = parts[0]
            value_part = parts[1]
            # 如果 value 以 " 结尾
            if value_part.endswith('",'):
                inner = value_part[:-2]  # 去掉末尾",
                # 修复中文引号为书名号
                inner = inner.replace('"', '「').replace('"', '」')
                fixed = key_part + ': "' + inner + '",'
                fixed_lines.append(fixed)
            elif value_part.endswith('"'):
                inner = value_part[:-1]
                inner = inner.replace('"', '「').replace('"', '」')
                fixed = key_part + ': "' + inner + '"'
                fixed_lines.append(fixed)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

fixed_content = '\n'.join(fixed_lines)

# 验证修复后的 JSON 是否合法
try:
    data = json.loads(fixed_content)
    print("✅ JSON 验证通过！")
    
    # 保存修复后的文件
    with open('/root/.openclaw/workspace/ai-news-site/data/content.json', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    print("✅ content.json 已修复")
    
except json.JSONDecodeError as e:
    print(f"❌ JSON 仍有问题: {e}")
    print(f"错误位置: 行 {e.lineno}, 列 {e.colno}")
    # 显示错误行
    err_lines = fixed_content.split('\n')
    if e.lineno <= len(err_lines):
        print(f"内容: {err_lines[e.lineno-1]}")

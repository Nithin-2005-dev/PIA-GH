import sys
with open('scripts/platform_showcase/context.py', 'r') as f:
    content = f.read()

idx = content.find('"""Shared', 1)
if idx != -1:
    with open('scripts/platform_showcase/context.py', 'w') as f:
        f.write(content[idx:])

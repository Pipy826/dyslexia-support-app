import re
import ast

with open('app/api/auth.py', 'r', encoding='utf-8') as f:
    text = f.read()

fixed = text

fixed = re.sub(r'\?""(\s*\n)', '"""\\1', fixed)
fixed = re.sub(r"\?''(\s*\n)", "'''\\1", fixed)
fixed = re.sub(r'\?"', '"', fixed)
fixed = re.sub(r"\?'", "'", fixed)
fixed = re.sub(r'\?\)', ')', fixed)
fixed = re.sub(r'\?\n', '\n', fixed)
fixed = re.sub(r'\? ', ' ', fixed)
fixed = re.sub(r'\?$', '', fixed)
fixed = fixed.replace('\ufffd', '')
fixed = re.sub(r'\?([^a-zA-Z0-9_\-\.])', '\\1', fixed)
fixed = re.sub(r'\?$', '', fixed, flags=re.MULTILINE)

try:
    ast.parse(fixed)
    print('Syntax OK!')
    with open('app/api/auth.py', 'w', encoding='utf-8') as f:
        f.write(fixed)
    print('Done')
except SyntaxError as e:
    print('SyntaxError at line ' + str(e.lineno) + ': ' + str(e.msg))
    lines = fixed.split('\n')
    start = max(0, e.lineno - 3)
    end = min(len(lines), e.lineno + 3)
    for i in range(start, end):
        marker = '>>>' if i == e.lineno - 1 else '   '
        print(marker + ' ' + str(i+1) + ': ' + repr(lines[i]))

import re
import ast

with open('app/api/auth.py', 'r', encoding='utf-8') as f:
    text = f.read()

fixed = text

# 1. Fix broken triple-quote docstrings ending with ?""
fixed = re.sub(r'\?"""', '"""', fixed)
fixed = re.sub(r"\?'''", "'''", fixed)

# 2. Fix ?""  at end of line (was triple quote, lost one ")
fixed = re.sub(r'\?""(\s*\n)', '"""\\1', fixed)

# 3. Fix known broken string literals - ? before closing quote
#    e.g. '悦读小灯?' -> '悦读小灯'
fixed = re.sub(r"\?'", "'", fixed)
fixed = re.sub(r'\?"', '"', fixed)

# 4. Fix ? before ) in function calls / raise statements
fixed = re.sub(r'\?\)', ')', fixed)

# 5. Remove remaining replacement chars
fixed = fixed.replace('\ufffd', '')

# 6. Fix remaining bare ? at end of string literals
#    Pattern: Chinese text followed by ? then newline (string not closed)
#    We need to add the closing quote
lines = fixed.split('\n')
result = []
i = 0
while i < len(lines):
    line = lines[i]
    # Check for unterminated double-quoted string
    # Simple: count " not preceded by backslash
    in_triple = False
    fixed_line = line
    
    # Count standalone double quotes (not triple)
    # Remove triple quotes first for counting
    temp = line.replace('"""', '').replace("'''", '')
    dq = temp.count('"')
    sq = temp.count("'")
    
    if dq % 2 == 1:
        # Odd number of double quotes - string not closed
        fixed_line = line.rstrip('\n') + '"\n' if line.endswith('\n') else line + '"'
    elif sq % 2 == 1:
        # Check it's not a contraction or similar
        # Only fix if line has Chinese chars (likely a Chinese string)
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in line)
        if has_chinese:
            fixed_line = line.rstrip('\n') + "'\n" if line.endswith('\n') else line + "'"
    
    result.append(fixed_line)
    i += 1

fixed = '\n'.join(result)

try:
    ast.parse(fixed)
    print('Syntax OK!')
    with open('app/api/auth.py', 'w', encoding='utf-8') as f:
        f.write(fixed)
    print('Done - auth.py fixed')
except SyntaxError as e:
    print('SyntaxError at line ' + str(e.lineno) + ': ' + str(e.msg))
    lines2 = fixed.split('\n')
    start = max(0, e.lineno - 4)
    end = min(len(lines2), e.lineno + 4)
    for idx in range(start, end):
        marker = '>>>' if idx == e.lineno - 1 else '   '
        print(marker + ' ' + str(idx+1) + ': ' + repr(lines2[idx]))

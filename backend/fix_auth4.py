import re
import ast

with open('app/api/auth.py', 'r', encoding='utf-8') as f:
    text = f.read()

fixed = text

# Fix broken triple-quote docstrings: ?""  -> """
fixed = re.sub(r'\?""(\s*\n)', '"""\\1', fixed)
fixed = re.sub(r"\?''(\s*\n)", "'''\\1", fixed)

# Fix string literals where ? appears before closing quote
fixed = re.sub(r'\?"', '"', fixed)
fixed = re.sub(r"\?'", "'", fixed)

# Fix ? before closing paren/bracket
fixed = re.sub(r'\?\)', ')', fixed)
fixed = re.sub(r'\?\]', ']', fixed)

# Remove replacement chars
fixed = fixed.replace('\ufffd', '')

# Now fix lines where a string literal is unterminated because
# the closing quote was lost. Pattern: line has an odd number of
# unescaped double-quotes (string not closed).
# Strategy: for each line, if it has an unclosed string, append the quote.
lines = fixed.split('\n')
result = []
for line in lines:
    # Count unescaped double quotes not in comments
    # Simple heuristic: if line has content after last Chinese char and ends
    # with a Chinese char (no closing quote), add the quote
    stripped = line.rstrip()
    if stripped and not stripped.endswith(('"""', "'''", '"', "'", ')', ']', ',', ':', '\\')):
        # Check if there's an open string on this line
        # Count double quotes
        dq = stripped.count('"') - stripped.count('\\"')
        sq = stripped.count("'") - stripped.count("\\'")
        # If odd number of double quotes, line has unclosed string
        if dq % 2 == 1:
            line = line.rstrip() + '"' + '\n' if line.endswith('\n') else line + '"'
        elif sq % 2 == 1:
            line = line.rstrip() + "'" + '\n' if line.endswith('\n') else line + "'"
    result.append(line)

fixed = '\n'.join(result)

try:
    ast.parse(fixed)
    print('Syntax OK!')
    with open('app/api/auth.py', 'w', encoding='utf-8') as f:
        f.write(fixed)
    print('Done')
except SyntaxError as e:
    print('SyntaxError at line ' + str(e.lineno) + ': ' + str(e.msg))
    lines2 = fixed.split('\n')
    start = max(0, e.lineno - 3)
    end = min(len(lines2), e.lineno + 3)
    for i in range(start, end):
        marker = '>>>' if i == e.lineno - 1 else '   '
        print(marker + ' ' + str(i+1) + ': ' + repr(lines2[i]))

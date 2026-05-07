with open('app/api/auth.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print('Total lines:', len(lines))
for i, line in enumerate(lines):
    stripped = line.rstrip()
    if '?' in stripped:
        last = stripped[-1] if stripped else ''
        second_last = stripped[-2] if len(stripped) >= 2 else ''
        if last == '?' or (second_last == '?' and last in ('"', "'")):
            print(str(i+1) + ': ' + repr(stripped))

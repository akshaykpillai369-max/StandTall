import subprocess
current_pid = 12345
result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq StandTall Pro.exe', '/NH', '/FO', 'CSV'], capture_output=True, text=True)
print('returncode:', result.returncode)
print('stdout:', repr(result.stdout))
if result.returncode == 0 and result.stdout.strip():
    for line in result.stdout.strip().split('\n'):
        if 'StandTall Pro.exe' in line:
            parts = line.split(',')
            print('parts:', parts)
            if len(parts) >= 2:
                pid_str = parts[1].strip('"')
                print('pid_str:', pid_str)
                try:
                    if int(pid_str) != current_pid:
                        print('Found other instance')
                except ValueError:
                    pass
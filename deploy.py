import subprocess
import sys

folders = [
    'assets', 'experiments', 'src',
]
files = [
    'main.py'
]

def upload_file(path):
    result = subprocess.run(
        ['mpremote', 'cp', path, ':'+path],
        capture_output=True,
        text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"mpremote failed to upload file {path}")

    return result.stdout

def upload_folder(path):
    result = subprocess.run(
        ['mpremote', 'cp', '-r', f'./{path}/', ':'],
        capture_output=True,
        text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"mpremote failed to upload folder {path}")


if __name__ == '__main__':
    for folder in folders:
        upload_folder(folder)
        print(f'{folder} folder uploaded.')

    for file in files:
        upload_file(file)
        print(f'{file} file uploaded.')

    print('Finished!')
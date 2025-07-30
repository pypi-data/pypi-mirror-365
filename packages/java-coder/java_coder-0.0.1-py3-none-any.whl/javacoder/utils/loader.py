import subprocess


def load_content(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        full_content = file.read()
    return full_content


def get_git_config_property(git_property):
    return subprocess.check_output(['git', 'config', git_property]).strip().decode('utf-8')

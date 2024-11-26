import argparse
import subprocess
import os


def get_commits(repo_path, date):
    command = ['git', '-C', repo_path, 'log', '--pretty=format:%H %P', f'--before={date}']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    print(f"Выполнена команда: {' '.join(command)}")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")

    if result.stderr.strip():
        print(f"Ошибки команды git log: {result.stderr.strip()}")

    commits = {}
    for line in result.stdout.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        if ' ' in line:
            hash, parents = line.split(' ', 1)
            commits[hash] = parents.split()
        else:
            hash = line
            commits[hash] = []
    print(f"Коммиты: {commits}")
    return commits


def generate_mermaid_graph(commits):
    mermaid_code = 'graph TD;\n'
    if not commits:
        mermaid_code += '    NoCommits\n'
    else:
        for commit, parents in commits.items():
            if not parents:
                mermaid_code += f'    {commit[:7]}[\"{commit[:7]}\"];\n'  # Узел без родителей
            for parent in parents:
                mermaid_code += f'    {commit[:7]} --> {parent[:7]};\n'
    print(f"Mermaid-код:\n{mermaid_code}")
    return mermaid_code


def render_mermaid(mermaid_code, renderer_path, output_image):
    with open('diagram.mmd', 'w') as f:
        f.write(mermaid_code)
    subprocess.run(f'"{renderer_path}" -i diagram.mmd -o {output_image}', shell=True)


def display_image(image_path):
    if os.name == 'nt':
        os.startfile(image_path)
    elif os.name == 'posix':
        subprocess.run(['open', image_path], check=False)
    else:
        print(f'Пожалуйста, откройте {image_path} вручную.')


def main():
    parser = argparse.ArgumentParser(description='Визуализация графа зависимостей коммитов.')
    parser.add_argument('repo_path', help='Путь к репозиторию.')
    parser.add_argument('date', help='Дата коммита в формате ГГГГ-ММ-ДД.')
    parser.add_argument('renderer_path', help='Путь к программе визуализации (mmdc).')
    args = parser.parse_args()

    commits = get_commits(args.repo_path, args.date)
    mermaid_code = generate_mermaid_graph(commits)
    output_image = 'commit_graph.png'
    render_mermaid(mermaid_code, args.renderer_path, output_image)
    display_image(output_image)


if __name__ == '__main__':
    main()

import os
import sys
import argparse
from pathlib import Path

EXTENSIONS = {
    'python': {'.py', '.txt'},
    'react': {'.js', '.jsx', '.ts', '.tsx', '.css', '.html', '.json'}
}

IGNORE_DIRS = {
    '__pycache__', '.git', '.pytest_cache', '.venv', 'venv', 'env', 'ENV',
    'node_modules', 'build', 'dist', '.next', '.vscode', '.idea', 'migrations'
}

OUTPUT_FILES = {
    'fastapi': 'fastapi_project.txt',
    'react': 'react_project.txt'
}

def should_ignore_dir(dirname):
    return dirname in IGNORE_DIRS or dirname.startswith('.')

def collect_files(start_path, extensions):
    start_path = Path(start_path)
    files = []
    for root, dirs, filenames in os.walk(start_path):
        dirs[:] = [d for d in dirs if not should_ignore_dir(d)]
        for filename in filenames:
            file_path = Path(root) / filename
            if file_path.suffix in extensions:
                rel_path = file_path.relative_to(start_path)
                files.append(rel_path)
    return sorted(files)

def extract_project(project_root, output_file, extensions):
    project_root = Path(project_root).resolve()
    if not project_root.exists():
        print(f"Pasta não encontrada: {project_root}")
        return False
    files = collect_files(project_root, extensions)
    if not files:
        print(f"Nenhum arquivo com extensões {extensions} encontrado em {project_root}")
        return False
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for rel_path in files:
            full_path = project_root / rel_path
            out_f.write(f"===== Arquivo: {rel_path} =====\n")
            try:
                with open(full_path, 'r', encoding='utf-8') as in_f:
                    out_f.write(in_f.read())
            except UnicodeDecodeError:
                try:
                    with open(full_path, 'r', encoding='latin-1') as in_f:
                        out_f.write(in_f.read())
                except Exception as e:
                    out_f.write(f"[Erro ao ler arquivo: {e}]\n")
            out_f.write("\n\n")
    print(f"Projeto extraído com sucesso: {output_file}")
    return True

def detect_projects(base_dir):
    base_dir = Path(base_dir)
    frontend = None
    backend = None

    if (base_dir / 'package.json').exists():
        frontend = base_dir
    elif any(base_dir.glob('*.py')) or (base_dir / 'requirements.txt').exists():
        backend = base_dir

    if not frontend or not backend:
        for item in base_dir.iterdir():
            if not item.is_dir() or should_ignore_dir(item.name):
                continue
            if (item / 'package.json').exists() and not frontend:
                frontend = item
            elif (any(item.glob('*.py')) or (item / 'requirements.txt').exists()) and not backend:
                backend = item

    return frontend, backend

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frontend', help='Caminho do projeto React')
    parser.add_argument('--backend', help='Caminho do projeto FastAPI')
    args = parser.parse_args()

    if not args.frontend and not args.backend:
        print("Procurando projetos no diretório atual...")
        frontend, backend = detect_projects(Path.cwd())
        if frontend:
            print(f"Frontend detectado: {frontend}")
            args.frontend = frontend
        if backend:
            print(f"Backend detectado: {backend}")
            args.backend = backend
        if not args.frontend and not args.backend:
            print("Nenhum projeto encontrado. Use --frontend e/ou --backend.")
            sys.exit(1)

    if args.frontend:
        extract_project(args.frontend, OUTPUT_FILES['react'], EXTENSIONS['react'])
    if args.backend:
        extract_project(args.backend, OUTPUT_FILES['fastapi'], EXTENSIONS['python'])
    print("Extração concluída.")

if __name__ == '__main__':
    main()
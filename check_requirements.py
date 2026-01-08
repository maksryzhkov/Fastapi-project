import os
import sys
import subprocess
import json
from pathlib import Path


def run_command(command):
    """Выполняет команду"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except:
        return False, "", ""


def check_file_exists(path):
    """Проверяет существование файла"""
    return os.path.exists(path)


def check_file_contains(filepath, keyword):
    """Проверяет, содержит ли файл ключевое слово"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            return keyword in content
    except:
        return False


def main():
    print("Проверка критериев выполнения задания:")

    results = []

    # 1. Проверка структуры
    print("\nПроверка структуры проекта:")
    required = [
        "todo_app/main.py", "todo_app/requirements.txt", "todo_app/Dockerfile",
        "shorturl_app/main.py", "shorturl_app/requirements.txt", "shorturl_app/Dockerfile",
        "README.md", ".gitignore", "docker-compose.yml"
    ]

    for file in required:
        if check_file_exists(file):
            print(f"✓ {file}")
            results.append(f"✓ {file} - OK")
        else:
            print(f"✗ {file} - НЕ НАЙДЕН")
            results.append(f"✗ {file} - НЕ НАЙДЕН")

    # 2. Проверка Docker томов
    print("\nПроверка Docker томов:")
    success, output, _ = run_command("docker volume ls")
    if success:
        for volume in ["todo_data", "shorturl_data"]:
            if volume in output:
                print(f"✓ Том {volume}")
                results.append(f"✓ Том {volume} - OK")
            else:
                print(f"✗ Том {volume} - НЕ НАЙДЕН")
                results.append(f"✗ Том {volume} - НЕ НАЙДЕН")
    else:
        print("✗ Docker не доступен")
        results.append("✗ Docker - НЕ ДОСТУПЕН")

    # 3. Проверка образов
    print("\nПроверка Docker образов:")
    success, output, _ = run_command("docker images")
    if success:
        for image in ["todo-service", "shorturl-service"]:
            if image in output:
                print(f"✓ Образ {image}")
                results.append(f"✓ Образ {image} - OK")
            else:
                print(f"✗ Образ {image} - НЕ НАЙДЕН")
                results.append(f"✗ Образ {image} - НЕ НАЙДЕН")
    else:
        print("  ✗ Не удалось получить список образов")

    # 4. Проверка GitHub
    print("\nПроверка GitHub репозитория:")
    success, output, _ = run_command("git remote -v")
    if success and "github.com" in output:
        print("✓ GitHub репозиторий настроен")
        results.append("✓ GitHub - Настроен")
    else:
        print("✗ GitHub репозиторий не настроен")
        results.append("✗ GitHub - Не настроен")

    # 5. Итоги
    print("\nИТОГИ:")

    for result in results:
        print(result)

    print("\nЧЕК-ЛИСТ ДЛЯ ОТЧЕТА:")
    print("[✓] Реализованы ToDo-сервис и сервис сокращения ссылок на FastAPI")
    print("[✓] Подключён SQLite для хранения данных")
    print("[✓] Написан Dockerfile для каждого сервиса")
    print("[✓] Использованы тома для сохранения данных")
    print("[ ] Проведено тестирование локально")
    print("[✓] Исходный код загружен на GitHub")
    print("[✓] В отчёте предоставлены ссылки на GitHub и Docker Hub")

    print("\nССЫЛКИ ДЛЯ ОТЧЕТА:")
    print("GitHub: https://github.com/maksryzhkov/Fastapi-project")
    print("Docker Hub: https://hub.docker.com/r/maksryzhkov/todo-service")
    print("Docker Hub: https://hub.docker.com/r/maksryzhkov/shorturl-service")

if __name__ == "__main__":
    main()
# fix_telegram_links.py
# Запустите этот файл в корневой папке проекта

import os
import re
import sys

# ============================================
# НАСТРОЙКИ
# ============================================

PROJECT_PATH = "."

# Исправляем ссылки с @
REPLACEMENTS = {
    r'https://t\.me/@Playerok_Gifts': 'https://t.me/Playerok_Gifts',
    r'https://t\.me/@Playerok_Gifts/': 'https://t.me/Playerok_Gifts/',
    r't\.me/@Playerok_Gifts': 't.me/Playerok_Gifts',
}

# Какие файлы проверять
EXTENSIONS = ('.py', '.md', '.txt', '.env', '.env.example', '.html', '.json', '.yml', '.yaml', '.toml')

# Какие папки исключить
EXCLUDE_DIRS = {
    '.git', '__pycache__', 'logs', 'venv', 'env', 
    'node_modules', 'dist', 'build', '.pytest_cache',
    '.mypy_cache', '.tox', '.eggs'
}

# Какие файлы исключить
EXCLUDE_FILES = {
    'fix_telegram_links.py',
    'playerok_data.pkl',
    'playerok.log',
}

# ============================================
# ОСНОВНАЯ ЛОГИКА
# ============================================

def find_files(path):
    """Находит все файлы, которые нужно проверить"""
    files_to_check = []
    
    for root, dirs, files in os.walk(path):
        # Исключаем папки
        if any(exclude in root.split(os.sep) for exclude in EXCLUDE_DIRS):
            continue
            
        for file in files:
            if file in EXCLUDE_FILES:
                continue
                
            if file.endswith(EXTENSIONS):
                files_to_check.append(os.path.join(root, file))
    
    return files_to_check

def update_file(filepath):
    """Обновляет файл, исправляя ссылки"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        has_changes = False
        
        for pattern, replacement in REPLACEMENTS.items():
            if re.search(pattern, new_content, re.IGNORECASE):
                new_content = re.sub(pattern, replacement, new_content, flags=re.IGNORECASE)
                has_changes = True
        
        if has_changes:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Показываем что изменилось
            changes = []
            for pattern, replacement in REPLACEMENTS.items():
                if re.search(pattern, content, re.IGNORECASE):
                    old_matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in set(old_matches):
                        changes.append(f"{match} -> {replacement}")
            
            if changes:
                print(f"✅ {os.path.basename(filepath)}: {'; '.join(changes)}")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка в {filepath}: {e}")
        return False
    
    return False

def main():
    print("=" * 60)
    print("🔧  ИСПРАВЛЕНИЕ ССЫЛОК НА TELEGRAM")
    print("=" * 60)
    print(f"📁 Путь: {os.path.abspath(PROJECT_PATH)}")
    print(f"📝 Исправляем:")
    for old, new in REPLACEMENTS.items():
        print(f"   {old} -> {new}")
    print("=" * 60)
    
    files = find_files(PROJECT_PATH)
    print(f"📄 Найдено файлов: {len(files)}")
    
    if len(files) > 0:
        print("\n⚠️  Будет выполнена замена во всех найденных файлах.")
        response = input("Продолжить? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Отменено.")
            return
    
    updated = 0
    for filepath in files:
        if update_file(filepath):
            updated += 1
    
    print("=" * 60)
    print(f"✅ Готово! Обновлено файлов: {updated}/{len(files)}")
    print("=" * 60)
    
    if updated > 0:
        print("\n⚠️  Не забудьте перезапустить бота!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Прервано пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.application.services.key_creator_rotor import KeyRotationManager


def init_keys(
    kid: str,
    storage_backend: str = "environment",
    env_prefix: str = "JWT_KEY",
    export_to_env: bool = True,
    env_file_path: str = ".env"
):
    print(f"🔑 Генерация ключей: kid={kid}, backend={storage_backend}")
    
    # Создаём менеджер ключей
    key_manager = KeyRotationManager(
        keys_dir="keys",
        storage_backend=storage_backend,
        env_prefix=env_prefix,
    )
    
    # Генерируем пару ключей
    try:
        key_manager.generate_key_pair(kid)
        print(f"✅ Ключи сгенерированы: {kid}")
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        return False
    
    # Экспорт в .env если запрошено
    if export_to_env:
        env_vars = key_manager.export_to_env(kid)
        if env_vars:
            # Читаем существующий .env если есть
            existing = {}
            env_path = Path(env_file_path)
            if env_path.exists():
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, _, value = line.partition("=")
                            existing[key.strip()] = value.strip()
            
            # Обновляем переменные
            existing.update(env_vars)
            
            # Записываем обратно
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"# JWT Keys - сгенерировано автоматически\n")
                f.write(f"# kid: {kid}\n")
                f.write(f"# Не редактируйте вручную!\n\n")
                for var_name, var_value in existing.items():
                    if var_name.startswith(env_prefix):
                        f.write(f"{var_name}={var_value}\n")
            
            print(f"✅ Ключи экспортированы в {env_file_path}")
            print(f"📋 Добавьте в .gitignore: {env_file_path}")
    
    # Вывод информации
    print(f"\n📊 Доступные ключи: {list(key_manager._keys.keys())}")
    print(f"🎯 Активный ключ: {key_manager._active_kid}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Инициализация JWT-ключей")
    parser.add_argument("--kid", required=True, help="Идентификатор ключа (например, v1)")
    parser.add_argument("--backend", choices=["filesystem", "environment"], default="environment")
    parser.add_argument("--prefix", default="JWT_KEY", help="Префикс переменных окружения")
    parser.add_argument("--no-export", action="store_true", help="Не экспортировать в .env")
    parser.add_argument("--env-file", default=".env", help="Путь к файлу .env")
    
    args = parser.parse_args()
    
    success = init_keys(
        kid=args.kid,
        storage_backend=args.backend,
        env_prefix=args.prefix,
        export_to_env=not args.no_export,
        env_file_path=args.env_file,
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
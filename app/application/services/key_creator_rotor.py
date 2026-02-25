from jose import jwt, JWTError, ExpiredSignatureError
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
import json
import os
import base64
import re

class KeyRotationManager:
    """
    Менеджер ротации ключей с поддержкой двух бэкендов:
    - filesystem (по умолчанию): ключи в файлах .pem
    - environment: ключи в переменных окружения (Base64)
    """
    
    def __init__(
        self, 
        keys_dir: str = "keys",
        storage_backend: str = "filesystem",  # "filesystem" | "environment"
        env_prefix: str = "JWT_KEY"
    ):
        self.keys_dir = keys_dir
        self.storage_backend = storage_backend
        self.env_prefix = env_prefix
        self._keys: Dict[str, Dict] = {}
        self._active_kid: Optional[str] = None
        
        if storage_backend == "filesystem":
            os.makedirs(keys_dir, exist_ok=True)
        
        self.load_keys()

    # ==================== Утилиты Base64 ====================
    
    @staticmethod
    def _encode_pem(pem: str) -> str:
        """Кодирование PEM-ключа в Base64 строку для env var"""
        return base64.b64encode(pem.encode('utf-8')).decode('utf-8')

    @staticmethod
    def _decode_pem(b64: str) -> str:
        """Декодирование Base64 строки обратно в PEM"""
        return base64.b64decode(b64.encode('utf-8')).decode('utf-8')

    @staticmethod
    def _is_base64(s: str) -> bool:
        """Проверка, является ли строка Base64"""
        if not s or len(s) < 10:
            return False
        try:
            # Убираем возможные переносы и проверяем валидность
            cleaned = re.sub(r'\s+', '', s)
            base64.b64decode(cleaned, validate=True)
            return True
        except Exception:
            return False

    # ==================== Генерация ключей ====================
    
    def generate_key_pair(self, kid: str) -> Tuple[str, str]:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        if self.storage_backend == "filesystem":
            self._save_keys_to_file(kid, private_pem, public_pem)
        # Для environment — ключи возвращаются, но не сохраняются автоматически
        # (см. export_to_env() для явного экспорта)
        
        return private_pem, public_pem

    def _save_keys_to_file(self, kid: str, private_pem: str, public_pem: str):
        with open(f"{self.keys_dir}/{kid}_private.pem", "w") as f:
            f.write(private_pem)
        with open(f"{self.keys_dir}/{kid}_public.pem", "w") as f:
            f.write(public_pem)

    # ==================== Загрузка ключей ====================
    
    def load_keys(self):
        """Загрузка ключей из выбранного бэкенда"""
        self._keys.clear()
        
        if self.storage_backend == "environment":
            self._load_keys_from_env()
        else:
            self._load_keys_from_filesystem()
        
        # Выбор активного ключа (последний созданный с приватным ключом)
        active_keys = [
            kid for kid, data in self._keys.items() 
            if data.get("private")
        ]
        if active_keys:
            self._active_kid = max(
                active_keys,
                key=lambda k: self._keys[k].get("created_at", datetime.min)
            )

    def _load_keys_from_filesystem(self):
        if not os.path.exists(self.keys_dir):
            return
        for filename in os.listdir(self.keys_dir):
            if filename.endswith("_public.pem"):
                kid = filename.replace("_public.pem", "")
                public_path = f"{self.keys_dir}/{filename}"
                private_path = f"{self.keys_dir}/{kid}_private.pem"
                
                with open(public_path, "r") as f:
                    public_key = f.read()
                
                private_key = None
                if os.path.exists(private_path):
                    with open(private_path, "r") as f:
                        private_key = f.read()
                
                self._keys[kid] = {
                    "public": public_key,
                    "private": private_key,
                    "created_at": datetime.fromtimestamp(os.path.getctime(public_path)),
                    "source": "filesystem"
                }

    def _load_keys_from_env(self):
        """
        Загрузка ключей из переменных окружения.
        Ожидаемый формат:
          JWT_KEY_V1_PRIVATE_B64=<base64>
          JWT_KEY_V1_PUBLIC_B64=<base64>
          JWT_KEY_V2_PRIVATE_B64=<base64>
          ...
        """
        # Поиск всех переменных с префиксом
        env_vars = {k: v for k, v in os.environ.items() if k.startswith(self.env_prefix)}
        
        # Группировка по kid: {kid: {type: value}}
        kids_data: Dict[str, Dict[str, str]] = {}
        pattern = re.compile(
            rf"^{self.env_prefix}_(?P<kid>.+?)_(?P<type>PRIVATE|PUBLIC)(_B64)?$"
        )
        
        for var_name, var_value in env_vars.items():
            match = pattern.match(var_name)
            if not match:
                continue
            kid = match.group('kid').lower()
            key_type = match.group('type').lower()
            is_b64 = '_B64' in var_name or self._is_base64(var_value)
            
            if kid not in kids_data:
                kids_data[kid] = {}
            
            if is_b64:
                try:
                    kids_data[kid][key_type] = self._decode_pem(var_value.strip())
                except Exception:
                    # Если декодирование не удалось, пробуем как plain PEM
                    kids_data[kid][key_type] = var_value
            else:
                kids_data[kid][key_type] = var_value
        
        # Формирование структуры ключей
        for kid, key_data in kids_data.items():
            if "public" not in key_data:
                continue
            self._keys[kid] = {
                "public": key_data["public"],
                "private": key_data.get("private"),
                "created_at": datetime.utcnow(),  # Нет точной даты из env
                "source": "environment"
            }

    # ==================== Экспорт в Environment ====================
    
    def export_to_env(self, kid: Optional[str] = None) -> Dict[str, str]:
        """
        Экспорт ключей в формат переменных окружения.
        Возвращает dict для использования в .env или CI/CD.
        
        Пример вывода:
        {
            "JWT_KEY_V1_PRIVATE_B64": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0t...",
            "JWT_KEY_V1_PUBLIC_B64": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0..."
        }
        """
        result = {}
        kids_to_export = [kid] if kid else list(self._keys.keys())
        
        for k in kids_to_export:
            if k not in self._keys:
                continue
            kid_upper = k.upper().replace('-', '_')
            data = self._keys[k]
            
            if data.get("private"):
                result[f"{self.env_prefix}_{kid_upper}_PRIVATE_B64"] = self._encode_pem(data["private"])
            result[f"{self.env_prefix}_{kid_upper}_PUBLIC_B64"] = self._encode_pem(data["public"])
        
        return result

    def print_env_export(self, kid: Optional[str] = None):
        """Вывод ключей в формате .env для копирования"""
        env_vars = self.export_to_env(kid)
        print(f"# Добавьте эти переменные в .env или CI/CD secrets:")
        print(f"# Префикс: {self.env_prefix}")
        for var_name, var_value in env_vars.items():
            # Перенос длинных строк для удобства
            wrapped_value = var_value
            print(f"{var_name}={wrapped_value}")

    # ==================== Управление ключами ====================
    
    def get_active_key(self) -> Tuple[str, str, str]:
        """Получение активной пары ключей: (kid, private_pem, public_pem)"""
        if not self._active_kid:
            raise RuntimeError("Нет активного ключа. Сгенерируйте ключи или загрузите их.")
        key_data = self._keys[self._active_kid]
        if not key_data.get("private"):
            raise RuntimeError(f"Приватный ключ для {self._active_kid} недоступен (возможно, выведен из эксплуатации)")
        return self._active_kid, key_data["private"], key_data["public"]

    def get_public_keys(self) -> Dict[str, str]:
        """Получение всех публичных ключей для верификации"""
        return {kid: data["public"] for kid, data in self._keys.items()}

    def rotate_keys(self, new_kid: Optional[str] = None) -> str:
        """Создание новой пары ключей и активация"""
        if not new_kid:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            new_kid = f"key-{timestamp}"
        
        private_pem, public_pem = self.generate_key_pair(new_kid)
        
        # Если backend = environment, выводим инструкцию
        if self.storage_backend == "environment":
            print(f"\n⚠️  Backend: environment")
            print(f"Сгенерирован ключ: {new_kid}")
            print("Добавьте эти переменные в окружение:\n")
            self.print_env_export(new_kid)
            print(f"\nПосле добавления переменных перезапустите приложение.")
        
        self.load_keys()
        return new_kid

    def retire_key(self, kid: str):
        """Удаление приватного ключа (вывод из эксплуатации)"""
        if kid not in self._keys:
            raise ValueError(f"Ключ {kid} не найден")
        
        if self.storage_backend == "filesystem":
            private_path = f"{self.keys_dir}/{kid}_private.pem"
            if os.path.exists(private_path):
                os.remove(private_path)
        
        # В любом случае удаляем из памяти
        self._keys[kid]["private"] = None
        self.load_keys()

    # ==================== JWKS ====================
    
    def get_jwks(self) -> Dict:
        """Формирование JWKS для публикации"""
        keys = []
        for kid, data in self._keys.items():
            public_key = serialization.load_pem_public_key(
                data["public"].encode(), backend=default_backend()
            )
            numbers = public_key.public_numbers()
            keys.append({
                "kty": "RSA",
                "kid": kid,
                "use": "sig",
                "alg": "RS256",
                "n": base64.urlsafe_b64encode(
                    numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, 'big')
                ).rstrip(b'=').decode('utf-8'),
                "e": base64.urlsafe_b64encode(
                    numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, 'big')
                ).rstrip(b'=').decode('utf-8'),
            })
        return {"keys": keys}


class RotationJWT:
    def __init__(self, key_manager: KeyRotationManager, algorithm: str = "RS256"):
        self.key_manager = key_manager
        self.algorithm = algorithm

    def create_token(self, payload: Dict, expires_in: int = 3600) -> str:
        kid, private_key, _ = self.key_manager.get_active_key()
        now = datetime.now()
        payload.update({
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
            "nbf": int(now.timestamp())
        })
        headers = {"kid": kid, "alg": self.algorithm, "typ": "JWT"}
        return jwt.encode(payload, private_key, algorithm=self.algorithm, headers=headers)

    def verify_token(self, token: str) -> Dict:
        try:
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            if not kid:
                raise JWTError("Отсутствует kid в заголовке токена")
            
            public_keys = self.key_manager.get_public_keys()
            if kid not in public_keys:
                raise JWTError(f"Неизвестный kid: {kid}. Доступные: {list(public_keys.keys())}")
            
            return jwt.decode(
                token,
                public_keys[kid],
                algorithms=[self.algorithm],
                options={"verify_exp": True, "verify_nbf": True, "verify_iat": True}
            )
        except ExpiredSignatureError:
            raise JWTError("Токен истёк")
        except JWTError:
            raise
        except Exception as e:
            raise JWTError(f"Ошибка верификации: {str(e)}")
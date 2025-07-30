# 🔐 JWTifyPy

**JWTifyPy** — это легковесная и расширяемая Python-библиотека для генерации и проверки JWT-токенов с поддержкой различных алгоритмов (`HS256`, `ES256`, `RS256` и др.).  
Библиотека построена поверх [PyJWT](https://pyjwt.readthedocs.io/) и предоставляет интуитивный интерфейс, удобную конфигурацию и безопасное хранилище ключей — всё, что нужно для работы с JWT.

---

## 📦 Установка

```bash
pip install jwtifypy
````

## ⚙️ Опциональные зависимости

Для работы с переменными окружения (`.env`) и криптографическими алгоритмами (`ES256`) используются дополнительные пакеты: `python-dotenv` и `cryptography`.
Они подключаются как опциональные зависимости и **не устанавливаются по умолчанию**.

Чтобы установить библиотеку с нужными дополнительными пакетами, используйте extras:

* С поддержкой переменных окружения (dotenv):

```bash
pip install jwtifypy[env]
```

* С поддержкой криптографии:

```bash
pip install jwtifypy[crypto]
```

* Полный набор дополнительных возможностей:

```bash
pip install jwtifypy[full]
```

## 🚀 Быстрый старт

### 🔧 Инициализация

```python
from jwtifypy import JWTConfig

JWTConfig.init(config={
    "keys": {
        "algorithm": "HS256",
        "secret": "env:MY_SECRET_ENV"
    }
})
```

### 🔹 Базовые примеры

```python
from jwtifypy import JWTManager

# 📥 Токен по умолчанию (используется ключ "default")
token = JWTManager.create_access_token("user123")
print(token)
# 👉 eyJhbGciOiJIUzI1NiIsInR5cCI6...

# 🔑 Токен с именованным ключом
admin_token = JWTManager.using("admin").create_access_token("admin42")
print(admin_token)
# 👉 eyJhbGciOiJSUzI1NiIsInR5cCI6...
```

---

### 📛 Добавление issuer (iss)

```python
# 🧾 Токен с указанием issuer
token_with_issuer = (
    JWTManager.using("admin")
    .with_issuer("my-service")
    .create_access_token("issuer-user")
)
print(token_with_issuer)
```

---

### 🎯 Добавление audience (aud)

```python
# 🎯 Одиночная аудитория
token_with_aud = (
    JWTManager.using("admin")
    .with_audience("client-app")
    .create_access_token("aud-user")
)
print(token_with_aud)

# 📦 Множественная аудитория (для проверки)
token_with_multiple_aud = (
    JWTManager.using("admin")
    .with_audience(
        audience_for_encoding="web",
        audience_for_decoding=["web", "mobile"]
    )
    .create_access_token("multi-aud-user")
)
print(token_with_multiple_aud)
```

---

### 🤖 Удобное переиспользование менеджера

```python
# 🤖 Создание отдельного менеджера с выбранным ключом
JWTAdmin = JWTManager.using("admin")

# 🎯 Audience
token_with_aud = (
    JWTAdmin
    .with_audience("client-app")
    .create_access_token("aud-user")
)
print(token_with_aud)

# 🔗 Issuer + Audience вместе
token_full = (
    JWTAdmin
    .with_issuer("auth-server")
    .with_audience("bot")
    .create_access_token("full-user")
)
print(token_full)
```

---

### 🔍 Верификация токена с `iss` и `aud`

```python
payload = (
    JWTManager.using("admin")
    .with_issuer("auth-server")
    .with_audience("bot")
    .decode_token(token_full)
)

print(payload["sub"])  # 👉 full-user
print(payload["aud"])  # 👉 web
print(payload["iss"])  # 👉 auth-server
```

---

## ⚙️ Основные возможности

* ✅ Поддержка алгоритмов `HS256`, `ES256`, `RS256`, и др.
* 🔐 Хранилище ключей по именам (`default`, `admin`, `service-X`…)
* 📤 Простой интерфейс создания/декодирования JWT
* 🛠 Расширяемая архитектура для нестандартных сценариев
* ⏱ Поддержка стандартных claim'ов: `sub`, `exp`, `iat`, `aud`, и др.

---

## 🧩 Кастомная конфигурация

```python
from jwtifypy import JWTConfig

JWTConfig.init(config={
    "keys": {
        # 🔑 Симметричный ключ (HS256) — используется общий секрет
        "default": {
            "alg": "HS256",
            "secret": "secret"
        },

        # 🔐 Асимметричный ключ (RS256) — RSA, ключи читаются из файлов
        "admin": {
            "algorithm": "RS256",
            "private_key": "file:/path/to/private.pem",
            "public_key": "file:/path/to/public.pem"
        },

        # 🧬 Асимметричный ключ (ES256) — ECDSA, приватный ключ из переменной окружения
        # public_key будет автоматически сгенерирован, если установлена библиотека `cryptography`
        "service": {
            "alg": "ES256",
            "private_key": "env:PRIVATE_KEY"
        }
    },

    # ⏱ Leeway в секундах — допускаемая погрешность в проверке времени (exp, iat)
    "leeway": 1.0,

    # ⚙️ Дополнительные опции валидации (соответствуют PyJWT)
    "options": {
        "verify_sub": False,  # Не проверять наличие claim "sub"
        "strict_aud": False   # Для мягкой проверки audience
    }
})
```

---

## 🗂️ Структура проекта

```
jwtifypy/
├── __init__.py          # Основной интерфейс библиотеки
├── manager.py           # Класс JWTManager
├── config.py            # Конфигурация и инициализация
├── key.py               # Обработка ключей (HS/RS/ES)
├── store.py             # Хранилище JWTKeyStore
├── exceptions.py        # Кастомные исключения
└── utils.py             # Вспомогательные утилиты
```

---

## 🧪 Тестирование

```bash
pytest tests/
```

---

## 🛡️ Рекомендации по безопасности

* ❗ **Не храните секреты в коде.** Используйте переменные окружения.
* 🔐 Используйте `RS256`/`ES256` для межсервисной авторизации.
* ⏳ Устанавливайте короткое время жизни токенов (`exp`).
* 🔎 Включайте и проверяйте claims, если безопасность важна (`iss`, `aud`, `sub`).

---

## 📜 Лицензия

MIT © 2025
Created by \[LordCode Projects] / \[Dybfuo Projects]

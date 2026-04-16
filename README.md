# Telegram-бот напоминаний

## 

- **Бот:** [@bot_bot](https://t.me/bot_bot)
- **Презентация:** [Презентация](https://docs.google.com/presentation/d/1DhV1a41K_DPxv5WG9N_defYvAOZpuaX3lQPt--H8TQY/edit?usp=sharing)

---

## Описание проекта

Telegram-бот для напоминаний, написанный на Python с использованием библиотеки **aiogram 3**.

Бот позволяет пользователям создавать неограниченное количество напоминаний, удалять их, смотреть их статус. 

Все данные хранятся в локальной базе данных SQLite (`db.db`).


---

## Структура проекта

```
Python-1-Artemev/
├── main.py           # Основной файл бота (хэндлеры, логика)
├── base.py           # Класс SQL для работы с базой данных
├── config.py         # Токен бота (создаётся вручную, не хранится в репозитории)
├── db.db             # База данных SQLite
├── requirements.txt  # Зависимости проекта
       
```


## Инструкция по запуску на Windows

### 1. Клонирование / копирование проекта

Если проект уже есть на рабочем столе, этот шаг можно пропустить.

Если используете GitHub:

```bash
git clone https://github.com/ivan-artemev24/Python-1-Artemev
cd Python-1-Artemev
```

### 2. Создание и активация виртуального окружения

```powershell
# Создать виртуальное окружение (папка venv появится в корне проекта)
python -m venv venv

# Активировать окружение
.\venv\Scripts\Activate.ps1
```

При успешной активации в начале строки PowerShell появится префикс `(venv)`.

> **Если PowerShell выдаёт ошибку выполнения скриптов**, выполните один раз:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 3. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Настройка токена

Создайте файл `config.py` в корне проекта:

```python
TOKEN = "ваш_токен_от_BotFather"
```

Токен можно получить у [@BotFather](https://t.me/BotFather) в Telegram.

### 5. Запуск бота

```bash
python main.py
```

Бот запустится в режиме long polling. Для остановки нажмите `Ctrl+C`.

---

## Требования

- Python 3.10+
- Токен бота от [@BotFather](https://t.me/BotFather)
- Зависимости из `requirements.txt`:

```
aiogram==3.26.0
```

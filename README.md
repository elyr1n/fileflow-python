# FileFlow

FileFlow — это современная и легковесная система для загрузки, управления и удаления файлов в Django-приложениях. Она поддерживает предпросмотр изображений, PDF и текстовых файлов, использует Tailwind CSS для стильного и адаптивного интерфейса, а также позволяет гибко настраивать ограничения на размер файлов (по умолчанию до 512 МБ). Проект идеально подходит для веб-приложений, где требуется удобное управление файлами с минимальной сложностью.

## Особенности

- **Загрузка файлов**: Поддержка любых типов файлов с валидацией размера и типа (настраивается в `settings.py`).
- **Предпросмотр файлов**: Автоматическая генерация миниатюр для изображений (Pillow), PDF (pdf2image) и текстовых файлов.
- **Управление файлами**: Просмотр списка файлов, детальная информация, удаление с подтверждением.
- **Адаптивный интерфейс**: Современный дизайн на Tailwind CSS, оптимизированный для десктопов и мобильных устройств.
- **Гибкость**: Настраиваемые лимиты размера файлов, типы и дополнительные проверки.
- **Платежи (WIP)**: Планируется интеграция Stripe для подписок на дополнительное пространство.
- **Производительность**: Поддержка асинхронной обработки (опционально через Celery) и кэширования (Redis).

## Структура проекта

```
fileflow-python/
├── manage.py                  # Точка входа для Django-команд
├── requirements.txt           # Зависимости Python
├── fileflow/                 # Ядро логики работы с файлами
│   ├── __init__.py
│   ├── admin.py              # Настройка админ-панели
│   ├── apps.py               # Конфигурация приложения
│   ├── migrations/           # Миграции базы данных
│   ├── models.py             # Модель File (метаданные файлов)
│   ├── urls.py               # URL-маршруты
│   ├── views.py              # Логика загрузки, предпросмотра, удаления
│   └── utils.py              # Утилиты (валидация, обработка файлов)
├── uploader/                 # Фронтенд-интерфейс
│   ├── __init__.py
│   ├── admin.py              # Админ-панель (опционально)
│   ├── apps.py               # Конфигурация приложения
│   ├── migrations/           # Миграции
│   ├── models.py             # Дополнительные модели (если нужно)
│   ├── templates/uploader/   # HTML-шаблоны
│   │   ├── base.html         # Базовый шаблон с Tailwind CSS
│   │   ├── uploader.html     # Форма загрузки
│   │   ├── file_detail.html  # Страница деталей файла
│   │   └── file_list.html    # Список всех файлов
│   ├── urls.py               # URL-маршруты
│   └── views.py              # Представления интерфейса
├── payments/                 # Модуль платежей (WIP)
│   ├── __init__.py
│   ├── models.py             # Модели для подписок и транзакций (TODO)
│   ├── views.py              # Webhooks и checkout (TODO)
│   ├── urls.py               # URL-маршруты (TODO)
│   └── migrations/           # Миграции (TODO)
```

- **fileflow/**: Основная логика — модель `File`, обработка загрузки/удаления, генерация превью.
- **uploader/**: Пользовательский интерфейс — формы, списки файлов, адаптивные шаблоны.
- **payments/**: Заготовка для Stripe-интеграции (требует доработки).

## Требования

- Python 3.9+
- PostgreSQL (рекомендуется для production)
- Redis (опционально, для кэширования)

## Установка

1. **Клонируйте репозиторий**:
   ```
   git clone https://github.com/elyr1n/fileflow-python.git
   cd fileflow-python
   ```

2. **Создайте виртуальное окружение и установите зависимости**:
   ```
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Настройте окружение**:
   Скопируйте `.env.example` в `.env` и заполните:
   ```
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_NAME=fileflow_db
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
   FILE_UPLOAD_MAX_MEMORY_SIZE=524288000  # 512 MB
   ```

4. **Настройте базу данных**:
   - Установите PostgreSQL и создайте базу/пользователя.
   - Выполните миграции:
     ```
     python manage.py makemigrations
     python manage.py migrate
     ```

5. **Соберите статические файлы**:
   ```
   python manage.py collectstatic --noinput
   ```

6. **Запустите сервер**:
   ```
   python manage.py runserver
   ```
   Откройте [http://127.0.0.1:8000/uploader/](http://127.0.0.1:8000/uploader/) для интерфейса.

7. **Создайте суперпользователя** (для админки):
   ```
   python manage.py createsuperuser
   ```
   Админка: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

### Для production
- Используйте Gunicorn + NGINX.
- Установите `DEBUG=False` и настройте HTTPS.
- Настройте `ALLOWED_HOSTS` и подключите Redis для кэширования.

## Использование

1. **Загрузка файла**:
   - Перейдите на `/uploader/`.
   - Выберите файл (макс. размер — из настроек).
   - Файл сохраняется в `media/files/`, метаданные — в базе данных.

2. **Просмотр файлов**:
   - Список: `/uploader/file-list/`.
   - Детали: `/uploader/file/<id>/` (с предпросмотром).

3. **Удаление**:
   - Подтвердите удаление на странице деталей файла.

Пример кода (uploader/views.py):
```python
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import UploadFile

@login_required
def uploader(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        if uploaded_file:
            max_size_bytes = request.user.max_file_size()
            if uploaded_file.size > max_size_bytes:
                messages.error(
                    request,
                    f"Файл превышает допустимый размер {max_size_bytes // (1024*1024)} МБ",
                )
                return redirect("uploader:uploader")
            obj = UploadFile(user=request.user, file=uploaded_file)
            obj.save()
            messages.success(request, "Файл успешно загружен!")
            return redirect("uploader:uploader")
        messages.error(request, "Вы не выбрали файл!")
    files = UploadFile.objects.filter(user=request.user).order_by("-uploaded_at")
    return render(request, "uploader/uploader.html", {"files": files})
```

## Зависимости

См. `requirements.txt`:
- Django>=4.2
- Pillow>=10.0
- pdf2image>=1.16
- stripe>=7.0
- psycopg2-binary>=2.9
- python-dotenv>=1.0

## Платежи (WIP)

Модуль `payments/` находится в разработке. Планируется:
- Webhooks для обработки событий.
- Модели для транзакций и подписок.
- Рефакторинг кода.

Для активации:
1. Получите ключи Stripe (тестовые или боевые).
2. Настройте `.env` с `STRIPE_SECRET_KEY` и `STRIPE_PUBLISHABLE_KEY`.
3. Доработайте `payments/views.py` и `payments/models.py`.

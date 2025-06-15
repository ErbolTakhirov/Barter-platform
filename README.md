# Django Bartering Platform
**Веб-платформа для обмена товарами между пользователями, построенная на Django с REST API и современным веб-интерфейсом.
Платформа позволяет пользователям:**

- Размещать объявления о товарах для обмена
- Искать и фильтровать объявления по категориям и состоянию
- Отправлять предложения обмена другим пользователям
- Управлять входящими и исходящими предложениями
- Использовать REST API для интеграции с другими приложениями

## Основные возможности:
- Управление объявлениями
- Создание, редактирование и удаление объявлений
- Загрузка изображений по URL
- Категоризация товаров (электроника, одежда, книги и др.)
- Указание состояния товара (новый, б/у, с дефектами)
- Поиск и фильтрация
- Поиск по названию и описанию
- Фильтрация по категориям и состоянию
- Пагинация результатов
- Система обмена
- Отправка предложений обмена
- Управление статусами предложений (ожидание, принято, отклонено)
- Просмотр истории всех предложений

## REST API

- Полнофункциональный API для всех операций
- Аутентификация и авторизация
- Документированные эндпоинты

## Технологии

- Backend: Django 4.2+, Django REST Framework
- Database: SQLite (по умолчанию)
- Frontend: Bootstrap 5, HTML/CSS/JavaScript
- Дополнительно: Pillow, django-filter


# Пошаговая установка

1) Клонируйте репозиторий
```
git clone https://github.com/ErbolTakhirov/Barter-platform.git
```
2)Создайте виртуальное окружение
```
python -m venv venv
source venv/bin/activate  #  Linux/Mac

venv\Scripts\activate  #  Windows
```
3) Установите зависимости
```
pip install -r requirements.txt
```
4) Настройте базу данных
```
cd barter_platform
python manage.py makemigrations
python manage.py migrate
```
5) Создайте суперпользователя
```
python manage.py createsuperuser
```

6) Запустите сервер разработки
```
python manage.py runserver
```
Сайт будет доступен по адресу: http://127.0.0.1:8000/
Структура проекта
```
barter_platform/
├── manage.py
├── requirements.txt
├── README.md
├── barter_platform/          #  Основные настройки Django
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── ads/                      #  Приложение объявлений
    ├── __init__.py
    ├── admin.py             #  Админ-панель
    ├── models.py            #  Модели данных
    ├── views.py             #  Веб-представления
    ├── api_views.py         #  API представления
    ├── forms.py             #  Формы
    ├── urls.py              #  URL маршруты
    ├── serializers.py       #  API сериализаторы
    ├── tests.py
    ├── migrations/
    └── templates/           #  HTML шаблоны
        └── ads/
```

Объявления
```
GET /api/ads/ - Список всех объявлений
POST /api/ads/ - Создание нового объявления
GET /api/ads/{id}/ - Получение объявления по ID
PUT /api/ads/{id}/ - Обновление объявления
DELETE /api/ads/{id}/ - Удаление объявления
GET /api/ads/my_ads/ - Объявления текущего пользователя
```
Предложения обмена
```
GET /api/proposals/ - Список предложений пользователя
POST /api/proposals/ - Создание предложения обмена
PUT /api/proposals/{id}/ - Обновление статуса предложения
GET /api/proposals/sent/ - Отправленные предложения
GET /api/proposals/received/ - Полученные предложения
```
## Параметры фильтрации

?category=electronics - Фильтр по категории
?condition=new - Фильтр по состоянию
?search=телефон - Поиск по тексту

# Использование
# Веб-интерфейс

Регистрация/Авторизация: Используйте админ-панель Django (/admin/)
Создание объявления: Перейдите в "Создать объявление"
Поиск товаров: Используйте фильтры на главной странице
Предложение обмена: На странице товара выберите свой товар для обмена

## API
## Пример создания объявления через API:
import requests

```
url = 'http://127.0.0.1:8000/api/ads/'
data = {
    'title': 'iPhone 12',
    'description': 'Отличное состояние, полный комплект',
    'category': 'electronics',
    'condition': 'used',
    'image_url': 'https://example.com/iphone.jpg'
}

response = requests.post(url, json=data, auth=('username', 'password'))
```
# Настройка
## Основные настройки в settings.py:

```
LANGUAGE_CODE = 'ru-RU' - Русский язык интерфейса
TIME_ZONE = 'Asia/Bishkek' - Часовой пояс Бишкека
DEBUG = True - Режим разработки
Настройки REST Framework для API
```

## Изменение базы данных
Для использования PostgreSQL вместо SQLite:
```
pythonDATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'barter_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
## Тестирование
Модели данных
Ad (Объявление)

- title - Заголовок
- description - Описание
- image_url - URL изображения
- category - Категория товара
- condition - Состояние товара
- user - Владелец объявления

## ExchangeProposal (Предложение обмена)

- ad_sender - Объявление отправителя
- ad_receiver - Объявление получателя
- comment - Комментарий к предложению
- status - Статус (ожидает/принято/отклонено)

## Безопасность

Аутентификация пользователей через Django Auth
Авторизация на уровне API и веб-интерфейса
Валидация данных на стороне сервера
CSRF защита для форм


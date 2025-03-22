# Блогикум

### ОПИСАНИЕ
**Блогикум** — это блог-платформа, разработанная на Django, которая позволяет пользователям публиковать посты, комментировать их, управлять профилем и взаимодействовать с контентом. Проект включает в себя множество функций, таких как пагинация, загрузка изображений, отложенные публикации и кастомные страницы ошибок.

Проект решает следующие задачи:
1. Пользователи могут регистрироваться, авторизоваться и управлять своим профилем.
2. Аутентифицированные пользователи могут создавать, редактировать и удалять посты, а также прикреплять к ним изображения.
3. Реализована возможность комментирования постов. Только автор комментария может изменять или удалять его.
4. Посты могут быть отложенными (публикация в будущем) и привязаны к категориям и местоположениям.
5. Администраторы могут управлять категориями, местоположениями и пользователями через административную панель.
6. Реализованы кастомные страницы для ошибок 403, 404 и 500.

Проект будет полезен для разработчиков, которые хотят создать блог-платформу с расширенными возможностями управления контентом и пользователями.

### СТЕК
- Python 3.9
- Django 3.2.16
- Django Bootstrap5 22.2
- Pillow 9.3.0 (для работы с изображениями)
- Faker 12.0.1 (для тестовых данных)
- Flake8 5.0.4 (для проверки кода)
- Pytest 7.1.3 (для тестирования)
- BeautifulSoup4 4.11.2 (для тестирования HTML)

### КАК ЗАПУСТИТЬ ПРОЕКТ

Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone https://github.com/DmitryProtasevich/blogicum-django.git
cd blogicum-django
```
Создать и активировать виртуальное окружение:
```bash
python3 -m venv env
source env/bin/activate  # для Linux/MacOS
# или
env\Scripts\activate  # для Windows
```
Установить зависимости из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
Выполнить миграции:
```bash
python3 manage.py migrate
```
Создать суперпользователя (для доступа к административной панели):
```bash
python3 manage.py createsuperuser
```
Запустить проект:
```bash
python3 manage.py runserver
```
Перейти в браузере по адресу: http://127.0.0.1:8000/.

АДМИНИСТРАТИВНАЯ ПАНЕЛЬ
Для доступа к административной панели перейдите по адресу:
```bash
http://127.0.0.1:8000/admin/
```
Используйте данные суперпользователя, созданного на этапе установки.

# ОСНОВНЫЕ ФУНКЦИИ
- Регистрация и авторизация:  
- Пользователи могут регистрироваться и авторизоваться.  
- Возможность редактирования профиля, изменения пароля и данных пользователя.  

# Публикация постов:  
- Создание, редактирование и удаление постов.  
- Прикрепление изображений к постам.  
- Отложенные публикации (посты с будущей датой публикации).  

# Комментирование:  
- Добавление, редактирование и удаление комментариев.  
- Комментирование доступно только авторизованным пользователям.  

# Пагинация:  
- Ограничение вывода постов на главной странице, странице пользователя и странице категории (не более 10 постов на страницу).  

# Категории и местоположения:  
- Посты могут быть привязаны к категориям и местоположениям.  
- Управление категориями и местоположениями доступно только администраторам.  

# Кастомные страницы ошибок:  
Страницы для ошибок 403, 404 и 500.  

# ТЕСТИРОВАНИЕ
Для запуска тестов используйте команду:
```bash
pytest
```
# АВТОР  
Дмитрий Протасевич  
GitHub: https://github.com/DmitryProtasevich  
Telegram: https://t.me/DmitryProtasevich/

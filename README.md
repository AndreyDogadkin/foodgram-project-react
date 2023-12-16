# **FOODGRAM PROJECT**

## О проекте:
Foodgram — социальная сеть для обмена рецептами любимых блюд. 
Это полностью рабочий проект, который состоит из бэкенд-приложения на Django 
и фронтенд-приложения на React.
___
## Деплой на сервер:

### **Установите Docker и Docker Compose**
В домашней дирректории поочередно выполните следующие команды:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin 
```
Проверьте, что Docker работает:
```
sudo systemctl status docker 
```
___

### **Установите и запустите Nginx:**

```
sudo apt install nginx -y
```

```
sudo systemctl start nginx
```

**Отредактируйте файл конфигурации:**

```
sudo nano /etc/nginx/sites-enabled/default
```

Новое содержимое файла:
```
server {
    server_name # Ваш адрес сервера;

    location / {
        proxy_pass http://127.0.0.1:10000;
    }
```

Для проверки конфигурации:

```
sudo nginx -t
```

**Укажите файрволу, какие порты должны остаться открытыми и активируйте его:**

```
sudo ufw allow OpenSSH
```
```
sudo ufw allow 'Nginx Full'
```

```
sudo ufw enable
```

**Перезагрузите Nginx:**

```
sudo systemctl reload nginx
```
____
### **Разверните Foodgram:**
- Создайте дирректорию проекта
- Скопируйте в созданную дирректорию файл docker-compose.production.yml
- Создайте файл .env на основе .env.example
```
# Содержимое файла .env.example
POSTGRES_DB=  #str
POSTGRES_USER=  #str
POSTGRES_PASSWORD=  #str
DB_NAME=  #str
DB_HOST=  #str
DB_PORT=  #int

SECRET_KEY=  # Сгенерируйте секретный ключ для Django
DEBUG=  #bool
ALLOWED_HOSTS=  # Список разрешенных хостов через запятую
```
Выполните команду для запуска Docker Compose в режиме демона:

```
sudo docker compose -f docker-compose.production.yml up -d 
```
Выполните миграции, соберите статические файлы бэкенда:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/ 
```
Деплой выполнен.
___
## Получение SSL-сертификата:

**Установите пакетный менеджер snap:**
```
sudo apt install snapd
```
```
sudo snap install core; sudo snap refresh core
```

**Установите certbot:**
```
sudo snap install --classic certbot
```
Добавьте доступ к пакету с правами администратора:
```
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```
**Запустите certbot и получите SSL-сертификат:**
```
sudo certbot --nginx
```
**Укажите имена, для которых вы хотели бы активировать HTTPS отправив соответвующую цифру:**
```
Account registered.
Which names would you like to activate HTTPS for?
We recommend selecting either all domains, or all domains
in a VirtualHost/server block.
1: <доменное_имя_вашего_проекта_1>
2: <доменное_имя_вашего_проекта_2>
3: <доменное_имя_вашего_проекта_3>
...
Select the appropriate numbers separated by commas and/or spaces, or leave input
blank to select all options shown (Enter 'c' to cancel):
```
После этого certbot отправит ваши данные на сервер Let's Encrypt и там будет выпущен сертификат, 
который автоматически сохранится на вашем сервере в системной директории /etc/ssl/. 
Также будет автоматически изменена конфигурация Nginx: в файл /etc/nginx/sites-enbled/default 
добавятся новые настройки и будут прописаны пути к сертификату.

**Выполните проверку и перезапуск кофигурационного файла:**
```
sudo nginx -t
```
```
sudo systemctl reload nginx
```
___
## Ипользуемые библиотеки:
- Django 3.2.3
- djangorestframework 3.12.4
- djoser 2.1.0
- webcolors 1.11.1
- Pillow 9.0.0
- pytest 6.2.4
- pytest-django 4.4.0
- pytest-pythonpath 0.7.3
- environs
- gunicorn 20.1.0
- npm
- nodejs
- nginx
- certbot

___
## Авторы:

- [@yandex-praktikum](https://github.com/yandex-praktikum) 
- [@AndreyDogadkin](https://github.com/AndreyDogadkin)
___

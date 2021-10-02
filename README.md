# Дипломный проект курса Python-разработчик от Яндекс.Практикума
### Описание
Данный проект выполняется для курса Python-разработчик от Яндекс.Практикума

[![Django-app workflow](https://github.com/Darioing/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/Darioing/foodgram-project-react/actions/workflows/main.yml)
### Технологии
В проекте используются:
- Python 3.8.5
- Django 3.0.5
- Docker
## Установка Docker
Для запуска проекта на cервере необходимо выполнить следующий ряд действий для операционной системы Ubuntu:
- Сделайте fork репозитория
- После fork'а склонируйте его себе на компьютер
```
git clone https://github.com/<ваш_username>/yamdb_final.git
```
- После этого удалите старые версии Docker(при их наличии) командой
```
sudo apt remove docker docker-engine docker.io containerd runc
```
- Обновите индексы пакетов командой 
```
sudo apt update
```
- После обновления индексов установите пакеты которые позволят загружать пакеты по протоколу HTTPS командой
```
sudo apt install \
apt-transport-https \
ca-certificates \
curl gnupg-agent \
software-properties-common -y
```
- Добавьте ключ GPG для подтверждения подлинности в процессе установки командой
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```
- Добавьте репозиторий Docker в пакеты apt командой
```
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```
- Так как в APT добавлен новый репозиторий необходиом обновить индекс пакетов
```
sudo apt update
```
- Устанавливаем Docker
```
sudo apt install docker-ce docker-compose -y
```
- Далее добавляем команду для запуска демона Docker при старте системы
```
sudo systemctl enable docker
```
## Запуск Docker
Для запуска проекта на локальном компьютере необходио выполнить следующий ряд действий:
- Открываем терминал в склонированной ранее папке
- Переходим в папку infra/
- Создаем файл .env с такими параметрами:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
- Поднимаем контейнеры Docker командой
```
sudo docker-compose up
```
- После этого применяем миграции командами
```
sudo docker-compose exec backend python3 manage.py makemigration
```
```
sudo docker-compose exec backend python3 manage.py migrate
```
- Создаем суперпользователя командой
```
sudo docker-compose exec backend python3 manage.py createsuperuser
```
- Проект поднимится локально и будет доступен по адресу http://0.0.0.0/
- Для перехода в панель администратора нужно перейти по адресу http://0.0.0.0/admin/

# Диплом

Создать файл <имя>.env

### Тестовый запуск
Файл - `test.env`
```commandline
sudo docker compose -f docker-compose-test.yml --env-file test.env up
```

### В режиме разработки
Файл - `dev.env`
```commandline
sudo docker compose -f docker-compose-dev.yml --env-file dev.env up
```

### Для деплоя
Файл = `.env`
```commandline
sudo docker compose --env-file .env up
```

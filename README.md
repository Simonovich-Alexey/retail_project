# Дипломный проект профессии «Python-разработчик: расширенный курс»

Приложение предназначено для автоматизации закупок в розничной сети через REST API.

## API

[Документация по запросам в PostMan](https://documenter.getpostman.com/view/34255099/2sA3rzHs3C)

## Запуск проекта

### Запуск PostgeSQL:
```bash
docker-compose --env-file .env_example up db -d
```

### Запуск Redis:
```bash
docker-compose --env-file .env_example up redis -d
```

### Запуск приложения:
```bash
docker-compose --env-file .env_example up retail_project nginx -d
```

### Суперпользователь

email - *root@example.com*

password - *root*
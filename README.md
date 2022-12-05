# Как запустить сервис?
1. Собрать докер контейнер 
   docker build -t scoring_service .
2. Запускаем 
   docker run -p 1234:1234 scoring_service

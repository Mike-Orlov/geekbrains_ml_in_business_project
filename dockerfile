# Какой образ берем за основу, например, python:3.7
FROM python:3.7
LABEL maintainer='orlov.msr@gmail.com'
# Копирует из текущей директории файлы в /app и потом делает её рабочей директорией
COPY . /app
WORKDIR /app
# Быстро выгрузить список библиотек для проекта
# pip freeze > requirements.txt (сразу в нужном формате)
RUN pip install -r requirements.txt
# 2 порта, т.к. будет 2 сервера, один API и один GUI, иначе хватило бы одного
EXPOSE 8180
EXPOSE 8181
# Тут будет лежать модель в формате .pkl (.dill)
# VOLUME - чтобы смонтировать виртуальную папку с реальной папкой на ПК
# а там локально будет лежать модель. Туда же можно сохранять отчеты/логи.
VOLUME /app/app/models
COPY ./docker-entrypoint.sh /
# Открываем файл на исполнение +eXecute
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

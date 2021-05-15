# python-flask-docker
Итоговый проект курса "Машинное обучение в бизнесе"

Стек:

ML: sklearn, pandas, numpy, xgboost
API: flask

Данные: с kaggle - https://www.kaggle.com/c/sberbank-russian-housing-market/data

Задача: предсказать цену жилья по известным признакам (общая площадь, год постройки дома, число комнат)

Используемые признаки:

- full_sq (float)
- build_year (int)
- num_room (int)

Преобразования признаков: NaN и нули заменяю на медиану.

Модель: xgboost

### Клонируем репозиторий и создаем образ
```
$ git clone https://github.com/Mike-Orlov/geekbrains_ml_in_business_project.git
$ cd geekbrains_ml_in_business_project
$ docker build -t course_project .
```

### Запускаем контейнер

Здесь Вам нужно создать каталог локально и сохранить туда предобученную модель (<your_local_path_to_pretrained_models> нужно заменить на полный путь к этому каталогу)
```
$ docker run -d -p 8180:8180 -p 8181:8181 -v <your_local_path_to_pretrained_models>:/app/app/models course_project
```

### Переходим на localhost:8181

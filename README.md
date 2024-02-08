# Megano Backend

Welcome to the Megano backend, a Django web application for managing a car dealership store.

## How to Download

Clone the repository. 

    > git clone https://gitlab.skillbox.ru/karen_teknedzhian/python_django_diploma.git

## How to run

### Development Version

***To start the development version <br>
(app + PostgreSQL + default server + Celery + Redis):***

1. First Set up the required environment variables. 

2. Build and up container with docker-compose file
     > docker-compose -f docker-compose.yml up --build

3. Open a new window of terminal and then go to container bash

     > docker-compose exec web /bin/sh

4. And then enter the command to the bash to load data from fixtures

     > python manage.py loaddata mycatalog/fixtures/custom_data.json

5. Now you can run auto tests
     
     > python manage.py test

6. If there isn`t any error you can open a page at:

     > http://127.0.0.1:8000/


### Production Version

***To start the production version <br>
(app + Postgresql + Nginx + gunicorn + celery + redis):***

1. First Set up the required environment variables. 

2. Build and up container with docker-compose file
     > docker-compose -f docker-compose.prod.yml up -d --build

3. Go to container bash

     > docker-compose exec web /bin/bash

4. If it is first start you have to run migrate:
   
     > python manage.py migrate

4. And then enter the command to the bash to load data from fixtures

     > python manage.py loaddata mycatalog/fixtures/custom_data.json

5. Now you can run auto tests
     
     > python manage.py test

6. If there isn`t any error you can open a page at:

     > http://localhost:1337/


Megano consists of several backend apps: 
- 
- **MyAuth**: Handles user authentication. 
- **MyCatalog**: Manages the catalog of cars, jeeps, and trucks. 
- **MyOrders**: Manages customer orders.

## Requirements 

The project dependencies are listed in the `requirements.txt` file.

## To look at swagger and api docs you have to go to

   > http://127.0.0.1:8000/api/schema/swagger-ui/ <br>
   > http://127.0.0.1:8000/api/schema/redoc/ 
   
or if you are use production version

   > http://localhost:1337/api/schema/swagger-ui/ <br>
   > http://localhost:1337/api/schema/redoc/
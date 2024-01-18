# Megano Backend

Welcome to the Megano backend, a Django web application for managing a car dealership store.

## How to Run

### Development Version

To start the development version (app + Postgres + default server):

## Getting Started To get started with Megano, follow these steps:
1. Clone the repository. 
 https://gitlab.skillbox.ru/karen_teknedzhian/python_django_diploma.git
2. Set up the required environment variables. 
3. Build and run the Docker containers.
'docker-compose -f docker-compose.prod.yml up -d --build'
4. If you are using production version, and it is first build you have to enter in container bash and run 'python manage.py migrate'. After that the data will save in volumes.
5. You can chak if the app is work by run in container bash:
'python manage.py test' (there are 15 test include almost all aspects which have to check for correct work)
6. To load data run:
'python manage.py loaddata mycatalog/fixtures/custom_data.json'
7. open http://127.0.0.1:8000/ to use develop version, 
8. open http://localhost:1337/ to use production version



## Docker Compose 

Two Docker Compose files are provided: 
- `docker-compose.yml`: For development.
- `docker-compose.prod.yml`: For production. 

## Frontend App
The frontend app is located in the `megano` directory. 

It includes the main Django application along with necessary configuration files.

Megano consists of several backend apps: 
- 
- **MyAuth**: Handles user authentication. 
- **MyCatalog**: Manages the catalog of cars, jeeps, and trucks. 
- **MyOrders**: Manages customer orders.

## Nginx Configuration 

The `nginx` directory contains the Nginx Dockerfile and configuration file. 

## Requirements 

The project dependencies are listed in the `requirements.txt` file.
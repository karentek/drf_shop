# pull official base image
FROM python:3.11.4-alpine
# set work directory
WORKDIR /usr/src/diploma

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#
#RUN pip install virtualenv
#RUN python -m virtualenv venv
#RUN /bin/bash -c "source venv/bin/activate"

# install system dependencies
#RUN apt-get update && apt-get install -y netcat

# install dependencies
RUN pip install --upgrade pip
COPY ./megano/requirements.txt .

RUN pip install -r requirements.txt
RUN pip install eventlet
#RUN pip install django-celery-beat



# copy entrypoint.sh
#COPY ./megano/entrypoint.sh usr/src/megano_app/entrypoint.sh
COPY ./megano/entrypoint.sh /usr/src/diploma/megano/entrypoint.sh

RUN sed -i 's/\r$//g' /usr/src/diploma/megano/entrypoint.sh
RUN chmod +x /usr/src/diploma/megano/entrypoint.sh

# copy project
COPY . .
# Enter the frontend directory and run setup.py
WORKDIR /usr/src/diploma/megano/diploma-frontend
RUN python setup.py sdist

# Install the generated tar.gz file
RUN pip install dist/diploma-frontend-0.6.tar.gz

WORKDIR /usr/src/diploma/megano

# run entrypoint.sh
ENTRYPOINT ["/usr/src/diploma/megano/entrypoint.sh"]
# Python base image
FROM python:3.11-slim

# set working directory
WORKDIR /app

# copy project
COPY . /app

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# environment variables for flask
ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0

# expose port
EXPOSE 5000

# default command
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

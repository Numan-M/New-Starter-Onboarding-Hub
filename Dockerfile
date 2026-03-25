# Python base image - pull rate limit workaround
FROM numanepa.azurecr.io/python:3.11-slim

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
EXPOSE 80

# default command
CMD ["python", "nsoh.py"]

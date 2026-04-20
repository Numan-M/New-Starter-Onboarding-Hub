# Python base image - pull rate limit workaround
FROM numanepa.azurecr.io/python:3.11-slim

# set working directory
WORKDIR /app

# copy project
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# expose port
EXPOSE 5000

# default command
CMD ["python", "app.py"]

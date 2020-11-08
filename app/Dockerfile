FROM python:3.8.6

WORKDIR usr/src/greevil-app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
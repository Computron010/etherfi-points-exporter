FROM python:3.12.3-slim-bullseye
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
ENV PORT=8000
CMD [ "python3", "main.py" ]
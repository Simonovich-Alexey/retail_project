FROM python:3.10-alpine
RUN apk add --no-cache gcc musl-dev linux-headers
RUN mkdir /app
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt .
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY . .
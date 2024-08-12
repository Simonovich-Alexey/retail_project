FROM python:3.10-alpine
RUN apk add --no-cache gcc musl-dev linux-headers
RUN mkdir /app
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt .
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD python manage.py migrate \
    && python manage.py collectstatic --no-input \
    && python manage.py shell -c "from api.models import CustomUser; CustomUser.objects.create_superuser(email='root@example.com', password='root')" \
    && gunicorn retail_project.wsgi:application --bind 0.0.0.0:8000
FROM python:3.9-slim
RUN apt-get update && apt-get install -y \
    libssl-dev \
    libffi-dev \
    build-essential \
    libsasl2-dev \
    libldap2-dev \
    && rm -rf /var/lib/apt/lists/*
COPY . /app


RUN pip install pyOpenSSL
RUN pip install --no-cache-dir -r /app/requirements.txt
EXPOSE 57309
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
CMD ["flask", "run"]

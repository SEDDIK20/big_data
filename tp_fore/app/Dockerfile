FROM python:3.12-slim
WORKDIR /app

# نسخ requirements.txt أولاً
COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    libgomp1 \
 && apt-get install -y \
    build-essential \
 && apt-get install -y \
    libatlas-base-dev \
 && apt-get install -y \
    libopenblas-dev \
 && apt-get install -y \
    gfortran \
 && apt-get install -y \
    libfreetype6 \
 && apt-get install -y \
    libpng-dev \
 && rm -rf /var/lib/apt/lists/*

# تثبيت الحزم عبر pip
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# نسخ باقي الملفات
COPY . .

CMD ["python", "app.py"]

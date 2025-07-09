# Python image
FROM python:3.11-slim

# Ishchi katalog
WORKDIR /app

# requirements.txt ni copy qilish
COPY requirements.txt .

# Kutubxonalarni o‘rnatish
RUN pip install --no-cache-dir -r requirements.txt

# Butun loyihani copy qilish
COPY . .

# Ustun port
EXPOSE 8000

# Loyihani ishga tushirish
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


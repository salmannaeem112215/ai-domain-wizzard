# ==========================
# 1️⃣ Use lightweight Python image
# ==========================
FROM python:3.11-slim

# ==========================
# 2️⃣ Set working directory
# ==========================
WORKDIR /app

# ==========================
# 3️⃣ Copy and install dependencies
# ==========================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==========================
# 4️⃣ Copy all source code
# ==========================
COPY . .

# ==========================
# 5️⃣ Set environment variables
# ==========================
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ==========================
# 6️⃣ Expose port & run app
# ==========================
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


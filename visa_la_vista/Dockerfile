FROM python:3.12
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Set working directory
WORKDIR /code

# --- NEW SECTION: Install System Dependencies ---
# We do this before pip install so that system tools are ready
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*
# -----------------------------------------------

# 3. Copy requirements (for cache optimization)
COPY requirements.txt .

# 4. Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy project
COPY . .

RUN python manage.py collectstatic --noinput

# 6. Set Environment Variables
ENV DJANGO_SETTINGS_MODULE=visa_la_vista.settings

# 8. Command to run server
CMD ["gunicorn", "visa_la_vista.wsgi:application", "--config", "gunicorn.conf.py"]
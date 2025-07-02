# Utilise une image officielle Python
FROM python:3.10-slim

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers de dépendances en premier (optimise le cache Docker)
COPY requirements.txt .

# Installe les dépendances système (pour psycopg2 par exemple) + pip requirements
RUN apt-get update && apt-get install -y gcc libpq-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc && apt-get autoremove -y

# Copie le code source
COPY . .

# Définit les variables d'environnement par défaut
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Expose le port sur lequel Gunicorn écoutera
EXPOSE 8000

# Commande de démarrage : collectstatic + migrations + gunicorn
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn automate_api.wsgi:application --bind 0.0.0.0:8000"]

# AnimeOnix Backend

The backend for [AnimeOnix](https://animeonix.win/), a platform where users can explore anime titles, write reviews, and rate both titles and reviews. Built with FastAPI and PostgreSQL, the backend provides a robust REST API to power the platform's features.

---

## Features

- **User Management**: Register, login, and manage user accounts.
- **Anime Titles**: Fetch, update, and display anime information.
- **Reviews and Ratings**: Users can write reviews, rate titles, and rate other reviews.
- **Secure API**: Authentication using JWT.
- **Scalable Deployment**: Optimized for Docker and Kubernetes environments.
- **CI/CD**: New changes in the project are delivered to production seamlessly and with zero downtime.

---

## Requirements

- **Python 3.9+**
- **Docker**
- **PostgreSQL 14+**
- Dependencies listed in `requirements.txt` (automatically installed with Docker).

---

## Getting Started

### Clone the repository

```bash
git clone https://github.com/Hepik/animeonix-back.git
cd animeonix-back
```

### Environment Variables

Copy the default `.default.env` file and update the values as needed:

```bash
cp .default.env .env
```

#### Example `.env` file:

```env
STATIC_DIR="/tmp"
SECRET_KEY='secretkey'
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
SENDER_EMAIL="example@gmail.com"
SENDER_PASSWORD="password"
PORT=8000
POSTGRES_DB="animeonix"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="password"
POSTGRES_PORT=5432
POSTGRES_HOST="db"
SQLALCHEMY_DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
CF_DNS_API_TOKEN="cftoken"
CF_API_EMAIL="example2@gmail.com"
FRONTEND_URL="http://localhost:3000"
BACKEND_URL="http://localhost:8000"
```

### Run Locally

To run the backend locally:

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:

   ```bash
   python .\main.py
   ```

3. The API will be available at: `http://localhost:8000`.

### Run with Docker

To run the backend in a containerized environment:

```bash
docker-compose up -d
```

This command starts all services (backend, database, Traefik, frontend).

---

## API Documentation

Interactive API documentation is available via Swagger UI:

- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Testing

Run unit tests with:

```bash
pytest
```

---

## Deployment

The backend is deployed using Docker and Traefik. Key deployment configurations:

### Docker Compose Configuration for backend

It`s just a backend part

```yaml
backend:
  image: ghcr.io/hepik/animeonix-back:latest
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.backend.rule=Host(`api.animeonix.win`)"
    - "traefik.http.routers.backend.entrypoints=websecure"
    - "traefik.http.routers.backend.tls=true"
    - "traefik.http.routers.backend.tls.certresolver=cloudflare"
  volumes:
    - static-data:/app/static
  env_file:
    - .env
  depends_on:
    - db
```

---

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b my-feature`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin my-feature`.
5. Open a pull request.

## Additional Information

For more details, visit the live website:
[AnimeOnix](https://animeonix.win/)

FrontEnd repository: [animeonix-front](https://github.com/Hepik/animeonix-front)

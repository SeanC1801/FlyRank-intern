
## Database Setup

Run PostgreSQL in Docker:
docker run --name taskdb -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=tasks -p 5432:5432 -v taskdata:/var/lib/postgresql -d postgres

Connect via psql:
docker exec -it taskdb psql -U postgres -d tasks

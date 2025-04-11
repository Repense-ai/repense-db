from repensedb.connections.factory import ConnectionFactory

# MySQL connection
mysql_url = "mysql://user:password@localhost:3306/mydatabase"
mysql_conn = ConnectionFactory.create(mysql_url)
mysql_conn.connect()

# Redis connection
redis_url = "redis://localhost:6379/0"
redis_conn = ConnectionFactory.create(redis_url)
redis_conn.connect()

# Docker Compose compatible URLs
docker_mysql = "mysql://user:password@mysql:3306/mydatabase"
docker_redis = "redis://redis:6379/0"

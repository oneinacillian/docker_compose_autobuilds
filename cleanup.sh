docker-compose down
docker volume rm autobuilds_node autobuilds_esdata1 autobuilds_esdata3 autobuilds_esdata2 autobuilds_node_modules autobuilds_rabbitmqdata autobuilds_redisdata autobuilds_hyperiondata
docker system prune -a --volumes
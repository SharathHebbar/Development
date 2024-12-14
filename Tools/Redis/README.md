# Redis

REmote DIctionary Service

- In memory Databases
- Runs on RAM
- It is a powerhouse


[Install Redis on Windows](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-windows/)

Installation Steps

```bash
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
```

```bash
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
```

```bash
sudo apt-get update
sudo apt-get install redis
```

start the Redis server like so:

```bash
sudo service redis-server start
```

Once Redis is running, you can test it by running redis-cli:

```bash
redis-cli
```

Test the connection with the ping command:

```
127.0.0.1:6379> ping
PONG
```
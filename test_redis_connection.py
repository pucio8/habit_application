import redis

r = redis.Redis(
  host='settling-chicken-15815.upstash.io',
  port=6379,
  password='AT3HAAIncDEyNmE2NmUzMjk2Mzk0MWE3OTc4MjI0YzUzODE4M2Y3YnAxMTU4MTU',
  ssl=True
)

r.set('foo', 'bar')
print(r.get('foo'))
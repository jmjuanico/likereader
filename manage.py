import os
import psycopg2
import urlparse

hardurl = "postgres://eftucjcsbhjhxo:6GJ7kzgFIhmgKYb041hVUdmYui@ec2-107-22-197-152.compute-1.amazonaws.com:5432/d1alnm3vi8kdem"
urlparse.uses_netloc.append("postgres")
# url = urlparse.urlparse(os.environ["DATABASE_URL"])
url = urlparse.urlparse(hardurl)

"""
print 'port: ' + str(url.port)
print 'hostname: ' + url.hostname
print 'hostname: ' + url.username
print 'password: ' + url.password
print 'database: ' + url.path[1:]
"""

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port,
    sslmode= 'require'
)

cur = conn.cursor()
cur.execute("select * from post")
results = cur.fetchall()
print results
for r in results:
    print r
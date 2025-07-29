# core-db
_______________________________________________________________________________

This project/library contains common elements related to database engines and 
provides clients to simplify the connections...

## Execution Environment

### Install libraries
```shell
pip install --upgrade pip 
pip install virtualenv
```

### Create the Python Virtual Environment.
```shell
virtualenv --python={{python-version}} .venv
virtualenv --python=python3.11 .venv
```

### Activate the Virtual Environment.
```shell
source .venv/bin/activate
```

### Install required libraries.
```shell
pip install .
```

### Optional libraries.
```shell
pip install '.[all]'  # For all...
pip install '.[mysql]'
pip install '.[postgres]'
pip install '.[oracle]'
pip install '.[mongo]'
pip install '.[mssql]'
pip install '.[snowflake]'
pip install '.[db2]'
```

### Check tests and coverage...
```shell
python manager.py run-tests
python manager.py run-coverage
```

## Clients

### Postgres
```python
from core_db.engines.postgres import PostgresClient

with PostgresClient(conninfo=f"postgresql://postgres:postgres@localhost:5432/test") as client:
    client.execute("SELECT version() AS version;")
    print(client.fetch_one()[0])
```

### Mongo
```python
from core_db.engines.mongo import MongoClient

client = MongoClient(**{"host": "host", "database": "db"})
client.connect()
print(client.test_connection())
```

### MsSql
```python
from core_db.engines.mssql import MsSqlClient

with MsSqlClient(
        dsn="DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=master;UID=SA;PWD=sOm3str0ngP@33w0rd;Encrypt=no",
        autocommit=True, timeout=5) as client:
    
    client.execute("SELECT @@VERSION AS 'version';")
    print(list(client.fetch_records()))
```

### Oracle
```python
from core_db.engines.oracle import OracleClient

with OracleClient(user="...", password="...", dsn=f"{host}:{port}/{service_name}") as client:
    res = client.execute("SELECT * FROM ...")
    for x in client.fetch_all():
        print(x)
```

### MySQL
```python
from core_db.engines.mysql import MySQLClient

with MySQLClient(host="localhost", user="root", password="SomePassword") as client:
    client.execute("SELECT * FROM ...;")
    for x in client.fetch_all():
        print(x)
```

### IBM DB2
```python
from core_db.engines.db2 import Db2Client

dsn_hostname, dsn_port, dsn_database = "localhost", "50000", "sample"
dsn_uid, dsn_pwd = "db2inst1", "SomePassword"

dsn = (
    f"DATABASE={dsn_database};"
    f"HOSTNAME={dsn_hostname};"
    f"PORT={dsn_port};"
    f"PROTOCOL=TCPIP;"
    f"UID={dsn_uid};"
    f"PWD={dsn_pwd};"
)

with Db2Client(dsn=dsn, user="", password="") as client:
    client.execute("select * from department FETCH FIRST 2 ROWS ONLY;")
    print(client.fetch_one())
    print(client.fetch_record())
```

### Snowflake
```python

```

## Testing Clients Locally
We can test the clients locally by executing the below commands that are required to install
dependencies, run Docker containers and perform a series of query execution in the database engine
to ensure it's working as expected...

### PostgresSQL
```shell
docker run \
  --env=POSTGRES_PASSWORD=postgres \
  --env=PGDATA=/var/lib/postgresql/data \
  --volume=/var/lib/postgresql/data \
  -p 5432:5432 -d postgres:12.18-bullseye
  
python manager.py run-database-test \
  -client PostgresClient \
  -params '{"conninfo":"postgresql://postgres:postgres@localhost:5432/postgres"}'
```

### MySQL
```shell
docker run \
  --env=MYSQL_ROOT_PASSWORD=mysql_password \
  --volume=/var/lib/mysql \
  -p 3306:3306 \
  --restart=no \
  --runtime=runc \
  -d mysql:latest
  
python manager.py run-database-test \
  -client MySQLClient \
  -params '{"host": "localhost", "database": "sys", "user": "root", "password": "mysql_password"}'
```

### Oracle
```shell
docker pull container-registry.oracle.com/database/express:latest
docker container create -it --name OracleSQL -p 1521:1521 -e ORACLE_PWD=oracle_password container-registry.oracle.com/database/express:latest
docker start OracleSQL

python manager.py run-database-test \
  -client OracleClient \
  -params '{"user": "SYSTEM", "password": "oracle_password", "dsn": "localhost:1521/xe"}'
```
![How to connect](./assets/OracleCxn.png)

### MsSQL
```shell
docker pull mcr.microsoft.com/mssql/server:2022-latest

docker run\
  -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=sOm3str0ngP@33w0rd" \
  -p 1433:1433 --name MsSQL --hostname MsSQL \
  -d mcr.microsoft.com/mssql/server:2022-latest

docker start MsSQL
sudo /bin/bash ./scripts/install_mssql_driver.sh

python manager.py run-database-test \
  -client MsSqlClient \
  -params '{"dsn": "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=master;UID=SA;PWD=sOm3str0ngP@33w0rd;Encrypt=no"}'
```

### DB2

===================================================
Driver Installation -- 
Debian-based and Ubuntu-based Distributions
===================================================

More information:
https://ibmi-oss-docs.readthedocs.io/en/latest/odbc/installation.html

```shell
curl https://public.dhe.ibm.com/software/ibmi/products/odbc/debs/dists/1.1.0/ibmi-acs-1.1.0.list | sudo tee /etc/apt/sources.list.d/ibmi-acs-1.1.0.list
sudo apt update
sudo apt install ibm-iaccess
```

```text
# Create file -> .env_db2
LICENSE=accept
DB2INSTANCE=db2inst1
DB2INST1_PASSWORD=SomePassword
DBNAME=sample
BLU=false
ENABLE_ORACLE_COMPATIBILITY=false
UPDATEAVAIL=NO
TO_CREATE_SAMPLEDB=false
REPODB=false
IS_OSXFS=false
PERSISTENT_HOME=true
HADR_ENABLED=false
ETCD_ENDPOINT=
ETCD_USERNAME=
ETCD_PASSWORD=
```

```shell
docker pull icr.io/db2_community/db2

docker run \
  -h db2server --name db2server \
  --restart=always --detach --privileged=true \
  -p 50000:50000 --env-file .env_db2 \
  -v /var/lib/db2:/database \
  icr.io/db2_community/db2
```

```shell
docker exec -ti db2server bash -c "su - db2inst1"
db2sampl -force -sql
```

Output...
```text
[db2inst1@db2server ~]$ db2sampl -force -sql
  Creating database "SAMPLE"...
  Connecting to database "SAMPLE"...
  Creating tables and data in schema "DB2INST1"...
  'db2sampl' processing complete.
```

```shell
docker run \
  -d --name=db2 \
  --privileged=true \
  -v /var/lib/db2:/database \
  -e DB2INST1_PASSWORD=SomePassword \
  -e LICENSE=accept \
  -p 50000:50000 ibmcom/db2

python manager.py run-database-test \
  -client Db2Client \
  -params '{"dsn": "DATABASE=sample;HOSTNAME=localhost;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=SomePassword;"}'
```

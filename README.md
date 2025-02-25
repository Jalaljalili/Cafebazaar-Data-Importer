# Cafebazaar-Data-Importer
This Python script fetches **active install** and **new install** data from **Cafebazaar API** and stores it into a PostgreSQL database. It ensures that already imported Persian dates are not reinserted, optimizing performance.

## Requirements

1. Install Dependencies

You need Python 3.x installed along with the required libraries:
```shell
pip install psycopg2 requests
```

2. PostgreSQL Database

Ensure you have a PostgreSQL database with a table named cafebazaar:

```query
CREATE TABLE cafebazaar (
    id SERIAL PRIMARY KEY,
    date TEXT UNIQUE NOT NULL,
    active_install BIGINT,
    new_install BIGINT
);
```
3. Required Files

Create two text files for storing sensitive information:

1. Access Token File

Create a file **token_file.txt** and store your access token:

```
YOUR_ACCESS_TOKEN_HERE
```
2. Database Configuration File

Create a file db_config.txt with the following format:

```
db_name
db_user
db_password
db_host
db_port
```
For example:
```
cafebazaar_db
postgres
mypassword
localhost
5432
```
## How It Works

### 1. Reads Configurations

* Reads API Access Token from cafebazaar.txt.

* Reads Database Credentials from db_config.txt.

### 2. Fetches Data from APIs

* Fetches active install data from:

```url
https://pishkhan.cafebazaar.ir/api/insight/app.rbmain.a/stats/?range=last-six-months&stat_type=install&child=active_install&lang=fa
```
* Fetches new install data from:

```url
https://pishkhan.cafebazaar.ir/api/insight/app.rbmain.a/stats/?range=last-six-months&stat_type=install&child=new_install&lang=fa
```

### 3. Avoids Duplicate Imports

* Fetches already imported date values from the database.

* Only inserts new records that are not already stored.

### 4. Inserts Data into PostgreSQL

* New data is inserted into the cafebazaar table.

* Existing dates are skipped to prevent duplicates.

Running the Script

## Simply execute:

```shell
python3 app.py
```
### Expected Output
```shell
Successfully connected to the database
Found 120 existing records in the database.
Successfully retrieved data.
Inserted 10 new records into the database.
Database connection closed.
```
### Notes

* Make sure the PostgreSQL service is running.

* Your API token should be **valid**; otherwise, requests will fail.

* If date already exists in the database, it will not be inserted again.

## Future Enhancements

✅ Logging system for better monitoring.

✅ Automated scheduling (e.g., using cron or Windows Task Scheduler).

✅ Improved error handling for network failures.

------------------------------------------
Author: Jalal Jalili

Last Updated: 2025-02-25



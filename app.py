import psycopg2
import requests

def read_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Read access token and database config from files
token_file_path = 'token_file.txt'
db_config_file_path = 'db_config.txt'

# Read the token and database configuration
access_token = read_from_file(token_file_path)
db_config = read_from_file(db_config_file_path).split('\n')

# Database connection details from db_config.txt
db_name = db_config[0]
db_user = db_config[1]
db_password = db_config[2]
db_host = db_config[3]
db_port = db_config[4]

# Connect to the PostgreSQL database
try:
    connection = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    print("Successfully connected to the database")

    # Fetch already existing Persian dates from the database
    existing_dates = set()
    with connection.cursor() as cursor:
        cursor.execute("SELECT date FROM cafebazaar;")
        existing_dates = {row[0] for row in cursor.fetchall()}

    print(f"Found {len(existing_dates)} existing records in the database.")

    # Define the API URLs and headers
    url_active_install = "https://pishkhan.cafebazaar.ir/api/insight/app.rbmain.a/stats/?range=last-six-months&stat_type=install&child=active_install&lang=fa"
    url_new_install = "https://pishkhan.cafebazaar.ir/api/insight/app.rbmain.a/stats/?range=last-six-months&stat_type=install&child=new_install&lang=fa"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }

    # Fetch active_install data
    response_active = requests.get(url_active_install, headers=headers)
    response_new = requests.get(url_new_install, headers=headers)

    if response_active.status_code == 200 and response_new.status_code == 200:
        data_active = response_active.json()
        data_new = response_new.json()
        print("Successfully retrieved data.")

        # Extract Persian dates and install values
        dates_active = data_active['charts'][0]['dates']
        active_install_data = data_active['charts'][0]['series'][0]['data']

        dates_new = data_new['charts'][0]['dates']
        new_install_data = data_new['charts'][0]['series'][0]['data']

        # Create a dictionary to store both active and new install values
        install_data = {}

        # Insert active_install data
        for i in range(len(dates_active)):
            date = dates_active[i]  
            if date in existing_dates:
                continue  # Skip already imported dates
            active_install = active_install_data[i]
            install_data[date] = {'active_install': active_install, 'new_install': None}

        # Insert new_install data
        for i in range(len(dates_new)):
            date = dates_new[i]  
            if date in existing_dates:
                continue  # Skip already imported dates
            new_install = new_install_data[i]
            if date in install_data:
                install_data[date]['new_install'] = new_install
            else:
                install_data[date] = {'active_install': None, 'new_install': new_install}

        # Insert new data into PostgreSQL
        with connection.cursor() as cursor:
            for date, values in install_data.items():
                active_install = values['active_install']
                new_install = values['new_install']

                query = """
                INSERT INTO cafebazaar (date, active_install, new_install)
                VALUES (%s, %s, %s);
                """
                cursor.execute(query, (date, active_install, new_install))

            # Commit the changes
            connection.commit()
            print(f"Inserted {len(install_data)} new records into the database.")
    
    else:
        print(f"Failed to retrieve data. Status codes: active_install={response_active.status_code}, new_install={response_new.status_code}")

except Exception as error:
    print(f"Error connecting to the database: {error}")

finally:
    if connection:
        connection.close()
        print("Database connection closed.")

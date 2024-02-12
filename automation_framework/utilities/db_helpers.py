import sqlite3


class DatabaseHelper:
    def __init__(self, db_name="data.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        # Create tables if they don't exist
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS weather_data (
                city TEXT PRIMARY KEY,
                temperature REAL,
                feels_like REAL
            )''')

    def is_column_exists(self, table_name, column_name):
        # Check if a column exists in a table
        try:
            with self.conn:
                self.conn.execute(f'''
                    SELECT {column_name}
                    FROM {table_name}
                ''')
            return True
        except sqlite3.OperationalError:
            return False

    def add_column_to_table(self, table_name, column_name, column_type):
        # Add a column to a table if it doesn't exist
        if not self.is_column_exists(table_name, column_name):
            with self.conn:
                self.conn.execute(f'''
                    ALTER TABLE {table_name}
                    ADD COLUMN {column_name} {column_type};
                ''')
            print(f"Column '{column_name}' was successfully added to the '{table_name}' table.")
        else:
            print(f"Column '{column_name}' already exists in the '{table_name}' table.")

    def remove_column_from_table(self, table_name, column_name):
        # Remove a column from a table if it exists
        if self.is_column_exists(table_name, column_name):
            with self.conn:
                self.conn.execute(f'''
                    ALTER TABLE {table_name}
                    DROP COLUMN {column_name};
                ''')
            print(f"Column '{column_name}' removed from '{table_name}' table.")
        else:
            print(f"Column '{column_name}' does not exist in '{table_name}' table.")

    def insert_weather_data(self, city, temperature, feels_like):
        # receive the data from the API response and insert it into the database
        with self.conn:
            self.conn.execute('''
                INSERT INTO weather_data (city, temperature, feels_like)
                VALUES (?, ?, ?)
                ON CONFLICT(city) 
                DO UPDATE SET temperature = excluded.temperature, 
                              feels_like = excluded.feels_like
            ''', (city, temperature, feels_like))

    def insert_data(self, city, data_type, value):
        # insert any data, from the API response, into the database... not just weather data
        # such as 'average_temperature'
        """
        Updates a specific type of weather data for a given city.

        :param city: The name of the city to update.
        :param data_type: The type of data to update (e.g., 'average_temperature').
        :param value: The new value for the data.
        """
        try:
            with self.conn:
                sql = f"UPDATE weather_data SET {data_type} = ? WHERE city = ?"
                self.conn.execute(sql, (value, city))
                print(f"{data_type} updated for {city} to {value}.")
        except Exception as e:
            print(f"Failed to update {data_type} for {city}: {e}")

    def get_weather_data(self, city, weather):
        # Validate the column name to prevent SQL injection
        db_columns = ['temperature', 'feels_like']  # Define allowed column names
        if weather not in db_columns:
            raise ValueError(f"Invalid weather column: {weather}")

        column_name = weather  # It's now safe to use
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                SELECT {column_name}
                FROM weather_data
                WHERE city = ?
            ''', (city,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_param_boundary_value(self, MIN_or_MAX: str, parameter: str):
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT {MIN_or_MAX.upper()}({parameter}) FROM weather_data")
                # Fetch the result and return the first value
                result = cursor.fetchone()
                if result and result[0] is not None:
                    return result[0]
                else:
                    print("No temperature data found in the database.")
                    return None
        except Exception as e:
            print(f"Failed to get highest temperature: {e}")
            return None

    def get_city_by_param(self, MIN_or_MAX: str, parameter: str):
        if MIN_or_MAX.upper() not in ["MIN", "MAX"]:
            print("MIN_or_MAX must be either 'MIN' or 'MAX'")
            return None
        try:
            with self.conn:
                cursor = self.conn.cursor()
                # Use a subquery to find the max/min value of the parameter first
                cursor.execute(f'''
                    SELECT city 
                    FROM weather_data 
                    WHERE {parameter} = (SELECT {MIN_or_MAX.upper()}({parameter}) FROM weather_data)
                ''')
                result = cursor.fetchone()
                if result and result[0] is not None:
                    return result[0]
                else:
                    print(f"No data found for the specified parameter: {parameter}.")
                    return None
        except Exception as e:
            print(f"Failed to get city by parameter: {e}")
            return None




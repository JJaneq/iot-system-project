import psycopg

class DBManager:
    def __init__(self, db_name, user, password, host='db', port=5432):
        print("Connecting to database...")
        print(f"DB Name: {db_name}, User: {user}, Host: {host}, Port: {port}")
        self.connection = psycopg.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor(
                id UUID PRIMARY KEY,
                type VARCHAR(50) NOT NULL,
                room_number INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sensor_data(
                id SERIAL PRIMARY KEY,
                sensor_id UUID REFERENCES sensor(id),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                value FLOAT
            );
        """)
        self.connection.commit()
        # rozwiązanie potężnie leniwe - wiem
        self._insert_sensor('82f5e80c-822e-4e93-a6c7-ee1a6b7d22b2', 'temperature', 1)
        self._insert_sensor('c942b154-1afc-4d17-af3a-1bc6c8e345c9', 'light_level', 1)
        self._insert_sensor('fa7c3cc2-3055-41e6-9781-69e1caf98c1d', 'humidity', 1)
        self._insert_sensor('15cd0086-00d9-4dca-9336-2dd1b5486c7a', 'movement', 1)
        self._insert_sensor('c3fb408a-2998-4a68-9fa3-30924ef40a69', 'temperature', 2)
        self._insert_sensor('adcb8691-4e16-42a8-8a01-3624b9bf4990', 'light_level', 2)
        self._insert_sensor('ef61a4a2-fd66-4189-acd7-926ead1bfeb3', 'humidity', 2)
        self._insert_sensor('a268325f-f7f4-4d0d-8861-5d89c2e4ca59', 'movement', 2)

    def _insert_sensor(self, sensor_id, sensor_type, room_number):
        self.cursor.execute("""
            INSERT INTO sensor (id, type, room_number)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (sensor_id, sensor_type, room_number))
        self.connection.commit()

    def insert_sensor_data(self, sensor_id, value=None):
        if value is not None:
            self.cursor.execute("""
                INSERT INTO sensor_data (sensor_id, value)
                VALUES (%s, %s);
            """, (sensor_id, value))
        else:
            self.cursor.execute("""
                INSERT INTO sensor_data (sensor_id)
                VALUES (%s);
            """, (sensor_id,))
        self.connection.commit()
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
            CREATE TABLE IF NOT EXISTS room_thresholds(
                room_number INTEGER PRIMARY KEY,
                temp_min FLOAT,
                temp_max FLOAT,
                humidity_min FLOAT,
                humidity_max FLOAT,
                light_min FLOAT,
                light_max FLOAT
            );
            CREATE TABLE IF NOT EXISTS activator(
                id UUID PRIMARY KEY,
                type VARCHAR(50) NOT NULL,
                room_number INTEGER NOT NULL
            );
        """)
        self.connection.commit()
        # rozwiązanie potężnie leniwe - wiem xd
        self._insert_sensor('82f5e80c-822e-4e93-a6c7-ee1a6b7d22b2', 'temperature', 1)
        self._insert_sensor('c942b154-1afc-4d17-af3a-1bc6c8e345c9', 'light_level', 1)
        self._insert_sensor('fa7c3cc2-3055-41e6-9781-69e1caf98c1d', 'humidity', 1)
        self._insert_sensor('15cd0086-00d9-4dca-9336-2dd1b5486c7a', 'movement', 1)
        self._insert_sensor('c3fb408a-2998-4a68-9fa3-30924ef40a69', 'temperature', 2)
        self._insert_sensor('adcb8691-4e16-42a8-8a01-3624b9bf4990', 'light_level', 2)
        self._insert_sensor('ef61a4a2-fd66-4189-acd7-926ead1bfeb3', 'humidity', 2)
        self._insert_sensor('a268325f-f7f4-4d0d-8861-5d89c2e4ca59', 'movement', 2)
        
        self.register_activator('5435887c-d251-4007-9dcd-3618238edd17', 'heater', 1)
        self.register_activator('3de9c84a-fbda-4e74-a898-7735321bece1', 'vent', 1)
        self.register_activator('9e9da477-ac57-4d0b-a802-4d283de67005', 'alarm', 1)
        self.register_activator('504895d3-4cf8-4516-ad7f-98daf340304c', 'light', 1)
        self.register_activator('a21b600f-28b5-4c9a-b5cc-e554b2ec9f1f', 'heater', 2)
        self.register_activator('a3aeaee4-d84e-4ebe-b8c4-db0c6a66eee1', 'vent', 2)
        self.register_activator('d8e7200c-9f1c-4e66-a4fc-7b5c322e03ea', 'alarm', 2)
        self.register_activator('6966b068-cef5-4d30-b73d-9b9a057e4a64', 'light', 2)

        self.register_room_data(1, 20, 25, 30, 50, 40, 70)
        self.register_room_data(2, 19, 24, 35, 55, 45, 75)

    def _insert_sensor(self, sensor_id, sensor_type, room_number):
        self.cursor.execute("""
            INSERT INTO sensor (id, type, room_number)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (sensor_id, sensor_type, room_number))
        self.connection.commit()

    def register_room_data(self, room_number: int, 
                      temp_min: float=0, temp_max: float=30, 
                      humidity_min: float=0, humidity_max: float=100, 
                      light_min: float=0, light_max: float=100):
        self.cursor.execute("""
            INSERT INTO room_thresholds (room_number, temp_min, temp_max, humidity_min, humidity_max, light_min, light_max)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (room_number) DO UPDATE
            SET temp_min = EXCLUDED.temp_min,
                temp_max = EXCLUDED.temp_max,
                humidity_min = EXCLUDED.humidity_min,
                humidity_max = EXCLUDED.humidity_max,
                light_min = EXCLUDED.light_min,
                light_max = EXCLUDED.light_max;
        """, (room_number, temp_min, temp_max, humidity_min, humidity_max, light_min, light_max))
        self.connection.commit()

    def register_activator(self, activator_id, activator_type, room_number):
        self.cursor.execute("""
            INSERT INTO activator (id, type, room_number)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (activator_id, activator_type, room_number))
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

    def get_last_sensors_data(self) -> dict:
        self.cursor.execute("""
            SELECT s.id, s.type, s.room_number, sd.timestamp, sd.value
            FROM sensor s
            LEFT JOIN LATERAL (
                SELECT *
                FROM sensor_data
                WHERE sensor_id = s.id
                ORDER BY timestamp DESC
                LIMIT 1
            ) sd ON true;
        """)

        data = self.cursor.fetchall()
        data_dicts = []
        for row in data:
            data_dicts.append({
                "sensor_id": str(row[0]),
                "sensor_type": row[1],
                "room_number": row[2],
                "timestamp": str(row[3]),
                "value": row[4]
            })
        return data_dicts
    
    def get_room_thresholds(self, room_number: int) -> dict:
        self.cursor.execute("""
            SELECT temp_min, temp_max, humidity_min, humidity_max, light_min, light_max
            FROM room_thresholds
            WHERE room_number = %s;
        """, (room_number,))
        row = self.cursor.fetchone()
        if row:
            return {
                "temp_min": row[0],
                "temp_max": row[1],
                "humidity_min": row[2],
                "humidity_max": row[3],
                "light_min": row[4],
                "light_max": row[5]
            }
        else:
            return {}
        
    def get_all_sensors(self) -> list:
        self.cursor.execute("""
            SELECT id, type, room_number
            FROM sensor;
        """)
        rows = self.cursor.fetchall()
        sensors = []
        for row in rows:
            sensors.append({
                "id": str(row[0]),
                "type": row[1],
                "room_number": row[2]
            })
        return sensors
    
    def get_all_activators(self) -> list:
        self.cursor.execute("""
            SELECT id, type, room_number
            FROM activator;
        """)
        rows = self.cursor.fetchall()
        activators = []
        for row in rows:
            activators.append({
                "id": str(row[0]),
                "type": row[1],
                "room_number": row[2]
            })
        return activators
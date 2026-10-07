import psycopg

class Database:
    def __init__(self,db_config):
        self._conn = psycopg.connect(
            dbname = db_config["db_name"],
            user = db_config["user"],
            host = db_config["host"]
        )

        self._cursor = self._conn.cursor()

        self._create_table(table_name = db_config["table_name"])

    def _create_table(self,table_name:str):
        try:
            self._cursor.execute(
                f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    total_frames_tracked INT,
                    category TEXT,
                    category_probability FLOAT8,
                    start_timestamp FLOAT8,
                    end_timestamp FLOAT8,
                    shape_feature VECTOR,
                    colour_histogram FLOAT8[],
                    thumbnail_image_path TEXT
                )
                '''

            )
        except BaseException as e:
            print("An error occurred\n",e)
            self._conn.rollback()
        else:
            self._conn.commit()

    def insert(self,table_name:str,insertion_data:list[dict]):
        #insert multiple rows
        insertion_query = f'''
            INSERT INTO {table_name}
            (total_frames_tracked,category,category_probability,start_timestamp,end_timestamp,shape_feature,colour_histogram,thumbnail_image_path)
            VALUES
            (%(total_frames_tracked)s,%(category)s,%(category_probability)s,%(start_timestamp)s,%(end_timestamp)s,%(shape_feature)s,%(colour_histogram)s,%(thumbnail_image_path)s)
        '''

        try:
            self._cursor.executemany(insertion_query,insertion_data)
        except BaseException as e:
            print("An error occured\n",e)
            self._conn.rollback()
        else:
            self._conn.commit()

    def __del__(self):
        self._cursor.close()
        self._conn.close()


if __name__ == "__main__":
    db_obj = Database()

    db_obj.insert(
        table_name = "test",
        insertion_data = [{
            "total_frames_tracked": 20,
            "category": "car",
            "category_probability": 0.799,
            "start_timestamp": 10.55,
            "end_timestamp": 30.17,
            "shape_feature": [1.44,8.99,3.145,1.22,-1.66,0.14,0.44],
            "colour_histogram": [1.0,2.0,0.5,4.1,7.9],
            "thumbnail_image_path": "./assets/.db_thumbnail_images/test/object_1.png"
        }]
    )


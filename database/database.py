import psycopg
from psycopg.rows import dict_row

class Database:
    def __init__(self,db_config):
        self._conn = psycopg.connect(
            dbname = db_config["db_name"],
            user = db_config["user"],
            host = db_config["host"]
        )

        self._cursor = self._conn.cursor()
        self._dict_cursor = self._conn.cursor(row_factory = dict_row)

        if db_config.get("table_name",None) is not None:
            self._create_table(table_name = db_config["table_name"])

    def _get_db_tables(self)->list:
        query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        tables = list()

        try:
            results = self._cursor.execute(query)

            tables = [res[0] for res in results.fetchall()]
        except BaseException as e:
            print("An error occurred\n",e)
            self._conn.rollback()
        else:
            self._conn.commit()

        return tables

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

    def query_by_all_features(self,table_name:str,shape_feature:list,filter_str:str=None,vals_dict:dict=dict(),use_dict_cursor:bool=True)->list:
        cursor = self._dict_cursor if use_dict_cursor else self._cursor

        query_str = (
            "SELECT total_frames_tracked,category,category_probability,"
            "start_timestamp,end_timestamp,"
            "shape_feature <-> %(shape_feature)s AS shape_cost,"
            "shape_feature,colour_histogram,thumbnail_image_path "
            f"FROM {table_name}"
        )

        vals_dict["shape_feature"] = shape_feature

        if filter_str is not None:
            query_str+=f" WHERE {filter_str}"

        results = list()

        try:
            query_res = cursor.execute(query_str,vals_dict)

            results = query_res.fetchall()
        except BaseException as e:
            print("An error occurred\n",e)
            self._conn.rollback()
        else:
            self._conn.commit()

        return results

    def query_by_colour_feature(self,table_name:str,filter_str:str=None,vals_dict:dict=dict(),use_dict_cursor:bool=True)->list:
        return self.query(
            table_name = table_name,
            filter_str = filter_str,
            vals_dict = vals_dict,
            limit = -1,
            order = False,
            use_dict_cursor = use_dict_cursor
        )

    def query_by_shape_feature(self,table_name:str,shape_feature:list,filter_str:str=None,vals_dict:dict=dict(),limit:int=20,use_dict_cursor:bool=True)->list:
        cursor = self._dict_cursor if use_dict_cursor else self._cursor

        query_str = (
            "SELECT total_frames_tracked,category,category_probability,start_timestamp,"
            "end_timestamp,shape_feature,colour_histogram,thumbnail_image_path "
            f"FROM {table_name} "
            "{0} "
            f"ORDER BY shape_feature <-> %(shape_feature)s LIMIT {limit} "
        )

        vals_dict["shape_feature"] = shape_feature

        if filter_str is not None:
            query_str = query_str.format(f"WHERE {filter_str}")
        else:
            query_str = query_str.format('')

        results = list()

        try:
            query_res = cursor.execute(query_str,vals_dict)

            results = query_res.fetchall()
        except BaseException as e:
            print("An error occurred\n",e)
            self._conn.rollback()
        else:
            self._conn.commit()

        return results

    def query(self,table_name:str,filter_str:str=None,vals_dict:dict=dict(),limit:int=20,offset:int=0,order:bool=True,use_dict_cursor:bool=True)->list:
        cursor = self._dict_cursor if use_dict_cursor else self._cursor

        query_str = (
            "SELECT total_frames_tracked,category,category_probability,start_timestamp,"
            "end_timestamp,shape_feature,colour_histogram,thumbnail_image_path "
            f"FROM {table_name}"
        )

        results = list()

        if filter_str is not None:
            query_str+= f" WHERE {filter_str}"

        if order:
            query_str+=" ORDER BY category_probability DESC"

        if limit > 0:
            query_str+=f" LIMIT {limit}"

        try:
            if vals_dict:
                query_res = cursor.execute(query_str,vals_dict)
            else:
                query_res = cursor.execute(query_str)

            results = query_res.fetchall()

        except BaseException as e:
            print("An error occurred\n",e)
            self._conn.rollback()
        else:
            self._conn.commit()

        return results

    def __del__(self):
        self._cursor.close()
        self._dict_cursor.close()
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


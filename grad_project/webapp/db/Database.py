import sqlite3
import logging

class MyConnection(sqlite3.Connection):

    def cursor(self):
        return super().cursor(MyCursor)

class MyCursor(sqlite3.Cursor):

    def execute(self, sql, parameters=''):
        print(f'statement: {sql!r}, parameters: {parameters!r}')
        return super().execute(sql, parameters)

conn = sqlite3.connect(':memory:', timeout=60, factory=MyConnection)

def register_user_in_db(db: str, service: str, params):
    conn = sqlite3.connect(db)

    doctor_id = params['doctor_id']
    patient_id = params['patient_id']
    Gender = params['Gender']
    Dob = params['Dob']
    age = params['age']
    leftm = params['leftm']
    rightm = params['rightm']
    left = params['left']
    right = params['right']
    result = params['result']

    query4 = f"insert into main.{service} (doctor_id, patient_id, Gender, Dob, age, leftm,left, rightm, right, result) VALUES (:doctor_id, :patient_id, :Gender, :Dob, :age, :leftm,:left, :rightm, :right, :result);"
    try:
        conn.execute(query4, params)
        conn.commit()
        conn.close()
        logging.info(msg=f"{patient_id} has been registered in '{db}'")
    except Exception as e:
        logging.error(msg=e)
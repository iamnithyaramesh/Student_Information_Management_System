import cx_Oracle

connection = cx_Oracle.connect(username='SCOTT',password='tiger',dsn='orcl')

cursor = connection.cursor()

cursor.execute('CREATE TABLE STUD(id INTEGER PRIMARY KEY);')

cursor.execute('INSERT INTO STUD VALUES(1);')

connection.commit()

cursor.execute('SELECT * FROM STUD;')
data = cursor.fetchall()

for row in data:
    print(row)

cursor.close()
connection.close()

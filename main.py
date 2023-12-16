import pandas as pd
import cx_Oracle

cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_12",
                             config_dir=r"C:\oracle\product\10.2.0\db_1\NETWORK\ADMIN")

username = "SCOTT"
password = "tiger"
dsn = "orcl"

connection = cx_Oracle.connect(username, password, dsn)
cursor = connection.cursor()

cursor.execute("CREATE TABLE MARK (SNO INT,MARK INT)")
cursor.execute("INSERT INTO MARK VALUES (1,95)")
connection.commit()
cursor.execute("SELECT * FROM MARK")
row=cursor.fetchall()
for i in row:
    print(row)


'''try:
    # Create the STUDENT_1 table
    cursor.execute("CREATE TABLE STUDENT_1(SNO INT, \"REGISTER NUMBER\" INT, \"Student Name\" VARCHAR2(50), "
                   "\"Year\" VARCHAR2(10), \"Sub.Code\" VARCHAR2(50), "
                   "\"NPTEL Course Title\" VARCHAR2(100), \"No of credits earned\" INT, "
                   "\"Actual NPTEL Marks\" INT, \"SSN Marks (Max 100)\" INT)")

    # Read data from Excel file
    excel_file_path = 'NPTEL course-format_IT_Even sem_AY2022-2023.xlsx'
    df = pd.read_excel(excel_file_path)

    # Define the range of rows to process
    start_row = 8
    end_row = 138

    # Insert data into the STUDENT_1 table
    for index, row in df.iloc[start_row:end_row].iterrows():
        cursor.execute("INSERT INTO STUDENT_1 VALUES(:1, :2, :3, :4, :5, :6, :7, :8, :9)",
                       (row['S.No'], row['REGISTER NUMBER'], row['Student Name'], row['Year'],
                        row['Sub.Code(will be allotted by the CoE office)'], row['NPTEL Course Title'],
                        row['No of credits earned'], row['Actual NPTEL Marks'], row['SSN Marks (Max 100)']))

    # Commit the changes
    connection.commit()

    # Fetch and print the inserted data
    cursor.execute("SELECT * FROM STUDENT_1")
    result = cursor.fetchall()

    for row in result:
        print(row)

except Exception as e:
    print(f"Error: {e}")

finally:
    cursor.close()
    connection.close()'''

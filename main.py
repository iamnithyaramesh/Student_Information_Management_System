from flask import Flask, render_template, request, flash, redirect, url_for,jsonify
import pandas as pd
import cx_Oracle
import os
import secrets


from flask_cors import CORS

app = Flask(__name__)
CORS(app)  
app.secret_key = secrets.token_hex(16)

cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_12", config_dir=r"C:\oracle\product\10.2.0\db_1\NETWORK\ADMIN")

def get_db_connection():
    return cx_Oracle.connect(user='SCOTT', password='tiger', dsn='orcl')

def table_exists(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM all_tables WHERE table_name = '{table_name.upper()}'")
    return cursor.fetchone()[0] > 0

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if any(char.isdigit() for char in username):
            return redirect(url_for('student'))
        else:
            return redirect(url_for('admin'))

    return render_template('login.html')

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/upload_results', methods=['GET', 'POST'])
def upload_results():
    if request.method == 'POST':
        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            flash('No file selected!', 'danger')
            return redirect(url_for('upload_results'))

        try:
            df = pd.read_excel(uploaded_file)

            connection = get_db_connection()
            cursor = connection.cursor()

            table_name = 'NPTEL_RESULTS'

            if table_exists(cursor, table_name):
                cursor.execute(f"DROP TABLE {table_name}")

    
            cursor.execute(f"""
                CREATE TABLE {table_name} (
                    SNO VARCHAR2(50) PRIMARY KEY,
                    REGISTER_NUMBER VARCHAR2(50),
                    STUDENT_NAME VARCHAR2(100),
                    YEAR VARCHAR2(50),
                    SUBCODE VARCHAR2(50),
                    COURSE_TITLE VARCHAR2(100),
                    CREDITS VARCHAR2(50),
                    NPTEL_MARK INT,
                    SSN_MARKS INT
                )""")
        
            for row in df.iloc[7:136].itertuples(index=False, name=None):
                try:
                    query = f"INSERT INTO NPTEL_RESULTS VALUES('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}', '{row[6]}', {row[7]}, {row[8]})"
                    cursor.execute(query)
                    print(f"Row inserted: {row}")
                except Exception as e:
                    print(f"Error inserting row {row}: {e}")
                
                connection.commit()


            flash('Database initialized and records inserted successfully!', 'success')
            print("Redirecting to success route...")

            cursor.execute(f"""CREATE OR REPLACE TRIGGER nptel_changes_trigger
                           
BEFORE INSERT OR UPDATE OR DELETE ON NPTEL_RESULTS
FOR EACH ROW
BEGIN
    RAISE_APPLICATION_ERROR(-20001, 'Modifications to NPTEL_RESULTS table are not allowed.');
END;
/""")
            
            connection.commit()
            return redirect(url_for('success'))
        


        except ValueError as e:
            flash(f'Invalid data format: {e}', 'danger')

        except Exception as e:
            flash(f'Unexpected error: {e}', 'danger')

        finally:
            cursor.close()
            connection.close()

    return render_template('upload_results.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/main_search')
def main_search():
    return render_template('main_search.html')

@app.route('/year_wise', methods=['GET', 'POST'])
def year_wise():
    if request.method == 'POST':
        year = request.form.get('selectedYear')

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            query = f"SELECT * FROM NPTEL_RESULTS WHERE YEAR = :year"
            q1= f"SELECT DISTINCT(STUDENT_NAME) FROM NPTEL_RESULTS WHERE YEAR = :year"

            cursor.execute(query, {'year': year})
            students = cursor.fetchall()

            app.logger.info(f"Fetched {len(students)} students for year {year}")

            cursor.execute(q1,{'year': year})
            num_students=cursor.fetchall()

            return render_template('year_search.html', students=students , num_students=len(num_students))

        except Exception as e:
            flash(f'Error fetching students: {e}', 'danger')
            app.logger.error(f'Error fetching students: {e}')

        finally:
            cursor.close()
            connection.close()

    else:
        
        return render_template('year_search.html', students=None)

@app.route('/complete_courses', methods=['GET', 'POST'])
def complete_courses():
    if request.method == 'POST':
        student_name = request.form.get('studentName')

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            student_records=[]
            print(f"Fetched {student_name}")
            cursor.execute(f'SELECT * from NPTEL_RESULTS where STUDENT_NAME=\'{student_name}\'')
            print("Query executed")
            l = cursor.fetchall()
            for i in l:
                student_records.append(i)
            print('Got records', student_records)
            return render_template('student_search.html', students=student_records)

        except Exception as e:
            flash(f'Error fetching student records: {e}', 'danger')

        finally:
            cursor.close()
            connection.close()

    return render_template('student_search.html')


@app.route('/courses', methods=['GET'])
def get_courses():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT UPPER(COURSE_TITLE) AS DISTINCT_COURSE_TITLE, COUNT(*) AS RECORD_COUNT FROM NPTEL_RESULTS GROUP BY UPPER(COURSE_TITLE)')

        courses = {row[0]:row[1] for row in cursor.fetchall()}

        flash(f"Fetched {len(courses)} courses")

        return render_template('course_search.html',courses=courses)

    except Exception as e:
        flash(f'Error fetching courses: {e}', 'danger')

    finally:
        cursor.close()
        connection.close()

    return render_template('course_search.html')

@app.route('/acyear', methods=['GET','POST'])
def academic_year():

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            
            overall_count_query = f"SELECT COUNT(*) FROM NPTEL_RESULTS"
            cursor.execute(overall_count_query)
            overall_count = cursor.fetchall()[0][0]

            ab_90=f"SELECT COUNT(*) FROM NPTEL_RESULTS WHERE SSN_MARKS>=91"
            cursor.execute(ab_90)
            count_above_90=cursor.fetchall()[0][0]

            ab_80=f"SELECT COUNT(*) FROM NPTEL_RESULTS WHERE SSN_MARKS BETWEEN 80 AND 90"
            cursor.execute(ab_80)
            count_above_80=cursor.fetchall()[0][0]

            ab_70=f"SELECT COUNT(*) FROM NPTEL_RESULTS WHERE SSN_MARKS BETWEEN 70 AND 79"
            cursor.execute(ab_70)
            count_above_70=cursor.fetchall()[0][0]

            ab_50=f"SELECT COUNT(*) FROM NPTEL_RESULTS WHERE SSN_MARKS BETWEEN 50 AND 69"
            cursor.execute(ab_50)
            count_above_50=cursor.fetchall()[0][0]

            return(render_template('acyear.html',overall_count=overall_count,above_90=count_above_90,above_80=count_above_80,above_70=count_above_70,above_50=count_above_50))

        except Exception as e:
            flash(f'Error processing academic year data: {e}', 'danger')

        finally:
            cursor.close()
            connection.close()

        return(render_template('acyear.html'))

@app.route('/verify', methods=['GET','POST'])
def verify():
    register_number = request.form.get('registernumber')
    print('Got register number',register_number)

    if not register_number:
        flash('Register number is required.', 'danger')
        return redirect(url_for('student'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        
        cursor.execute(f"SELECT * FROM NPTEL_RESULTS WHERE REGISTER_NUMBER = {register_number}"),          
        print("Query executed")
        students = cursor.fetchall()
        print("fetched",students)

        return render_template('student.html', students=students)

    except Exception as e:
        flash(f'Error fetching courses: {e}', 'danger')

    finally:
        cursor.close()
        connection.close()

    return render_template('student.html')

@app.route('/insert_records')
def insert_records():

    try:
     connection = get_db_connection()
     cursor = connection.cursor()
     cursor.execute(f'INSERT INTO NPTEL_RESULTS VALUES ("1", "205002001", "AADHITHYA K PRAVEEN", "III year","None" "DBMS", "3", 85, 90)')
    
    except Exception as e:
        data='Cannot Perform this action'
        return render_template('insert_portal.html',data=data)
    
    finally:
       cursor.close()
       connection.close()

if __name__ == '__main__':
    app.run(debug=True)
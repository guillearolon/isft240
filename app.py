from flask import Flask, render_template, request, redirect, url_for, flash, Response
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = '15#6!#78!443¡'

def crear_db():
    conexion = sqlite3.connect('asistencia.db')
    cursor = conexion.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS alumnos(id INTEGER PRIMARY KEY AUTOINCREMENT,
                       nombre VARCHAR(30),
                       apellido VARCHAR(30),
                       materia VARCHAR(30),
                       fecha DATE DEFAULT(DATE('now', 'localtime')))""")
    conexion.commit()

# Crea la tabla para los Alumnos
crear_db()

def crear_tb_login():
    conexion = sqlite3.connect('asistencia.db')
    cursor = conexion.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuario(id INTEGER PRIMARY KEY,
                       user TEXT,
                       password TEXT)''')
        
    # Verifica si hay algún registro en la tabla usuario
    cursor.execute('SELECT * FROM usuario LIMIT 1')
    usuario_existente = cursor.fetchone()

    if not usuario_existente:
        # Insertar datos solo si no hay registros
        cursor.execute('INSERT INTO usuario(user, password) VALUES("alumnos", "isft240")')
        conexion.commit()

# Crea la tabla Usuarios
crear_tb_login()

@app.route('/', methods=('POST', 'GET'))
def login():
    if request.method == 'POST':
        conexion = sqlite3.connect('asistencia.db')
        cursor = conexion.cursor()
        log = cursor.execute('SELECT * FROM usuario').fetchall()

        usuario = request.form.get('usuario')
        passw = request.form.get('passw')

        # Verifica si el usuario y contraseña coinciden con los registros
        if any(entry[1] == usuario and entry[2] == passw for entry in log) and (usuario,passw) is not None:
            return redirect(url_for('index'))
        else:
            flash('Usuario y/o contraseña incorrectos', 'failed')
            return redirect(url_for('login'))
            
    return render_template('login.html')        

# Asistencia de alumnos
@app.route('/asistencias1', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if 'nombre' in request.form and 'apellido' in request.form and 'materia' in request.form:
            conexion = sqlite3.connect('asistencia.db')
            cursor = conexion.cursor()
            nombre = request.form.get('nombre')
            apellido = request.form.get('apellido')
            materia = request.form.get('materia')
            cursor.execute("INSERT INTO alumnos (nombre, apellido, materia) VALUES (?,?,?)", (nombre.title(),apellido.title(),materia.title(),))
            conexion.commit()
            flash('Datos cargados correctamente', 'success')

            return redirect(url_for('index'))

    conexion = sqlite3.connect('asistencia.db')
    cursor = conexion.cursor()
    datos = cursor.execute("SELECT * FROM alumnos").fetchall()

    return render_template('index.html', datos=datos)

#manejo de errores / página no encontrada
@app.errorhandler(404)
def error_pag(e):
    return '<h1 style="text-align: center; margin-top: 100px; font-size: 50px; font-family: Cambria;">ERROR 404: <br> Página no encontrada</h1>', 404

# Botón para eliminar individualmente
@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    conexion = sqlite3.connect('asistencia.db')
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM alumnos WHERE id = ?", (id,))
    conexion.commit()

    return redirect(url_for('index'))

# Botón para eliminar todo
@app.route('/delete_all', methods=['GET'])
def delete_all():
    conexion = sqlite3.connect('asistencia.db')
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM alumnos")
    conexion.commit()

    return redirect(url_for('index'))

# Función para exportar el listado en formato XLSX
@app.route('/export')
def exportar():
    conexion = sqlite3.connect('asistencia.db')
    datos = pd.read_sql_query("SELECT nombre, apellido, materia, fecha FROM alumnos", conexion)

    hoja_excel = 'alumnos.xlsx'
    datos.to_excel(hoja_excel, index=False)

    with open(hoja_excel, 'rb') as hoja_excel:
        response = Response(hoja_excel.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response.headers['Content-Disposition'] = 'attachment; filename = alumnos.xlsx'

    return response

if __name__ == '__main__':
    app.run(debug=True)

import sqlite3
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DATABASE = "bd_instituto.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS cursos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descripcion TEXT NOT NULL,
        horas INTEGER NOT NULL
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellidos TEXT NOT NULL,
        fecha_nacimiento TEXT NOT NULL
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS inscripciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        curso_id INTEGER NOT NULL,
        estudiante_id INTEGER NOT NULL,
        FOREIGN KEY (curso_id) REFERENCES cursos (id),
        FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id)
    )
    """
    )

    # Datos iniciales opcionales
    cursor.execute("SELECT COUNT(*) FROM cursos")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO cursos (descripcion, horas) VALUES (?, ?)",
            [
                ("HTML Y CSS", 10),
                ("JavaScript Principiante", 20),
                ("Java EE", 60),
            ],
        )

    cursor.execute("SELECT COUNT(*) FROM estudiantes")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO estudiantes (nombre, apellidos, fecha_nacimiento) VALUES (?, ?, ?)",
            [
                ("Armando", "Carpas", "1995-01-10"),
                ("Elsa", "Capunta", "1998-05-12"),
                ("Alan", "Brito", "2000-08-20"),
                ("Bruno", "Diaz", "1980-12-20"),
            ],
        )

    conn.commit()
    conn.close()


@app.route("/")
def index():
    return redirect(url_for("listar_cursos"))


# --- RUTAS CURSOS ---
@app.route("/cursos")
def listar_cursos():
    conn = get_db_connection()
    cursos = conn.execute("SELECT * FROM cursos").fetchall()
    conn.close()
    return render_template("cursos.html", cursos=cursos)


@app.route("/cursos/nuevo", methods=["GET", "POST"])
def nuevo_curso():
    if request.method == "POST":
        descripcion = request.form["descripcion"]
        horas = request.form["horas"]
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO cursos (descripcion, horas) VALUES (?, ?)",
            (descripcion, horas),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("listar_cursos"))
    return render_template("form_curso.html", curso=None)


@app.route("/cursos/editar/<int:id>", methods=["GET", "POST"])
def editar_curso(id):
    conn = get_db_connection()
    if request.method == "POST":
        descripcion = request.form["descripcion"]
        horas = request.form["horas"]
        conn.execute(
            "UPDATE cursos SET descripcion = ?, horas = ? WHERE id = ?",
            (descripcion, horas, id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("listar_cursos"))

    curso = conn.execute(
        "SELECT * FROM cursos WHERE id = ?", (id,)
    ).fetchone()
    conn.close()
    return render_template("form_curso.html", curso=curso)


@app.route("/cursos/eliminar/<int:id>")
def eliminar_curso(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM cursos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("listar_cursos"))


# --- RUTAS ESTUDIANTES ---
@app.route("/estudiantes")
def listar_estudiantes():
    conn = get_db_connection()
    estudiantes = conn.execute("SELECT * FROM estudiantes").fetchall()
    conn.close()
    return render_template("estudiantes.html", estudiantes=estudiantes)


@app.route("/estudiantes/nuevo", methods=["GET", "POST"])
def nuevo_estudiante():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        fecha_nacimiento = request.form["fecha_nacimiento"]
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO estudiantes (nombre, apellidos, fecha_nacimiento) VALUES (?, ?, ?)",
            (nombre, apellidos, fecha_nacimiento),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("listar_estudiantes"))
    return render_template("form_estudiante.html", estudiante=None)


@app.route("/estudiantes/eliminar/<int:id>")
def eliminar_estudiante(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM estudiantes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("listar_estudiantes"))


# --- RUTAS INSCRIPCIONES ---
@app.route("/inscripciones")
def listar_inscripciones():
    conn = get_db_connection()
    query = """
        SELECT i.id, i.fecha, (e.nombre || ' ' || e.apellidos) AS estudiante, c.descripcion AS curso
        FROM inscripciones i
        JOIN estudiantes e ON i.estudiante_id = e.id
        JOIN cursos c ON i.curso_id = c.id
    """
    inscripciones = conn.execute(query).fetchall()
    conn.close()
    return render_template("inscripciones.html", inscripciones=inscripciones)


@app.route("/inscripciones/nuevo", methods=["GET", "POST"])
def nueva_inscripcion():
    conn = get_db_connection()
    if request.method == "POST":
        fecha = request.form["fecha"]
        estudiante_id = request.form["estudiante_id"]
        curso_id = request.form["curso_id"]
        conn.execute(
            "INSERT INTO inscripciones (fecha, estudiante_id, curso_id) VALUES (?, ?, ?)",
            (fecha, estudiante_id, curso_id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("listar_inscripciones"))

    estudiantes = conn.execute("SELECT * FROM estudiantes").fetchall()
    cursos = conn.execute("SELECT * FROM cursos").fetchall()
    conn.close()
    return render_template(
        "form_inscripcion.html", estudiantes=estudiantes, cursos=cursos
    )


@app.route("/inscripciones/eliminar/<int:id>")
def eliminar_inscripcion(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM inscripciones WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("listar_inscripciones"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
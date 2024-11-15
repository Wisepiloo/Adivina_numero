from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'mi_clave_secreta'
db = SQLAlchemy(app)

#################----------INGRESAR----------------#################

@app.route("/")
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        usuario = request.form.get("username")
        clave = request.form.get("password")
        if intentar_logearse(usuario, clave) and not(campos_vacios(usuario, clave)):
            return redirect(url_for("juego"))
        
    return render_template("login.html")

#################----------REGISTRARSE----------------#################

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        usuario = request.form.get("username")
        clave = request.form.get("password")
        clave_repetida = request.form.get("repeat_password")
        if intentar_crear_usuario(usuario,clave,clave_repetida) and not(campos_vacios(usuario, clave)):
            return redirect(url_for("login"))
        
    return render_template("register.html")

#################----------JUEGO PRINCIPAL----------------#################

@app.route("/juego")
def juego():
    puntaje = obtener_puntaje()
    return render_template("juego.html", puntaje=puntaje)

#################----------ESTADISTICAS----------------#################

@app.route("/estadisticas")
def estadisticas():
    correctas, incorrectas = obtener_correctas_incorrectas()
    porcentaje = calcular_porcentaje(correctas, incorrectas)
    usuario = obtener_usuario_activo()
    return render_template("estadisticas.html", correctas=correctas, incorrectas=incorrectas, porcentaje=porcentaje, usuario=usuario.nombre)

#################----------RECEPCION DE DATOS JSON----------------#################

@app.route('/guardar_datos', methods=['POST'])
def guardar_datos():
    datos = request.get_json()
    correctas = datos.get('correctas')
    incorrectas = datos.get('incorrectas')
    puntaje = datos.get('puntaje')
    actualizar_datos_de_usuario(puntaje, correctas, incorrectas)

############-------Redirecciones y errores en registrar usuarios ------#####################

def intentar_crear_usuario(usuario,clave,clave_repetida):
    resultado = False
    if verificar_usuario(usuario) == None:
        if verificar_contraseña(clave, clave_repetida):
            crear_usuario(usuario, clave)
            resultado = True
        else:
            flash("Las claves no son iguales.", "error_form")
    else:
        flash("Usuario en uso, pruebe con otro.", "error_form")
    return resultado

############-------Redirecciones y errores en ingresar usuarios ------#####################

def intentar_logearse(usuario, clave):
    resultado = False
    if verificar_usuario_contraseña(usuario, clave) != None:
        crear_session(usuario, clave)
        resultado = True
    else:
        flash("Usuario o Contraseña incorrecto.", "error_form")
    return resultado


############-------Funciones necesarias para ingresar y registrar usuarios------#####################

#Si los campos estan vacios, muestra una alerta
def campos_vacios(usuario, clave):
    resultado = False
    if usuario == "" or clave == "":
        flash("Debes completar los campos para continuar.", "error_form")
        resultado = True
    return resultado

#Verifica la existencia de un nombre de usuario en la base de datos, sino devuelve None
def verificar_usuario(nombre):
    existe = db.session.query(Usuario).filter_by(nombre=nombre).first()
    return existe if existe is not None else None

#Verifica nombre de usuario y clave en la base de datos, sino devuelve None
def verificar_usuario_contraseña(usuario, contraseña):
    existe = db.session.query(Usuario).filter_by(nombre=usuario, clave=contraseña).first()
    return existe if existe is not None else None

#Compara contraseñas cuando registramos un usuario
def verificar_contraseña(contraseña, contraseña_repetida):
    return contraseña == contraseña_repetida

#Crear un nuevo usuario con las estadisticas en 0.
def crear_usuario(nombre_usuario, clave_usuario):
    nuevo_usuario = Usuario(nombre=nombre_usuario, clave=clave_usuario)
    nuevas_estadisticas = Estadisticas(puntaje=0, correcto=0, incorrecto=0)

    # Asociar las estadísticas al usuario
    nuevo_usuario.estadisticas = nuevas_estadisticas
    db.session.add(nuevo_usuario)
    db.session.commit()
    
############-------Manejo sesion de usuario------#####################

#Crea una sesion --> Guarda id de usuario
#LLamada desde intentar_logearse
def crear_session(usuario, contraseña):
    usuario = db.session.query(Usuario).filter_by(nombre=usuario, clave=contraseña).first()
    session["usuario_id"] = usuario.id

#verifica si hay una sesion activa
def verificar_session_activa():
    return "usuario_id" in session

#Obtiene el usuario activo por su id
def obtener_usuario_activo():
    id_usuario = session["usuario_id"]
    usuario = db.session.query(Usuario).filter_by(id=id_usuario).first()
    return usuario

############-------Manejo de datos de usuario------#####################

def actualizar_datos_de_usuario(puntaje, correctas, incorrectas):
    usuario = obtener_usuario_activo()
    usuario.estadisticas.puntaje = puntaje
    usuario.estadisticas.correcto = correctas
    usuario.estadisticas.incorrecto = incorrectas
    db.session.commit()
    
def obtener_correctas_incorrectas():
    usuario = obtener_usuario_activo()
    return usuario.estadisticas.correcto, usuario.estadisticas.incorrecto

def obtener_puntaje():
    usuario = obtener_usuario_activo()
    return usuario.estadisticas.puntaje

def calcular_porcentaje(correctas, incorrectas):
    total = correctas + incorrectas
    return ((correctas * 100) // (total))

############-----Tablas----------###################

class Usuario(db.Model):
    __tablename__ = "usuarios"
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, unique=True, nullable=False)
    clave = db.Column(db.String, nullable=False)

    # Relación uno-a-uno con Estadisticas
    estadisticas = db.relationship("Estadisticas", uselist=False, back_populates="usuario", cascade="all, delete-orphan")

class Estadisticas(db.Model):
    __tablename__ = "estadisticas"
    
    id = db.Column(db.Integer, primary_key=True)
    puntaje = db.Column(db.Integer, default=0)
    correcto = db.Column(db.Integer, default=0)
    incorrecto = db.Column(db.Integer, default=0)

    # Clave foránea que referencia a Usuario
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"))

    # Relación inversa hacia Usuario
    usuario = db.relationship("Usuario", back_populates="estadisticas")

#Inicia la app y si es necesario crea la base de datos.
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
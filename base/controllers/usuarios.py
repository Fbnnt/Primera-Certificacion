from flask import render_template, redirect, request, session, Blueprint, flash
from base.models.usuario_model import Usuario
from bcrypt import hashpw, gensalt, checkpw

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@bp.route('/procesar_registro', methods=['POST'])
def procesar_registro():
    # Validación de campos vacíos
    if not request.form['nombre'] or not request.form['apellido'] or not request.form['email'] or not request.form['password']:
        flash("Todos los campos son obligatorios para registrarse.", "registro")
        return redirect('/')
    if not Usuario.validar_registro(request.form):
        return redirect('/')
    password_hash = hashpw(request.form['password'].encode('utf-8'), gensalt())
    data = {
        **request.form,
        'password': password_hash.decode('utf-8')
    }
    usuario_id = Usuario.guardar_usuario(data)
    usuario_db = Usuario.obtener_por_id(usuario_id)
    session['usuario_id'] = usuario_id
    session['nombre'] = usuario_db.nombre
    flash("¡Registro exitoso!", 'exito')
    return redirect('/dashboard')

@bp.route('/procesar_login', methods=['POST'])
def procesar_login():
    # Validación de campos vacíos
    if not request.form['email'] or not request.form['password']:
        flash("Todos los campos son obligatorios para iniciar sesión.", "login")
        return redirect('/')
    if not Usuario.validar_login(request.form):
        return redirect('/')
    usuario_db = Usuario.obtener_por_email(request.form)
    if not usuario_db:
        flash("El correo no está registrado.", "login")
        return redirect('/')
    # Verifica la contraseña
    if not checkpw(request.form['password'].encode('utf-8'), usuario_db.password.encode('utf-8')):
        flash("Contraseña incorrecta.", "login")
        return redirect('/')
    session['usuario_id'] = usuario_db.id
    session['nombre'] = usuario_db.nombre
    flash(f"¡Bienvenido de nuevo, {usuario_db.nombre}!", 'exito')
    return redirect('/dashboard')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

from base.models.cita_model import Cita
from base.models.usuario_model import Usuario
from flask import render_template, redirect, request, session, Blueprint, flash


bp = Blueprint('citas', __name__, url_prefix='/citas')


@bp.route('/agregar', methods=['POST'])
def agregar_cita():
    """
    Ruta para agregar una nueva cita.
    Solo usuarios autenticados pueden agregar.
    Valida la cita y muestra errores si es necesario.
    """
    if 'usuario_id' not in session:
        return redirect('/')
    if not Cita.validar_cita(request.form):
        return redirect('/citas')
    data = {
        'cita': request.form['cita'],
        'autor_id': session['usuario_id']
    }
    Cita.guardar_cita(data)
    return redirect('/citas')


@bp.route('/editar/<int:id>')
def pagina_editar(id):
    """
    Ruta para mostrar el formulario de edición de una cita.
    Solo el autor de la cita puede editarla.
    """
    if 'usuario_id' not in session:
        return redirect('/')
    cita = Cita.obtener_por_id(id)
    if not cita or cita.autor_id != session['usuario_id']:
        flash("No tienes permiso para editar esta cita.", 'error')
        return redirect('/citas')
    return render_template('editar_cita.html', cita=cita)


@bp.route('/procesar_editar', methods=['POST'])
def procesar_editar():
    """
    Procesa la edición de una cita.
    Solo el autor puede editar y se validan los datos.
    """
    if 'usuario_id' not in session:
        return redirect('/')
    cita_a_editar = Cita.obtener_por_id(request.form['id'])
    if not cita_a_editar or cita_a_editar.autor_id != session['usuario_id']:
        flash("No tienes permiso para editar esta cita.", 'error')
        return redirect('/citas')
    if not Cita.validar_cita(request.form):
        return redirect(f"/citas/editar/{request.form['id']}")
    Cita.actualizar_cita(request.form)
    return redirect('/citas')


@bp.route('/borrar/<int:id>')
def borrar_cita(id):
    """
    Ruta para borrar una cita.
    Solo el autor puede borrar su cita.
    """
    if 'usuario_id' not in session:
        return redirect('/')
    cita_a_borrar = Cita.obtener_por_id(id)
    if not cita_a_borrar or cita_a_borrar.autor_id != session['usuario_id']:
        flash("No tienes permiso para borrar esta cita.", 'error')
        return redirect('/citas')
    Cita.eliminar_cita(id)
    return redirect('/citas')


@bp.route('/perfil')
def perfil():
    """
    Muestra el perfil del usuario actual, sus citas y el total de publicaciones.
    """
    if 'usuario_id' not in session:
        return redirect('/')
    usuario = Usuario.obtener_por_id(session['usuario_id'])
    citas_usuario = Cita.obtener_citas_usuario(session['usuario_id'])
    total_citas = len(citas_usuario)
    return render_template('perfil.html', usuario=usuario, citas=citas_usuario, total_citas=total_citas)


@bp.route('/')
def dashboard():
    """
    Muestra el dashboard principal con todas las citas y las favoritas del usuario.
    """
    if 'usuario_id' not in session:
        return redirect('/')
    usuario = Usuario.obtener_por_id(session['usuario_id'])
    citas_no_favoritas = Cita.obtener_citas_no_favoritas(session['usuario_id'])
    citas_favoritas = Cita.obtener_favoritos_de_usuario(session['usuario_id'])
    return render_template('dashboard.html', usuario=usuario,
                            citas=citas_no_favoritas, favoritos=citas_favoritas)


@bp.route('/agregar_favorito/<int:cita_id>')
def agregar_favorito(cita_id):
    """
    Permite al usuario agregar una cita a su lista de favoritos.
    """
    if 'usuario_id' not in session:
        return redirect('/')
    data = {
        'usuario_id': session['usuario_id'],
        'cita_id': cita_id
    }
    Cita.agregar_favorito(data)
    return redirect('/citas')


@bp.route('/remover_favorito/<int:cita_id>')
def remover_favorito(cita_id):
    """
    Permite al usuario remover una cita de su lista de favoritos.
    """
    if 'usuario_id' not in session:
        return redirect('/')
    data = {
        'usuario_id': session['usuario_id'],
        'cita_id': cita_id
    }
    Cita.remover_de_favoritos(data)
    return redirect('/citas')
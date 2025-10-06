from flask import Blueprint, render_template, redirect, request, session, flash
from base.models.cita_model import Cita


bp = Blueprint('asesorias', __name__, url_prefix='/asesorias')


def require_login():
	if not session.get('usuario_id'):
		return redirect('/')
	return None


@bp.route('/')
def index():
	redirect_if = require_login()
	if redirect_if:
		return redirect_if
	asesorias = Cita.obtener_todas_futuras()
	return render_template('asesorias/index.html', asesorias=asesorias)


@bp.route('/nueva')
def nueva():
	redirect_if = require_login()
	if redirect_if:
		return redirect_if
	usuarios = Cita.obtener_usuarios_para_tutor(session['usuario_id'])
	return render_template('asesorias/crear.html', usuarios=usuarios)


@bp.route('/crear', methods=['POST'])
def crear():
	redirect_if = require_login()
	if redirect_if:
		return redirect_if
	if not Cita.validar_cita(request.form, validar_fecha_pasado=True):
		return redirect('/asesorias/nueva')
	data = {
		'titulo': request.form['titulo'].strip(),
		'fecha': request.form['fecha'],
		'duracion': int(request.form['duracion']),
		'notas': request.form.get('notas', '').strip(),
		'creador_id': session['usuario_id'],
		'tutor_id': int(request.form['tutor_id']) if request.form.get('tutor_id') else None,
	}
	Cita.guardar_cita(data)
	flash('Asesoría creada correctamente.', 'exito')
	return redirect('/asesorias')


@bp.route('/ver/<int:id>')
def ver(id):
	redirect_if = require_login()
	if redirect_if:
		return redirect_if
	asesoria = Cita.obtener_por_id(id)
	if not asesoria:
		flash('Asesoría no encontrada.', 'error')
		return redirect('/asesorias')
	usuarios = Cita.obtener_usuarios_para_tutor(asesoria.creador_id)
	return render_template('asesorias/ver.html', asesoria=asesoria, usuarios=usuarios)


@bp.route('/editar/<int:id>')
def editar(id):
	redirect_if = require_login()
	if redirect_if:
		return redirect_if
	asesoria = Cita.obtener_por_id(id)
	if not asesoria or asesoria.creador_id != session['usuario_id']:
		flash('No tienes permiso para editar esta asesoría.', 'error')
		return redirect('/asesorias')
	usuarios = Cita.obtener_usuarios_para_tutor(session['usuario_id'])
	return render_template('asesorias/editar.html', asesoria=asesoria, usuarios=usuarios)


@bp.route('/actualizar', methods=['POST'])
def actualizar():
	redirect_if = require_login()
	if redirect_if:
		return redirect_if
	asesoria = Cita.obtener_por_id(int(request.form['id']))
	if not asesoria or asesoria.creador_id != session['usuario_id']:
		flash('No tienes permiso para editar esta asesoría.', 'error')
		return redirect('/asesorias')
	if not Cita.validar_cita(request.form, validar_fecha_pasado=True):
		return redirect(f"/asesorias/editar/{asesoria.id}")
	data = {
		'id': asesoria.id,
		'titulo': request.form['titulo'].strip(),
		'fecha': request.form['fecha'],
		'duracion': int(request.form['duracion']),
		'notas': request.form.get('notas', '').strip(),
		'tutor_id': int(request.form['tutor_id']) if request.form.get('tutor_id') else None,
	}
	Cita.actualizar_cita(data)
	flash('Asesoría actualizada.', 'exito')
	return redirect('/asesorias')


@bp.route('/borrar/<int:id>')
def borrar(id):
	redirect_if = require_login()
	if redirect_if:
		return redirect_if
	asesoria = Cita.obtener_por_id(id)
	if not asesoria or asesoria.creador_id != session['usuario_id']:
		flash('No tienes permiso para borrar esta asesoría.', 'error')
		return redirect('/asesorias')
	Cita.eliminar_cita(id)
	flash('Asesoría eliminada.', 'exito')
	return redirect('/asesorias')


@bp.route('/<int:id>/cambiar_tutor', methods=['POST'])
def cambiar_tutor(id):
	redirect_if = require_login()
	if redirect_if:
		return redirect_if
	asesoria = Cita.obtener_por_id(id)
	if not asesoria:
		flash('Asesoría no encontrada.', 'error')
		return redirect('/asesorias')
	# Cualquier usuario puede cambiar el tutor, excepto que el creador no puede ser tutor
	nuevo_tutor_id = int(request.form['tutor_id']) if request.form.get('tutor_id') else None
	if nuevo_tutor_id == asesoria.creador_id:
		flash('El creador no puede ser el tutor.', 'asesoria')
		return redirect(f"/asesorias/ver/{id}")
	Cita.actualizar_tutor({'id': id, 'tutor_id': nuevo_tutor_id})
	flash('Tutor actualizado.', 'exito')
	return redirect(f"/asesorias/ver/{id}")



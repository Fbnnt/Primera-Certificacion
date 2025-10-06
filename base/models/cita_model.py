from base.config.mysqlconection import connectToMySQL
from flask import flash
from datetime import datetime, date


class Cita:
	"""
	Modelo de Asesoría (cita) con CRUD y validaciones.
	Campos: titulo, fecha, duracion (1-8), notas (<=50), creador_id, tutor_id
	"""
	db = "proyecto_crud"

	def __init__(self, data):
		self.id = data['id']
		self.titulo = data.get('titulo') or data.get('cita')
		self.fecha = data.get('fecha')
		self.duracion = data.get('duracion')
		self.notas = data.get('notas')
		self.creador_id = data.get('creador_id') or data.get('autor_id')
		self.tutor_id = data.get('tutor_id')
		self.creado_en = data.get('creado_en')
		self.actualizado_en = data.get('actualizado_en')
		self.autor = data.get('autor')
		self.tutor = data.get('tutor')

	@classmethod
	def guardar_cita(cls, data):
		query = """
			INSERT INTO asesorias (titulo, fecha, duracion, notas, creador_id, tutor_id)
			VALUES (%(titulo)s, %(fecha)s, %(duracion)s, %(notas)s, %(creador_id)s, %(tutor_id)s);
		"""
		return connectToMySQL(cls.db).query_db(query, data)

	@classmethod
	def obtener_por_id(cls, cita_id):
		query = """
			SELECT a.*, CONCAT(u.nombre,' ',u.apellido) AS autor,
			       CONCAT(t.nombre,' ',t.apellido) AS tutor
			FROM asesorias a
			JOIN usuarios u ON a.creador_id = u.id
			LEFT JOIN usuarios t ON a.tutor_id = t.id
			WHERE a.id = %(id)s;
		"""
		res = connectToMySQL(cls.db).query_db(query, {'id': cita_id})
		if not res:
			return None
		return cls(res[0])

	@classmethod
	def obtener_todas_futuras(cls):
		query = """
			SELECT a.*, CONCAT(u.nombre,' ',u.apellido) AS autor,
			       CONCAT(t.nombre,' ',t.apellido) AS tutor
			FROM asesorias a
			JOIN usuarios u ON a.creador_id = u.id
			LEFT JOIN usuarios t ON a.tutor_id = t.id
			WHERE a.fecha >= CURDATE()
			ORDER BY a.fecha ASC;
		"""
		res = connectToMySQL(cls.db).query_db(query)
		return [cls(r) for r in res] if res else []

	@classmethod
	def obtener_por_creador(cls, usuario_id):
		query = "SELECT * FROM asesorias WHERE creador_id = %(id)s;"
		res = connectToMySQL(cls.db).query_db(query, {'id': usuario_id})
		return [cls(r) for r in res] if res else []

	@classmethod
	def actualizar_cita(cls, data):
		query = """
			UPDATE asesorias
			SET titulo=%(titulo)s, fecha=%(fecha)s, duracion=%(duracion)s, notas=%(notas)s, tutor_id=%(tutor_id)s
			WHERE id = %(id)s;
		"""
		return connectToMySQL(cls.db).query_db(query, data)

	@classmethod
	def actualizar_tutor(cls, data):
		query = "UPDATE asesorias SET tutor_id=%(tutor_id)s WHERE id=%(id)s;"
		return connectToMySQL(cls.db).query_db(query, data)

	@classmethod
	def eliminar_cita(cls, cita_id):
		query = "DELETE FROM asesorias WHERE id = %(id)s;"
		return connectToMySQL(cls.db).query_db(query, {'id': cita_id})

	@staticmethod
	def validar_cita(form, validar_fecha_pasado=True):
		is_valid = True
		titulo = (form.get('titulo') or '').strip()
		fecha_str = (form.get('fecha') or '').strip()
		notas = (form.get('notas') or '').strip()
		duracion_raw = form.get('duracion')
		# Campos vacíos
		if not titulo:
			flash("El título es obligatorio.", 'asesoria')
			is_valid = False
		if not fecha_str:
			flash("La fecha es obligatoria.", 'asesoria')
			is_valid = False
		# Duración 1-8
		try:
			duracion = int(duracion_raw)
		except (TypeError, ValueError):
			flash("La duración debe ser un número entre 1 y 8.", 'asesoria')
			is_valid = False
			duracion = None
		if duracion is not None and (duracion < 1 or duracion > 8):
			flash("La duración debe ser un número entre 1 y 8.", 'asesoria')
			is_valid = False
		# Notas <= 50
		if len(notas) > 50:
			flash("Notas no puede tener más de 50 caracteres.", 'asesoria')
			is_valid = False
		# Fecha no en pasado (para BONUS y requerimiento de creación)
		if fecha_str:
			try:
				fecha_val = datetime.strptime(fecha_str, "%Y-%m-%d").date()
				if validar_fecha_pasado and fecha_val < date.today():
					flash("La fecha no puede ser en el pasado.", 'asesoria')
					is_valid = False
			except ValueError:
				flash("Formato de fecha inválido (YYYY-MM-DD).", 'asesoria')
				is_valid = False
		return is_valid

	@classmethod
	def obtener_usuarios_para_tutor(cls, excluir_usuario_id):
		query = "SELECT id, nombre, apellido FROM usuarios WHERE id != %(id)s;"
		res = connectToMySQL(cls.db).query_db(query, {'id': excluir_usuario_id})
		return res or []
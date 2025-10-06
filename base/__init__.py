from flask import Flask, render_template, redirect, session
from datetime import datetime


def create_app():
	app = Flask(__name__, template_folder="templates", static_folder="static")
	app.secret_key = "super-secret-key-change-me"

	# Filtro simple para fechas en templates
	@app.template_filter('format_date')
	def format_date(value, fmt="%Y-%m-%d"):
		if not value:
			return ""
		if isinstance(value, (datetime,)):
			return value.strftime(fmt)
		try:
			return datetime.strptime(str(value), "%Y-%m-%d").strftime(fmt)
		except Exception:
			return str(value)

	# Rutas/Blueprints
	from base.controllers.usuarios import bp as usuarios_bp
	app.register_blueprint(usuarios_bp)

	# Asesorías
	from base.controllers.asesorias import bp as asesorias_bp
	app.register_blueprint(asesorias_bp)

	# Ruta raíz: si está logueado, ir a asesorías; si no, mostrar auth
	@app.route("/")
	def root():
		if session.get('usuario_id'):
			return redirect('/asesorias')
		return render_template('auth.html')

	return app



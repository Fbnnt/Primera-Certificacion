from base.config.mysqlconection import connectToMySQL
from flask import flash, session


class Cita:
    @classmethod
    def obtener_citas_usuario(cls, usuario_id):
        """
        Obtiene todas las citas creadas por un usuario específico.
        """
        query = "SELECT * FROM citas WHERE autor_id = %(usuario_id)s;"
        data = {'usuario_id': usuario_id}
        resultados = connectToMySQL(cls.db).query_db(query, data)
        citas = []
        for row in resultados:
            citas.append(cls(row))
        return citas
    """
    Clase que representa una cita y sus operaciones en la base de datos.
    """
    db = "proyecto_crud"

    def __init__(self, data):
        """
        Constructor: inicializa los atributos de la cita.
        """
        self.id = data['id']
        self.cita = data['cita']
        self.autor_id = data['autor_id'] if 'autor_id' in data else None #
        self.usuario_id = data['usuario_id'] if 'usuario_id' in data else None
        self.creado_en = data['creado_en'] if 'creado_en' in data else None
        self.actualizado_en = data['actualizado_en'] if 'actualizado_en' in data else None

    @classmethod
    def guardar_cita(cls, data):
        """
        Guarda una nueva cita en la base de datos.
        """
        query = "INSERT INTO citas (cita, autor_id) VALUES (%(cita)s, %(autor_id)s);"
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return resultado


    @classmethod
    def obtener_por_id(cls, cita_id):
        """
        Busca una cita por su ID.
        """
        query = "SELECT * FROM citas WHERE id = %(id)s;"
        data = {'id': cita_id}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        if not resultado:
            return None
        return cls(resultado[0])
    
    @classmethod
    def obtener_todas(cls):
        """
        Obtiene todas las citas de la base de datos.
        """
        query = "SELECT * FROM citas;"
        resultados = connectToMySQL(cls.db).query_db(query)
        citas = []
        for row in resultados:
            citas.append(cls(row))
        return citas
    
    @classmethod
    def actualizar_cita(cls, data):
        """
        Actualiza los datos de una cita existente.
        """
        query = "UPDATE citas SET cita = %(cita)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def eliminar_cita(cls, cita_id):
        """
        Elimina una cita por su ID.
        """
        query = "DELETE FROM citas WHERE id = %(id)s;"
        data = {'id': cita_id}
        return connectToMySQL(cls.db).query_db(query, data)

    @staticmethod
    def validar_cita(cita):
        """
        Valida los datos del formulario de cita.
        Devuelve True si todo es válido, False si hay errores (y los muestra con flash).
        """
        is_valid = True
        if len(cita['cita']) < 5:
            flash("La cita debe tener al menos 5 caracteres.", 'cita')
            is_valid = False
        return is_valid

    @classmethod
    def agregar_favorito(cls, data):
        """
        Agrega una cita a la lista de favoritos de un usuario.
        """
        query = "INSERT INTO favoritos (usuario_id, cita_id) VALUES (%(usuario_id)s, %(cita_id)s);"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def quitar_favorito(cls, data):
        """
        Quita una cita de la lista de favoritos de un usuario.
        """
        query = "DELETE FROM favoritos WHERE usuario_id = %(usuario_id)s AND cita_id = %(cita_id)s;"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def obtener_favoritos_usuario(cls, usuario_id):
        """
        Obtiene todas las citas favoritas de un usuario.
        """
        query = "SELECT citas.* FROM favoritos JOIN citas ON favoritos.cita_id = citas.id WHERE favoritos.usuario_id = %(usuario_id)s;"
        data = {'usuario_id': usuario_id}
        resultados = connectToMySQL(cls.db).query_db(query, data)
        favoritos = []
        for row in resultados:
            favoritos.append(cls(row))
        return favoritos

    @classmethod
    def remover_de_favoritos(cls, data):
        query = "DELETE FROM favoritos WHERE usuario_id = %(usuario_id)s AND cita_id = %(cita_id)s;"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def obtener_favoritos_de_usuario(cls, usuario_id):
        query = """
            SELECT citas.*, usuarios.nombre, usuarios.apellido
            FROM favoritos
            JOIN citas ON favoritos.cita_id = citas.id
            JOIN usuarios ON citas.autor_id = usuarios.id
            WHERE favoritos.usuario_id = %(id)s;
        """
        data = {'id': usuario_id}
        resultados = connectToMySQL(cls.db).query_db(query, data)
        if not resultados:
            return []

        citas = []
        for row in resultados:
            cita = cls(row)
            cita.autor = f"{row['nombre']} {row['apellido']}"
            citas.append(cita)
        return citas

    @classmethod
    def obtener_citas_no_favoritas(cls, usuario_id):
        query = """
            SELECT citas.*, usuarios.nombre, usuarios.apellido
            FROM citas
            JOIN usuarios ON citas.autor_id = usuarios.id
            LEFT JOIN favoritos ON citas.id = favoritos.cita_id AND favoritos.usuario_id = %(id)s
            WHERE favoritos.cita_id IS NULL;
        """
        data = {'id': usuario_id}
        resultados = connectToMySQL(cls.db).query_db(query, data)
        if not resultados:
            return []

        citas = []
        for row in resultados:
            cita = cls(row)
            cita.autor = f"{row['nombre']} {row['apellido']}"
            citas.append(cita)
        return citas
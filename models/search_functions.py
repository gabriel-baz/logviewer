"""
Funciones de búsqueda para el módulo Database.
Se separan en un archivo aparte para mejorar la modularidad del código.
"""

def search_access_logs(self, search_term, page, per_page):
    """Busca registros de acceso que coincidan con el término de búsqueda"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            offset = (page - 1) * per_page
            # Búsqueda en múltiples columnas
            sql = """
            SELECT * FROM registros_acceso 
            WHERE ip LIKE %s 
            OR metodo LIKE %s 
            OR ruta LIKE %s 
            OR protocolo LIKE %s 
            OR CAST(codigo_estado AS CHAR) LIKE %s 
            OR CAST(bytes_enviados AS CHAR) LIKE %s 
            OR referer LIKE %s 
            OR user_agent LIKE %s 
            ORDER BY fecha_hora DESC 
            LIMIT %s OFFSET %s
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(sql, (
                search_pattern, search_pattern, search_pattern, search_pattern,
                search_pattern, search_pattern, search_pattern, search_pattern,
                per_page, offset
            ))
            return cursor.fetchall()
    finally:
        conn.close()

def count_search_access_logs(self, search_term):
    """Cuenta el total de registros de acceso que coinciden con el término de búsqueda"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT COUNT(*) as count FROM registros_acceso 
            WHERE ip LIKE %s 
            OR metodo LIKE %s 
            OR ruta LIKE %s 
            OR protocolo LIKE %s 
            OR CAST(codigo_estado AS CHAR) LIKE %s 
            OR CAST(bytes_enviados AS CHAR) LIKE %s 
            OR referer LIKE %s 
            OR user_agent LIKE %s
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(sql, (
                search_pattern, search_pattern, search_pattern, search_pattern,
                search_pattern, search_pattern, search_pattern, search_pattern
            ))
            result = cursor.fetchone()
            return result['count'] if result else 0
    finally:
        conn.close()

def search_access_logs_advanced(self, search_params, page, per_page):
    """Busca registros de acceso con parámetros avanzados"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            offset = (page - 1) * per_page
            conditions = []
            params = []
            
            # Filtro de fecha
            if search_params.get('start_date'):
                conditions.append("fecha_hora >= %s")
                params.append(search_params['start_date'])
            if search_params.get('end_date'):
                conditions.append("fecha_hora <= %s")
                params.append(search_params['end_date'])
            
            # Filtros de términos
            term1 = search_params.get('term1', '')
            term2 = search_params.get('term2', '')
            operator = search_params.get('operator', 'AND')
            
            # Construir condiciones para términos
            if term1 and term2:
                term1_condition = "(ip LIKE %s OR metodo LIKE %s OR ruta LIKE %s OR user_agent LIKE %s)"
                term2_condition = "(ip LIKE %s OR metodo LIKE %s OR ruta LIKE %s OR user_agent LIKE %s)"
                
                term1_pattern = f"%{term1}%"
                term2_pattern = f"%{term2}%"
                
                if operator == 'AND':
                    conditions.append(f"{term1_condition} AND {term2_condition}")
                    params.extend([term1_pattern, term1_pattern, term1_pattern, term1_pattern, 
                                  term2_pattern, term2_pattern, term2_pattern, term2_pattern])
                else:  # OR
                    conditions.append(f"{term1_condition} OR {term2_condition}")
                    params.extend([term1_pattern, term1_pattern, term1_pattern, term1_pattern, 
                                  term2_pattern, term2_pattern, term2_pattern, term2_pattern])
            elif term1:
                conditions.append("(ip LIKE %s OR metodo LIKE %s OR ruta LIKE %s OR user_agent LIKE %s)")
                term1_pattern = f"%{term1}%"
                params.extend([term1_pattern, term1_pattern, term1_pattern, term1_pattern])
            elif term2:
                conditions.append("(ip LIKE %s OR metodo LIKE %s OR ruta LIKE %s OR user_agent LIKE %s)")
                term2_pattern = f"%{term2}%"
                params.extend([term2_pattern, term2_pattern, term2_pattern, term2_pattern])
            
            # Filtro de campo específico si se proporciona
            if search_params.get('filter_field') and search_params.get('filter_value'):
                field = search_params['filter_field']
                value = search_params['filter_value']
                
                # Validación básica para evitar inyección SQL
                valid_fields = ['ip', 'metodo', 'ruta', 'protocolo', 'codigo_estado', 'bytes_enviados', 'referer', 'user_agent']
                if field in valid_fields:
                    conditions.append(f"{field} LIKE %s")
                    params.append(f"%{value}%")
            
            # Construir la consulta SQL final
            sql = "SELECT * FROM registros_acceso"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            sql += " ORDER BY fecha_hora DESC LIMIT %s OFFSET %s"
            
            params.extend([per_page, offset])
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()

def count_search_access_logs_advanced(self, search_params):
    """Cuenta el total de registros de acceso que coinciden con los parámetros de búsqueda avanzada"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            conditions = []
            params = []
            
            # Filtro de fecha
            if search_params.get('start_date'):
                conditions.append("fecha_hora >= %s")
                params.append(search_params['start_date'])
            if search_params.get('end_date'):
                conditions.append("fecha_hora <= %s")
                params.append(search_params['end_date'])
            
            # Filtros de términos
            term1 = search_params.get('term1', '')
            term2 = search_params.get('term2', '')
            operator = search_params.get('operator', 'AND')
            
            # Construir condiciones para términos
            if term1 and term2:
                term1_condition = "(ip LIKE %s OR metodo LIKE %s OR ruta LIKE %s OR user_agent LIKE %s)"
                term2_condition = "(ip LIKE %s OR metodo LIKE %s OR ruta LIKE %s OR user_agent LIKE %s)"
                
                term1_pattern = f"%{term1}%"
                term2_pattern = f"%{term2}%"
                
                if operator == 'AND':
                    conditions.append(f"{term1_condition} AND {term2_condition}")
                    params.extend([term1_pattern, term1_pattern, term1_pattern, term1_pattern, 
                                  term2_pattern, term2_pattern, term2_pattern, term2_pattern])
                else:  # OR
                    conditions.append(f"{term1_condition} OR {term2_condition}")
                    params.extend([term1_pattern, term1_pattern, term1_pattern, term1_pattern, 
                                  term2_pattern, term2_pattern, term2_pattern, term2_pattern])
            elif term1:
                conditions.append("(ip LIKE %s OR metodo LIKE %s OR ruta LIKE %s OR user_agent LIKE %s)")
                term1_pattern = f"%{term1}%"
                params.extend([term1_pattern, term1_pattern, term1_pattern, term1_pattern])
            elif term2:
                conditions.append("(ip LIKE %s OR metodo LIKE %s OR ruta LIKE %s OR user_agent LIKE %s)")
                term2_pattern = f"%{term2}%"
                params.extend([term2_pattern, term2_pattern, term2_pattern, term2_pattern])
            
            # Filtro de campo específico si se proporciona
            if search_params.get('filter_field') and search_params.get('filter_value'):
                field = search_params['filter_field']
                value = search_params['filter_value']
                
                # Validación básica para evitar inyección SQL
                valid_fields = ['ip', 'metodo', 'ruta', 'protocolo', 'codigo_estado', 'bytes_enviados', 'referer', 'user_agent']
                if field in valid_fields:
                    conditions.append(f"{field} LIKE %s")
                    params.append(f"%{value}%")
                    
            # Construir la consulta SQL final
            sql = "SELECT COUNT(*) as count FROM registros_acceso"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result['count'] if result else 0
    finally:
        conn.close()

def search_error_logs(self, search_term, page, per_page):
    """Busca registros de error que coincidan con el término de búsqueda"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            offset = (page - 1) * per_page
            # Búsqueda en múltiples columnas
            sql = """
            SELECT * FROM registros_error 
            WHERE nivel_error LIKE %s 
            OR cliente LIKE %s 
            OR mensaje LIKE %s 
            OR archivo LIKE %s 
            OR CAST(linea AS CHAR) LIKE %s
            ORDER BY fecha_hora DESC 
            LIMIT %s OFFSET %s
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(sql, (
                search_pattern, search_pattern, search_pattern, search_pattern,
                search_pattern, per_page, offset
            ))
            return cursor.fetchall()
    finally:
        conn.close()

def count_search_error_logs(self, search_term):
    """Cuenta el total de registros de error que coinciden con el término de búsqueda"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT COUNT(*) as count FROM registros_error 
            WHERE nivel_error LIKE %s 
            OR cliente LIKE %s 
            OR mensaje LIKE %s 
            OR archivo LIKE %s 
            OR CAST(linea AS CHAR) LIKE %s
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(sql, (
                search_pattern, search_pattern, search_pattern, search_pattern,
                search_pattern
            ))
            result = cursor.fetchone()
            return result['count'] if result else 0
    finally:
        conn.close()

def search_error_logs_advanced(self, search_params, page, per_page):
    """Busca registros de error con parámetros avanzados"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            offset = (page - 1) * per_page
            conditions = []
            params = []
            
            # Filtro de fecha
            if search_params.get('start_date'):
                conditions.append("fecha_hora >= %s")
                params.append(search_params['start_date'])
            if search_params.get('end_date'):
                conditions.append("fecha_hora <= %s")
                params.append(search_params['end_date'])
            
            # Filtros de términos
            term1 = search_params.get('term1', '')
            term2 = search_params.get('term2', '')
            operator = search_params.get('operator', 'AND')
            
            # Construir condiciones para términos
            if term1 and term2:
                term1_condition = "(nivel_error LIKE %s OR cliente LIKE %s OR mensaje LIKE %s OR archivo LIKE %s)"
                term2_condition = "(nivel_error LIKE %s OR cliente LIKE %s OR mensaje LIKE %s OR archivo LIKE %s)"
                
                term1_pattern = f"%{term1}%"
                term2_pattern = f"%{term2}%"
                
                if operator == 'AND':
                    conditions.append(f"{term1_condition} AND {term2_condition}")
                else:  # OR
                    conditions.append(f"{term1_condition} OR {term2_condition}")
                
                params.extend([
                    term1_pattern, term1_pattern, term1_pattern, term1_pattern,
                    term2_pattern, term2_pattern, term2_pattern, term2_pattern
                ])
            elif term1:
                conditions.append("(nivel_error LIKE %s OR cliente LIKE %s OR mensaje LIKE %s OR archivo LIKE %s)")
                term1_pattern = f"%{term1}%"
                params.extend([term1_pattern, term1_pattern, term1_pattern, term1_pattern])
            elif term2:
                conditions.append("(nivel_error LIKE %s OR cliente LIKE %s OR mensaje LIKE %s OR archivo LIKE %s)")
                term2_pattern = f"%{term2}%"
                params.extend([term2_pattern, term2_pattern, term2_pattern, term2_pattern])
            
            # Filtro de campo específico si se proporciona
            if search_params.get('filter_field') and search_params.get('filter_value'):
                field = search_params['filter_field']
                value = search_params['filter_value']
                
                # Validación básica para evitar inyección SQL
                valid_fields = ['nivel_error', 'cliente', 'mensaje', 'archivo', 'linea']
                if field in valid_fields:
                    conditions.append(f"{field} LIKE %s")
                    params.append(f"%{value}%")
            
            # Construir la consulta SQL final
            sql = "SELECT * FROM registros_error"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            sql += " ORDER BY fecha_hora DESC LIMIT %s OFFSET %s"
            
            params.extend([per_page, offset])
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()

def count_search_error_logs_advanced(self, search_params):
    """Cuenta el total de registros de error que coinciden con la búsqueda avanzada"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            conditions = []
            params = []
            
            # Filtro de fecha
            if search_params.get('start_date'):
                conditions.append("fecha_hora >= %s")
                params.append(search_params['start_date'])
            if search_params.get('end_date'):
                conditions.append("fecha_hora <= %s")
                params.append(search_params['end_date'])
            
            # Filtros de términos
            term1 = search_params.get('term1', '')
            term2 = search_params.get('term2', '')
            operator = search_params.get('operator', 'AND')
            
            # Construir condiciones para términos
            if term1 and term2:
                term1_condition = "(nivel_error LIKE %s OR cliente LIKE %s OR mensaje LIKE %s OR archivo LIKE %s)"
                term2_condition = "(nivel_error LIKE %s OR cliente LIKE %s OR mensaje LIKE %s OR archivo LIKE %s)"
                
                term1_pattern = f"%{term1}%"
                term2_pattern = f"%{term2}%"
                
                if operator == 'AND':
                    conditions.append(f"{term1_condition} AND {term2_condition}")
                else:  # OR
                    conditions.append(f"{term1_condition} OR {term2_condition}")
                
                params.extend([
                    term1_pattern, term1_pattern, term1_pattern, term1_pattern,
                    term2_pattern, term2_pattern, term2_pattern, term2_pattern
                ])
            elif term1:
                conditions.append("(nivel_error LIKE %s OR cliente LIKE %s OR mensaje LIKE %s OR archivo LIKE %s)")
                term1_pattern = f"%{term1}%"
                params.extend([term1_pattern, term1_pattern, term1_pattern, term1_pattern])
            elif term2:
                conditions.append("(nivel_error LIKE %s OR cliente LIKE %s OR mensaje LIKE %s OR archivo LIKE %s)")
                term2_pattern = f"%{term2}%"
                params.extend([term2_pattern, term2_pattern, term2_pattern, term2_pattern])
            
            # Filtro de campo específico si se proporciona
            if search_params.get('filter_field') and search_params.get('filter_value'):
                field = search_params['filter_field']
                value = search_params['filter_value']
                
                # Validación básica para evitar inyección SQL
                valid_fields = ['nivel_error', 'cliente', 'mensaje', 'archivo', 'linea']
                if field in valid_fields:
                    conditions.append(f"{field} LIKE %s")
                    params.append(f"%{value}%")
                    
            # Construir la consulta SQL final
            sql = "SELECT COUNT(*) as count FROM registros_error"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result['count'] if result else 0
    finally:
        conn.close()

def search_ftp_logs(self, search_term, page, per_page):
    """Busca registros FTP que coincidan con el término de búsqueda"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            offset = (page - 1) * per_page
            # Búsqueda en múltiples columnas
            sql = """
            SELECT * FROM registros_ftp 
            WHERE usuario LIKE %s 
            OR ip LIKE %s 
            OR accion LIKE %s 
            OR archivo LIKE %s 
            OR detalles LIKE %s 
            ORDER BY fecha_hora DESC 
            LIMIT %s OFFSET %s
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(sql, (
                search_pattern, search_pattern, search_pattern, search_pattern,
                search_pattern, per_page, offset
            ))
            return cursor.fetchall()
    finally:
        conn.close()

def count_search_ftp_logs(self, search_term):
    """Cuenta el total de registros FTP que coinciden con el término de búsqueda"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT COUNT(*) as count FROM registros_ftp 
            WHERE usuario LIKE %s 
            OR ip LIKE %s 
            OR accion LIKE %s 
            OR archivo LIKE %s 
            OR detalles LIKE %s 
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(sql, (
                search_pattern, search_pattern, search_pattern, search_pattern,
                search_pattern
            ))
            result = cursor.fetchone()
            return result['count'] if result else 0
    finally:
        conn.close()

def search_ftp_logs_advanced(self, search_params, page, per_page):
    """Busca registros FTP con parámetros avanzados"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            offset = (page - 1) * per_page
            conditions = []
            params = []
            
            # Filtro de fecha
            if search_params.get('start_date'):
                conditions.append("fecha_hora >= %s")
                params.append(search_params['start_date'])
            if search_params.get('end_date'):
                conditions.append("fecha_hora <= %s")
                params.append(search_params['end_date'])
            
            # Filtros de términos
            term1 = search_params.get('term1', '')
            term2 = search_params.get('term2', '')
            operator = search_params.get('operator', 'AND')
            
            # Construir condiciones para términos
            if term1 and term2:
                term1_condition = "(usuario LIKE %s OR ip LIKE %s OR accion LIKE %s OR archivo LIKE %s OR detalles LIKE %s)"
                term2_condition = "(usuario LIKE %s OR ip LIKE %s OR accion LIKE %s OR archivo LIKE %s OR detalles LIKE %s)"
                
                term1_pattern = f"%{term1}%"
                term2_pattern = f"%{term2}%"
                
                if operator == 'AND':
                    conditions.append(f"{term1_condition} AND {term2_condition}")
                else:  # OR
                    conditions.append(f"{term1_condition} OR {term2_condition}")
                
                params.extend([
                    term1_pattern, term1_pattern, term1_pattern, term1_pattern, term1_pattern,
                    term2_pattern, term2_pattern, term2_pattern, term2_pattern, term2_pattern
                ])
            elif term1:
                conditions.append("(usuario LIKE %s OR ip LIKE %s OR accion LIKE %s OR archivo LIKE %s OR detalles LIKE %s)")
                term1_pattern = f"%{term1}%"
                params.extend([term1_pattern, term1_pattern, term1_pattern, term1_pattern, term1_pattern])
            elif term2:
                conditions.append("(usuario LIKE %s OR ip LIKE %s OR accion LIKE %s OR archivo LIKE %s OR detalles LIKE %s)")
                term2_pattern = f"%{term2}%"
                params.extend([term2_pattern, term2_pattern, term2_pattern, term2_pattern, term2_pattern])
            
            # Filtro de campo específico si se proporciona
            if search_params.get('filter_field') and search_params.get('filter_value'):
                field = search_params['filter_field']
                value = search_params['filter_value']
                
                # Validación básica para evitar inyección SQL
                valid_fields = ['usuario', 'ip', 'accion', 'archivo', 'detalles']
                if field in valid_fields:
                    conditions.append(f"{field} LIKE %s")
                    params.append(f"%{value}%")
            
            # Construir la consulta SQL final
            sql = "SELECT * FROM registros_ftp"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            sql += " ORDER BY fecha_hora DESC LIMIT %s OFFSET %s"
            
            params.extend([per_page, offset])
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()

def count_search_ftp_logs_advanced(self, search_params):
    """Cuenta el total de registros FTP que coinciden con la búsqueda avanzada"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            conditions = []
            params = []
            
            # Filtro de fecha
            if search_params.get('start_date'):
                conditions.append("fecha_hora >= %s")
                params.append(search_params['start_date'])
            if search_params.get('end_date'):
                conditions.append("fecha_hora <= %s")
                params.append(search_params['end_date'])
            
            # Filtros de términos
            term1 = search_params.get('term1', '')
            term2 = search_params.get('term2', '')
            operator = search_params.get('operator', 'AND')
            
            # Construir condiciones para términos
            if term1 and term2:
                term1_condition = "(usuario LIKE %s OR ip LIKE %s OR accion LIKE %s OR archivo LIKE %s OR detalles LIKE %s)"
                term2_condition = "(usuario LIKE %s OR ip LIKE %s OR accion LIKE %s OR archivo LIKE %s OR detalles LIKE %s)"
                
                term1_pattern = f"%{term1}%"
                term2_pattern = f"%{term2}%"
                
                if operator == 'AND':
                    conditions.append(f"{term1_condition} AND {term2_condition}")
                else:  # OR
                    conditions.append(f"{term1_condition} OR {term2_condition}")
                
                params.extend([
                    term1_pattern, term1_pattern, term1_pattern, term1_pattern, term1_pattern,
                    term2_pattern, term2_pattern, term2_pattern, term2_pattern, term2_pattern
                ])
            elif term1:
                conditions.append("(usuario LIKE %s OR ip LIKE %s OR accion LIKE %s OR archivo LIKE %s OR detalles LIKE %s)")
                term1_pattern = f"%{term1}%"
                params.extend([term1_pattern, term1_pattern, term1_pattern, term1_pattern, term1_pattern])
            elif term2:
                conditions.append("(usuario LIKE %s OR ip LIKE %s OR accion LIKE %s OR archivo LIKE %s OR detalles LIKE %s)")
                term2_pattern = f"%{term2}%"
                params.extend([term2_pattern, term2_pattern, term2_pattern, term2_pattern, term2_pattern])
            
            # Filtro de campo específico si se proporciona
            if search_params.get('filter_field') and search_params.get('filter_value'):
                field = search_params['filter_field']
                value = search_params['filter_value']
                
                # Validación básica para evitar inyección SQL
                valid_fields = ['usuario', 'ip', 'accion', 'archivo', 'detalles']
                if field in valid_fields:
                    conditions.append(f"{field} LIKE %s")
                    params.append(f"%{value}%")
                    
            # Construir la consulta SQL final
            sql = "SELECT COUNT(*) as count FROM registros_ftp"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result['count'] if result else 0
    finally:
        conn.close()

def search_ftp_transfers(self, search_term, page, per_page):
    """Busca registros de transferencia FTP que coincidan con el término de búsqueda"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            offset = (page - 1) * per_page
            # Búsqueda en múltiples columnas
            sql = """
            SELECT * FROM transferencias_ftp 
            WHERE usuario LIKE %s 
            OR ip_remota LIKE %s 
            OR archivo LIKE %s 
            OR servidor LIKE %s 
            OR tipo_transferencia LIKE %s 
            OR servicio LIKE %s 
            OR CAST(tamaño_archivo AS CHAR) LIKE %s 
            ORDER BY fecha_hora DESC 
            LIMIT %s OFFSET %s
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(sql, (
                search_pattern, search_pattern, search_pattern, search_pattern,
                search_pattern, search_pattern, search_pattern,
                per_page, offset
            ))
            return cursor.fetchall()
    finally:
        conn.close()

def count_search_ftp_transfers(self, search_term):
    """Cuenta el total de registros de transferencia FTP que coinciden con el término de búsqueda"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT COUNT(*) as count FROM transferencias_ftp 
            WHERE usuario LIKE %s 
            OR ip_remota LIKE %s 
            OR archivo LIKE %s 
            OR servidor LIKE %s 
            OR tipo_transferencia LIKE %s 
            OR servicio LIKE %s 
            OR CAST(tamaño_archivo AS CHAR) LIKE %s 
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(sql, (
                search_pattern, search_pattern, search_pattern, search_pattern,
                search_pattern, search_pattern, search_pattern
            ))
            result = cursor.fetchone()
            return result['count'] if result else 0
    finally:
        conn.close()

def search_ftp_transfers_advanced(self, search_params, page, per_page):
    """Busca registros de transferencia FTP con parámetros avanzados"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            offset = (page - 1) * per_page
            conditions = []
            params = []
            
            # Filtro de fecha
            if search_params.get('start_date'):
                conditions.append("fecha_hora >= %s")
                params.append(search_params['start_date'])
            if search_params.get('end_date'):
                conditions.append("fecha_hora <= %s")
                params.append(search_params['end_date'])
            
            # Filtros de términos
            term1 = search_params.get('term1', '')
            term2 = search_params.get('term2', '')
            operator = search_params.get('operator', 'AND')
            
            # Construir condiciones para términos
            if term1 and term2:
                term1_condition = "(usuario LIKE %s OR ip_remota LIKE %s OR archivo LIKE %s OR servidor LIKE %s OR tipo_transferencia LIKE %s)"
                term2_condition = "(usuario LIKE %s OR ip_remota LIKE %s OR archivo LIKE %s OR servidor LIKE %s OR tipo_transferencia LIKE %s)"
                
                term1_pattern = f"%{term1}%"
                term2_pattern = f"%{term2}%"
                
                if operator == 'AND':
                    conditions.append(f"{term1_condition} AND {term2_condition}")
                else:  # OR
                    conditions.append(f"{term1_condition} OR {term2_condition}")
                
                params.extend([
                    term1_pattern, term1_pattern, term1_pattern, term1_pattern, term1_pattern,
                    term2_pattern, term2_pattern, term2_pattern, term2_pattern, term2_pattern
                ])
            elif term1:
                conditions.append("(usuario LIKE %s OR ip_remota LIKE %s OR archivo LIKE %s OR servidor LIKE %s OR tipo_transferencia LIKE %s)")
                term1_pattern = f"%{term1}%"
                params.extend([term1_pattern, term1_pattern, term1_pattern, term1_pattern, term1_pattern])
            elif term2:
                conditions.append("(usuario LIKE %s OR ip_remota LIKE %s OR archivo LIKE %s OR servidor LIKE %s OR tipo_transferencia LIKE %s)")
                term2_pattern = f"%{term2}%"
                params.extend([term2_pattern, term2_pattern, term2_pattern, term2_pattern, term2_pattern])
            
            # Filtro de campo específico si se proporciona
            if search_params.get('filter_field') and search_params.get('filter_value'):
                field = search_params['filter_field']
                value = search_params['filter_value']
                
                # Validación básica para evitar inyección SQL
                valid_fields = ['usuario', 'ip_remota', 'archivo', 'servidor', 'tipo_transferencia', 'duracion', 'servicio', 'tamaño_archivo']
                if field in valid_fields:
                    conditions.append(f"{field} LIKE %s")
                    params.append(f"%{value}%")
            
            # Construir la consulta SQL final
            sql = "SELECT * FROM transferencias_ftp"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            sql += " ORDER BY fecha_hora DESC LIMIT %s OFFSET %s"
            
            params.extend([per_page, offset])
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()

def count_search_ftp_transfers_advanced(self, search_params):
    """Cuenta el total de registros de transferencia FTP que coinciden con la búsqueda avanzada"""
    conn = self.get_connection()
    try:
        with conn.cursor() as cursor:
            conditions = []
            params = []
            
            # Filtro de fecha
            if search_params.get('start_date'):
                conditions.append("fecha_hora >= %s")
                params.append(search_params['start_date'])
            if search_params.get('end_date'):
                conditions.append("fecha_hora <= %s")
                params.append(search_params['end_date'])
            
            # Filtros de términos
            term1 = search_params.get('term1', '')
            term2 = search_params.get('term2', '')
            operator = search_params.get('operator', 'AND')
            
            # Construir condiciones para términos
            if term1 and term2:
                term1_condition = "(usuario LIKE %s OR ip_remota LIKE %s OR archivo LIKE %s OR servidor LIKE %s OR tipo_transferencia LIKE %s)"
                term2_condition = "(usuario LIKE %s OR ip_remota LIKE %s OR archivo LIKE %s OR servidor LIKE %s OR tipo_transferencia LIKE %s)"
                
                term1_pattern = f"%{term1}%"
                term2_pattern = f"%{term2}%"
                
                if operator == 'AND':
                    conditions.append(f"{term1_condition} AND {term2_condition}")
                else:  # OR
                    conditions.append(f"{term1_condition} OR {term2_condition}")
                
                params.extend([
                    term1_pattern, term1_pattern, term1_pattern, term1_pattern, term1_pattern,
                    term2_pattern, term2_pattern, term2_pattern, term2_pattern, term2_pattern
                ])
            elif term1:
                conditions.append("(usuario LIKE %s OR ip_remota LIKE %s OR archivo LIKE %s OR servidor LIKE %s OR tipo_transferencia LIKE %s)")
                term1_pattern = f"%{term1}%"
                params.extend([term1_pattern, term1_pattern, term1_pattern, term1_pattern, term1_pattern])
            elif term2:
                conditions.append("(usuario LIKE %s OR ip_remota LIKE %s OR archivo LIKE %s OR servidor LIKE %s OR tipo_transferencia LIKE %s)")
                term2_pattern = f"%{term2}%"
                params.extend([term2_pattern, term2_pattern, term2_pattern, term2_pattern, term2_pattern])
            
            # Filtro de campo específico si se proporciona
            if search_params.get('filter_field') and search_params.get('filter_value'):
                field = search_params['filter_field']
                value = search_params['filter_value']
                
                # Validación básica para evitar inyección SQL
                valid_fields = ['usuario', 'ip_remota', 'archivo', 'servidor', 'tipo_transferencia', 'duracion', 'servicio', 'tamaño_archivo']
                if field in valid_fields:
                    conditions.append(f"{field} LIKE %s")
                    params.append(f"%{value}%")
                    
            # Construir la consulta SQL final
            sql = "SELECT COUNT(*) as count FROM transferencias_ftp"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result['count'] if result else 0
    finally:
        conn.close()

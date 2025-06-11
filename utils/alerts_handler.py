import pymysql
import pymysql.cursors
from pymysql import Error
import config

class AlertsHandler:
    """Clase para manejar las alertas y errores en los logs"""
    
    def __init__(self):
        """Constructor para AlertsHandler"""
        self.config = config.DB_CONFIG
    
    def get_connection(self):
        """Establece conexión con la base de datos"""
        try:
            # Use pymysql for consistency with the Database class
            connection = pymysql.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except Error as e:
            print(f"Error conectando a la base de datos: {e}")
            return None
    
    def identify_table_with_data(self):
        """Identifica cual tabla tiene datos en la base de datos"""
        connection = self.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor()
        tables = ['registros_acceso', 'registros_error', 'registros_ftp', 'transferencias_ftp']
        table_with_data = None
        
        try:
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                result = cursor.fetchone()
                count = result['count'] if result else 0
                if count > 0:
                    table_with_data = table
                    break
            
            return table_with_data
        except Error as e:
            print(f"Error identificando tabla con datos: {e}")
            return None
        finally:
            # pymysql no tiene método is_connected()
            cursor.close()
            connection.close()
    
    def get_error_logs(self):
        """Obtiene logs de error según la tabla que contiene datos"""
        table_with_data = self.identify_table_with_data()
        if not table_with_data:
            return {'table': None, 'logs': []}
        
        connection = self.get_connection()
        if not connection:
            return {'table': table_with_data, 'logs': []}
        
        cursor = connection.cursor()
        error_logs = []
        
        try:
            # Lógica dependiendo de la tabla que tiene datos
            if table_with_data == 'registros_acceso':
                # Filtramos accesos con códigos de error (4xx y 5xx)
                cursor.execute("""
                    SELECT DISTINCT fecha_hora, ip, metodo, ruta, protocolo, codigo_estado, 
                                    bytes_enviados, referer, user_agent, tiempo_respuesta
                    FROM registros_acceso
                    WHERE codigo_estado >= 400
                    ORDER BY fecha_hora DESC
                """)
                error_logs = cursor.fetchall()
                
            elif table_with_data == 'registros_error':
                # Todos los registros en esta tabla son errores
                cursor.execute("""
                    SELECT id, fecha_hora, nivel_error, cliente, mensaje, archivo, linea
                    FROM registros_error
                    WHERE nivel_error != 'unknown'
                    ORDER BY 
                        CASE nivel_error
                            WHEN 'emerg' THEN 1
                            WHEN 'alert' THEN 2
                            WHEN 'crit' THEN 3
                            WHEN 'error' THEN 4
                            WHEN 'warn' THEN 5
                            WHEN 'notice' THEN 6
                            WHEN 'info' THEN 7
                            WHEN 'debug' THEN 8
                            ELSE 9
                                END,
                            fecha_hora DESC;
                    """)
                error_logs = cursor.fetchall()
                
            elif table_with_data == 'registros_ftp':
                # Filtramos eventos FTP que indiquen errores
                cursor.execute("""
                    SELECT fecha_hora, usuario, ip, accion, archivo, detalles
                    FROM registros_ftp
                    WHERE accion IN ('LOGIN FAIL', 'UPLOAD FAIL', 'ERROR', 'UNAUTHORIZED', 'INVALID COMMAND')
                        OR detalles LIKE '%fail%' OR detalles LIKE '%error%' OR detalles LIKE '%denied%'
                    ORDER BY fecha_hora DESC
                    """)
                error_logs = cursor.fetchall()
                
            elif table_with_data == 'transferencias_ftp':
                # Filtramos transferencias fallidas o con errores
                cursor.execute("""
                    SELECT fecha_hora, duracion, tamaño_archivo, ip_remota, archivo, accion_especial, usuario, servicio
                    FROM transferencias_ftp
                    WHERE duracion > 120
                        OR tamaño_archivo > 100000000
                    ORDER BY fecha_hora DESC;
                    """)
                error_logs = cursor.fetchall()
                
            return {
                'table': table_with_data,
                'logs': error_logs
            }
            
        except Error as e:
            print(f"Error al obtener logs de error: {e}")
            return {
                'table': table_with_data,
                'logs': []
            }
        finally:
            # pymysql no tiene método is_connected()
            cursor.close()
            connection.close()

# Función para usar externamente
def get_alerts():
    """Función para obtener las alertas y errores de los logs"""
    handler = AlertsHandler()
    return handler.get_error_logs()
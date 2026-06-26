import os

# Credenciales para Render (por defecto) y localhost para desarrollo
DB_HOST = os.getenv('DB_HOST', 'dpg-d8utbu4vikkc73f0piqg-a.virginia-postgres.render.com')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_NAME = os.getenv('DB_NAME', 'sistema_rifas_vkpx')
DB_USER = os.getenv('DB_USER', 'sistema_rifas_vkpx_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Ux10tLTtARXuVudmWmCG6niv7uB6828M')

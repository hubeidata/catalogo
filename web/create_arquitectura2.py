import os

def crear_estructura(base_dir='catalogo_san_valentin'):
    """
    Crea la estructura de carpetas y archivos para el proyecto 'catalogo_san_valentin'.
    """
    # Lista de directorios a crear
    directorios = [
        base_dir,
        os.path.join(base_dir, 'static'),
        os.path.join(base_dir, 'static', 'css'),
        os.path.join(base_dir, 'static', 'imagenes'),
        os.path.join(base_dir, 'static', 'imagenes', 'imagenes_extraidas'),
        os.path.join(base_dir, 'static', 'uploads'),
        os.path.join(base_dir, 'templates')
    ]
    
    # Crear cada directorio (si ya existe, no arroja error gracias a exist_ok=True)
    for directorio in directorios:
        os.makedirs(directorio, exist_ok=True)
        print(f"Directorio creado: {directorio}")

    # Diccionario de archivos a crear con contenido inicial
    archivos = {
        os.path.join(base_dir, 'app.py'): "# Código principal de la aplicación\n\nif __name__ == '__main__':\n    print('Aplicacióoooon iniciada')\n",
        os.path.join(base_dir, 'descripcion.json'): "{\n    \"descripcion\": \"Catálogo de San Valentín\"\n}\n",
        os.path.join(base_dir, 'catalogo.db'): "",  # Archivo vacío, se creará automáticamente al iniciar la aplicación
        os.path.join(base_dir, 'static', 'css', 'style.css'): "/* Archivo de estilos CSS */\n",
        os.path.join(base_dir, 'static', 'imagenes', 'fondo.jpg'): "",  # Archivo placeholder (puedes reemplazarlo por una imagen real)
        os.path.join(base_dir, 'static', 'imagenes', 'qr_code.png'): "",  # Archivo placeholder (imagen QR)
        os.path.join(base_dir, 'templates', 'base.html'): "<!-- Archivo base HTML -->\n",
        os.path.join(base_dir, 'templates', 'index.html'): "<!-- Página principal -->\n",
        os.path.join(base_dir, 'templates', 'carrito.html'): "<!-- Página del carrito de compras -->\n",
        os.path.join(base_dir, 'templates', 'checkout.html'): "<!-- Página de checkout -->\n"
    }
    
    # Crear cada archivo con el contenido indicado
    for ruta_archivo, contenido in archivos.items():
        with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write(contenido)
        print(f"Archivo creado: {ruta_archivo}")

if __name__ == '__main__':
    crear_estructura()

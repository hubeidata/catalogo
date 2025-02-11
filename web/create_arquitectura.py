import os

def crear_estructura():
    estructura = {
        "san-valentin-app": [
            "static/css/styles.css",
            "static/images/qr_code.png",
            "static/images/background.jpg",
            "static/js/scripts.js",
            "templates/index.html",
            "templates/cart.html",
            "app.py",
            "database.py",
            "descripcion.json"
        ]
    }
    
    for base, archivos in estructura.items():
        for ruta in archivos:
            ruta_completa = os.path.join(base, ruta)
            directorio = os.path.dirname(ruta_completa)
            
            if not os.path.exists(directorio):
                os.makedirs(directorio)
            
            with open(ruta_completa, "w") as f:
                f.write("")  # Crea archivos vacíos
    
    print("Estructura creada exitosamente.")

crear_estructura()

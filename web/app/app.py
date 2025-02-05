from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Cambia este valor

DATABASE = 'catalogo.db'
JSON_FILE = 'descripcion.json'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea la tabla de productos y carga los datos desde el JSON si aún no existen."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT,
            nombre TEXT,
            descripcion TEXT,
            precio REAL,
            imagen TEXT,
            codigo TEXT UNIQUE
        )
    ''')
    conn.commit()
    # Cargar datos del JSON
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for categoria, productos in data.items():
            for prod in productos:
                try:
                    cur.execute('''
                        INSERT INTO productos (categoria, nombre, descripcion, precio, imagen, codigo)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (categoria, prod['nombre'], prod['descripcion'], prod['precio'], prod['imagen'], prod['codigo']))
                except sqlite3.IntegrityError:
                    # Si el producto ya existe, continuar
                    pass
    conn.commit()
    conn.close()

@app.before_first_request
def initialize():
    init_db()

@app.route('/')
def index():
    """Muestra el catálogo de productos."""
    conn = get_db_connection()
    productos = conn.execute('SELECT * FROM productos').fetchall()
    categorias = conn.execute('SELECT DISTINCT categoria FROM productos').fetchall()
    conn.close()
    # Convertir la lista de categorías a un formato adecuado para la plantilla
    categorias = [categoria['categoria'] for categoria in categorias]
    return render_template('index.html', productos=productos, categorias=categorias)

@app.route('/add_to_cart/<codigo>')
def add_to_cart(codigo):
    """Agrega un producto al carrito usando el código único."""
    conn = get_db_connection()
    producto = conn.execute('SELECT * FROM productos WHERE codigo = ?', (codigo,)).fetchone()
    conn.close()
    if producto is None:
        flash("Producto no encontrado.")
        return redirect(url_for('index'))
    # Se utiliza la sesión para almacenar el carrito
    if 'cart' not in session:
        session['cart'] = []
    # Convertir el objeto sqlite3.Row a dict y asignar cantidad inicial 1
    producto_dict = { key: producto[key] for key in producto.keys() }
    producto_dict['cantidad'] = 1
    session['cart'].append(producto_dict)
    flash("Producto agregado al carrito.")
    return redirect(url_for('index'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Actualiza las cantidades y aplica cupón en el carrito."""
    cart = session.get('cart', [])
    updated_cart = []
    # Recorrer cada producto en el carrito y actualizar su cantidad
    for item in cart:
        codigo = item['codigo']
        quantity_field = f'quantity_{codigo}'
        if quantity_field in request.form:
            try:
                quantity = int(request.form[quantity_field])
            except ValueError:
                quantity = 1
            if quantity < 1:
                quantity = 1
            item['cantidad'] = quantity
            updated_cart.append(item)
    session['cart'] = updated_cart

    # Procesar cupón de descuento
    coupon = request.form.get('coupon', '').strip()
    if coupon:
        # Ejemplo: cupón "DESCUENTO10" aplica un 10% de descuento
        if coupon == "DESCUENTO10":
            flash("Cupón aplicado: 10% de descuento")
            session['coupon'] = coupon
        else:
            flash("Cupón inválido")
            session.pop('coupon', None)
    else:
        session.pop('coupon', None)

    flash("Carrito actualizado.")
    return redirect(url_for('carrito'))

@app.route('/carrito', methods=['GET', 'POST'])
def carrito():
    """Muestra el carrito de compras y permite proceder a la confirmación de pago."""
    # Si se envía el formulario de confirmación (por ejemplo, vía Yape), redirigir al checkout
    if request.method == 'POST':
        return redirect(url_for('checkout'))
    cart = session.get('cart', [])
    # Calcular total: precio * cantidad
    total = sum(item['precio'] * item.get('cantidad', 1) for item in cart)
    # Aplicar cupón si existe y es válido
    if 'coupon' in session and session['coupon'] == "DESCUENTO10":
        total = total * 0.9
    return render_template('carrito.html', cart=cart, total=total)

@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    """Redirige al formulario de checkout tras la confirmación de pago vía Yape."""
    return redirect(url_for('checkout'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Formulario para confirmar el pago y completar los datos del envío."""
    if request.method == 'POST':
        # Procesar los datos del formulario
        data = {
            'codigo_transaccion': request.form['codigo_transaccion'],
            'nombre_cliente': request.form['nombre_cliente'],
            'telefono_cliente': request.form['telefono_cliente'],
            'ubicacion_envio': request.form['ubicacion_envio'],
            'nombre_receptor': request.form['nombre_receptor'],
            'telefono_receptor': request.form['telefono_receptor'],
            'direccion_envio': request.form['direccion_envio'],
            'captura_yape': request.files['captura_yape']
        }
        # Guardar la imagen subida (captura del Yape)
        upload_folder = os.path.join('static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file = data['captura_yape']
        filename = file.filename
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Aquí se podrían almacenar los datos del pedido en la base de datos o enviarlos por correo
        
        flash("¡Pedido realizado con éxito!")
        session.pop('cart', None)  # Limpiar el carrito
        session.pop('coupon', None)
        return redirect(url_for('index'))
    return render_template('checkout.html')
#inicio de la aplicación hola
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)

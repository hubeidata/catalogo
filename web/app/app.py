from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import sqlite3
import os
from datetime import datetime  # Importamos datetime para trabajar con fechas
from send_order_email import send_order_email  # Asegúrate de que send_order_email.py esté en el mismo directorio o en el PYTHONPATH
import logging

# Configuración básica del logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Cambia este valor

DATABASE = 'catalogo.db'
JSON_FILE = 'descripcion.json'

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error("Error al conectar con la base de datos: %s", e)
        raise

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
    try:
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
                        logging.debug("Producto ya existe: %s", prod['codigo'])
                        pass
        conn.commit()
    except Exception as e:
        logging.error("Error al cargar datos desde el JSON: %s", e)
    finally:
        conn.close()

@app.before_first_request
def initialize():
    logging.debug("Inicializando la aplicación y la base de datos...")
    init_db()

# ======================================================
# Funciones para el carrito
# ======================================================

def obtener_productos_del_carrito():
    """
    Recupera los productos del carrito de la sesión y genera una lista de diccionarios.
    """
    cart = session.get('cart', [])
    cart_items = []
    for item in cart:
        cantidad = item.get('cantidad', 1)
        precio = item.get('precio', 0)
        cart_items.append({
            'id': item.get('id'),
            'image': item.get('imagen'),
            'product_name': item.get('nombre'),
            'product_code': item.get('codigo'),
            'unit_price': precio,
            'quantity': cantidad,
            'subtotal': precio * cantidad
        })
    logging.debug("Carrito actual: %s", cart_items)
    return cart_items

def calcular_gastos(cart_items):
    """
    Calcula los gastos de envío. En este ejemplo se asigna un costo fijo.
    """
    if cart_items:
        return 0.00
    return 0.00

# ======================================================
# Rutas de la aplicación
# ======================================================

@app.route('/')
def index():
    """Muestra el catálogo de productos."""
    logging.debug("Accediendo a la ruta '/' para mostrar el catálogo de productos.")
    conn = get_db_connection()
    try:
        productos = conn.execute('SELECT * FROM productos').fetchall()
        categorias = conn.execute('SELECT DISTINCT categoria FROM productos').fetchall()
        logging.debug("Se encontraron %d productos en la base de datos.", len(productos))
        for producto in productos:
            # Verificamos si algún campo crítico (como 'imagen') está vacío
            if not producto['imagen']:
                logging.warning("El producto con código '%s' y nombre '%s' no tiene imagen asignada.",
                                producto['codigo'], producto['nombre'])
    except Exception as e:
        logging.error("Error al obtener productos o categorías: %s", e)
        productos = []
        categorias = []
    finally:
        conn.close()
    categorias_list = [categoria['categoria'] for categoria in categorias]
    logging.debug("Categorías disponibles: %s", categorias_list)
    return render_template('index.html', productos=productos, categorias=categorias_list)

@app.route('/add_to_cart/<codigo>')
def add_to_cart(codigo):
    logging.debug("Intentando agregar al carrito el producto con código: %s", codigo)
    conn = get_db_connection()
    producto = conn.execute('SELECT * FROM productos WHERE codigo = ?', (codigo,)).fetchone()
    conn.close()
    
    if producto is None:
        logging.error("Producto no encontrado en la base de datos para el código: %s", codigo)
        flash("Producto no encontrado.")
        return redirect(url_for('index'))
    
    if 'cart' not in session:
        session['cart'] = []

    # Verificar si el producto ya está en el carrito
    for item in session['cart']:
        if item['codigo'] == codigo:
            item['cantidad'] += 1
            logging.debug("Incrementada la cantidad del producto %s en el carrito.", codigo)
            flash("Cantidad del producto incrementada en el carrito.")
            return redirect(url_for('index'))
    
    # Agregar el producto al carrito con cantidad 1
    producto_dict = {key: producto[key] for key in producto.keys()}
    producto_dict['cantidad'] = 1
    session['cart'].append(producto_dict)
    logging.debug("Producto %s agregado al carrito.", codigo)
    flash("Producto agregado al carrito.")
    return redirect(url_for('index'))

# (El resto de rutas permanecen sin cambios o puedes agregar logging similar según lo necesites)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    logging.debug("Actualizando el carrito...")
    cart = session.get('cart', [])
    if 'remove' in request.form:
        codigo_a_eliminar = request.form['remove']
        updated_cart = [item for item in cart if item.get('codigo') != codigo_a_eliminar]
        session['cart'] = updated_cart
        logging.debug("Producto %s eliminado del carrito.", codigo_a_eliminar)
        flash("Producto eliminado del carrito.")
        return redirect(url_for('carrito'))
    
    updated_cart = []
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

    coupon = request.form.get('coupon', '').strip()
    if coupon:
        if coupon == "DESCUENTO10":
            logging.debug("Cupón aplicado: %s", coupon)
            flash("Cupón aplicado: 10% de descuento")
            session['coupon'] = coupon
        else:
            logging.warning("Cupón inválido recibido: %s", coupon)
            flash("Cupón inválido")
            session.pop('coupon', None)
    else:
        session.pop('coupon', None)

    flash("Carrito actualizado.")
    return redirect(url_for('carrito'))

@app.route('/carrito')
def carrito():
    logging.debug("Mostrando el carrito de compras.")
    cart_items = obtener_productos_del_carrito()
    cart_subtotal = sum(item['subtotal'] for item in cart_items)
    shipping_cost = calcular_gastos(cart_items)
    coupon_discount = 0
    if 'coupon' in session and session['coupon'] == "DESCUENTO10":
        coupon_discount = cart_subtotal * 0.10
    total = cart_subtotal + shipping_cost - coupon_discount
    logging.debug("Subtotal: %.2f, Envío: %.2f, Descuento: %.2f, Total: %.2f", cart_subtotal, shipping_cost, coupon_discount, total)
    return render_template('carrito.html',
                           cart_items=cart_items,
                           total=total)

# Resto de rutas sin cambios...

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)

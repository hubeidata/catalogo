from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import sqlite3
import os
from datetime import datetime  # Importamos datetime para trabajar con fechas
from send_order_email import send_order_email  # Asegúrate de que send_order_email.py esté en el mismo directorio o en el PYTHONPATH

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

# ======================================================
# Funciones para el carrito
# ======================================================

def obtener_productos_del_carrito():
    """
    Recupera los productos del carrito de la sesión y genera una lista de diccionarios con:
      - image: ruta de la imagen (campo 'imagen')
      - product_name: nombre del producto (campo 'nombre')
      - product_code: código del producto (campo 'codigo')
      - unit_price: precio unitario (campo 'precio')
      - quantity: cantidad (campo 'cantidad', por defecto 1)
      - subtotal: unit_price * quantity
    """
    cart = session.get('cart', [])
    cart_items = []
    for item in cart:
        # Se usa el valor 'cantidad' que ya se actualizó (por defecto es 1)
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
    return cart_items

def calcular_gastos(cart_items):
    """
    Calcula los gastos de envío. En este ejemplo se asigna un costo fijo de 15.00 soles
    si hay al menos un producto en el carrito; si el carrito está vacío, el costo es 0.
    Puedes ajustar la lógica para que dependa del peso, la distancia u otros parámetros.
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
    conn = get_db_connection()
    productos = conn.execute('SELECT * FROM productos').fetchall()
    categorias = conn.execute('SELECT DISTINCT categoria FROM productos').fetchall()
    conn.close()
    # Convertir la lista de categorías a un formato adecuado para la plantilla
    categorias = [categoria['categoria'] for categoria in categorias]
    return render_template('index.html', productos=productos, categorias=categorias)

@app.route('/add_to_cart/<codigo>')
def add_to_cart(codigo):
    conn = get_db_connection()
    producto = conn.execute('SELECT * FROM productos WHERE codigo = ?', (codigo,)).fetchone()
    conn.close()
    
    if producto is None:
        flash("Producto no encontrado.")
        return redirect(url_for('index'))
    
    if 'cart' not in session:
        session['cart'] = []

    # Buscar si el producto ya está en el carrito
    for item in session['cart']:
        if item['codigo'] == codigo:
            item['cantidad'] += 1
            flash("Cantidad del producto incrementada en el carrito.")
            return redirect(url_for('index'))
    
    # Si no está en el carrito, agregarlo con cantidad 1
    producto_dict = {key: producto[key] for key in producto.keys()}
    producto_dict['cantidad'] = 1
    session['cart'].append(producto_dict)
    flash("Producto agregado al carrito.")
    return redirect(url_for('index'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', [])
    if 'remove' in request.form:
        codigo_a_eliminar = request.form['remove']
        updated_cart = [item for item in cart if item.get('codigo') != codigo_a_eliminar]
        session['cart'] = updated_cart
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

    # Validar cupón únicamente en el servidor
    coupon = request.form.get('coupon', '').strip()
    if coupon:
        if coupon.upper() == "ANYALUA442":
            flash("Cupón aplicado: descuento por ANYALUA442")
            session['coupon'] = coupon.upper()
        else:
            flash("Cupón inválido")
            session.pop('coupon', None)
    else:
        session.pop('coupon', None)

    flash("Carrito actualizado.")
    return redirect(url_for('carrito'))


@app.route('/carrito')
def carrito():
    cart_items = obtener_productos_del_carrito()  # Retorna la lista de productos con claves: 'product_code', 'image', 'product_name', 'unit_price', 'quantity'
    cart_subtotal = sum(item['subtotal'] for item in cart_items)
    shipping_cost = calcular_gastos(cart_items)
    coupon_discount = 0
    if 'coupon' in session and session['coupon'] == "ANYALUA442":
        coupon_discount = shipping_cost  # Descuento del 100% sobre el envío
    total = cart_subtotal + shipping_cost - coupon_discount
    return render_template('carrito.html',
                           cart_items=cart_items,
                           total=total)


@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    """Redirige al formulario de checkout tras la confirmación de pago vía Yape."""
    return redirect(url_for('checkout'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        data = {
            'codigo_transaccion': request.form['codigo_transaccion'],
            'nombre_cliente': request.form['nombre_cliente'],
            'telefono_cliente': request.form['telefono_cliente'],
            'correo_cliente': request.form['correo_cliente'],
            'ubicacion_envio': request.form['ubicacion_envio'],
            'nombre_receptor': request.form['nombre_receptor'],
            'telefono_receptor': request.form['telefono_receptor'],
            'direccion_envio': request.form['direccion_envio'],
            'fecha_envio': request.form['fecha_envio'],
            'captura_yape': request.files['captura_yape'].filename
        }
        
        # Guardar la imagen en static/uploads/
        upload_folder = os.path.join('static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file = request.files['captura_yape']
        filename = file.filename
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        data['captura_yape_path'] = filename
        
        # Leer el cupón ingresado y validar en el servidor (únicamente ANYALUA442 es válido)
        coupon = request.form.get('coupon', '').strip()
        if coupon.upper() == "ANYALUA442":
            session['coupon'] = "ANYALUA442"
        else:
            session.pop('coupon', None)
        
        # Obtener productos del carrito y calcular totales
        cart_items = obtener_productos_del_carrito()
        cart_subtotal = sum(item['subtotal'] for item in cart_items)
        
        try:
            shipping_cost = float(request.form.get('shipping_cost', 0))
        except ValueError:
            shipping_cost = 0.0
        
        # Aplicar descuento: si el cupón ANYALUA442 está en sesión, se descuenta el 100% del gasto de envío
        coupon_discount = 0
        if 'coupon' in session and session['coupon'] == "ANYALUA442":
            coupon_discount = shipping_cost
        
        total = cart_subtotal + shipping_cost - coupon_discount

        cart_table_html = render_template('cart_table_html.html',
                                          cart_items=cart_items,
                                          cart_subtotal=cart_subtotal,
                                          shipping_cost=shipping_cost,
                                          coupon_discount=coupon_discount,
                                          total=total)

        data['cart_table_html'] = cart_table_html
        data['cart_subtotal'] = cart_subtotal
        data['shipping_cost'] = shipping_cost
        data['coupon_discount'] = coupon_discount
        data['total'] = total

        from send_order_email import send_order_email
        order_code = send_order_email(data)

        flash("¡Pedido realizado con éxito! Revise su correo: " + data.get('correo_cliente'))
        session.pop('cart', None)
        session.pop('coupon', None)
        return redirect(url_for('index'))
    else:
        cart_items = obtener_productos_del_carrito()
        cart_subtotal = sum(item['subtotal'] for item in cart_items)
        shipping_cost = calcular_gastos(cart_items)  # Asegúrate de que esta función retorne un valor > 0 (por ejemplo, 15.00)
        coupon_discount = 0
        if 'coupon' in session and session['coupon'] == "ANYALUA442":
            coupon_discount = shipping_cost
        total = cart_subtotal + shipping_cost - coupon_discount
        fecha_envio_value = datetime.now().strftime("%Y-%m-%dT%H:%M")
        return render_template('checkout.html',
                               cart_items=cart_items,
                               cart_subtotal=cart_subtotal,
                               shipping_cost=shipping_cost,
                               coupon_discount=coupon_discount,
                               total=total,
                               fecha_envio_value=fecha_envio_value)


@app.route('/remove_from_cart/<codigo>', methods=['POST'])
def remove_from_cart(codigo):
    """Elimina un producto del carrito de compras."""
    cart = session.get('cart', [])
    updated_cart = [item for item in cart if item.get('codigo') != codigo]
    session['cart'] = updated_cart
    flash("Producto eliminado del carrito.")
    return redirect(url_for('carrito'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)

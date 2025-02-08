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
    # Si se ha enviado el botón "remove", eliminar el producto
    if 'remove' in request.form:
        codigo_a_eliminar = request.form['remove']
        updated_cart = [item for item in cart if item.get('codigo') != codigo_a_eliminar]
        session['cart'] = updated_cart
        flash("Producto eliminado del carrito.")
        return redirect(url_for('carrito'))
    
    # Si se ha enviado el formulario de actualización, procesar cantidades y cupón
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

    # Procesar cupón de descuento (opcional)
    coupon = request.form.get('coupon', '').strip()
    if coupon:
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
        # Recopilar los datos del formulario, incluyendo el nuevo campo de correo electrónico
        data = {
            'codigo_transaccion': request.form['codigo_transaccion'],
            'nombre_cliente': request.form['nombre_cliente'],
            'telefono_cliente': request.form['telefono_cliente'],
            'correo_cliente': request.form['correo_cliente'],  # Nuevo campo
            'ubicacion_envio': request.form['ubicacion_envio'],
            'nombre_receptor': request.form['nombre_receptor'],
            'telefono_receptor': request.form['telefono_receptor'],
            'direccion_envio': request.form['direccion_envio'],
            'fecha_envio': request.form['fecha_envio'],
            'captura_yape': request.files['captura_yape'].filename
        }
        
        # Guardar la imagen subida en la carpeta static/uploads/
        upload_folder = os.path.join('static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file = request.files['captura_yape']
        filename = file.filename
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        data['captura_yape_path'] = filename  # Se guarda la ruta relativa (se unirá con static/uploads/ en send_order_email)
        
        # Enviar el correo de pedido a los operadores (ya implementado en send_order_email)
        # Se asume que send_order_email ya envía el correo a rodety@gmail.com y fortydata@gmail.com.
        from send_order_email import send_order_email
        order_code = send_order_email(data)
        
        # Enviar acuse de recibo de confirmación de pago al cliente
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.header import Header

        # Preparar asunto y cuerpo del correo para el cliente
        confirmation_subject = Header(f"Acuse de Recibo - Pedido {order_code}", 'utf-8')
        confirmation_body = f"""
        <html>
          <head><meta charset="UTF-8"></head>
          <body>
            <p>Estimado/a {data.get('nombre_cliente')},</p>
            <p>Se recibió el pago y se procede a realizar el envío de su compra con los siguientes datos de envío:</p>
            <p><strong>Dirección de Envío:</strong> {data.get('direccion_envio')}</p>
            <p>Si desea cambiar o corregir alguno de los datos, por favor responda a este correo.</p>
            <p>Gracias por su compra.</p>
          </body>
        </html>
        """
        customer_email = data.get('correo_cliente')
        msg = MIMEMultipart("alternative")
        msg['From'] = "hubeidata@gmail.com"
        msg['To'] = customer_email
        msg['Subject'] = confirmation_subject
        msg.attach(MIMEText(confirmation_body, 'html', 'utf-8'))
        
        try:
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login("hubeidata@gmail.com", "TU_CONTRASEÑA_DE_APLICACION")
            server.sendmail("hubeidata@gmail.com", [customer_email], msg.as_string().encode('utf-8'))
            server.quit()
            print("Acuse de recibo enviado al cliente.")
        except Exception as e:
            print("Error al enviar el acuse de recibo al cliente:", e)
        
        flash("¡Pedido realizado con éxito!")
        session.pop('cart', None)  # Limpiar el carrito
        session.pop('coupon', None)
        return redirect(url_for('index'))
    else:
        cart = session.get('cart', [])
        total = sum(item['precio'] * item.get('cantidad', 1) for item in cart)
        if 'coupon' in session and session['coupon'] == "DESCUENTO10":
            total = total * 0.9
        from datetime import datetime
        fecha_hoy = datetime.today().strftime("%Y-%m-%d")
        return render_template('checkout.html', total=total, fecha_hoy=fecha_hoy)


@app.route('/remove_from_cart/<codigo>', methods=['POST'])
def remove_from_cart(codigo):
    """Elimina un producto del carrito de compras."""
    cart = session.get('cart', [])
    # Filtrar el carrito para eliminar el producto con el código indicado
    updated_cart = [item for item in cart if item.get('codigo') != codigo]
    session['cart'] = updated_cart
    flash("Producto eliminado del carrito.")
    return redirect(url_for('carrito'))



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)

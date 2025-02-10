#!/usr/bin/env python3
import smtplib
import email.charset
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
import uuid
from datetime import datetime
import os

# Configurar la codificación para soportar UTF-8 en email
email.charset.add_charset('utf-8', email.charset.SHORTEST, None, None)

def send_order_email(form_data):
    """
    Envía dos correos electrónicos al confirmar un pedido:
      1. A los operadores (rodety@gmail.com y fortydata@gmail.com) con los datos del pedido,
         imágenes adjuntas (la captura de Yape y, opcionalmente, las imágenes de los productos)
         y un botón "Pago Verificado".
      2. Un acuse de recibo de confirmación de pago al correo del cliente.
    
    Se espera que form_data contenga, entre otros, las siguientes claves:
      - 'codigo_transaccion'
      - 'nombre_cliente'
      - 'telefono_cliente'
      - 'correo_cliente'
      - 'ubicacion_envio'
      - 'nombre_receptor'
      - 'telefono_receptor'
      - 'direccion_envio'
      - 'fecha_envio'
      - 'captura_yape': nombre del archivo de la captura (por ejemplo, "captura_yape.jpg")
      - 'captura_yape_path': ruta (relativa o absoluta) de la captura; si es relativa, se buscará en "static/uploads/"
      - 'cart_items' (opcional): lista de diccionarios de productos con clave 'imagen' (por ejemplo, "producto1.jpg")
      - Además, se espera que se hayan incluido en form_data los totales (cart_subtotal, shipping_cost, coupon_discount, total)
    Retorna:
      order_code (str): Código único del pedido.
    """
    # Generar un código de pedido único (se usa la primera parte de un UUID)
    order_code = str(uuid.uuid4()).split('-')[0].upper()
    
    # Obtener la fecha y hora actual
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Configuración del correo
    sender_email = "hubeidata@gmail.com"
    sender_password = "ixnnzohjzdnxshmh"  # Reemplaza con tu contraseña de aplicación
    recipients_operators = ["rodety@gmail.com", "fortydata@gmail.com"]
    
    # Enlace mailto para el botón "Pago Verificado"
    mailto_link = (
        f"mailto:{form_data.get('correo_cliente')}?subject=Pago%20Verificado&"
        "body=Se%20recibió%20el%20pago%2C%20se%20prosigue%20con%20el%20env%C3%ADo%20de%20su%20compra.%20"
        "En%20caso%20de%20cambiar%20alguno%20de%20los%20datos%2C%20responda%20a%20este%20correo."
    )
    
    html_content = f"""
    <html>
      <head>
        <meta charset="UTF-8">
        <style>
          .button {{
            display: inline-block;
            padding: 10px 20px;
            font-size: 14px;
            color: #ffffff;
            background-color: #28a745;
            text-decoration: none;
            border-radius: 5px;
          }}
        </style>
      </head>
      <body>
        <h2>Anyalua regalos &amp; detalles</h2>
        <p><strong>Código de Pedido:</strong> {order_code}</p>
        <p><strong>Fecha y Hora de Pedido:</strong> {now}</p>
        <hr>
        <p><strong>Código de Transacción:</strong> {form_data.get('codigo_transaccion')}</p>
        <p><strong>Nombre del Cliente:</strong> {form_data.get('nombre_cliente')}</p>
        <p><strong>Teléfono del Cliente:</strong> {form_data.get('telefono_cliente')}</p>
        <p><strong>Ubicación de Envío:</strong> {form_data.get('ubicacion_envio')}</p>
        <p><strong>Nombre de la Persona que Recibe:</strong> {form_data.get('nombre_receptor')}</p>
        <p><strong>Teléfono de la Persona que Recibe:</strong> {form_data.get('telefono_receptor')}</p>
        <p><strong>Dirección de Envío:</strong> {form_data.get('direccion_envio')}</p>
        <p><strong>Fecha de Envío:</strong> {form_data.get('fecha_envio')}</p>
        <p><strong>Captura Yape:</strong> {form_data.get('captura_yape')}</p>
        <hr>
        <!-- Se puede incluir el detalle de compra (tabla) -->
        {form_data.get('cart_table_html', '')}
        <hr>
        <p>Este es un mensaje automático generado por el sistema de pedidos de Anyalua regalos &amp; detalles.</p>
        <p>
          <a href="{mailto_link}" class="button">Pago Verificado</a>
        </p>
      </body>
    </html>
    """
    
    # Crear el mensaje para operadores
    msg_ops = MIMEMultipart("related")
    msg_ops['From'] = sender_email
    msg_ops['To'] = ", ".join(recipients_operators)
    msg_ops['Subject'] = Header(f"Se recibió nuevo Pedido de {form_data.get('nombre_cliente')} {now}", 'utf-8')
    msg_alt_ops = MIMEMultipart("alternative")
    msg_ops.attach(msg_alt_ops)
    msg_alt_ops.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    # Función auxiliar para obtener la ruta completa de una imagen
    def obtener_ruta_imagen(ruta):
        if not os.path.isabs(ruta):
            base_dir = os.path.join(os.getcwd(), "static", "uploads")
            return os.path.join(base_dir, ruta)
        return ruta

    # Adjuntar la imagen de la captura del Yape
    captura_path = form_data.get('captura_yape_path')
    if captura_path:
        full_captura_path = obtener_ruta_imagen(captura_path)
        if os.path.exists(full_captura_path):
            try:
                with open(full_captura_path, 'rb') as f:
                    img_data = f.read()
                img_mime = MIMEImage(img_data)
                img_mime.add_header('Content-ID', '<captura_yape>')
                img_mime.add_header('Content-Disposition', 'attachment', filename=form_data.get('captura_yape'))
                msg_ops.attach(img_mime)
            except Exception as e:
                print("Error al adjuntar la imagen de la captura:", e)
        else:
            print("La imagen de la captura no existe en:", full_captura_path)
    
    # Opcional: Adjuntar las imágenes de los productos si se incluyen en form_data['cart_items']
    # Se utilizará la carpeta "static/imagenes_extraidas" para estas imágenes.
    cart_items = form_data.get('cart_items', [])
    # Construir la ruta base usando el directorio actual del archivo send_order_email.py
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'imagenes_extraidas')
    for item in cart_items:
        image_filename = item.get('imagen')
        if image_filename:
            # Construir la ruta completa de la imagen
            full_image_path = os.path.join(base_dir, image_filename)
            if os.path.exists(full_image_path):
                try:
                    with open(full_image_path, 'rb') as f:
                        prod_img_data = f.read()
                    prod_img_mime = MIMEImage(prod_img_data)
                    # Generar un Content-ID único (por ejemplo, usando el nombre de la imagen)
                    cid = f"<{image_filename}>"
                    prod_img_mime.add_header('Content-ID', cid)
                    prod_img_mime.add_header('Content-Disposition', 'attachment', filename=image_filename)
                    msg_ops.attach(prod_img_mime)
                except Exception as e:
                    print("Error al adjuntar la imagen del producto:", e)
            else:
                print("La imagen del producto no existe en:", full_image_path)
    
    # Enviar el correo a los operadores
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients_operators, msg_ops.as_string().encode('utf-8'))
        server.quit()
        print("Correo a operadores enviado exitosamente.")
    except Exception as e:
        print("Error al enviar el correo a operadores:", e)
    
    # -----------------------------------------------
    # Enviar acuse de recibo al cliente
    client_email = form_data.get('correo_cliente')
    if client_email:
        client_subject = Header(f"Acuse de Recibo - Pedido {order_code}", 'utf-8')
        client_html = f"""
    <html>
      <head>
        <meta charset="UTF-8">
        <style>
          .button {{
            display: inline-block;
            padding: 10px 20px;
            font-size: 14px;
            color: #ffffff;
            background-color: #28a745;
            text-decoration: none;
            border-radius: 5px;
          }}
        </style>
      </head>
      <body>
        <h2>Anyalua regalos &amp; detalles</h2>
        <p><strong>Código de Pedido:</strong> {order_code}</p>
        <p><strong>Fecha y Hora de Pedido:</strong> {now}</p>
        <hr>
        <p><strong>Código de Transacción:</strong> {form_data.get('codigo_transaccion')}</p>
        <p><strong>Nombre del Cliente:</strong> {form_data.get('nombre_cliente')}</p>
        <p><strong>Teléfono del Cliente:</strong> {form_data.get('telefono_cliente')}</p>
        <p><strong>Ubicación de Envío:</strong> {form_data.get('ubicacion_envio')}</p>
        <p><strong>Nombre de la Persona que Recibe:</strong> {form_data.get('nombre_receptor')}</p>
        <p><strong>Teléfono de la Persona que Recibe:</strong> {form_data.get('telefono_receptor')}</p>
        <p><strong>Dirección de Envío:</strong> {form_data.get('direccion_envio')}</p>
        <p><strong>Fecha de Envío:</strong> {form_data.get('fecha_envio')}</p>
        <p><strong>Captura Yape:</strong> {form_data.get('captura_yape')}</p>
        <hr>
        <p>Este es un mensaje automático generado por el sistema de pedidos de Anyalua regalos &amp; detalles.</p>        
      </body>
    </html>
    """
        msg_client = MIMEMultipart("alternative")
        msg_client['From'] = sender_email
        msg_client['To'] = client_email
        msg_client['Subject'] = client_subject
        msg_client.attach(MIMEText(client_html, 'html', 'utf-8'))
    
        # Adjuntar la imagen (captura del Yape) para el cliente
        if captura_path:
            full_captura_path = obtener_ruta_imagen(captura_path)
            if os.path.exists(full_captura_path):
                try:
                    with open(full_captura_path, 'rb') as f:
                        img_data = f.read()
                    img_mime = MIMEImage(img_data)
                    img_mime.add_header('Content-ID', '<captura_yape>')
                    img_mime.add_header('Content-Disposition', 'attachment', filename=form_data.get('captura_yape'))
                    msg_client.attach(img_mime)
                except Exception as e:
                    print("Error al adjuntar la imagen para cliente:", e)
            else:
                print("La imagen de la captura no existe en:", full_captura_path)
    
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [client_email], msg_client.as_string().encode('utf-8'))
            server.quit()
            print("Acuse de recibo enviado al cliente.")
        except Exception as e:
            print("Error al enviar el acuse de recibo al cliente:", e)
    else:
        print("No se proporcionó correo del cliente; no se envió acuse de recibo.")
    
    return order_code

# Ejemplo de uso directo (para pruebas)
if __name__ == "__main__":
    form_data = {
        'codigo_transaccion': 'TRANS123',
        'nombre_cliente': 'Juan Pérez',
        'telefono_cliente': '123456789',
        'correo_cliente': 'anyaluadetallesyregalos@gmail.com',
        'ubicacion_envio': 'Lima, Perú',
        'nombre_receptor': 'María López',
        'telefono_receptor': '987654321',
        'direccion_envio': 'Av. Siempre Viva 123',
        'fecha_envio': '2025-02-07',
        'captura_yape': 'captura_yape.jpg',
        'captura_yape_path': 'captura_yape.jpg',
        # Para pruebas, incluir una lista de productos:
        'cart_items': [
            {
                'imagen': 'producto1.jpg',
                'product_name': 'Producto 1',
                'product_code': 'P001',
                'unit_price': 10.0,
                'quantity': 2,
                'subtotal': 20.0
            },
            {
                'imagen': 'producto2.jpg',
                'product_name': 'Producto 2',
                'product_code': 'P002',
                'unit_price': 15.0,
                'quantity': 1,
                'subtotal': 15.0
            }
        ],
        'cart_subtotal': 35.0,
        'shipping_cost': 15.0,
        'coupon_discount': 0.0,
        'total': 50.0
    }
    order_code = send_order_email(form_data)
    print("Código de pedido:", order_code)

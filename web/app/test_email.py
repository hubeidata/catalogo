from send_order_email import send_order_email

if __name__ == "__main__":
    form_data = {
        'codigo_transaccion': 'TRANS123',
        'nombre_cliente': 'Juan Perez',
        'telefono_cliente': '123456789',
        'ubicacion_envio': 'Lima, Perú',
        'nombre_receptor': 'María López',
        'telefono_receptor': '987654321',
        'direccion_envio': 'Av. Siempre Viva 123',
        'fecha_envio': '2025-02-07',
        'captura_yape': 'captura_yape.jpg',
        'captura_yape_path': 'captura_yape.jpg'
    }
    order_code = send_order_email(form_data)
    print("Código de pedido:", order_code)

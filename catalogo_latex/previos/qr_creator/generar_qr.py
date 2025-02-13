import qrcode
from PIL import Image

def main():
    # URL que se codificará en el QR
    url = "958206357"
    
    # Crear el código QR con alta corrección de errores
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta corrección para permitir modificaciones en el centro
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Generar la imagen del código QR
    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    ancho_qr, alto_qr = img_qr.size
    
    # Definir el tamaño del área central para el logo (por ejemplo, el 25% del ancho del QR)
    tamano_area_logo = int(ancho_qr * 0.25)
    
    # Crear un cuadrado blanco donde se insertará el logo
    area_logo = Image.new("RGB", (tamano_area_logo, tamano_area_logo), "white")
    
    # Abrir la imagen del logo
    try:
        logo = Image.open("logo.jpg")
    except Exception as e:
        print("Error al abrir 'logo.jpg':", e)
        return
    
    # Redimensionar el logo para que se ajuste dentro del área blanca, dejando un margen (por ejemplo, el 80% del área)
    max_logo_dimension = int(tamano_area_logo)
    logo_ancho, logo_alto = logo.size
    factor = min(max_logo_dimension / logo_ancho, max_logo_dimension / logo_alto)
    nuevo_ancho = int(logo_ancho * factor)
    nuevo_alto = int(logo_alto * factor)
    
    # Usar Image.LANCZOS para un redimensionamiento de alta calidad
    logo = logo.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
    
    # Calcular la posición para centrar el logo dentro del área blanca
    pos_logo_en_area = ((tamano_area_logo - nuevo_ancho) // 2, (tamano_area_logo - nuevo_alto) // 2)
    area_logo.paste(logo, pos_logo_en_area)
    
    # Calcular la posición para centrar el área del logo en el QR
    pos_area_qr = ((ancho_qr - tamano_area_logo) // 2, (alto_qr - tamano_area_logo) // 2)
    img_qr.paste(area_logo, pos_area_qr)
    
    # Guardar la imagen final del QR
    img_qr.save("qr_anyalua.png")
    print("Imagen QR guardada como 'qr_anyalua.png'")

if __name__ == "__main__":
    main()

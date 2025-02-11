import fitz  # PyMuPDF
import os

def extract_images_from_pdf(pdf_path, output_folder):
    # Crear la carpeta de salida si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Abrir el documento PDF
    pdf_document = fitz.open(pdf_path)

    # Iterar sobre cada página del PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)

        # Extraer imágenes de la página
        for img_index, img in enumerate(image_list):
            xref = img[0]  # Referencia de la imagen
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]  # Bytes de la imagen
            image_ext = base_image["ext"]  # Extensión de la imagen (por ejemplo, "png", "jpeg")
            image_path = f"{output_folder}/image{page_num + 1}_{img_index + 1}.{image_ext}"

            # Guardar la imagen en la carpeta de salida
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

    # Cerrar el documento PDF
    pdf_document.close()

# Llamar a la función para extraer imágenes
extract_images_from_pdf("catalogo.pdf", "imagenes_extraidas")
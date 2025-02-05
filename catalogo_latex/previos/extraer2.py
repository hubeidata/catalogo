import fitz  # PyMuPDF
import os
import json
import re

def extract_images_from_pdf(pdf_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    pdf_document = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_rect = page.get_image_rects(xref)[0]  # Obtener coordenadas de la imagen
            image_path = f"{output_folder}/image_{page_num + 1}_{img_index + 1}.{image_ext}"
            
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
                
            images.append({
                "path": image_path,
                "page": page_num + 1,
                "rect": image_rect
            })
    
    pdf_document.close()
    return images

def extract_text_with_positions(pdf_path):
    pdf_document = fitz.open(pdf_path)
    text_data = []
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        blocks = page.get_text("blocks")  # Obtener texto con coordenadas
        for block in blocks:
            text_data.append({
                "text": block[4],
                "page": page_num + 1,
                "rect": block[:4]  # Coordenadas (x0, y0, x1, y1)
            })
    
    pdf_document.close()
    return text_data

def match_text_to_images(images, text_data):
    catalog_data = []
    
    for image in images:
        related_texts = [t for t in text_data if t["page"] == image["page"] and abs(t["rect"][1] - image["rect"].y1) < 100]
        combined_text = " ".join([t["text"] for t in sorted(related_texts, key=lambda x: x["rect"][1])])
        
        match = re.search(r"(\w.+?) S/\.\s*(\d+(\.\d{2})?)", combined_text)
        if match:
            product = {
                "nombre": match.group(1).strip(),
                "descripcion": combined_text.strip(),
                "precio": float(match.group(2)),
                "imagen": image["path"]
            }
            catalog_data.append(product)
    
    return catalog_data

def save_to_json(data, output_file):
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

def main():
    pdf_path = "catalogo.pdf"
    output_folder = "imagenes_extraidas"
    json_output = "descripcion.json"
    
    print("Extrayendo imágenes y sus posiciones...")
    images = extract_images_from_pdf(pdf_path, output_folder)
    
    print("Extrayendo texto con posiciones...")
    text_data = extract_text_with_positions(pdf_path)
    
    print("Asociando texto con imágenes...")
    catalog_data = match_text_to_images(images, text_data)
    
    print("Guardando datos en JSON...")
    save_to_json(catalog_data, json_output)
    
    print(f"Proceso completado. Imágenes guardadas en '{output_folder}', datos en '{json_output}'")

if __name__ == "__main__":
    main()

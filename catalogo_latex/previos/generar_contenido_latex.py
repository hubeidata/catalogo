import json

# Cargar el archivo JSON
with open("descripcion.json", "r", encoding="utf-8") as file:
    productos = json.load(file)

# Generar el contenido LaTeX
contenido_latex = ""

# Variable para controlar si es el primer título
primer_titulo = True

# Iterar sobre las claves (categorías) y los productos en el archivo JSON
for categoria, lista_productos in productos.items():
    # Si no es el primer título, insertar salto de página
    if not primer_titulo:
        contenido_latex += "\\newpage\n"
    primer_titulo = False
    
    # Título para la categoría (tulipanes o rosas)
    contenido_latex += f"""
    \\begin{{center}}
        \\textbf{{\\Huge\\textcolor{{red}}{{{categoria.replace('_', ' ').title()}}}}}
    \\end{{center}}
    """

    # Iniciar las columnas para esta categoría
    contenido_latex += "\\begin{multicols}{2}\n"  # Dos columnas
    
    # Productos de la categoría correspondiente
    for producto in lista_productos:
        contenido_latex += """
    \\begin{{minipage}}{{\\linewidth}}
        \\centering
        \\includegraphics[height=7cm]{{{imagen}}} % Escalar la imagen a una altura fija
        \\newline
        \\vspace{{0.1cm}}
        \\textbf{{\\Large \\textcolor{{red}}{{{nombre}}}}} \\\\ % Texto en rojo
        \\vspace{{0.2cm}}
        \\textbf{{\\textcolor{{pink}}{{Precio: S/. {precio}}}}} \\\\ % Texto en rosa
        \\vspace{{0.2cm}}
        \\textbf{{\\textcolor{{blue}}{{Codigo {codigo}}}}} \\\\ % Texto en blue
        \\vspace{{0.2cm}}
        \\begin{{minipage}}{{0.8\\linewidth}} 
            \\small \\textcolor{{purple}}{{{descripcion}}} % Texto en morado
        \\end{{minipage}}
        \\vspace{{0.1cm}}        
        \\rule{{\\linewidth}}{{0.5pt}}
    \\end{{minipage}}
    """.format(
            imagen=producto["imagen"],
            nombre=producto["nombre"],
            precio=producto["precio"],
            descripcion=producto["descripcion"].replace("\n", "\\\\"),  # Reemplaza saltos de línea
            codigo=producto["codigo"],
        )
    
    # Finalizar las columnas para esta categoría
    contenido_latex += "\\end{multicols}\n"

# Guardar el contenido en un archivo .tex
with open("contenido_generado.tex", "w", encoding="utf-8") as file:
    file.write(contenido_latex)

print("El archivo 'contenido_generado.tex' se ha creado correctamente.")

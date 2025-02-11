import json

# Archivos de entrada y salida
descripcion_file = "descripcion.json"
contenido_file = "contenido_generado1.tex"
catalogo_file = "catalogo1.tex"

# Leer archivo JSON
with open(descripcion_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# Generar contenido LaTeX para los productos
contenido_latex = ""
primera_categoria = True  # Variable para verificar si es la primera categoría

for categoria, productos in data.items():
    # Si no es la primera categoría, agregar un salto de página
    if not primera_categoria:
        contenido_latex += "\\newpage\n"
    primera_categoria = False

    # Agregar título de la categoría en color azul
    contenido_latex += f"\\begin{{center}}\\textcolor[HTML]{{191970}}{{\\huge {categoria.replace('_', ' ').title()}}}\\end{{center}}\n"

    
    for index, producto in enumerate(productos):
        if index % 2 == 0:
            # Si el índice es par (primera, tercera, quinta posición, etc.), la imagen a la derecha
            contenido_latex += (f"\\noindent\n"
                            f"\\begin{{minipage}}{{0.6\\textwidth}}\n"
                            f"    \\textcolor[HTML]{{FF8C00}}{{\\textbf{{\\huge {producto['nombre']} }}}}\\\\\n"
                            f"    {{\\textit{{Mini Ramo}}}} \\\\\n"
                            f"    \\textcolor[HTML]{{FF8C00}}{{\\Huge ♥}} \\\\\n"
                            f"    \\vspace{{0.5cm}}\n"
                            f"    \\begin{{itemize}}\n"
                            f"        \\item {producto['descripcion']}\n"
                            f"    \\end{{itemize}}\n"
                            f"\\end{{minipage}}\n"
                            f"\\hspace{{1cm}}\n"  # Separación de 2cm entre las columnas
                            f"\\begin{{minipage}}{{0.35\\textwidth}}\n"
                            f"    \\includegraphics[width=1.0\\textwidth]{{{producto['imagen']}}}\n"
                            f"\\end{{minipage}}\n"
                            f"\\vspace{{0.3cm}}\n"
                            f"\\begin{{center}}\n"                             
                            f"   \\textbf{{\\Large Precio: \\textcolor[HTML]{{228B22}}{{S/. {producto['precio']} }}}}\n"
                            f"\\end{{center}}\n"
                            f"\\begin{{center}}\n"
                            f"    \\textcolor[HTML]{{191970}}{{\\texttt{{Código: {producto['codigo']}}}}}\n"
                            f"\\end{{center}}\n"
                            f"\\vspace{{1cm}}\n")
        else:
            # Si el índice es impar (segunda, cuarta, sexta posición, etc.), la imagen a la izquierda
            contenido_latex += (f"\\noindent\n"
                            f"\\begin{{minipage}}{{0.35\\textwidth}}\n"
                            f"    \\includegraphics[width=1.0\\textwidth]{{{producto['imagen']}}}\n"
                            f"\\end{{minipage}}\n"
                            f"\\hspace{{1cm}}\n"  # Separación de 2cm entre las columnas
                            f"\\begin{{minipage}}{{0.6\\textwidth}}\n"
                            f"    \\textcolor[HTML]{{FF8C00}}{{\\textbf{{\\huge {producto['nombre']} }}}}\\\\\n"
                            f"    {{\\textit{{Mini Ramo}}}} \\\\\n"
                            f"    \\textcolor[HTML]{{FF8C00}}{{\\Huge ♥}} \\\\\n"
                            f"    \\vspace{{0.5cm}}\n"
                            f"    \\begin{{itemize}}\n"
                            f"        \\item {producto['descripcion']}\n"
                            f"    \\end{{itemize}}\n"
                            f"\\end{{minipage}}\n"
                            f"\\vspace{{0.3cm}}\n"
                            f"\\begin{{center}}\n"                             
                            f"   \\textbf{{\\Large Precio: \\textcolor[HTML]{{228B22}}{{S/. {producto['precio']} }}}}\n"
                            f"\\end{{center}}\n"
                            f"\\begin{{center}}\n"
                            f"    \\textcolor[HTML]{{191970}}{{\\texttt{{Código: {producto['codigo']}}}}}\n"
                            f"\\end{{center}}\n"
                            f"\\vspace{{1cm}}\n")

# Guardar contenido generado
titulo = "Catálogo de Productos"
contenido_completo = f"""
\\documentclass[12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[spanish]{{babel}} % Soporte para español
\\usepackage{{graphicx}} % Para imágenes
\\usepackage{{geometry}} % Para márgenes
\\usepackage{{setspace}} % Para espaciado
\\usepackage{{fancyhdr}} % Para encabezados y pies de página
\\usepackage{{xcolor}} % Para colores
\\usepackage{{background}} % Para fondo
\\usepackage{{fontspec}} % Para fuentes personalizadas
\\usepackage{{pgfornament}} % Para decoraciones
\\usepackage{{titling}} % Para controlar el título
\\usepackage{{multicol}} % Agregar este paquete para usar multicols

% Configuración de márgenes
\\geometry{{left=2cm, right=2cm, top=2cm, bottom=2cm}}

\\pagestyle{{fancy}}

\\fancyhead[C]{{\\textbf{{\\textcolor{{red}}{{Catálogo de San Valentín 2025}}}}}}
\\fancyfoot[C]{{\\textcolor{{pink}}{{\\thepage}}}}

% Fuente más legible
\\renewcommand{{\\rmdefault}}{{ptm}} % Cambia la fuente a Times New Roman (serif)
\\setlength{{\\parindent}}{{0pt}} % Quita la sangría en los párrafos
\\setlength{{\\parskip}}{{1ex plus 0.5ex minus 0.5ex}} % Espaciado entre párrafos

\\begin{{document}}

% Título del catálogo con mayor espacio y mejor formato
\\begin{{center}}
    \\Huge\\textbf{{\\textcolor{{red}}{{Catálogo de San Valentín 2025}}}} \\\\[0.5cm]
    \\large\\textit{{\\textcolor{{pink}}{{Regalos y rosas para el día del amor y la amistad}}}} \\\\[1cm]
    \\pgfornament[width=0.5\\linewidth, color=red]{{88}} % Decoración romántica
\\end{{center}}

{contenido_latex}
\\end{{document}}
"""

with open(catalogo_file, "w", encoding="utf-8") as file:
    file.write(contenido_completo)

print("Catálogo LaTeX generado correctamente en catalogo.tex")

import json

# Archivos de entrada y salida
descripcion_file = "descripcion.json"
contenido_file = "contenido_generado.tex"
catalogo_file = "catalogo.tex"

# Leer archivo JSON
with open(descripcion_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# Generar contenido LaTeX para los productos
contenido_latex = ""
for categoria, productos in data.items():
    for index, producto in enumerate(productos):
        if index % 2 == 0:
            # Si el índice es par (primera, tercera, quinta posición, etc.), la imagen a la derecha
            contenido_latex += (f"\\noindent\n"
                                f"\\begin{{minipage}}{{0.6\\textwidth}}\n"
                                f"    \\textcolor{{cpred}}{{\\textbf{{\\huge {producto['nombre']} }}}}\\\\\n"
                                f"    {{\\textit{{Mini Ramo}}}} \\\\\n"
                                f"    \\textcolor{{cpred}}{{\\Huge ♥}} \\\\\n"
                                f"    \\vspace{{0.5cm}}\n"
                                f"    \\begin{{itemize}}\n"
                                f"        \\item {producto['descripcion']}\n"
                                f"        \\item Follaje Verde\n"
                                f"        \\item Cono con Listón\n"
                                f"        \\item Tarjeta Dedicatoria\n"
                                f"    \\end{{itemize}}\n"
                                f"\\end{{minipage}}\n"
                                f"\\hspace{{1cm}}\n"  # Separación de 2cm entre las columnas
                                f"\\begin{{minipage}}{{0.35\\textwidth}}\n"
                                f"    \\includegraphics[width=1.0\\textwidth]{{{producto['imagen']}}}\n"
                                f"\\end{{minipage}}\n"
                                f"\\vspace{{0.3cm}}\n"
                                f"\\begin{{center}}\n"                             
                                f"   \\textbf{{\\Large Precio: \\textcolor{{cpred}}{{S/. {producto['precio']} }}}}\n"
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
                                f"    \\textcolor{{cpred}}{{\\textbf{{\\huge {producto['nombre']} }}}}\\\\\n"
                                f"    {{\\textit{{Mini Ramo}}}} \\\\\n"
                                f"    \\textcolor{{cpred}}{{\\Huge ♥}} \\\\\n"
                                f"    \\vspace{{0.5cm}}\n"
                                f"    \\begin{{itemize}}\n"
                                f"        \\item {producto['descripcion']}\n"
                                f"        \\item Follaje Verde\n"
                                f"        \\item Cono con Listón\n"
                                f"        \\item Tarjeta Dedicatoria\n"
                                f"    \\end{{itemize}}\n"
                                f"\\end{{minipage}}\n"
                                f"\\vspace{{0.3cm}}\n"
                                f"\\begin{{center}}\n"                             
                                f"   \\textbf{{\\Large Precio: \\textcolor{{cpred}}{{S/. {producto['precio']} }}}}\n"
                                f"\\end{{center}}\n"
                                f"\\vspace{{1cm}}\n")

# Guardar contenido generado
titulo = "Catálogo de Productos"
contenido_completo = f"""
\\documentclass{{article}}
\\usepackage{{graphicx}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{xcolor}}
\\usepackage{{tcolorbox}}
\\usepackage{{geometry}}

% Configuración de márgenes
\\geometry{{left=2cm, right=2cm, top=2cm, bottom=2cm}}

% Definir colores
\\definecolor{{cpred}}{{RGB}}{{195,0,47}}
\\definecolor{{cpink}}{{RGB}}{{245,187,195}}

\\begin{{document}}
\\begin{{center}}
    \\includegraphics[width=0.3\\textwidth]{{logo.png}}
\\end{{center}}
\\title{{{titulo}}}
\\maketitle

{contenido_latex}
\\end{{document}}
"""

with open(catalogo_file, "w", encoding="utf-8") as file:
    file.write(contenido_completo)

print("Catálogo LaTeX generado correctamente en catalogo.tex")

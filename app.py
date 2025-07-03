import pandas as pd
import networkx as nx
from flask import Flask, render_template, request, jsonify
from geopy.distance import geodesic
import math

# ------------------- INICIALIZACIÓN DE LA APP -------------------
app = Flask(__name__)


# ------------------- FUNCIONES AUXILIARES -------------------

def find_nearest_node(graph, lat, lon):
    nearest_node = None
    min_dist = float('inf')
    for node in graph.nodes():
        dist = geodesic((lat, lon), node).meters
        if dist < min_dist:
            min_dist = dist
            nearest_node = node
    return nearest_node

def cargar_datos_y_crear_grafo(filepath="10000_calles_vecinas_lima.csv"):
    print("Cargando datos y construyendo el grafo con ponderación...")
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"--- ERRROR GRAVE ---")
        print(f"No se pudo encontrar el archivo de datos: '{filepath}'")
        return None, None, None

    df["punto_inicio"] = df.apply(lambda r: (round(r["lat_inicio"], 6), round(r["lon_inicio"], 6)), axis=1)
    df["punto_fin"] = df.apply(lambda r: (round(r["lat_fin"], 6), round(r["lon_fin"], 6)), axis=1)

    G = nx.Graph()

    for _, row in df.iterrows():
        costo_base = row["tiempo_estimado_min"]
        nombre_via = row.get("nombre_via", "")
        distrito=row.get("distrito", "")
        punto_inicio = row["punto_inicio"]
        punto_fin = row["punto_fin"]
        # Verifica que ambos nodos sean tuplas válidas de longitud 2
        if (
            isinstance(punto_inicio, tuple) and len(punto_inicio) == 2 and
            isinstance(punto_fin, tuple) and len(punto_fin) == 2 and
            all(isinstance(x, (int, float)) for x in punto_inicio + punto_fin)
        ):
            if isinstance(distrito, str) and (distrito.startswith("Miraflores") or distrito.startswith("San Borja")):
                costo_final = costo_base * 10
            else:
                costo_final = costo_base
            if isinstance(distrito, str) and (distrito.startswith("La Victoria")):
                costo_final = costo_base * 15
            else:
                costo_final = costo_base   
            if isinstance(distrito, str) and (distrito.startswith("San Isidro")):
                costo_final = costo_base * 9.5
            else:    
                costo_final = costo_base
            if isinstance(distrito, str) and (distrito.startswith("Surquillo")):
                costo_final = costo_base * 5
            else:    
                costo_final = costo_base
            G.add_edge(
                punto_inicio,
                punto_fin,
                name=nombre_via,
                length=row["longitud_metros"],
                time=costo_final
            )

    # Obtenemos la lista de calles para los menús desplegables
    lista_calles_unicas = sorted(df["nombre_via"].unique())

    print("¡Grafo ponderado cargado exitosamente!")
    # Devolvemos los 3 elementos
    return G, df, lista_calles_unicas


# ------------------- CARGA GLOBAL DE DATOS -------------------
GRAFO, DF_CALLES, LISTA_CALLES = cargar_datos_y_crear_grafo()
if GRAFO is None:
    exit()


# ------------------- RUTAS DE LA APLICACIÓN WEB -------------------

# --- Rutas para la Interfaz del MAPA ---
@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/ruta_json', methods=['POST'])
def ruta_json():
    data = request.get_json()
    start_coords = data['start']
    end_coords = data['end']
    start_node = find_nearest_node(GRAFO, start_coords[0], start_coords[1])
    end_node = find_nearest_node(GRAFO, end_coords[0], end_coords[1])
    # ... (resto de la lógica de ruta_json es igual)
    if not start_node or not end_node or start_node == end_node:
        return jsonify({'error': 'No se pudieron encontrar nodos válidos.'}), 400
    try:
        def heuristica(u, v): return geodesic(u, v).meters
        ruta_nodos = nx.astar_path(GRAFO, source=start_node, target=end_node, heuristic=heuristica, weight='time')
        tiempo_total, distancia_total = 0, 0
        for i in range(len(ruta_nodos) - 1):
            edge_data = GRAFO.get_edge_data(ruta_nodos[i], ruta_nodos[i+1])
            tiempo_total += edge_data.get('time', 0)
            distancia_total += edge_data.get('length', 0)
        return jsonify({'ruta': ruta_nodos, 'tiempo': tiempo_total, 'distancia': distancia_total / 1000})
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return jsonify({'error': 'No se encontró una ruta conectada en el grafo.'}), 404


# --- Rutas para la CALCULADORA CLÁSICA (menús desplegables) ---
@app.route('/calculadora')
def calculadora_clasica():
    """
    Muestra la página con los menús desplegables.
    """
    return render_template('calculadora_clasica.html', calles=LISTA_CALLES)


@app.route('/calcular_ruta', methods=['POST'])
def calcular_ruta():
    """
    Procesa el formulario de la calculadora clásica.
    """
    calle_inicio_nombre = request.form.get('calle_inicio')
    calle_fin_nombre = request.form.get('calle_fin')

    if not calle_inicio_nombre or not calle_fin_nombre or calle_inicio_nombre == calle_fin_nombre:
        error = "Por favor, selecciona una calle de inicio y una de fin distintas."
        return render_template('calculadora_clasica.html', calles=LISTA_CALLES, error=error)
    try:
        nodo_inicio = DF_CALLES[DF_CALLES['nombre_via'] == calle_inicio_nombre].iloc[0]['punto_inicio']
        nodo_fin = DF_CALLES[DF_CALLES['nombre_via'] == calle_fin_nombre].iloc[0]['punto_fin']
        
        def heuristica(u, v): return geodesic(u, v).meters
        ruta_nodos = nx.astar_path(GRAFO, source=nodo_inicio, target=nodo_fin, heuristic=heuristica, weight='time')
        
        ruta_calles, tiempo_total, distancia_total = [], 0, 0
        for i in range(len(ruta_nodos) - 1):
            edge_data = GRAFO.get_edge_data(ruta_nodos[i], ruta_nodos[i+1])
            ruta_calles.append(edge_data['name'])
            tiempo_total += edge_data['time']
            distancia_total += edge_data['length']
        
        ruta_limpia = [ruta_calles[0]]
        for i in range(1, len(ruta_calles)):
            if ruta_calles[i] != ruta_calles[i-1]:
                ruta_limpia.append(ruta_calles[i])

        return render_template('resultado.html',
                               ruta=ruta_limpia,
                               tiempo=round(tiempo_total, 2),
                               distancia=round(distancia_total / 1000, 2),
                               inicio=calle_inicio_nombre,
                               fin=calle_fin_nombre)
    except (nx.NetworkXNoPath, IndexError):
        error = f"No se pudo encontrar una ruta conectada entre '{calle_inicio_nombre}' y '{calle_fin_nombre}'."
        return render_template('calculadora_clasica.html', calles=LISTA_CALLES, error=error)


# ------------------- EJECUCIÓN DE LA APP -------------------
if __name__ == '__main__':
    app.run(debug=True)
import pandas as pd
import networkx as nx
from flask import Flask, render_template, request, jsonify
from geopy.distance import geodesic
import math
from datetime import datetime # <<<--- AÑADIR ESTA LÍNEA

# ------------------- INICIALIZACIÓN DE LA APP -------------------
app = Flask(__name__)

# ------------------- FUNCIONES AUXILIARES -------------------
def find_nearest_node(graph, lat, lon):
    # ... (esta función no cambia)
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
        # Asegúrate que tu CSV ahora tiene las columnas: tiempo_normal, tiempo_punta, tiempo_noche
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"--- ERRROR GRAVE ---")
        print(f"No se pudo encontrar el archivo de datos: '{filepath}'")
        return None, None, None

    df["punto_inicio"] = df.apply(lambda r: (round(r["lat_inicio"], 6), round(r["lon_inicio"], 6)), axis=1)
    df["punto_fin"] = df.apply(lambda r: (round(r["lat_fin"], 6), round(r["lon_fin"], 6)), axis=1)

    G = nx.Graph()

    for _, row in df.iterrows():
        distrito=row.get("distrito", "")
        tipo_via = row.get("tipo_via", "calle") # <<<--- OBTENER EL TIPO DE VÍA (si no existe, se asume 'calle')
        punto_inicio = row["punto_inicio"]
        punto_fin = row["punto_fin"]

        # --- CAMBIO: APLICAR PENALIZACIÓN DE DISTRITO ---
        # Primero, calcula el factor de penalización del distrito
        penalty_factor = 1.0
        if isinstance(distrito, str):
            if distrito.startswith("Miraflores") or distrito.startswith("San Borja"):
                penalty_factor = 2
            elif distrito.startswith("La Victoria"):
                penalty_factor = 2.5
            elif distrito.startswith("San Isidro"):
                penalty_factor = 2
            elif distrito.startswith("Surquillo"):
                penalty_factor = 2.3

        road_type_multiplier = 1.0
        if tipo_via == 'avenida':
            road_type_multiplier = 0.8  # 20% más rápido en avenidas
        elif tipo_via == 'via expresa':
            road_type_multiplier = 0.6  # 40% más rápido en vías expresas
        elif tipo_via == 'jiron':
            road_type_multiplier = 1.2  # 20% más lento en jirones


        # --- CAMBIO: GUARDAR TODOS LOS PERFILES DE TIEMPO CON LA PENALIZACIÓN APLICADA ---
        G.add_edge(
            punto_inicio,
            punto_fin,
            name=row.get("nombre_via", ""),
            length=row["longitud_metros"],
            # El tiempo base se multiplica por ambos factores
            time_normal=row["tiempo_normal"] * penalty_factor * road_type_multiplier,
            time_rush_hour=row["tiempo_punta"] * penalty_factor * road_type_multiplier,
            time_night=row["tiempo_noche"] * penalty_factor * road_type_multiplier
        )
        

    lista_calles_unicas = sorted(df["nombre_via"].unique())
    print("¡Grafo ponderado cargado exitosamente!")
    return G, df, lista_calles_unicas

# ------------------- CARGA GLOBAL DE DATOS -------------------
GRAFO, DF_CALLES, LISTA_CALLES = cargar_datos_y_crear_grafo()
if GRAFO is None:
    exit()

# ------------------- RUTAS DE LA APLICACIÓN WEB -------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ruta_json', methods=['POST'])
def ruta_json():
    data = request.get_json()
    start_coords = data['start']
    end_coords = data['end']
    start_node = find_nearest_node(GRAFO, start_coords[0], start_coords[1])
    end_node = find_nearest_node(GRAFO, end_coords[0], end_coords[1])

    if not start_node or not end_node or start_node == end_node:
        return jsonify({'error': 'No se pudieron encontrar nodos válidos.'}), 400
    try:
        # --- CAMBIO: LÓGICA PARA ELEGIR EL PESO SEGÚN LA HORA ---
        current_hour = datetime.now().hour # Obtiene la hora actual del servidor (0-23)
        
        # Define los rangos de hora
        if 7 <= current_hour < 10 or 17 <= current_hour < 20: # De 7-9am y 5-7pm
            weight_key = 'time_rush_hour'
            print("Cálculo con perfil: HORA PUNTA")
        elif 23 <= current_hour or current_hour < 6: # De 11pm a 5am
            weight_key = 'time_night'
            print("Cálculo con perfil: NOCHE")
        else: # El resto del día
            weight_key = 'time_normal'
            print("Cálculo con perfil: NORMAL")
        # --- FIN DEL CAMBIO ---

        def heuristica(u, v): return geodesic(u, v).meters
        
        # --- CAMBIO: USA LA LLAVE DE PESO DINÁMICA ---
        ruta_nodos = nx.astar_path(GRAFO, source=start_node, target=end_node, heuristic=heuristica, weight=weight_key)
        
        tiempo_total, distancia_total = 0, 0
        for i in range(len(ruta_nodos) - 1):
            edge_data = GRAFO.get_edge_data(ruta_nodos[i], ruta_nodos[i+1])
            # --- CAMBIO: USA LA MISMA LLAVE PARA SUMAR EL TIEMPO ---
            tiempo_total += edge_data.get(weight_key, 0)
            distancia_total += edge_data.get('length', 0)
            
        return jsonify({'ruta': ruta_nodos, 'tiempo': tiempo_total, 'distancia': distancia_total / 1000})
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return jsonify({'error': 'No se encontró una ruta conectada en el grafo.'}), 404

# ... (El resto de tu código para /calculadora y /calcular_ruta no necesita cambios urgentes,
# pero idealmente también deberían usar esta lógica de tiempo dinámico)

# ------------------- EJECUCIÓN DE LA APP -------------------
if __name__ == '__main__':
    app.run(debug=True)
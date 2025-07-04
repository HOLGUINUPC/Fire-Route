import pandas as pd
import re

def determinar_tipo_via(nombre_via):
    """
    Determina el tipo de vía basándose en el nombre de la vía.
    """
    if pd.isna(nombre_via) or not isinstance(nombre_via, str):
        return ""
    
    nombre_via_lower = nombre_via.lower().strip()
    
    # Diccionario de tipos de vías con sus patrones de búsqueda
    tipos_via = {
        'avenida': [r'^avenida\b', r'^av\.\s', r'^av\s'],
        'calle': [r'^calle\b'],
        'jiron': [r'^jirón\b', r'^jiron\b', r'^jr\.\s', r'^jr\s'],
        'via': [r'^vía\b', r'^via\b'],
        'ovalo': [r'^óvalo\b', r'^ovalo\b'],
        'malecon': [r'^malecón\b', r'^malecon\b'],
        'pasaje': [r'^pasaje\b'],
        'plaza': [r'^plaza\b'],
        'parque': [r'^parque\b'],
        'prolongacion': [r'^prolongación\b', r'^prolongacion\b'],
        'autopista': [r'^autopista\b'],
        'carretera': [r'^carretera\b'],
        'boulevard': [r'^boulevard\b'],
        'alameda': [r'^alameda\b'],
        'sendero': [r'^sendero\b'],
        'camino': [r'^camino\b']
    }
    
    # Buscar coincidencias con los patrones
    for tipo, patrones in tipos_via.items():
        for patron in patrones:
            if re.search(patron, nombre_via_lower):
                return tipo
    
    # Si no encuentra coincidencia específica, intentar detectar por palabras clave
    # Casos especiales comunes en Lima
    if 'expresa' in nombre_via_lower:
        return 'via'
    elif 'circuito' in nombre_via_lower:
        return 'circuito'
    elif 'diagonal' in nombre_via_lower:
        return 'avenida'  # Las diagonales suelen ser avenidas
    
    # Si no se puede determinar, devolver cadena vacía
    return ""

def completar_tipo_via(archivo_csv):
    """
    Completa la columna tipo_via en el archivo CSV basándose en el nombre_via.
    """
    print(f"Leyendo archivo: {archivo_csv}")
    
    # Leer el CSV
    df = pd.read_csv(archivo_csv)
    
    print(f"Total de filas: {len(df)}")
    
    # Contar filas con tipo_via vacío
    filas_vacias = df['tipo_via'].isna() | (df['tipo_via'] == '') | (df['tipo_via'].str.strip() == '')
    total_vacias = filas_vacias.sum()
    
    print(f"Filas con tipo_via vacío: {total_vacias}")
    
    if total_vacias == 0:
        print("No hay filas con tipo_via vacío para completar.")
        return
    
    # Completar tipo_via para las filas vacías
    df.loc[filas_vacias, 'tipo_via'] = df.loc[filas_vacias, 'nombre_via'].apply(determinar_tipo_via)
    
    # Contar cuántas se completaron exitosamente
    filas_completadas = (df.loc[filas_vacias, 'tipo_via'] != '').sum()
    
    print(f"Filas completadas exitosamente: {filas_completadas}")
    print(f"Filas que no se pudieron completar: {total_vacias - filas_completadas}")
    
    # Crear archivo de respaldo
    archivo_respaldo = archivo_csv.replace('.csv', '_respaldo.csv')
    df_original = pd.read_csv(archivo_csv)
    df_original.to_csv(archivo_respaldo, index=False)
    print(f"Archivo de respaldo creado: {archivo_respaldo}")
    
    # Guardar el archivo actualizado
    df.to_csv(archivo_csv, index=False)
    print(f"Archivo actualizado guardado: {archivo_csv}")
    
    # Mostrar estadísticas finales
    print("\n=== ESTADÍSTICAS FINALES ===")
    tipos_via_counts = df['tipo_via'].value_counts()
    print("Distribución de tipos de vía:")
    for tipo, cantidad in tipos_via_counts.items():
        if tipo and tipo.strip():  # Solo mostrar tipos no vacíos
            print(f"  {tipo}: {cantidad}")
    
    # Mostrar ejemplos de filas que no se pudieron completar
    filas_sin_completar = df[(df['tipo_via'].isna()) | (df['tipo_via'] == '') | (df['tipo_via'].str.strip() == '')]
    if len(filas_sin_completar) > 0:
        print(f"\nEjemplos de filas que no se pudieron completar (primeras 10):")
        for i, row in filas_sin_completar.head(10).iterrows():
            print(f"  Fila {i+1}: '{row['nombre_via']}'")

if __name__ == "__main__":
    archivo_csv = "10000_calles_vecinas_lima.csv"
    completar_tipo_via(archivo_csv)

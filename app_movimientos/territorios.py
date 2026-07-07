"""
Módulo de Gestión Territorial (Chile).

Este módulo es responsable de cargar la división político-administrativa de Chile
(Regiones, Provincias y Comunas) desde un archivo JSON local. Proporciona funciones
de utilidad y consulta para alimentar listas desplegables dependientes en los formularios
y validar la coherencia geográfica de las ubicaciones ingresadas en el sistema.

Buenas prácticas aplicadas:
- Carga en memoria en tiempo de importación para evitar lecturas repetidas al disco (IO optimization).
- Encapsulamiento del acceso al diccionario de territorios mediante funciones de consulta limpias.
"""

import json
from pathlib import Path

# Ruta absoluta al archivo de datos de territorios en el mismo directorio del módulo
_DATA_PATH = Path(__file__).with_name('territorios_chile.json')

# Carga del catálogo territorial en memoria una sola vez al iniciar la aplicación
with _DATA_PATH.open(encoding='utf-8') as data_file:
    TERRITORIOS = json.load(data_file)


def provincias_de(region):
    """
    Obtiene la lista de provincias pertenecientes a una región específica.

    Args:
        region (str): Identificador o nombre de la región.

    Returns:
        list: Lista de nombres de las provincias correspondientes a la región.
              Devuelve una lista vacía si la región no existe en el catálogo.
    """
    return list(TERRITORIOS.get(region, {}))


def comunas_de(region, provincia):
    """
    Obtiene la lista de comunas pertenecientes a una provincia dentro de una región.

    Args:
        region (str): Identificador o nombre de la región.
        provincia (str): Nombre de la provincia.

    Returns:
        list: Lista de nombres de las comunas asociadas. Devuelve lista vacía
              si la región o la provincia no se encuentran.
    """
    return TERRITORIOS.get(region, {}).get(provincia, [])


def ubicacion_valida(region, provincia, comuna):
    """
    Verifica la coherencia geográfico-administrativa de una terna (región, provincia, comuna).

    Utilizada en la validación de formularios y modelos para asegurar que el usuario no asigne
    una comuna a una provincia o región incorrecta (ej. Puente Alto en la Provincia de Valparaíso).

    Args:
        region (str): Identificador de la región.
        provincia (str): Nombre de la provincia a verificar.
        comuna (str): Nombre de la comuna a verificar.

    Returns:
        bool: True si la comuna pertenece a la provincia y la provincia a la región; False en caso contrario.
    """
    return provincia in provincias_de(region) and comuna in comunas_de(region, provincia)


import json
from pathlib import Path


_DATA_PATH = Path(__file__).with_name('territorios_chile.json')

with _DATA_PATH.open(encoding='utf-8') as data_file:
    TERRITORIOS = json.load(data_file)


def provincias_de(region):
    return list(TERRITORIOS.get(region, {}))


def comunas_de(region, provincia):
    return TERRITORIOS.get(region, {}).get(provincia, [])


def ubicacion_valida(region, provincia, comuna):
    return provincia in provincias_de(region) and comuna in comunas_de(region, provincia)

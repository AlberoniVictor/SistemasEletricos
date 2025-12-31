from django.http import JsonResponse
import pandas as pd
import numpy as np
import os

import requests
from django.views.decorators.http import require_GET
from django.http import JsonResponse

# Caminho absoluto do CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "global_horizontal_means.csv")

# Carrega o CSV uma vez (ao iniciar o servidor)
df = pd.read_csv(
    CSV_PATH,
    sep=';',
    usecols=['ID','LON','LAT','ANNUAL','JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'],
    dtype={
        'ID': np.int32, 'LON': np.float32, 'LAT': np.float32,
        'ANNUAL': np.int16, 'JAN': np.int16, 'FEB': np.int16, 'MAR': np.int16,
        'APR': np.int16, 'MAY': np.int16, 'JUN': np.int16, 'JUL': np.int16,
        'AUG': np.int16, 'SEP': np.int16, 'OCT': np.int16, 'NOV': np.int16, 'DEC': np.int16
    }
)


colunas_dividir = ['ANNUAL','JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
df[colunas_dividir] = df[colunas_dividir] / 1000.0

lats = df['LAT'].to_numpy()
lons = df['LON'].to_numpy()

def irradiacao_mais_proxima(lat, lon):
    dist = np.sqrt((lats - lat)**2 + (lons - lon)**2)
    idx = np.argmin(dist)
    return df.iloc[idx].to_dict()

def buscar_irradiacao(request):
    try:
        lat = float(request.GET.get('lat'))
        lon = float(request.GET.get('lon'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Parâmetros inválidos. Use ?lat=xx&lon=yy'}, status=400)

    resultado = irradiacao_mais_proxima(lat, lon)
    return JsonResponse(resultado, json_dumps_params={'ensure_ascii': False})


# ==========================
# 1) Buscar endereço por CEP
# ==========================

def buscar_endereco_por_cep(cep: str):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    r = requests.get(url, timeout=5)

    if r.status_code != 200:
        return None
    
    data = r.json()

    if "erro" in data:
        return None
    
    return data  # logradouro, bairro, localidade, uf...


# ==========================
# 2) Geocoding (endereço → coordenadas LAT/LON)
# ==========================

def geocodificar_endereco(endereco: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": endereco,
        "format": "json",
        "limit": 1,
    }

    headers = {
        "User-Agent": "SeuSistemaSolar/1.0 (contato@seudominio.com)"
    }

    r = requests.get(url, params=params, headers=headers, timeout=5)

    if r.status_code != 200:
        return None

    data = r.json()
    if not data:
        return None

    return {
        "lat": float(data[0]["lat"]),
        "lon": float(data[0]["lon"]),
        "display_name": data[0]["display_name"]
    }


# ==========================
# 3) Endpoint principal: CEP → Endereço → Coordenadas → Irradiação
# ==========================

@require_GET
def irradiacao_por_cep(request):
    cep = request.GET.get("cep", "").replace("-", "").strip()

    if len(cep) != 8 or not cep.isdigit():
        return JsonResponse({"error": "CEP inválido"}, status=400)

    # 1) Buscar endereço
    endereco_data = buscar_endereco_por_cep(cep)
    if not endereco_data:
        return JsonResponse({"error": "CEP não encontrado"}, status=404)

    # Monta string completa de endereço
    endereco_str = f"{endereco_data['logradouro']}, {endereco_data['bairro']}, {endereco_data['localidade']} - {endereco_data['uf']}, Brasil"

    # 2) Geocodificar
    coords = geocodificar_endereco(endereco_str)
    if not coords:
        return JsonResponse({"error": "Não foi possível obter coordenadas do endereço"}, status=500)

    lat = coords["lat"]
    lon = coords["lon"]

    # 3) Chama sua função existente
    irradiacao = irradiacao_mais_proxima(lat, lon)

    return JsonResponse({
        "cep": cep,
        "endereco": endereco_str,
        "lat": lat,
        "lon": lon,
        "irradiacao": irradiacao
    }, json_dumps_params={'ensure_ascii': False})
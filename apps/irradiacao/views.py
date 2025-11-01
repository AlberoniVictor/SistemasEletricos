from django.http import JsonResponse
import pandas as pd
import numpy as np
import os

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

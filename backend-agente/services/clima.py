import requests

def obtener_pronostico_la_paz(lat: float = None, lon: float = None) -> str:
    
    
    LAT_DEFAULT = -16.4957
    LON_DEFAULT = -68.1335
    
    lat = lat if lat is not None else LAT_DEFAULT
    lon = lon if lon is not None else LON_DEFAULT
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation&forecast_days=1"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        precipitaciones = data['hourly']['precipitation']
        
        if any(p > 0.1 for p in precipitaciones[:12]):
            return "Lluvioso durante el día"
        return "Despejado durante el día"
    except:
        return "Desconocido"
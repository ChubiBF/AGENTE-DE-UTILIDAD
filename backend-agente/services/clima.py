import requests

def obtener_pronostico_la_paz():
    
    lat, lon = -16.4897, -68.1193
    
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
# ingestion_manager.py
from adapters import football_data_adapter, api_football_adapter, weather_adapter

def run_all_ingestions():
    # Hier werden alle Adapter nacheinander aufgerufen
    football_data_adapter.sync()
    api_football_adapter.sync()
    weather_adapter.sync()
    print("Alle Quellen synchronisiert.")

name: Data Sync
on:
  workflow_dispatch: # Erlaubt dir, das Skript manuell auf dem iPhone zu starten
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with: {python-version: '3.9'}
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run ingestion
        env:
          API_FOOTBALL_KEY: ${{ secrets.API_FOOTBALL_KEY }}
          FOOTBALL_DATA_KEY: ${{ secrets.FOOTBALL_DATA_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          OPENWEATHER_KEY: ${{ secrets.OPENWEATHER_KEY }}
        run: python ingest.py

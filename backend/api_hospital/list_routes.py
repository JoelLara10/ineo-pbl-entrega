# list_routes.py
from app import create_app

app = create_app()

print("\n=== RUTAS REGISTRADAS ===\n")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.methods} - {rule}")
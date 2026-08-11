from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

# Configuración
from config import config

# Blueprints
from routes.auth import auth_bp
from routes.patients import patients_bp
from routes.medical import medical_bp
from routes.beds import beds_bp
from routes.catalog import catalog_bp
from routes.reports import reports_bp
from routes.appointments import appointment_bp
from routes.analytics import analytics_bp
from routes.studies import studies_bp
from routes.pdf import pdf_bp
from routes.exams import exams_bp
from routes.billing import billing_bp
from routes.administrative import admin_bp, mobile_admin_bp
from routes.backup import backup_bp
from routes.performance import performance_bp
from middleware.auth_middleware import token_required
from scheduler.jobs import init_scheduler

def create_app():
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY
    
    # Configurar CORS
    #CORS(app, origins=config.CORS_ORIGINS, supports_credentials=True)
    CORS(
        app,
        resources={r"/*": {"origins": config.CORS_ORIGINS}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix=f'{config.API_PREFIX}/auth')
    app.register_blueprint(mobile_admin_bp, url_prefix=f'{config.API_PREFIX}')
    app.register_blueprint(patients_bp, url_prefix=f'{config.API_PREFIX}')
    app.register_blueprint(medical_bp, url_prefix=f'{config.API_PREFIX}')
    app.register_blueprint(beds_bp, url_prefix=f'{config.API_PREFIX}')
    app.register_blueprint(catalog_bp, url_prefix=f'{config.API_PREFIX}/catalog')
    app.register_blueprint(reports_bp, url_prefix=f'{config.API_PREFIX}')
    app.register_blueprint(appointment_bp, url_prefix=f'{config.API_PREFIX}')
    app.register_blueprint(analytics_bp, url_prefix=f'{config.API_PREFIX}')
    app.register_blueprint(studies_bp, url_prefix=f'{config.API_PREFIX}')
    app.register_blueprint(pdf_bp, url_prefix=f'{config.API_PREFIX}/pdf')
    app.register_blueprint(exams_bp, url_prefix=f'{config.API_PREFIX}/exams')
    app.register_blueprint(billing_bp, url_prefix=f'{config.API_PREFIX}')
    app.register_blueprint(admin_bp, url_prefix=f'{config.API_PREFIX}')
    app.register_blueprint(backup_bp, url_prefix=f'{config.API_PREFIX}/backup')
    app.register_blueprint(performance_bp, url_prefix=f'{config.API_PREFIX}/performance')

    # Iniciar tareas automáticas después de registrar las rutas.
    init_scheduler(app)
    

    @app.before_request
    def log_request_start():
        print(
        f">>> PETICIÓN RECIBIDA: {request.method} {request.full_path}",
        flush=True
    )
    

    @app.route(f'{config.API_PREFIX}/analytics/dashboard', methods=['GET'])
    @token_required
    def dashboard_fallback():
        from services.analytics_service import AnalyticsService
        return jsonify(AnalyticsService.get_dashboard_stats()), 200

    @app.route(f'{config.API_PREFIX}/studies/counts', methods=['GET'])
    @token_required
    def studies_counts_fallback():
        from services.exam_service import ExamService
        return jsonify(ExamService.get_counts()), 200
    
    # Ruta de salud
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'version': config.API_VERSION
        }), 200
    
    # Ruta raíz
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'name': config.API_TITLE,
            'version': config.API_VERSION,
            'endpoints': {
                'auth': f'{config.API_PREFIX}/auth',
                'patients': f'{config.API_PREFIX}/patients',
                'medical': f'{config.API_PREFIX}/medical'
            }
        }), 200
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso no encontrado'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno del servidor'}), 500
    

    return app

if __name__ == '__main__':
    app = create_app()
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 5001))
    
    app.run(debug=debug, host='0.0.0.0', port=port)

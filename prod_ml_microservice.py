from waitress import serve
import ml_microservice
serve(ml_microservice.app, host='0.0.0.0', port=5002)


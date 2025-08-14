from src.api import create_api_app
api = create_api_app()

api.run(port=5001, debug=1)
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    from app.controllers.routes import main
    app.register_blueprint(main)

    return app

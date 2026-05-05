from flask import Flask, render_template
from config import Config
from models import db
from routes import bp, init_login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    init_login_manager(app)

    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8000)

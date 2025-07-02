from flask import Flask, render_template
from dbModule import db,migrate
from config import Config
from dbModule.routes import api_bp, getAllFiles

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.sort_keys = False

    app.register_blueprint(api_bp)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def MainPage():
        data = getAllFiles().json["data"]
        return render_template("base.html",data=data)

    with app.app_context():
        db.create_all()

    return app

app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
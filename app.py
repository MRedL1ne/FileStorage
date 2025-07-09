from flask import Flask, render_template
from config import Config
from dbModule import db,migrate
from dbModule.routes import api_bp, getAllFiles

def createApp():
    app = Flask(__name__, template_folder="Templates")
    app.config.from_object(Config)
    app.json.sort_keys = False
    app.json.compact = False

    app.register_blueprint(api_bp)

    try:
        db.init_app(app)
        migrate.init_app(app, db)
        with app.app_context():
            db.create_all()
    except Exception as ex:
        print(ex)

    @app.route("/")
    def mainPage():
        data = getAllFiles().json["data"]
        return render_template("base.html",data=data)

    return app

app = createApp()

# Функция для вызова синхронизации
def runSync():
    with app.app_context():
        from dbModule.routes import sync
        sync()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
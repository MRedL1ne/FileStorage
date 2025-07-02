import os
import shutil
from datetime import datetime
import flask
from flask import Blueprint, jsonify, request
from dbModule.models import File
from config import filedir
from . import db

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/get", methods = ['POST'])
def getFiles():
    # Получение данных из запроса
    filename =  request.form["filename"].lower()
    name, extension = "", ""
    if filename != "":
        name, extension = filename.split(".")

    path = f"{filedir}\\{request.form["path"].strip()}".replace("/","\\").lower()
    if path[-1] != "\\":
        path += "\\"

    # Нахождение совпадений в БД
    file = (db.session.query(File).filter(File.name == name)
             .filter(File.extension == extension)
             .filter(File.path == path)).first()
    if file:
        return jsonify({
            "status": "ok",
            "data": file.getData()
        })
    else:
        return jsonify({
            "status": "error",
            "msg": "File isn't found!"
        })

@api_bp.route("/getByPath", methods=['POST'])
def getByPathFiles():
    # Получение данных из запроса
    path = f"{filedir}\\{request.form["path"].strip()}".replace("/","\\").lower()
    path = path.replace("\\", "\\\\")
    if path[-1] != "\\":
        path += "\\"

    # Нахождение совпадений части пути в БД
    files = db.session.query(File).filter(File.path.startswith(path))
    files.all()

    if len(files.all()) == 0:
        return jsonify({
            "status": "error",
            "msg": "Files aren't found!"
        })
    else:
        lst = []
        for file in files:
            lst.append(file.getData())
        return jsonify({
            "status": "ok",
            "data": lst
        })

@api_bp.route("/getAll")
def getAllFiles():
    files = db.session.query(File).all()
    lst = []
    for file in files:
        lst.append(file.getData())
    return jsonify({
        "status": "ok",
        "data": lst
    })

@api_bp.route("/add", methods=['POST'])
def addFile():
    # Получение данных из запроса
    file = request.files["file"]
    filename = file.filename.lower()
    name, extension = filename.split(".")
    size = len(file.read())
    path = f"{filedir}\\{request.form["path"].strip()}".replace("/","\\").lower()
    if path[-1] != "\\":
        path += "\\"
    comment = request.form["comment"]

    fullpath = f"{path+name}.{extension}"
    os.makedirs(path, mode=0o777, exist_ok=True)

    file.seek(0)
    if not os.path.exists(fullpath):
        created_at = datetime.now()
        file.save(fullpath)
        newFile = File(name, extension, size, path, created_at, created_at, comment)
        db.session.add(newFile)
        db.session.commit()
        return jsonify({
            "status": "ok",
            "msg": "File is added!",
            "data": newFile.getData()
        })
    else:
        return jsonify({
            "status": "error",
            "msg": "File is existed!"
        })

@api_bp.route("/edit", methods=['POST'])
def editFile():
    # Получение данных из запроса
    id = int(request.form["id"])
    name = request.form["name"].lower()
    comment = request.form["comment"]

    path = f"{filedir}\\{request.form["path"].strip()}".replace("/", "\\").lower()
    if path[-1] != "\\":
        path += "\\"

    # Нахождение нужного файла (по id)
    file = db.session.query(File).filter(File.id == id).first()
    if file:
        extension = file.extension.strip()
        oldName = file.name.strip()
        oldPath = file.path.replace("\\\\", "\\")

        # Перемещение файла и обновление данных в БД
        if not os.path.exists(path):
            os.makedirs(path, mode=0o777, exist_ok=True)
        shutil.move(f"{oldPath + oldName}.{extension}",f"{path + name}.{extension}")

        try:
            os.removedirs(oldPath)
        except: pass

        file.updated_at = datetime.now()
        file.name = name
        file.path = path
        file.comment = comment

        db.session.commit()
        return jsonify({
            "status": "ok",
            "msg": "File is edited!"
        })
    else:
        return jsonify({
            "status": "error",
            "msg": "Wrong id!"
        })

@api_bp.route("/delete", methods=['POST'])
def deleteFile():
    # Получение id из запроса
    id = request.form["id"]

    # Нахождение файла в БД
    file = db.session.query(File).filter(File.id == id).first()
    if file == None:
        return jsonify({
            "status": "error",
            "msg": "Wrong id!"
        })

    name = file.name.strip()
    extension = file.extension.strip()
    path = file.path.replace("\\\\","\\")
    fullpath = f"{path+name}.{extension}"

    # Удаление файла
    os.remove(fullpath)
    try:
        os.removedirs(path)
    except: pass
    db.session.delete(file)
    db.session.commit()
    return jsonify({
        "status": "ok",
        "msg": "File is deleted!",
        "data": file.getData()
    })

@api_bp.route("/download", methods=['POST'])
def downloadFile():
    # Получение id из запроса
    id = request.form["id"]

    # Нахождение файла в БД
    file = db.session.query(File).filter(File.id == id).first()
    if file:
        name = file.name.strip()
        extension = file.extension.strip()
        path = file.path.replace("\\\\","\\")
        fullpath = f"{path+name}.{extension}"

        return flask.send_file(fullpath, as_attachment=True)
    else:
        return jsonify({
            "status": "error",
            "msg": "Wrong id!"
        })
@api_bp.route("/sync")
def sync():
    files = []
    filesDB = db.session.query(File).all()

    # Обновление информации в БД по добавленным файлам
    for dirpath, dirname, filenames in os.walk(filedir):
        path = f"{dirpath}\\".lower()
        for filename in filenames:
            name, extension = filename.lower().split(".")
            files.append((path,name,extension))

            fullpath = f"{path+name}.{extension}"
            size = os.path.getsize(fullpath)
            created_at = datetime.fromtimestamp(os.path.getctime(fullpath))
            updated_at = datetime.fromtimestamp(os.path.getmtime(fullpath))

            file = (db.session.query(File).filter(File.path == path)
                     .filter(File.name == name)
                     .filter(File.extension == extension).first())

            if file == None:
                newFile = File(name,extension,size,path,created_at,updated_at,"")
                db.session.add(newFile)
            else:
                file.size, file.created_at, file.updated_at = size, created_at, updated_at

    #Обновление информации в БД по удаленным файлам
    for file in filesDB:
        tpl = (file.path,file.name.strip(),file.extension.strip())
        if tpl not in files:
            try:
                os.removedirs(file.path)
            except: pass
            db.session.delete(file)

    db.session.commit()
    return jsonify({
        "status": "ok",
        "msg": "Sync is completed!"
    })



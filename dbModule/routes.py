import os
import shutil
import flask
from datetime import datetime
from flask import Blueprint, jsonify, request
from dbModule.models import File
from dbModule.validateForms import PathForm, EditForm
from config import filedir
from . import db

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/files/<int:id>", methods = ['GET'])
def getFile(id):
    # Нахождение нужного файла (по id)
    file = (db.session.query(File).filter(File.id == id)).one_or_none()
    if file:
        return jsonify({
            "status": "ok",
            "data": file.getData()
        })
    else:
        return jsonify({
            "status": "error",
            "msg": "Wrong id!"
        })

@api_bp.route("/files/search", methods=['GET'])
def getByPathFiles():
    # Получение данных из запроса
    pathForm = PathForm(request.args)
    subcheck = request.args.get("subcheck")
    if subcheck and subcheck.lower() == "false":
        subcheck = False

    # Проверка корректности пути
    if pathForm.validate():
        path = f"{filedir}\\{pathForm.path.data}".lower()

        # Нахождение совпадений пути в БД
        if subcheck:
            path = path.replace("\\", "\\\\")
            files = db.session.query(File).filter(File.path.startswith(path))
        else:
            path = path.replace("\\\\", "\\")
            files = db.session.query(File).filter(File.path == path)
        files.all()

        if not files.all():
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
    else:
        return jsonify({
            "status": "error",
            "errors": pathForm.errors
        })

@api_bp.route("/files")
def getAllFiles():
    files = db.session.query(File).all()
    lst = []
    for file in files:
        lst.append(file.getData())
    return jsonify({
        "status": "ok",
        "data": lst
    })

@api_bp.route("/files", methods=['POST'])
def addFile():
    # Проверка корректности пути
    pathForm = PathForm(request.form)
    if pathForm.validate():
        # Получение данных из запроса
        file = request.files["file"]
        filename = file.filename.lower()

        name, extension = filename.rsplit(".",1)
        if not name or not extension:
            return jsonify({
                "status": "error",
                "msg": "Unsupported filename!"
            })

        file.seek(0, os.SEEK_END)
        size = file.tell()
        path = f"{filedir}\\{pathForm.path.data}".lower()
        comment = request.form.get("comment")
        if not comment: comment = None

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
                "msg": "File already exists!"
            })
    else:
        return jsonify({
        "status": "error",
        "msg": "Incorrect form!"
    })

@api_bp.route("/files/<int:id>", methods=['PUT'])
def editFile(id):
    # Проверка корректности формы
    editForm = EditForm(request.form)

    if editForm.validate():
        name = editForm.name.data
        path = f"{filedir}\\{editForm.path.data}".lower()
        comment = request.form.get("comment")

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

            file.name = name
            file.path = path
            file.comment = comment
            file.updated_at = datetime.now()

            db.session.commit()
            return jsonify({
                "status": "ok",
                "msg": "File is edited!",
                "data": file.getData()
            })
        else:
            return jsonify({
                "status": "error",
                "msg": "Wrong id!"
            })
    else:
        return jsonify({
            "status": "error",
            "errors": editForm.errors
        })

@api_bp.route("/files/<int:id>", methods=['DELETE'])
def deleteFile(id):
    # Нахождение нужного файла (по id)
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

@api_bp.route("/files/<int:id>/download", methods=['GET'])
def downloadFile(id):
    # Нахождение нужного файла (по id)
    file = db.session.query(File).filter(File.id == id).first()
    if file:
        name = file.name.strip()
        extension = file.extension.strip()
        path = file.path.replace("\\\\","\\")
        fullpath = f"{path+name}.{extension}"

        if not name: name = "file"

        return flask.send_file(fullpath, as_attachment=True, download_name=f"{name}.{extension}")
    else:
        return jsonify({
            "status": "error",
            "msg": "Wrong id!"
        })

@api_bp.route("files/sync")
def sync():
    files = []
    filesDB = db.session.query(File).all()

    # Обновление информации в БД по добавленным файлам
    for dirpath, dirname, filenames in os.walk(filedir):
        path = f"{dirpath}\\".lower()
        for filename in filenames:
            name, extension = filename.rsplit(".",1)

            files.append((path,name,extension))

            fullpath = f"{path+name}.{extension}"
            size = os.path.getsize(fullpath)
            created_at = datetime.fromtimestamp(os.path.getctime(fullpath))
            updated_at = datetime.fromtimestamp(os.path.getmtime(fullpath))

            file = (db.session.query(File).filter(File.path == path)
                     .filter(File.name == name)
                     .filter(File.extension == extension).first())

            if not file:
                newFile = File(name,extension,size,path,created_at,updated_at,None)
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
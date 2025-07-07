from os.path import altsep
from wtforms import Form, IntegerField, StringField, validators
import os

class PathForm(Form):
    path = StringField("Path", [validators.regexp(r"(^(\w+[\\\/])+)$|^$")])
    def filter_path(form, field):
        if not field:
            return ""

        sep = os.path.sep
        if sep=="/":
            altsep="\\"
        else:
            altsep="/"
        path = field.replace("'", "").replace('"', '').replace(altsep, sep)

        if (len(path) != 0) and  (path[0] == sep):
            path = path[1::]

        if (len(path) != 0) and (path[-1] != sep):
            path = path + sep
        return path.strip().lower()

class EditForm(PathForm):
    name = StringField("Name", [validators.regexp(r'^[^\\\/:*?"<>|]+$'),
                                validators.length(1,255),
                                validators.input_required()])
    def filter_name(form,field):
        if not field:
            return ""

        name = field.replace("'", "").replace('"', '')
        return name.strip().lower()
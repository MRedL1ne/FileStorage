from wtforms import Form, StringField, validators

class PathForm(Form):
    path = StringField("Path", [validators.regexp(r"(^\w+[\\])+$|^$")])
    def filter_path(form, field):
        if not field:
            return field

        path = field.replace("/", "\\")
        if path[0] == "\\":
            path = path[1::]
        if path[-1] != "\\":
            path = path + "\\"
        return path.strip()

class EditForm(PathForm):
    name = StringField("Name", [validators.regexp(r'^[^\\\/:*?"<>|]+$'),
                                validators.length(1,255),
                                validators.input_required()])
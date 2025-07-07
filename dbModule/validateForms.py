from wtforms import Form, IntegerField, StringField, validators

class PathForm(Form):
    path = StringField("Path", [validators.regexp(r"(^(\w+[\\])+)$|^$")])
    def filter_path(form, field):
        if not field:
            return ""

        path = field.replace("'", "").replace('"', '').replace("/", "\\")

        if (len(path) != 0) and  (path[0] == "\\"):
            path = path[1::]

        if (len(path) != 0) and (path[-1] != "\\"):
            path = path + "\\"
        return path.strip()

class EditForm(PathForm):
    name = StringField("Name", [validators.regexp(r'^[^\\\/:*?"<>|]+$'),
                                validators.length(1,255),
                                validators.input_required()])
    def filter_name(form,field):
        if not field:
            return ""

        name = field.replace("'", "").replace('"', '')
        return name.strip()
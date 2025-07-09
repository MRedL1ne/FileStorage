# FileStorage [Flask + Postgres]
 Backend Web-приложения, управляющего файловым 
хранилищем и базой данных, которая содержит информацию о каждом файле.

## Описание запуска (Docker)

### 1. Клонирование репозитория
    git clone https://github.com/MRedL1ne/FileStorage.git

### 2. Переход в директорию FileStorage
```
cd FileStorage
```

### 3. Изменение файла `.env` для конфигурации БД
#### Пример файла:
    POSTGRES_USER = postgres
    POSTGRES_PW = postgres
    POSTGRES_URL = host.docker.internal
    POSTGRES_PORT = 5432
    POSTGRES_DB = fileStorage
   
### 4. Создание образов
    docker-compose build

### 5. Запуск контейнера
    docker-compose up 

## Зависимости
 * flask
 * flask_sqlalchemy
 * flask_migrate
 * psycopg2
 * wtforms
 * dotenv
  
## Документация API 
____
### GET-Запросы:
____

### api/files
```http://127.0.0.1:5000/api/files```

Получение списка информации о всех файлах
____

### api/files/search
```http://127.0.0.1:5000/api/files/search?path=[filepath]&subcheck=[boolean]```
* path - путь, где будут искаться файлы 
* subcheck - булевое значения для поиска файлов в подкаталогах. (По умолчанию - False)

Получение списка информации о файлах, расположенных по определенной части пути. Может учитывать файлы, находяшиеся в подкаталогах
____

### api/files/<id\>
```http://127.0.0.1:5000/api/files/<int:id> ```
* id - индентификатор файла из БД

Получение информации о файле по его ID
____

### api/files/<id\>/download
```http://127.0.0.1:5000/api/files/<int:id>/download ```
* id - индентификатор файла из БД

Скачивание существующего файла из хранилища

____

### api/files/sync
```http://127.0.0.1:5000/api/files/sync```

Синхронизация файлового хранилища и базы данных, когда файлы были добавлены/удалены вручную
____

____
### POST-Запросы:
____
### api/files
`http://127.0.0.1:5000/api/files`
Пример формы:
```
<form action="http://127.0.0.1:5000/api/files" method="POST" enctype="multipart/form-data">
   <h2>Add the file:</h2>
      <input type="file" name="file">
      <label>Path: files\<input type="text" name="path"></label>
      <label>Comment:<input type="text" name="comment"></label>
   <input type="submit" value="Add">
</form>
```
* file - файл, который будет загружен в файловое хранилище
* path - путь, где создастся файл
* comment [опционально] - комментарий, который будет храниться в БД

Загрузка нового файла в файловое хранилище и создание записи в базе 
данных, соответствующей этому файлу
____

____
### PUT-Запросы:
____
### api/files/<id\>
`http://127.0.0.1:5000/api/files/<int:id>` Измененные данные передаются через форму:
* name - новое название файла
* path - новый путь файла
* comment [опционально] - комментарий, который будет храниться в БД

Изменение информации о файле в базе данных. Внесенные изменения также отразятся и в хранилище 
____

____
### DELETE-Запросы:
____
### api/files/<id\>
```http://127.0.0.1:5000/api/files/<int:id>```
* id - индентификатор файла из БД

Удаление записи о файле из базы данных и удаление самого файла из 
файлового хранилища
____


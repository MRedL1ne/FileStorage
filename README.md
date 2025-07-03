# FileStorage [Flask + Postgres]
 Backend Web-приложения, управляющего файловым 
хранилищем и базой данных, которая содержит информацию о каждом файле.

## Описание запуска
1. Клонирование репозитория 
    ```
    git clone https://github.com/MRedL1ne/FileStorage.git
    ```

2. Установка зависимостей
    ```
    pip3 install -r requirements.txt
    ```

3. Изменение файла .env для конфигурации БД
    #### Пример файла:
      ```
      POSTGRES_USER = postgres
      POSTGRES_PW = postgres
      POSTGRES_URL = localhost:5432
      POSTGRES_DB = fileStorage
      ```
4. Запуск приложения
    ```
    python3 app.py
    ```

    ## Зависимости
    * flask
    * flask_sqlalchemy
    * flask_migrate
    * psycopg2
    * wtforms
    * dotenv
  
      
## Документация API
Большинство функций данного Web-приложения поддерживают POST и GET-запросы. Ознакомиться с формами для POST-запросов можно при помощи `Templates\base.html` 
____

### api/get
```http://127.0.0.1:5000/api/get?id=[fileid] ```
* id - индентификатор файла из БД

Поиск файла по его ID
____

### api/getByPath
```http://127.0.0.1:5000/api/getByPath?path=[filepath]&subcheck=[boolean]```
* path - путь, в котором будут искаться файлы 
* subcheck - булевое значения для поиска файлов в подкаталогах

Получение списка информации о файлах, расположенных по определенной части пути. Может учитывать файлы, находяшиеся в подкаталогах
____

### api/getAll 
```http://127.0.0.1:5000/api/getAll```

Получение списка информации о всех файлах
____

### api/add
`(Только POST-запрос через форму)`
Пример формы:
```
<form action="http://127.0.0.1:5000/api/add" method="POST" enctype="multipart/form-data">
  <h2>Add the file:</h2>
  <input type="file" name="file">
  <label>Path: files\<input type="text" name="path"></label>
  <label>Comment:<input type="text" name="comment"></label>
  <input type="submit">
</form>
```

Загрузка нового файла в файловое хранилище и создание записи в базе 
данных, соответствующей этому файлу.
____

### api/edit
```http://127.0.0.1:5000/api/edit?id=[fileid]&name=[filename]&path=[filepath]&comment=[optional]```
* id - индентификатор файла из БД 
* name - Новое название файла
* path - новый путь файла
* comment [опционально] - комментарий, который будет храниться в БД

Изменение информации о файле в базе данных. Внесенные изменения также отразятся и в хранилище 
____

### api/delete
```http://127.0.0.1:5000/api/delete?id=[fileid] ```
* id - индентификатор файла из БД

Удаление записи о файле из базы данных и удаление самого файла из 
файлового хранилища
____

### api/download
```http://127.0.0.1:5000/api/download?id=[fileid] ```
* id - индентификатор файла из БД

Скачивание существующего файла из хранилища
____

### api/sync
```http://127.0.0.1:5000/api/sync```

Синхронизация файлового хранилища и базы данных, когда файлы были добавлены/удалены вручную
____


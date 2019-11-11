# api
API for the SWARM project

# API Lib
Just a bunch of library functions to help with the API. Things like routes get defined here and possibly transformation functions.


# Notes
- flask request shape: (explanation)[https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request]
    - request.args: the key/value pairs in the URL query string
    - request.form: the key/value pairs in the body, from a HTML post form, or JavaScript request that isn't JSON encoded
    - request.files: the files in the body, which Flask keeps separate from form. HTML forms must use enctype=multipart/form-data or files will not be uploaded.
    - request.values: combined args and form, preferring args if keys overlap
    - request.json: parsed JSON data. The request must have the application/json content type, or use request.get_json(force=True) to ignore the content type.
import io
import os
import sys
import json
import datetime
import pandas as pd
from flask import Flask, render_template, send_from_directory, send_file, url_for
from flask import request, current_app, jsonify
from config import GetConfig
import model as Model
import functions as Func

Directorio = os.path.dirname(os.path.realpath('__file__'))
Func.Informo("Directorio='"+str(Directorio)+"'", Tipo="l", Section="root")
os.environ['BACKEND_DIRECTORY'] = Directorio
config_mode = GetConfig(os.environ.get('BACKEND_CONFIG_MODE', 'Production'))
if config_mode is None:
    exit('Mercadona:Backend:Error: Invalid BACKEND_CONFIG_MODE environment variable entry.')

app = Model.create_app(config_mode)

# @app.after_request
# def add_header(response):
#     #print("after_request::response='"+str(response)+"'", flush=True, file=sys.stdout)
#     response.headers['Server'] = 'Apache httpd 2.4.41 ((Windows))'
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
#     response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
#     response.headers['Access-Control-Max-Age'] ='300'
#     return response

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        PasoDatos = Func.ProcesaVariables(request)
        Func.Informo(PasoDatos, Tipo="e", Section="index access")
        return "{}"  # render_template('templates/index.html')
    except Exception as e:
        Func.Informo(e, Tipo="e", Section="index")


"""
API Interface:
"""

@app.route('/api/data', methods=['GET'])
def data(id: int = None):
    """
       Return all items
    """
    response = "{}"
    if request.method == 'GET':
        id = request.values.get('id')
        Func.Informo("id='"+str(id)+"'", Tipo="l", Section="Items")
        if id is None:
            Func.Informo("id=es None", Tipo="l", Section="Items")
            data = Model.Productos.query
        else:
            data = Model.Productos.query.filter(Model.Productos.id == id)
        QueryDataValue = pd.read_sql(data.statement, Model.db.session.bind.engine)
        if QueryDataValue.shape[0] > 0:
            QueryDataValue["image"] = "http://"+os.environ.get('BACKEND_FLASK_IP_EXTERNAL', "localhost")+":"+os.environ.get('BACKEND_FLASK_PORT', str(8081))+"/api/image?id="+QueryDataValue['id'].astype(str)
            QueryDataValue['datecreated'] = QueryDataValue['datecreated'].dt.strftime('%Y-%m-%d')
            QueryDataValue['datemodified'] = QueryDataValue['datemodified'].dt.strftime('%Y-%m-%d')
        response = jsonify(QueryDataValue.to_dict(orient="records"))
    return response


@app.route('/api/delete', methods=['GET','POST'])
def delete(id: int = None):
    Func.MuestraEnvios(request, "delete")
    if id is None:
        id = request.get_json()
    if id is None:
        return Model.db.app.response_class(response=json.dumps({"Error": "ID NOT specified"}), status=200, mimetype='application/json')
    id=id['id']
    Func.Informo("id='"+str(id)+"'", Tipo="l", Section="delete")
    data = Model.Productos.query.with_entities(Model.Productos.imagename).filter(Model.Productos.id == int(id)).first()
    if data is not None:
        Fichero = os.path.join('./static/images/'+data[0]+'.png')
        if os.path.exists(Fichero): os.remove(Fichero)
        Model.Productos.query.filter(Model.Productos.id == int(id)).delete()
        Model.db.session.commit()
    response = Model.db.app.response_class(response=json.dumps({"Action": "Deleted"}), status=200, mimetype='application/json')
    return response


@app.route('/api/add', methods=['GET','POST'])
def add(Producto: dict = None):
    Func.MuestraEnvios(request, "add")
    if Producto is None:
        Func.MuestraEnvios(request, "add")
        Producto = request.get_json()
    Func.Informo("Producto='"+str(Producto)+"'", Tipo="l", Section="add")
    if Producto is not None and len(Producto) > 0:
        if 'id' in Producto.keys():
            data = Model.Productos.query.with_entities(Model.Productos.id).filter(Model.Productos.id == int(Producto['id'])).first()
            if data is not None:
                return Model.db.app.response_class(response=json.dumps({"Error": "ID Exist"}), status=200, mimetype='application/json')
        if "image" in Producto.keys() and type(Producto["image"]) is str and Producto["image"]!='':
            Func.Base64ImageToLocalFile(Producto["image"],Producto['imagename'])
            del(Producto["image"])
        elif "image" in Producto.keys():
            del(Producto["image"])
            del(Producto['imagename'])
        if "datecreated" in Producto.keys(): Producto["datecreated"]=Func.ProcessPostedDateToString(Producto["datecreated"])
        if "datemodified" in Producto.keys(): Producto["datemodified"]=Func.ProcessPostedDateToString(Producto["datemodified"])
        Nuevo = Model.Productos(**Producto)
        Model.db.session.add(Nuevo)
        Model.db.session.commit()
        response = Model.db.app.response_class(response=json.dumps({"Action": "add"}), status=200, mimetype='application/json')
    else:
        response = "{}"
    return response


@app.route('/api/update', methods=['GET','POST'])
def update(Producto: dict = None):
    Func.MuestraEnvios(request, "update")
    if Producto is None:
        Func.MuestraEnvios(request, "update")
        Producto = request.get_json()
    Func.Informo("Producto='"+str(Producto)+"'", Tipo="l", Section="update")
    if Producto is not None and len(Producto) > 0:
        data = Model.Productos.query.with_entities(Model.Productos.id).filter(
            Model.Productos.id == int(Producto['id'])).first()
        if data is not None:
            if "image" in Producto.keys() and type(Producto["image"]) is str and Producto["image"]!='':
                Func.Base64ImageToLocalFile(Producto["image"],Producto['imagename'])
                del(Producto["image"])
            elif "image" in Producto.keys():
                del(Producto["image"])
                del(Producto['imagename'])
            if "datecreated" in Producto.keys(): Producto["datecreated"]=Func.ProcessPostedDateToString(Producto["datecreated"])
            if "datemodified" in Producto.keys(): Producto["datemodified"]=Func.ProcessPostedDateToString(Producto["datemodified"])
            Model.Productos.query.filter(Model.Productos.id == int(Producto['id'])).update(Producto)
            Model.db.session.commit()
        response = Model.db.app.response_class(response=json.dumps({"Action": "update"}), status=200, mimetype='application/json')
    else:
        response = "{}"
    return response


@app.route('/api/image', methods=['GET', 'POST'])
def image(id: int = None, image: str = None):
    Func.MuestraEnvios(request, "image")
    response = "{}"

    if request.method == 'GET':
        if id is None:
            id = request.values.get('id')
        if id is None:
            return Model.db.app.response_class(response=json.dumps({"Error": "ID NOT specified"}), status=200, mimetype='application/json')
        
        data = Model.Productos.query.with_entities(Model.Productos.imagename).filter(Model.Productos.id == str(id)).first()
        if data is not None and data[0] is not None:
            Fichero = os.path.join('./static/images/'+data[0].rsplit('.', 1)[0]+'.png')
            if os.path.exists(Fichero):
                Func.Informo("Fichero='"+str(Fichero)+"' Existe",Tipo="l",Section="image")
                with open(Fichero, 'rb') as image_file:
                    return send_file(io.BytesIO(image_file.read()),
                                     attachment_filename=data[0].rsplit('.', 1)[0]+".png",
                                     mimetype='image/png')
                return Model.db.app.response_class(data['imagename'], mimetype='image/png')
        
        Fichero = os.path.join('./static/images/noimage.png')
        # Func.Informo("Fichero='"+str(Fichero)+"'",Tipo="l",Section="image")
        extension = Fichero.split(".")[-1]
        with open(Fichero, 'rb') as image_file:
            return send_file(io.BytesIO(image_file.read()), attachment_filename="noimage.png", mimetype='image/'+extension.lower())
        
    return response

@app.route('/api/exist', methods=['GET','POST'])
def exist(id: int = None):
    if request.method == 'POST':
        Posted = dict()
        if image is not None and id is not None:
            Posted['id'] = id
        else:
            Posted = request.get_json()
            
        if "id" not in Posted.keys():
            return Model.db.app.response_class(response=json.dumps({"Error": "ID NOT specified"}), status=200, mimetype='application/json')
        id=id['id']
        data = Model.Productos.query.with_entities(Model.Productos.id).filter(Model.Productos.id == int(id)).first()
        if data is not None:
            return Model.db.app.response_class(response=json.dumps({"Exist": True}), status=200, mimetype='application/json')
        else:
            return Model.db.app.response_class(response=json.dumps({"Exist": False}), status=200, mimetype='application/json')
        
    return "{}"
    
# Errors
@app.errorhandler(403)
def access_forbidden(error):
    Func.Informo("403", Tipo="e", Section="unauthorized_handler")
    return render_template('page-403.html'), 403


@app.errorhandler(404)
def not_found_error(error):
    Func.Informo("404", Tipo="e", Section="unauthorized_handler")
    return render_template('page-404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    Func.Informo("500", Tipo="e", Section="unauthorized_handler")
    return render_template('page-500.html'), 500


if __name__ == "__main__":
    app.run(host=os.environ.get('MERCADONA_FLASK_IP', "0.0.0.0"),
            port=int(os.environ.get('MERCADONA_FLASK_PORT', 8081)),
            threaded=True)

# https://l-lin.github.io/angular-datatables/#/basic/server-side-angular-way

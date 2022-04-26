#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 00:12:22 2022

@author: eusebio
"""
import pandas as pd
from flask import request
from user_agents import parse
import os,io,re,sys,inspect,linecache,ipaddress,base64,datetime
from urllib.parse import unquote
import model as Model
import functions as Func
from PIL import Image

###############################################
###############################################
#######         Funciones Generales 
###############################################
###############################################
#######      Depuro Impresiones o Errores
###############################################
###############################################

def SelectColor(Color='white'):
    if type(Color) is not str:
        return '\033[0m'  # white (normal)
    Color=Color.lower()
    if   Color in ['green','verde']: return '\033[32m' # green
    elif Color in ['red','rojo']: return '\033[31m' # red
    elif Color in ['orange','naranja']: return '\033[33m' # orange
    elif Color in ['blue','azul']: return '\033[34m' # blue
    elif Color in ['cyan','cian']: return '\033[36m' # Cyan
    elif Color in ['purple','purpura']: return '\033[35m' # purple
    elif Color in ['gray','dark gray','darkgray','gris','gris ligero','grisligero']: return '\033[30m' # Dark Gray
    elif Color in ['light gray','lightgray','light','ligero','gris ligero','gris ligero']: return '\033[37m' # Light Gray
    elif Color in ['white','blanco','normal']: return '\033[0m'  # white (normal)
    else: return '\033[0m'  # white (normal)
    
def Informo(Text,Section=None,Tipo="l",Class=None,Function=None,Color=None):
    
    LogLevel=["Error","Warning","Log"]
    UserLog=[]#["eusebiomarques"]
    
    if Tipo[0].lower()=="e":
        Tipo="error"
    elif Tipo[0].lower()=="w":
        Tipo="warning"
    else:
        Tipo="log"
    
    Tipo=Tipo.capitalize()
    exc_type, exc_obj, tb = sys.exc_info()
    
    if Function is None:
        try:
            Function=inspect.stack()[1][3]
        except:
            Class="NULO"
    
    if Class is None:
        try:
            Class=inspect.stack()[2][3]
        except:
            Class="NULO"
    
    RutasCodigo=list()
    try:
        for Linea in range(len(inspect.stack())):
            RutasCodigo.append(inspect.stack()[Linea].function)
        RutasCodigo=",".join(RutasCodigo)
    except:
        pass
    
    Cabezeras = ProcesaCabezeras()
    
    if tb!=None:
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        Tipo="Error"
        
        TextoPrint=str(Text)+"--> EXCEPTION IN ("+str(filename)+", LINE "+str(lineno)+" "+str(line.strip())+"): "
        FileName= str(os.path.sep).join(str(filename).split(os.path.sep)[-3:])
        
        DatosError={'FileName':str(FileName),'LineNumber': str(lineno),'Line':str(line.strip())}
            
    else:
        TextoPrint=str(Text)
        DatosError=dict()
    
    Datos={'Type':str(Tipo),"Class":str(Class),"Function":str(Function),"Section":str(Section),"RutasCodigo":str(RutasCodigo),"Content":str(Text),
           'IpAddress':Cabezeras['IpAddress'],'Agent':Cabezeras['Agent'],'Browser':Cabezeras['Browser'],'BrowserVersion':Cabezeras['BrowserVersion'],
           'OperatingSystem':Cabezeras['OperatingSystem'],'OperatingSystemVersion':Cabezeras['OperatingSystemVersion']}
        
    Datos.update({"authenticated":None,"username":None})
    Datos.update(DatosError)
    
    if "gunicorn" not in os.environ.get("SERVER_SOFTWARE", ""):
        Texto=str(Tipo)+"::"+str(Section)+"::"+str(TextoPrint)
        if Color is not None:
            Texto=SelectColor(Color)+Texto+SelectColor()
        print(Texto, flush=True, file=sys.stdout)
    
    # if Tipo=="Error" or Tipo in LogLevel:
    #     contact = Model.DebugTable(**Datos)
    #     Model.db.session.add(contact)
    #     Model.db.session.commit()
    
    return None

def MuestraEnvios(request,Section,ShowDicts=False):
    try:
        Func.Informo("request='"+str(request)+"'",Tipo="l",Section=Section)
    except:
        Func.Informo("Sin request",Tipo="l",Section=Section)
        pass
    try:
        Func.Informo("json='"+str(request.get_json())+"'",Tipo="l",Section=Section)
    except:
        Func.Informo("Sin json",Tipo="l",Section=Section)
        pass
    try:
        Func.Informo("values='"+str(request.values.to_dict())+"'",Tipo="l",Section=Section)
    except:
        Func.Informo("Sin Values",Tipo="l",Section=Section)
        pass
    try:
        Func.Informo("get_data='"+str(request.get_data())+"'",Tipo="l",Section=Section) # fotos
    except:
        Func.Informo("Sin get_data",Tipo="l",Section=Section)
        pass
    try:
        Func.Informo("form='"+str(request.form.to_dict())+"'",Tipo="l",Section=Section)
    except:
        Func.Informo("Sin form",Tipo="l",Section=Section)
        pass


def Base64ImageToLocalFile(ImageBase64,Destino,Formato="PNG"):
    try:
        if os.path.sep not in Destino:
            Destino = os.path.join('./static/images/'+Destino.rsplit('.', 1)[0]+'.png')
        
        Match=re.match("^data:image\/[a-z]+;base64,", ImageBase64.lower())
        if Match is not None:
            Pos=Match.span()[1]
            Func.Informo("Head of base64 Removed='"+str(ImageBase64[:Pos])+"'",Tipo="l",Section="ProcessBase64Image")
            ImageBase64=ImageBase64[Pos:]
            
        if os.path.exists(Destino): os.remove(Destino)
        
        image = Image.open(io.BytesIO(base64.b64decode(ImageBase64)))
        image.save(Destino, format=Formato)
        
        Func.Informo("Saved Image in ='"+str(Destino)+"'",Tipo="l",Section="Base64ImageToLocalFile")
        
    except:
        return False
        pass
    return True

def FinalMayorInicio(Inicio=None,Fin=None):
    
    if type(Inicio) is str:
        Inicio=FechaToDatetime(Inicio,OnlyDate=False)
    elif type(Inicio) is datetime.datetime:     # no hago nada es lo que quiero
        Inicio=Inicio
    elif type(Inicio) is datetime.date:
        Inicio=datetime.datetime(year=Inicio.year, month=Inicio.month,day=Inicio.day)
    elif type(Inicio) is pd.Timestamp:
        Inicio=FechaToDatetime(Inicio.strftime('%Y-%m-%d %H:%M:%S'),OnlyDate=False)
    else:
        print("FinalMayorInicio::>>Error de tipo Inicio")
    
    if type(Fin) is str:
        Fin=FechaToDatetime(Fin,OnlyDate=False)
    elif type(Fin) is datetime.datetime:     # no hago nada es lo que quiero
        Fin=Fin
    elif type(Fin) is datetime.date:
        Fin=datetime.datetime(year=Fin.year, month=Fin.month,day=Fin.day)
    elif type(Fin) is pd.Timestamp:
        Fin=FechaToDatetime(Fin.strftime('%Y-%m-%d %H:%M:%S'),OnlyDate=False)
    else:
        print("FinalMayorInicio::>>Error de tipo Fin")

    if type(Fin) is datetime.datetime and type(Inicio) is datetime.datetime:
        return Fin>Inicio
    else:
        print("Inicio='"+str(Inicio)+"' typoInicio='"+str(type((Inicio)))+"' Fin='"+str(Fin)+"' typoFIN='"+str(type((Fin)))+"'")
        return False
    
def StrFechaDatetime(Fecha,Year=datetime.datetime.now().strftime('%Y'),OnlyDate=True,DiaEnFinal=False):

    if type(Fecha) is str:
        if "T" in Fecha:
            Troceado=Fecha.split("T")
            if len(Troceado) == 2:
                Date=Troceado[0].strip()
                if "." in Troceado[1]:
                    Time=Troceado[1].strip().split(".")[0]
                else:
                    Time=Troceado[1].strip()
            else:
                print("No puedo Trocear la T fecha '"+str(Fecha)+"'")
        elif ":" in Fecha:
            Troceado=Fecha.split(" ")
            if len(Troceado) == 2:
                Date=Troceado[0].strip()
                Time=Troceado[1].strip()
            else:
                print("No puedo Trocear la : fecha '"+str(Fecha)+"'")
        else:
            Date=Fecha.strip()
            Time=None

        if " " in Date:
            Inicio=StrFechaDatetime(Date.split(" ")[0],Year=Year,OnlyDate=OnlyDate,DiaEnFinal=DiaEnFinal)
            Fin=StrFechaDatetime(Date.split(" ")[1],Year=Year,OnlyDate=OnlyDate,DiaEnFinal=DiaEnFinal)
            if FinalMayorInicio(Inicio,Fin):
                return (Inicio,Fin)
            else:
                return (Fin,Inicio)
        elif "/" in Date:
            Troceado=Date.split("/")
        elif "-" in Date:
            Troceado=Date.split("-")
        elif "_" in Date:
            Troceado=Date.split("_")        
        else:
            print("No puedo Trocear la fecha '"+str(Fecha)+"'")
            return None
        
        if len(Troceado)==3:
            if len(Troceado[0])==4:
                FechaSalida=datetime.datetime(int(Troceado[0]),int(Troceado[1]),int(Troceado[2]),0,0,0)
            else:
                FechaSalida=datetime.date(int(Troceado[2]),int(Troceado[1]),int(Troceado[0]))
        else:
            if int(Troceado[0])>2000:
                FechaSalida=datetime.datetime(int(Troceado[0]),int(Troceado[1]),1,0,0,0)
            else:
                if DiaEnFinal or int(Troceado[1])>12:
                    FechaSalida=datetime.datetime(int(Year),int(Troceado[0]),int(Troceado[1]),0,0,0)
                else:
                    FechaSalida=datetime.datetime(int(Year),int(Troceado[1]),int(Troceado[0]),0,0,0)
            
        if OnlyDate and type(FechaSalida) is not datetime.date: FechaSalida=FechaSalida.date()
                
        if  not OnlyDate and Time is not None:
            Troceado=Time.split(":")
            FechaSalida=FechaSalida.replace(hour=int(Troceado[0]), minute=int(Troceado[1]), second=int(Troceado[2]))
            return FechaSalida
        else:
            return FechaSalida
    else:
        return None

def FechaToDatetime(Fecha=datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                    Year=datetime.datetime.now().strftime('%Y'),
                    OnlyDate=True,
                    DiaEnFinal=False):
    
    if type(Fecha) is str:
        if ":" in Fecha:
            Troceado=Fecha.split(" ")
            if len(Troceado) == 4:
                if OnlyDate:
                    Inicio=StrFechaDatetime(Fecha=" ".join(Troceado[:2]),Year=Year,OnlyDate=OnlyDate,DiaEnFinal=DiaEnFinal)
                    Fin=StrFechaDatetime(Fecha=" ".join(Troceado[2:4]),Year=Year,OnlyDate=OnlyDate,DiaEnFinal=DiaEnFinal)
                    if FinalMayorInicio(Inicio,Fin):
                        return (Inicio,Fin)
                    else:
                        return (Fin,Inicio)
        
        FechaSalida=StrFechaDatetime(Fecha=Fecha,Year=Year,OnlyDate=OnlyDate,DiaEnFinal=DiaEnFinal)
        
        return FechaSalida
    
    elif type(Fecha) is datetime.datetime:
        if OnlyDate:
            return Fecha.date()
        else:
            return Fecha
    elif type(Fecha) is datetime.date:
        return Fecha
    elif type(Fecha) is pd.Timestamp:
        return FechaToDatetime(str(Fecha).split()[0])
    
    return None

#if False:
    # id=1
    # Producto={"datecreated": '2022-04-01', 'datemodified': '2022-04-02'}
    # Model.Productos.query.filter(Model.Productos.id == id).update(Producto)
    # Model.db.session.commit()
    
    # Response=Model.Productos.query.filter(Model.Productos.id == id).all()[0]
    # Response.datecreated
    # Response.datemodified

def ProcessPostedDateToString(DatePosted,OnlyDate=True):
    DateOut = None
    if type(DatePosted) is datetime.datetime or type(DatePosted) is datetime.date:
        if OnlyDate:
            DateOut=DatePosted.strftime('%Y-%m-%d')
        else:
            DateOut=DatePosted.strftime('%Y-%m-%d %H:%M:%S')
    elif type(DatePosted) is str:
        if OnlyDate:
            DateOut=FechaToDatetime(DatePosted,OnlyDate=True).strftime('%Y-%m-%d')
        else:
            DateOut=FechaToDatetime(DatePosted,OnlyDate=True).strftime('%Y-%m-%d %H:%M:%S')
    
    return DateOut

def ProcessBase64Image(ImageBase64,Formato="PNG"):
    
    # if False:
    #     import base64,re,unidecode
    #     from PIL import Image
    #     Formato="PNG"
    #     Fichero=os.path.join('./static/images/noimage.png')
    #     ImageBase64=Image.open(Fichero)
    #     Format=ImageBase64.format.lower()
    #     ImageBase64.show()
    #     with open(Fichero, 'rb') as image_file:
    #         ImageBin=image_file.read()
    #     ImageBase64=base64.b64encode(ImageBin).decode('utf-8')
    #     ImageBase64 = str("data:image/"+Format+";base64,")+ImageBase64
    #     print(str(type(ImageBase64)))
    #     ImageBase64[:50]
            
    Match=re.match("^data:image\/[a-z]+;base64,", ImageBase64.lower())
    if Match is not None:
        Pos=Match.span()[1]
        Func.Informo("Head of base64 Removed='"+str(ImageBase64[:Pos])+"'",Tipo="l",Section="ProcessBase64Image")
        ImageBase64=ImageBase64[Pos:]
    
    image = Image.open(io.BytesIO(base64.b64decode(ImageBase64)))
    with io.BytesIO() as output:
        image.save(output, format=Formato)
        contents = output.getvalue()
    
    Func.Informo("contentsType='"+str(type(contents))+"'",Tipo="l",Section="ProcessBase64Image")
    
    return contents

# bytes.fromhex(contents)
# Nuevo = Model.Productos(id=5,image=contents)
# contens=psycopg2.Binary(ImageBase64)
# Nuevo = Model.Productos(id=5,image=io.BytesIO(image_file.read())})
# Nuevo = Model.Productos(**{"id":5,"image":bytes(ImageBase64,"utf-8")})
# Nuevo = Model.Productos(**{"id":5,"image":unidecode.unidecode(str("data:image/"+Format+";base64,")+base64.b64encode(ImageBin).decode('utf-8'),"utf-8")})
# Model.db.session.add(Nuevo)
# Model.db.session.commit()
# Model.db.session.rollback()
# import psycopg2
# psycopg2.Binary(ImageBase64)

# with open(Fichero, 'rb') as image_file:
#     contents = io.BytesIO(image_file.read())
#     Nuevo = Model.Productos(id=5,image=contents)
#     Model.db.session.add(Nuevo)
#     Model.db.session.commit()
    
###############################################
###############################################
#######           Funciones Flask
###############################################
###############################################
#######          Extraigo los Post
###############################################
###############################################
    
def ProcesaPost(Modelo,Posted=None,Requested=None,Remove=[],FillEmptyColumns=True,Debug=True):
    
    if Debug: print("Posted='"+str(Posted)+"' Requested='"+str(Requested)+"' Requested='"+str(dir(Requested))+"'", flush=True, file=sys.stdout)
    
    PostedLocal=dict()
    
    try:
        if Debug: print(request.get_json(), flush=True, file=sys.stdout)
        PostedLocal.update(request.get_json())
    except:
        pass
    
    if Remove is None:
        Remove=list()
    elif type(Remove) is str:
        Remove=[Remove]
        
    if Posted is None and Requested is None:
        print("Error::ProcesaPost:: Posted y Requested no pueden ser Nulos", flush=True, file=sys.stdout)
        return None
    
    if Posted is not None and type(Posted) is not dict:
        PostedLocal.update(Posted.form.to_dict())
    
    if Requested is not None and type(Requested) is not dict:
        PostedLocal.update(Requested.form.to_dict())
    
    Datos=dict()
    for SendedKey in PostedLocal:
        key=SendedKey
        Tabla=EncuentraParametro(Modelo,key)
        
        if Debug: print("key='"+str(key)+"' key='"+str(key)+"'", flush=True, file=sys.stdout)
        
        if Tabla is None and "_" in key:
            key=key.split("_")[-1]
            Tabla=EncuentraParametro(Modelo,key)
        
        if Tabla is not None and key not in Datos.keys():
            valor=PostedLocal[SendedKey]
            if Debug: print("key='"+str(key)+"' Type='"+str(type(valor))+"'", flush=True, file=sys.stdout)
            if type(valor) is bytes:
                if Debug: print("key='"+str(key)+"' es bytes", flush=True, file=sys.stdout)
                valor=valor.decode('utf-8')
            if valor is not None:
                if "varchar" in str(Tabla.type).lower():
                    LengthStr=re.findall(r'\d+', str(Tabla.type))
                    Length=int(LengthStr[0])
                    Datos.update({key:valor[:Length]})
                elif "text" in str(Tabla.type).lower():
                    Datos.update({key:valor.replace("\r\n\t\t\t\t","").replace("\t","")})
                elif "int" in str(Tabla.type).lower():
                    if type(valor) is str:
                        if valor != '':
                            valor=re.findall(r'[-+]?\d+', valor)
                            valor=int(valor[0])
                            Datos.update({key:valor})
                        else:
                            if Tabla.expression.nullable:
                                valor=None
                                Datos.update({key:valor})
                elif "float" in str(Tabla.type).lower():
                    if type(valor) is str:
                        if valor != '':
                            valor=re.findall(r'[-+]?\d*\.\d+|\d+', valor)
                            valor=float(valor[0])
                            Datos.update({key:valor})
                        else:
                            if Tabla.expression.nullable:
                                valor=None
                                Datos.update({key:valor})
                elif "decimal" in str(Tabla.type).lower():
                    if type(valor) is str:
                        if valor != '':
                            valor=re.findall(r'[-+]?\d*\.\d+|\d+', valor)
                            valor=float(valor[0])
                            Datos.update({key:valor})
                        else:
                            if Tabla.expression.nullable:
                                valor=None
                                Datos.update({key:valor})
                elif "boolean" in str(Tabla.type).lower():
                    if type(valor) is str:
                        if valor.lower() in ['false','off']:
                            Datos.update({key:0})
                        elif valor.lower() in ['checked','true','on']:
                            Datos.update({key:1})
                        else:
                            print("ProcesaPost:Tipo boolean Con Valor Desconocido '"+str(valor)+"'", flush=True, file=sys.stdout)
                    else:
                        Datos.update({key:valor})
                elif "datetime" in str(Tabla.type).lower():
                    Datos.update({key:valor})
                else:
                    if Debug: print("ProcesaPost:Tipo='"+str(Tabla.type)+"' no Tenido en cuenta", flush=True, file=sys.stdout)
                    Datos.update({key:valor})
    
    if FillEmptyColumns:
        Tablas=[Tabla.name for Tabla in Modelo.__table__.columns if not (("autoincrement" in dir(Tabla) and Tabla.autoincrement == True) or Tabla.name in ["datecreated","datemodified","datedeleted","datedisabled","daterate"])]
        EmptyColumns=set(Tablas)-set(list(Datos.keys())+["datecreated","datemodified","datedeleted","datedisabled","daterate"])
    
        for EmptyColumn in EmptyColumns:
            Tabla=Func.EncuentraParametro(Modelo,EmptyColumn)
            if Tabla is not None and EmptyColumn not in Remove:
                if "boolean" in str(Tabla.type).lower():
                    Datos.update({EmptyColumn:False})
                elif Tabla.expression.nullable:
                    Datos.update({EmptyColumn:None})

    return Datos


###############################################
###############################################
#######            Funciones Flask
###############################################
###############################################
#######    Busco Parametro en los Modelos
###############################################
###############################################

def EncuentraParametro(Datos=None,Busca=None,Valor=None,Debug=False):
        
    if Datos is None or Busca is None:
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        Func.Informo("Necesito Datos y que Buscar ("+str(caller.lineno)+") '"+str(caller)+"' '"+str(caller.flename)+"'",Tipo="l",Section="EncuentraParametro")
        return None        

    if type(Datos) is not list:
        Datos=[Datos]
    
    if type(Busca) is not list:
        Busca=[Busca]

    for Dato in Datos:
        for Busc in Busca:
            if Debug:
                Func.Informo("EncuentraParametro::Busc='"+str(Busc)+"' TypeBusc='"+str(type(Busc))+"' Dato='"+str(Dato)+"' TypeDato='"+str(type(Dato))+"'",Tipo="l",Section="EncuentraParametro")
            if "model" in str(type(Dato)):
                if type(Busc) is str or type(Busc) is dict:
                    if type(Busc) is dict:
                        Bus=list(Busc.keys())[0]
                    else:
                        Bus=Busc
                    for Item in Dato.__dict__.keys():
                        Columna=Dato.__getattribute__(Dato,Item)
                        #if Debug: print("Item='"+str(type(Item))+"' Columna='"+str(type(Columna))+"'", flush=True, file=sys.stdout)
                        if "Attribute" in str(type(Columna)) and Bus.lower() in [Columna.expression.key.lower(),Item.lower()]:
                            if type(Busc) is dict:
                                print("model::Bus='"+Busc[Bus]+"'")
                                return Columna.label(Busc[Bus])
                            else:
                                return Columna
                elif "model" in str(type(Busc)):
                    return True if Busc.__name__==Dato.__name__ else None
                elif  "attributes" in str(type(Busc)):
                    if Busc.expression.table.key==Dato.__name__:
                        return True  
                    else:
                        return None
                elif  "Label" in str(type(Busc)):
                    Childrens=Busc.get_children()
                    if len(Childrens)>0:
                        return True if Childrens[0].table.name==Dato.__name__ else None
                    else:
                        return None
                else:
                    if Debug: Func.Informo("modelo Dato pero Busca='"+str(Busca)+"' TypeBusc='"+str(type(Busc))+"' no Contemplado",Tipo="e",Section="EncuentraParametro")

            elif "attributes" in str(type(Dato)):
                if type(Busc) is str or type(Busc) is dict:
                    if type(Busc) is dict:
                        Bus=list(Busc.keys())[0]
                    else:
                        Bus=Busc
                    if Bus.lower() in [Dato.key.lower(),Dato.expression.name.lower()]:
                        if type(Busc) is dict:
                            print("attributes::Bus='"+Busc[Bus]+"'")
                            return Dato.label(Busc[Bus])
                        else:
                            return Dato
                elif "model" in str(type(Busc)):
                    return True if Busc.__name__==Dato.expression.table.key else None
                elif "attributes" in str(type(Busc)):
                    return True if Busc.expression.table.key==Dato.expression.table.key else None
                elif  "Label" in str(type(Busc)):
                    Childrens=Busc.get_children()
                    if len(Childrens)>0:
                        return True if Childrens[0].table.name==Dato.expression.table.key else None
                    else:
                        return None
                else:
                    if Debug: Func.Informo("attributes Dato pero Busca='"+str(Busca)+"' TypeBusc='"+str(type(Busc))+"' no Contemplado",Tipo="e",Section="EncuentraParametro")

            elif "Label" in str(type(Dato)):
                if type(Busc) is str:
                    if Busc.lower() in [Dato.key.lower(),Dato.expression.name.lower()]:
                        return Dato
                elif "model" in str(type(Busc)):
                    Childrens=Dato.get_children()
                    return True if Childrens[0].table.name==Busc.__name__ else None
                elif "attributes" in str(type(Busc)):
                    Childrens=Dato.get_children()
                    return True if Childrens[0].table.name==Busc.expression.table.key else None
                elif  "Label" in str(type(Busc)):
                    ChildrensDato=Dato.get_children()
                    ChildrensBusc=Busc.get_children()
                    if len(ChildrensBusc)>0 and len(ChildrensDato)>0:
                        return True if ChildrensBusc[0].table.name==ChildrensDato[0].table.name else None
                    else:
                        return None
                else:
                    if Debug: Func.Informo("Label Dato pero Busca='"+str(Busca)+"' TypeBusc='"+str(type(Busc))+"' no Contemplado",Tipo="e",Section="EncuentraParametro")

            elif type(Dato) is dict:
                if Busc.lower() in [x.lower() for x in Dato.keys()]:
                    diccionario=dict(zip(map(lambda x:x.lower(),Dato.keys()), Dato.keys()))
                    if Busc.lower() in diccionario.keys():
                        if Valor is not None:
                            return Dato[diccionario[Busc.lower()]][Valor]
                        else:
                            return Dato[diccionario[Busc.lower()]]
            elif type(Dato) is list:
                #este fastidia 
                for Dat in Dato:
                    if type(Dat) is str:
                        if Busc.lower() == Dat.lower():
                            return True
                    elif "attributes" in str(type(Dat)):
                        if type(Busc) is str:
                            if Busc.lower() in [Dat.key.lower(),Dat.expression.name.lower(),Dat.expression.key.lower()]:
                                return Dat
                        elif "model" in str(type(Busc)):
                            return True if Busc.__name__==Dat.expression.table.key else None
                        elif "attributes" in str(type(Busc)):
                            return True if Busc.expression.table.key==Dat.expression.table.key else None
                        elif  "Label" in str(type(Busc)):
                            Childrens=Busc.get_children()
                            if len(Childrens)>0:
                                return True if Childrens[0].table.name==Dat.expression.table.key else None
                            else:
                                return None
                        else:
                            if Debug: Func.Informo("attributes Dat pero Busca='"+str(Busca)+"' TypeBusc='"+str(type(Busc))+"' no Contemplado",Tipo="e",Section="EncuentraParametro")
        
                    elif "Label" in str(type(Dat)):
                        if type(Busc) is str:
                            if Busc.lower() in [Dat.key.lower(),Dat.expression.name.lower(),Dat.expression.element.key.lower()]:
                                return Dat
                        elif "model" in str(type(Busc)):
                            Childrens=Dat.get_children()
                            return True if Childrens[0].table.name==Busc.__name__ else None
                        elif "attributes" in str(type(Busc)):
                            Childrens=Dat.get_children()
                            return True if Childrens[0].table.name==Busc.expression.table.key else None
                        elif  "Label" in str(type(Busc)):
                            ChildrensDato=Dat.get_children()
                            ChildrensBusc=Busc.get_children()
                            if len(ChildrensBusc)>0 and len(ChildrensDato)>0:
                                return True if ChildrensBusc[0].table.name==ChildrensDato[0].table.name else None
                            else:
                                return None
                        else:
                            if Debug: Func.Informo("Label Dat pero Busca='"+str(Busca)+"' TypeBusc='"+str(type(Busc))+"' no Contemplado",Tipo="e",Section="EncuentraParametro")

            elif type(Dato) is str:
                if Busc.lower() == Dato.lower():
                    return True
                
    if Debug: print("EncuentraParametro::en Datos no hay Buscar='"+str(Busca)+"' typeDatos='"+str(type(Datos))+"' ", flush=True, file=sys.stdout)
    return None

###############################################
###############################################
#######           Funciones En Redes
###############################################
###############################################
#######        Es Cliente Local o No?
###############################################
###############################################

def IsClienteLocal():
    RealIp = request.remote_addr
    #print("IsClienteLocal::'"+str(RealIp)+"'")
    if ipaddress.ip_address(RealIp) in ipaddress.ip_network('192.168.0.0/23'):
        return True
    else:
        return False
    
###############################################
###############################################
#######           Funciones En Redes
###############################################
###############################################
#######       Extraigo Las Cabezeras del
#######              User-Agent
###############################################
###############################################

def ProcesaCabezeras():
    try:
        UserAgent = parse(request.headers.get('User-Agent'))
        
        if request.headers.getlist("X-Forwarded-For"):
           ip = request.headers.getlist("X-Forwarded-For")[0]
        else:
           ip = request.remote_addr
        
        Datos=dict({'IpAddress':ip, \
                    'Agent':request.headers.get('User-Agent'), \
                    'LocalIP': True if IsClienteLocal() else False, \
                    'Mobil': True if request.MOBILE else False, \
                    'Browser':UserAgent.browser.family if UserAgent is not None else None, \
                    'BrowserVersion':UserAgent.browser.version_string if UserAgent is not None else None, \
                    'OperatingSystem':UserAgent.os.family if UserAgent is not None else None, \
                    'OperatingSystemVersion':UserAgent.os.version_string if UserAgent is not None else None, \
                    'DeviceProperties':UserAgent.device.family if UserAgent is not None else None, \
                    'DevicePropertiesBrand':UserAgent.device.brand if UserAgent is not None else None, \
                    'DevicePropertiesModel':UserAgent.device.model if UserAgent is not None else None})
        
        #print("ProcesaCabezeras::request='"+str(list(dir(request)))+"'", flush=True, file=sys.stdout)
            
        if "form" in list(dir(request)) and 'username' in request.form.keys():
            Datos.update({'username':request.form['username']})
            
        if "form" in list(dir(request)) and 'password' in request.form.keys():
            Datos.update({'password':request.form['password']})
        
        return Datos
    except:
        #Informo(e,Tipo="e",Section="ProcesaCabezeras")
        return dict({'IpAddress':None, \
                    'Agent':None, \
                    'LocalIP':None, \
                    'Mobil':None, \
                    'Browser':None, \
                    'BrowserVersion':None, \
                    'OperatingSystem':None, \
                    'OperatingSystemVersion':None, \
                    'DeviceProperties':None, \
                    'DevicePropertiesBrand':None, \
                    'DevicePropertiesModel':None})

def ProcesaVariables(Requested,Variables=["page","length"],CaseSensitive=False):
    
    PasoDatos=dict()
    RequestedVariables={**Requested.args.to_dict(),**Requested.values.to_dict()}
    RequestedVariablesLower=dict(zip([x.lower() for x in RequestedVariables.keys()],RequestedVariables.keys()))
    
    if Variables is not None and ((type(Variables) is str and Variables.lower() == "all") or (type(Variables) is list and Variables[0].lower() == "all")):
        Variables=list(set(list(Requested.args.to_dict().keys())+list(Requested.values.to_dict().keys())))
    
    for Variable in Variables:
        VariableLower=Variable.lower()
        if VariableLower in RequestedVariablesLower.keys():
            PasoDatos[Variable]=unquote(RequestedVariables[RequestedVariablesLower[VariableLower]])
        else:
            PasoDatos[Variable]=None

    return PasoDatos
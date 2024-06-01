from fastapi import FastAPI  
from pydantic import BaseModel 
from typing import Optional
from contextlib import closing
import sqlite3
from fastapi.middleware.cors import CORSMiddleware


appA = FastAPI()
 


# Configurar CORS
appA.add_middleware(
    CORSMiddleware,
    allow_origins=["https://agustin2999.github.io"],  # o "*", si deseas permitir desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



 



# esto del arroba es importante, le decimos: cuando vayas a home, ejecuta index()
@appA.get("/")
def index():
    return {"mensage" : "Hola"}


# Para levantar el servidor tenemos que usar  uvicorn xxxxxx --reload (con env)
# reload para que se mantenga siempre escuchando

# fastapi automatico te lo convierte en json

# Fastapi crea la documentacion automaticamente: /docs



#sirve para validar que los tipos de datos sean los siguientes:
class Message(BaseModel):
    sender: str
    receiver: str
    message: str
    time: float
    timeNormalizado: str   

class Post(BaseModel):
    id: int = 0 #por defecto será 0
    urlImage: str = ""
    username: str = ""
    post: str = ""
    like: int = 0
    numLikes: int = 0 
    dislike: int = 0
    numDislikes: int = 0
    date: float = 0






# Spidder
@appA.post("/spidderinsertmessage")
def spidderInsertMessage(objMsg : Message):
    try:
        
        miConexion = sqlite3.connect("apiagustin")
       
        with closing(miConexion) as connection:
            miCursor = miConexion.cursor()
            miCursor.execute("INSERT INTO spiddermsg (sender, receiver, message, time, timeNormalizado) VALUES (?, ?, ?, ?, ?)",
                        (objMsg.sender, objMsg.receiver, objMsg.message, objMsg.time, objMsg.timeNormalizado))
            # La conexión se cerrará automáticamente al salir del bloque 'with'
            miConexion.commit()
               
        return {"Exito": f"Mensaje insertado correctamente"}
    except Exception as error:
        return {"Error al insertar": f"{error}"} 



@appA.get("/spiddergetallmsg")
def spidderGetAllMsg():
    try:
        miConexion = sqlite3.connect("apiagustin")
        
        with closing(miConexion) as connection:
            miCursor = miConexion.cursor()
           
            miCursor.execute("SELECT sender, receiver, message, time, timeNormalizado FROM spiddermsg")
             
            select = miCursor.fetchall()
        
        mensaje = []
        for item in select:
            mensaje.append({
                "sender" : item[0] ,
                "receiver" : item[1] ,
                "message" : item[2] ,
                "time" : item[3] ,
                "timeNormalizado" : item[4] 
            })
        
        return {"Mensajes": mensaje} 
    except Exception as error:
        return {"Error al obtener mensajes": f"{error}"} 



# Nuevo
@appA.get("/spiddergetallposts")
def spidderGetAllPosts():
    try:
        miConexion = sqlite3.connect("apiagustin")
        
        with closing(miConexion) as connection:
            miCursor = miConexion.cursor()
           
            miCursor.execute("SELECT id,urlImage,username,post,like,numLikes,dislike,numDislikes,date FROM spidderposts")
             
            select = miCursor.fetchall()
        
        mensaje = []
        for item in select:
            mensaje.append({
                "id": item[0],
                "urlImage": item[1],
                "username": item[2],
                "post": item[3],
                "like": item[4],
                "numLikes": item[5],
                "dislike": item[6],
                "numDislikes": item[7],
                "date": item[8]
            })
        
        return {"Posts": mensaje} 
    except Exception as error:
        return {"Error al obtener posts": f"{error}"}




@appA.post("/spidderinsertpost")
def spidderInsertPost(objPost : Post):
    try:
        
        miConexion = sqlite3.connect("apiagustin")
       
        with closing(miConexion) as connection:
            miCursor = miConexion.cursor()
            miCursor.execute("INSERT INTO spidderposts (urlImage,username,post,like,numLikes,dislike,numDislikes,date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (objPost.urlImage,objPost.username,objPost.post,objPost.like,objPost.numLikes,
                         objPost.dislike,objPost.numDislikes,objPost.date))
            miConexion.commit()

        # Una vez que insertó, quiero que me devuelva el id que acaba de insertar 
        miConexion = sqlite3.connect("apiagustin")
        with closing(miConexion) as connection:
            miCursor = miConexion.cursor()
            miCursor.execute("SELECT id FROM spidderposts ORDER BY id desc LIMIT 1")
            select = miCursor.fetchall()
                    
        idInsertado = 0
        for item in select:
            idInsertado = item[0]               
            break #para que haga una sola iteracion
         

               
        return {"Exito": f"Post insertado correctamente." ,
                "IdInsertado": idInsertado}
    except Exception as error:
        return {"Error al insertar": f"{error}"} 


 

@appA.post("/spidderupdatepost")
def spidderUpdatePost(objPost : Post):
    try:
        miConexion = sqlite3.connect("apiagustin")
       
        with closing(miConexion) as connection:
            miCursor = miConexion.cursor()
            retorno = miCursor.execute("UPDATE spidderposts SET username= '" + objPost.username + "' , post= '" + 
                             objPost.post + "' , numLikes=" + str(objPost.numLikes) + ", numDislikes=" + str(objPost.numDislikes) + 
                             ", date=" + str(objPost.date) + " WHERE id="+ str(objPost.id))
            
            miConexion.commit()
               
        return {"Exito": "Post id: " + str(objPost.id) + " editado correctamente",
                "Filas afectadas": str(retorno.rowcount)}
    except Exception as error:
        return {"Error al editar": f"{error}"} 


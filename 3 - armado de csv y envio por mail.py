# -*- coding: cp1252 -*-
 
import acceso_arcgis
import postgresql_connection
import datetime
import time
import json
import csv
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from email.mime.base import MIMEBase
from email import encoders
# unicode
# print("\u00E1\u00E9\u00ED\u00F3\u00FA") aeiou con ascentos


# variables_entorno  
mail= "example@gmail.com"
password = 'password'
smtp = 'smtp.abc.com'
port = 1
sqlSelect = "SELECT *"
sqlFrom = "FROM TABLA"
sqlWhere = "WHERE id>8 "
sqlGroupBy = "GROUP BY id "
sqlOrderBy = "ORDER BY id "


def main():

    #mail
    server = smtplib.SMTP_SSL(smtp, port)
    server.login(mail,password)

    # Obtenemos la fecha y hora actual
    now = datetime.datetime.now()
    print("Inicio -resumen de cada mes- : " + str(now))



    # Obtenemos la fecha del primer dia del mes anterior - 1 dia, a las 21:00 hs. Ej: 28feb 21hs
    start_time = (now - datetime.timedelta(days=2)).replace(hour=21, minute=0, second=0, microsecond=0).replace(day=1)- datetime.timedelta(days=1)
    
    # Obtenemos la fecha de ayer a las 21:00 hs
    end_time = (now - datetime.timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
    
     
    print("El start_time es: " + str(start_time) )
    print("El end_time es: " + str(end_time) )

    if(now.day != 1): #si no es el primero de cada mes, que no haga nada
        print("No es primero de mes, no se envia mail")
        exit()

             
    # Borrado de archivo anterior
    print("Borramos csv mes anterior:")
    nombre_archivo_viejo = "datos_mes_anterior" + start_time.strftime("%m-%Y") + ".csv"
    ruta_archivo_viejo = os.path.join(os.path.dirname(__file__), nombre_archivo_viejo)

    if os.path.exists(ruta_archivo_viejo):
        os.remove(ruta_archivo_viejo)
        print(f"El archivo {nombre_archivo_viejo} ha sido eliminado.")
    else:
        # cuando el archivo no existe
        print(f"No se encontro el archivo {nombre_archivo_viejo} para poder borrarlo.")

    


    print('desde: ' + start_time.strftime("%Y-%m-%d %H:%M:%S"))
    print('hasta: ' + end_time.strftime("%Y-%m-%d %H:%M:%S"))

    
    # Obtener registros agrupados por DIA (para todo el mes anterior)
    query = sqlSelect
    query += sqlFrom
    query += sqlWhere
    query += "AND fecha >=  '" + start_time.strftime("%Y-%m-%d %H:%M:%S") + "' "
    query += "AND fecha <  '" + end_time.strftime("%Y-%m-%d %H:%M:%S") + "' "
    query += sqlGroupBy
    query += sqlOrderBy
       

    resumenesSQL = postgresql_connection.execute_select(query)

    
    listaResumenCompleta = []
    for rSQL in resumenesSQL:
                     
        # id	nombre	ciudad pais	cantidad 
        
        resumen = {
            "Fecha": (end_time.strftime("%m-%Y")),#%d-
            "id": str(rSQL[0]),
            "nombre": str(rSQL[1]),
            "ciudad": str(rSQL[2]),
            "pais": str(rSQL[3]),
            "cantidad": str(rSQL[4]).replace('.', ','),
        }

        listaResumenCompleta.append(resumen) # lista de objetos
        
    # Definimos la lista de datos
    datos = listaResumenCompleta
     
    #creo un dataframe con la lista de objetos
    
    df_datos = pd.DataFrame(datos, columns=['Fecha', 'id', 'nombre', 'ciudad', 'pais', 'cantidad'])
    
 
    
    # # print(fecha_ejecucion)
    nombre_archivo ="datos_mes_anterior" + end_time.strftime("%m-%Y") + ".csv"

    # ## Si se cambia el nombre del archivo, se debe cambiar en la funcion de enviar mail para que se adjunte al mail
    df_datos.to_csv(nombre_archivo, index=False,sep=';', encoding='UTF-8', line_terminator='\n' )
     

    
    armar_mail()
            
    recipientCC =  []
    recipient = ["abc@gmail.com"]
   
    send_email(recipient, recipientCC, asuntoMail, htmlMail,nombre_archivo)

    print("Fin -resumen de cada mes- :" + str(datetime.datetime.now()))

   #print(len(listaResumenCompleta))



def armar_mail():
    global htmlMail
    global asuntoMail
     
    asuntoMail = "datos mes anterior"
    htmlMail = """
        <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        </head>

        <body>
        
        <h3>Hola.</h3>

        <h4>Se adjunta al presente correo un archivo con el resumen MENSUAL de datos.<br />
        El resumen esta realizado a partir de los datos registrados durante el mes anterior.</h4>
        
        
        <h4>NO RESPONDER ESTE CORREO, POR CUALQUIER CONSULTA CONTACTARSE A:</h4>

        <h4><br />
        <a href="mailto:abcde@gmail.com" target="_blank">abcde@gmail.com</a><br />
        <br />
        </body>

        </html>
        """

# print (htmlMail)


def send_email(recipient, recipientCC, subject, htmlMail, nombre_archivo):
    
    # Crear el mensaje de correo electronico
    # msg = MIMEMultipart()
    msg = MIMEMultipart('alternative')
    
    msg['From'] = "sender@gmail.com"
    
    msg['To'] = ",".join(recipient)
    
    msg['Cc'] =  ",".join(recipientCC) 

    msg['Subject'] = subject
    msg.attach(MIMEText(htmlMail,'html'))


    filename = nombre_archivo
    attach1 = "./" + nombre_archivo
    attachment = open(attach1, "rb")


    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
 
    msg.attach(part)


    # Enviar el correo electronico
    smtp = smtplib.SMTP_SSL(smtp, port)
     
    smtp.login(mail, password)
    
    smtp.sendmail("Aviso", recipient, msg.as_string())
    print("Mail enviado")
    smtp.quit()

    # print("se finalizo el proceso de enviado")



if (__name__ == "__main__"):
    main()
    


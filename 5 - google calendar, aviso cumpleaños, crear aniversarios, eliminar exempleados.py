import requests
import datetime
from pprint import pprint
import acceso_sistema
import calendar_api
import datetime
from dateutil.relativedelta import relativedelta
from sendEmail import sendEmail
import json



calendarId = 'cvjkhwqiejorpoih34uioph@group.calendar.google.com' 
organizacion_url = 'https://organizacionabc.com/'
service = 'https://servicios.com/tabla5'
username = 'username'
password = 'password'

# https://calendar.google.com/calendar/embed?src=cvjkhwqiejorpoih34uioph%40group.calendar.google.com&ctz=America%2FArgentina%2FCordoba






def main():

       
    print("Start Date: "+ str(datetime.datetime.now()))

    legajoActivos = []
    legajoInactivos = []

    token = acceso_sistema.generate_token(organizacion_url, username, password)

    datosLegajos = acceso_sistema.query(service, token, 
                                                       fields=['fecha_ingreso', 'empleado', 'mail', 'nombre_simple', 'legajo', 'fecha_nacimiento', 'id'])
    

    # Conversion de formato Epoch a Human Date
    for i in datosLegajos:
                       
        if i['attributes']['legajo'] == 'activo':
            i['attributes']['fecha_ingreso_obj'] = datetime.datetime.fromtimestamp(i['attributes']['fecha_ingreso']/1000.0)
            i['attributes']['fecha_ingreso'] = i['attributes']['fecha_ingreso_obj'].strftime('%Y-%m-%d')
            
            if i['attributes']['fecha_nacimiento'] != None:
                timestamp = i['attributes']['fecha_nacimiento']
                if timestamp < 0:
                    i['attributes']['fecha_nacimiento_obj'] = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=i['attributes']['fecha_nacimiento'])
                    i['attributes']['fecha_nacimiento'] = i['attributes']['fecha_nacimiento_obj'].strftime("%Y-%m-%d")
                else:
                    i['attributes']['fecha_nacimiento_obj'] = datetime.datetime.fromtimestamp(i['attributes']['fecha_nacimiento']/1000.0)
                    i['attributes']['fecha_nacimiento'] = i['attributes']['fecha_nacimiento_obj'].strftime("%Y-%m-%d")
            legajoActivos.append(i['attributes'])
        else:
            legajoInactivos.append(i['attributes'])




    # Devuelve una lista con todos los eventos de ese calendario
    print("Obtenemos eventlist")
    eventsList = calendar_api.get_events_of_calendar(calendarId)
    

    
    # -Eliminacion-
        
    # Borrado automatico por legajo inactivo
    for i in legajoInactivos:
            for j in eventsList:
                # print(i['nombre_simple'])
                nameFriendly = i['nombre_simple'].split("_")[1].capitalize() + " " + i['nombre_simple'].split("_")[0].capitalize()             
                if(nameFriendly.lower() in j['summary'].lower()):
                    print("Borrado automatico por legajo inactivo:")
                    calendar_api.delete_event(calendarId, j['id'])  
                    print("Se borró " + j['summary'] + " de " + nameFriendly)
    
    

    # Borrado manual
    # Aca poner el nombre individual de la persona que se desea borrar. 
    nombreABorrar = "VACIO"
    if(nombreABorrar != "VACIO" and nombreABorrar != "" and nombreABorrar != None):
        print("Borrado manual:")
        for j in eventsList:
            if(nombreABorrar.lower() in j['summary'].lower()):
                calendar_api.delete_event(calendarId, j['id'])  
                print("Se borró " + j['summary'] + " de " + nombreABorrar.lower() )
            

    years = relativedelta(years=1)




    
    # -Agregacion-
    for i in legajoActivos:
            

        # Control para los que no tienen fecha de nacimiento
        if i['fecha_nacimiento'] is None:
            print("fecha nacimiento none en " + i['nombre_simple'])
            # exit()
            break


       
        existEvent = False
        summarySinTilde = ""
        
        nameFriendly = i['nombre_simple'].split("_")[1].capitalize() + " " + i['nombre_simple'].split("_")[0].capitalize()  
                 
        for j in eventsList:
            
            summarySinTilde = j['summary'].lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u') 
                        
            if nameFriendly.lower() in summarySinTilde:
                
                existEvent = True #compara si tiene cumpleaños o aniversario
                
            
                
                
            

        if not existEvent : # no tiene, entonces agrega
            
            # Crea cumpleaños: 
            month = i['fecha_nacimiento_obj'].month
            day = i['fecha_nacimiento_obj'].day
            rule_cumpleaños = 'RRULE:FREQ=YEARLY;BYMONTH=' + str(month) + ';BYMONTHDAY=' + str(day)
                        
            createdEvent_birth = calendar_api.create_event(calendarId,'Cumple ' + nameFriendly, i['fecha_nacimiento'], i['fecha_nacimiento'], rule_cumpleaños)
            print('Creado Cumple ' + nameFriendly + " , " + i['fecha_nacimiento'])


            
            

            
            # -Aca se crean los aniversarios (hasta 60 años)- :
            for r in range(1, 60):
                years = relativedelta(years=r)
                date_aniversario = i['fecha_ingreso_obj'] + years
                
                print( "Creado Aniv. " + str(r) + ' '+ nameFriendly + " , " + date_aniversario.strftime("%Y-%m-%d")  )
                createdEvent_aniv = calendar_api.create_event(calendarId,'Aniversario '+ str(r) + ' ' + nameFriendly, date_aniversario.strftime("%Y-%m-%d"), date_aniversario.strftime("%Y-%m-%d"))
            




    # -Aviso de cumpleaños cercano-:
    for i in legajoActivos:
        
        if i['fecha_nacimiento'] is None:
            print("fecha nacimiento none en " + i['nombre_simple'] + " (aviso cumpleaños)")
            break
        
        fecha_nacimiento = i["fecha_nacimiento_obj"].strftime('%m-%d')
        fecha_prox_6_dias = (datetime.datetime.today() + relativedelta(days=6)).strftime('%m-%d')  
       
        
        if fecha_nacimiento == fecha_prox_6_dias : 
            sendEmail(i['mail'], i["nombre_simple"])
            print("Mail enviado a: " + str(i["nombre_simple"]))
        


        
        



    print("End Date: "+ str(datetime.datetime.now()) + "\n")







if __name__ == '__main__': 
    main()

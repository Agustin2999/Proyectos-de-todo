import acceso_sistema
import datetime
from dateutil.relativedelta import relativedelta
from sendEmail import sendEmail, sendEmailAviso1



organizacion_url = 'https://organizacion_url.com/'
service = "https://services.com/table0"
username = 'username'
password = 'password'
 
today = datetime.datetime.today().date()
linkEncuestaEdicion = "https://encuestaedicion.com/?id="
facturasAcumuladas60dias = []


# Mails para recibir avisos
mail1 = "mail1@gmail.com"
mail2 = "mail2@gmail.com"
mail3 = "mail3@gmail.com"
mail4 = "mail4@gmail.com"
 


class facturasAcumuladas:
    # Es para usar en Aviso2 (se cargan en Aviso1, y se usan en Aviso2)
    def __init__ (self, fecha, cliente, id):
        self.fecha = fecha
        self.cliente = cliente
        self.id = id
        



def main():
       
    print("Start Time: " + str(datetime.datetime.now()))
    global token
    token = acceso_sistema.generate_token(organizacion_url, username, password)
   
    global datosFacturas
    
    datosFacturas = acceso_sistema.query_paginacion(service, token, '*')
   
    

    aviso1()
    if(len(facturasAcumuladas60dias) >= 0 and int(today.day) == 2):
        aviso2() # depende de aviso1
        # aviso2 deberia ejecutarse 1 vez al mes, por es se le puso dia==2, empieza 2 ene 2024
    else:
        print("------Aviso2------ \nOmitido porque se ejecuta solo el dia 2 de cada mes")
    aviso3()
    avisos4y5()
 
    print("End Time: " + str(datetime.datetime.now()))
           
           
 






def aviso1():
    """
    Correo 1:
    Si en el campo "Estado" dice 'presupuesto_hecho', enviar un correo de aviso a los 15, 30, 45 y 60 días
    de la "fecha_presu". Dejar de enviar luego de los 60 días o si cambia el Estado.
    Mail:
    Asunto: Presupuesto realizado.
    Contenido: El "fecha_presu" de "Cliente"  + link de formulario de edicion. Destacar con algún semáforo
    color los 15, 30, 45 o 60 días.
    Destinatario: Destinatarios: mail1 y si "area_vendedor" es 'pasantes' o 'primer_nivel' incluir también a mail2.
    """        
   
    print("------Aviso1------")


    # Recorremos registro por registro
    for itemFactura in datosFacturas:

               
        if(itemFactura['fecha_presu'] != None and itemFactura['Estado'] != None and itemFactura['Estado'].lower() == 'presupuestado'):
           
            # Color para la tarjeta de acuerdo a la diferencia de dias. Por default es white
            colorAviso = 'white'


            # A quien se le envia el mail. Siempre va a ser mail1 y hay casos que se suman otros
            sendTo = [mail1]  


            if(itemFactura['area_vendedor'] != None and (itemFactura['area_vendedor'].lower() == "pasantes" or itemFactura['area_vendedor'].lower() == "primer_nivel")):
                sendTo.append(mail2)  
           
           
            try:
                # usamos try porque hay algunos que no tienen bien el dia

                # Calculamos diferencia de dias
                fecha_presuItemFactura = datetime.datetime.fromtimestamp(itemFactura['fecha_presu']/1000.0).date()
                restaDias = ""
                restaDiasNumber = None
                if today == fecha_presuItemFactura:
                    restaDiasNumber = 0
                else:
                    restaDias =  str(today - fecha_presuItemFactura)
                    restaDiasNumber = int(restaDias.split(" ")[0])
               
                


                # Definimos el color de la tarjeta, y si es mayor a 60 dias se va acumulando (para luego usar en aviso2)
                if(restaDiasNumber != 0 and restaDiasNumber is not None):
                    if(restaDiasNumber == 15):
                        colorAviso = '#FFF081'
                    elif(restaDiasNumber == 30):
                        colorAviso = '#FFC681'
                    elif(restaDiasNumber == 45):
                        colorAviso = '#F96F2A'
                    elif(restaDiasNumber == 60):
                        colorAviso = '#F9302A'
                    elif(restaDiasNumber > 60):
                        # print("La diferencia es mayor a 60 dias - se acumula")
                        # acumula en todo el for y luego envia
                   
                        facturaAcumulable = facturasAcumuladas(str(fecha_presuItemFactura),itemFactura['Cuentas']
                                                                , itemFactura['ID'])
                        facturasAcumuladas60dias.append(facturaAcumulable)
                        continue #para que saltee el envio de mail individual, y vaya a la siguiente itemFactura
                    else:
                        # Cuando pasaron 50 dias por ejemplo. No hay que avisar nada
                        continue #salta a la siguiente iteracion del for






                    # -- Envio de mails individuales --
                    for receiver_email_item in sendTo: #lo hicimos asi porque no nos dejaba enviar varios al mismo tiempo      
                        sendEmailAviso1("Presupuesto realizado", restaDiasNumber, itemFactura['Cliente'], itemFactura['ID'],
                            fecha_presuItemFactura, itemFactura['area_vendedor'], receiver_email_item,
                            linkEncuestaEdicion + str(itemFactura['ID']), colorAviso)
                        print("Se envio mail a " + receiver_email_item + " aviso de " + str(restaDiasNumber)  + " dias " )
                   
            except Exception as e:
                print("Omitido por error:")
                print(e)
                print("id: " + str(itemFactura['ID']))
                continue






























def aviso2():
    # Enviar un mail para todas las facturas acumuladas
    """
    Si en el campo "Estado" dice 'presupuesto_hecho' y  la "fecha_presu" es mayor a 61 días.
    Juntar todos los presupuestos que cumplan esa condición y enviar un correo.
    Mail:
    Asunto: Resumen de presupuestos mayores a 2 meses.
    Contenido: Hacer una lista de los presupuestos que indiquen: "Cliente" + "fecha_presu" + LINK ENCUESTA MODO EDICIÓN.
    Destinatario: Destinatarios: mail1, mail3 y mail2.
    """


    print("------Aviso2------")


    html = """\
        <!DOCTYPE html>
        <html>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500&display=swap" rel="stylesheet">
        <body>
        <div style="background:white;padding-left: 35px;padding-right: 35px;padding-top: 15px; border:3px solid #7590D7; border-radius:25px;background-size:100% 100%; padding-bottom:40px">
           
            <center>
                <img src="https://uvn-brightspot.s3.amazonaws.com/assets/vixes/btg/cine.batanga.com/files/Los-15-mejores-logos-de-equipos-y-empresas-ficticias-en-el-cine-4.png" width="150">
               
            </center>
            <center style="font-family: 'Montserrat', sans-serif;font-weight:500;font-size: 20px; color: black;text-align:left">
               
            <p> Hola
                </p>
               
            <p> Estas son las facturas presupuestadas pendientes: </p>
            <br>
        """
   
    # Se arma renglon por renglon cada presupuesto, y se va sumando al html
    for factAcumulada in facturasAcumuladas60dias:
               
        html += "<p>Cliente: " + factAcumulada.cliente + " - Fecha factura: " + factAcumulada.fecha + " - id:" + factAcumulada.id + " - "
        html += "<a href={}>Link encuesta edicion</a></p>".format(linkEncuestaEdicion + factAcumulada.id)
        html += "<br>"


   
    # Se cierra el html
    html+= """</center>
            </div>
        </body>
        </html>"""



   
    # Envia mails con las facturas acumuladas juntas
    mailsAEnviar  = [mail1, mail3, mail2]
    for receiver_item in mailsAEnviar:
        sendEmail("Resumen de presupuestos hechos mayores a 2 meses", receiver_item, html)
        print("Se envio mail de fact acumuladas a " + receiver_item )
         






























def aviso3():
    """
    Correo 3:
    Si en el campo "Estado" dice 'pagado', revisar la fecha de vencimiento que corresponda según el "Tipo":
    "Tipo" = 'productos' > ver la fecha "Venc_productos"
    "Tipo" = 'servicios' > ver "Venc_servicios"
    "Tipo" = 'datos' > ver "Venc_datos"
    
    Y un mes antes de la fecha que se encuentre enviar un mail que se vence ese producto, servicio o datos, segun corresponda
        Mail:
            Asunto: Vencimiento
            Contenido: En 1 mes se vence el "Tipo" de "Cliente": LINK ENCUESTA MODO EDICIÓN.
            Destinatario: Destinatarios: mail1 y si "area_vendedor" es 'pasantes' o 'primer_nivel' incluir también a mail2.
    """


    print("------Aviso3------")


    for itemFactura in datosFacturas:
       
        
        if(itemFactura['Estado'] != None and itemFactura['Estado'] == 'pagado'):

            fecha_venc_correspondiente = ""

            # Segun el tipo, consideramos diferentes fechas
            if(itemFactura['Tipo'] == 'productos'):
                fecha_venc_correspondiente = itemFactura["Venc_productos"]
            elif(itemFactura['Tipo'] == 'servicios'):
                fecha_venc_correspondiente = itemFactura["Venc_servicios"]
            elif(itemFactura['Tipo'] == 'datos'):
               fecha_venc_correspondiente = itemFactura["Venc_datos"]
            
            else:
                continue #pasa a la siguiente iteracion de for
           
            if(fecha_venc_correspondiente == "" or fecha_venc_correspondiente is None ):
                continue
               
           
            try:
               
                # Calculamos diferencia de dias
                fecha_presuItemFactura = datetime.datetime.fromtimestamp(fecha_venc_correspondiente/1000.0).date()
                restaDias = ""
                restaDiasNumber = None
                if today == fecha_presuItemFactura:
                    restaDiasNumber = 0
                else:
                    restaDias =  str(today - fecha_presuItemFactura )
                    restaDiasNumber = int(restaDias.split(" ")[0])


                # print(fecha_presuItemFactura)
                # print(restaDias)
                 
                # print("Diferencia de dias:")
                # print(restaDiasNumber)


                if(restaDiasNumber != 0 and restaDiasNumber is not None and restaDiasNumber == -30): #-30 porque es un mes antes


                    # Envio a mail1 por defecto, y posiblemente se agrega el de mail2
                    sendTo = [mail1]  
                   
                    if(itemFactura['area'] != None and (itemFactura['area_vendedor'].lower() == "pasantes" or 
                        itemFactura['area_vendedor'].lower() == "primer_nivel")):
                        sendTo.append(mail2)


                   
                    # Armamos html
                    html = """\
                        <!DOCTYPE html>
                        <html>
                        <link rel="preconnect" href="https://fonts.googleapis.com">
                        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500&display=swap" rel="stylesheet">
                        <body>
                        <div style="background:white;padding-left: 35px;padding-right: 35px;padding-top: 15px; border:3px solid #7590D7; border-radius:25px;background-size:100% 100%; padding-bottom:40px">
                           
                            <center>
                                <img src="https://uvn-brightspot.s3.amazonaws.com/assets/vixes/btg/cine.batanga.com/files/Los-15-mejores-logos-de-equipos-y-empresas-ficticias-en-el-cine-4.png" width="150">
                               
                            </center>
                            <center style="font-family: 'Montserrat', sans-serif;font-weight:500;font-size: 20px; color: black;text-align:left">
                               
                            <p> Hola
                                </p>
                               
                            <p> En un mes se vence factura '{}' de {} </p>
                        """.format(itemFactura["Tipo"], itemFactura['Cliente'])
                   
                   
                    # Ponemos link  de encuesta modo edicion    
                    html += "<a href={}>Link encuesta edicion</a>".format(linkEncuestaEdicion + str(itemFactura['ID']))
                    html += "<br><br>"


                   
                    # Se cierra el html
                    html += """</center>
                            </div>
                        </body>
                        </html>"""




                    # Envio de mails individualmente (por iteracion de for datosFacturas)
                    for receiver_email_item in sendTo: #lo hicimos asi porque no nos dejaba enviar varios al mismo tiempo      
                        sendEmail("Vencimiento", receiver_email_item, html)
                        print("Se envio mail a " + receiver_email_item + " - " + str(itemFactura['Cliente']))
                   
                   
            except Exception as e:
                print("Omitido por error:")
                print(e)
                print("Objectid: " + str(itemFactura['ID']))
                continue





























def avisos4y5():
    print("------Avisos4y5------")

    # link de tabla relacionada "Factura1" (tabla relacionada de tabla madre que usamos en aviso1, aviso2, aviso3)
    linkTablaRel = "https://services.com/table0/tablarel0"
      
   
    datosFacturasTablaRel = acceso_sistema.query_paginacion(linkTablaRel, token, '*')
   
    for itemFactura1 in datosFacturasTablaRel:

         # Tiene que cumplir con las siguientes condiciones
        if(itemFactura1["Estado_facturacion"] in ["Realizada", "Recibida por el cliente", "Hacer seguimiento"]):


            # ----- AVISO 4 ----------
            """
            Revisar tabla relacionada. Si en el campo "Estado_facturacion" dice 'Realizada',
            'Recibida por el cliente' o 'Hacer seguimiento' enviar un aviso 15 días ANTES de la 'Fecha_factura'.
       
            Mail:
                Asunto: Factura a hacer seguimiento
                Contenido: Hacer seguimiento de la factura enviada el día  'Fecha_factura', de "Cliente1": LINK ENCUESTA MODO EDICIÓN.
                Destinatario: Destinatarios: mail3, mail4, mail1. Y si "area1" es 'pasantes' o 'primer_nivel' incluir también a mail2.
            """    
           


            try:
                # Calculamos diferencia de dias
                fecha_factItemFactura1 = datetime.datetime.fromtimestamp(itemFactura1["Fecha_factura"]/1000.0).date()
                restaDias = ""
                restaDiasNumber = None
                if today == fecha_factItemFactura1:
                    restaDiasNumber = 0
                else:
                    restaDias =  str(today - fecha_factItemFactura1 )
                    restaDiasNumber = int(restaDias.split(" ")[0])
                # print("Diferencia de dias: " + str(restaDiasNumber))


                # "Enviar aviso 15 dias antes de la fecha_factura"
                if(restaDiasNumber != 0 and restaDiasNumber is not None and restaDiasNumber == -15): #negativo porque son 15 dias antes


                    print("------Aviso4------")  

                    # Envio a mail1, mail3, mail4 por defecto
                    sendTo = [mail1, mail3, mail4]  
               
                    if(itemFactura1['area1'] != None and (itemFactura1['area1'].lower() == "pasantes" 
                        or itemFactura1['area1'].lower() == "primer_nivel")):
                        sendTo.append(mail2)


                    # Armamos html
                    html = """\
                        <!DOCTYPE html>
                        <html>
                        <link rel="preconnect" href="https://fonts.googleapis.com">
                        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500&display=swap" rel="stylesheet">
                        <body>
                        <div style="background:white;padding-left: 35px;padding-right: 35px;padding-top: 15px; border:3px solid #7590D7; border-radius:25px;background-size:100% 100%; padding-bottom:40px">
                            <center>
                                <img src="https://uvn-brightspot.s3.amazonaws.com/assets/vixes/btg/cine.batanga.com/files/Los-15-mejores-logos-de-equipos-y-empresas-ficticias-en-el-cine-4.png" width="150">
                            </center>
                            <center style="font-family: 'Montserrat', sans-serif;font-weight:500;font-size: 20px; color: black;text-align:left">
                            <p>Hola</p>
                            <p>
                                Hacer seguimiento de la factura enviada el día {}, de {}:  
                            </p>
                        """.format(fecha_factItemFactura1, itemFactura1["Cliente1"])
               
               
                    # Ponemos link  de encuesta modo edicion    
                    html += "<a href={}>Link survey</a>".format(linkEncuestaEdicion + str(itemFactura1['id_tablamadre']))
                    # ponemos id_tablamadre porque estamos en tabla relacioanda, y necesitamos llevarlos hacia encuesta madre
               
                    html += "<br><br>"
               
                    # Se cierra el html
                    html += """
                            </center>
                            </div>
                            </body>
                            </html> """



                    # - Envio de mails individualmente - (por iteracion de for datosFacturas1)
                    for receiver_email_item in sendTo: #lo hicimos asi porque no nos dejaba enviar varios al mismo tiempo      
                        sendEmail("Factura a hacer seguimiento", receiver_email_item, html)
                        print("Se envio mail a " + receiver_email_item + " - " + str(itemFactura1["Cliente1"]))



            except Exception as e:
                print("Omitido por error:")
                print(e)
                print("aviso4 - id (de tablarel): " + str(itemFactura1['ID']))
                 
















        # ----- AVISO 5 (aprovechamos mismo for) ----------




        if(itemFactura1["Estado_facturacion"] == "Pendiente a realizar" and itemFactura1["Fecha_factura"] is not None):
               
            """
            Revisar tabla relacionada. Si en el campo "Estado_facturacion"  
            dice 'Pendiente a realizar', enviar un aviso en la fecha que indica el campo ' Fecha_facturar'.
            Mail:
                Asunto: Factura a realizar.
                Contenido: En el día de le fecha hay que realizar la factura del siguiente presupuesto
                de "Cliente1": LINK SURVEY MODO EDICIÓN.
                Destinatario: mail3, mail4, mail1. Y si "area1" es 'pasantes' o 'primer_nivel' incluir también a mail2.
            """




            try:    


                # Calculamos diferencia de dias
                fecha_factItemFactura1 = datetime.datetime.fromtimestamp(itemFactura1["Fecha_factura"]/1000.0).date()
                restaDias = ""
                restaDiasNumber = None
                if today == fecha_factItemFactura1:
                    restaDiasNumber = 0
                else:
                    restaDias =  str(today - fecha_factItemFactura1 )
                    restaDiasNumber = int(restaDias.split(" ")[0])
                # print("Diferencia de dias:")
                # print(restaDiasNumber)
                                 




                if(restaDiasNumber is not None and restaDiasNumber == 0 ):
                    print("------Aviso5------")    


                    # Envio a mail1, mail3, mail4 por defecto
                    sendTo = [mail1, mail3, mail4]  
               
                    if(itemFactura1['area1'] != None and (itemFactura1['area1'].lower() == "pasantes" or itemFactura1['area1'].lower() == "primer_nivel")):
                        sendTo.append(mail2)


                    # Armamos html
                    html = """\
                        <!DOCTYPE html>
                        <html>
                        <link rel="preconnect" href="https://fonts.googleapis.com">
                        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500&display=swap" rel="stylesheet">
                        <body>
                        <div style="background:white;padding-left: 35px;padding-right: 35px;padding-top: 15px; border:3px solid #7590D7; border-radius:25px;background-size:100% 100%; padding-bottom:40px">
                            <center>
                                <img src="https://uvn-brightspot.s3.amazonaws.com/assets/vixes/btg/cine.batanga.com/files/Los-15-mejores-logos-de-equipos-y-empresas-ficticias-en-el-cine-4.png" width="150">
                            </center>
                            <center style="font-family: 'Montserrat', sans-serif;font-weight:500;font-size: 20px; color: black;text-align:left">
                            <p>Hola</p>
                            <p>
                                En el día de la fecha hay que realizar la factura del siguiente presupuesto de {}:  
                            </p>
                        """.format(itemFactura1["Cliente1"])
               
                   
                    # Ponemos link  de encuesta modo edicion    
                    html += "<a href={}>Link Encuesta</a>".format(linkEncuestaEdicion + str(itemFactura1['id_tablamadre']))
                    # ponemos id_tablamadre porque estamos en tabla relacionada, y necesitamos llevarlos hacia encuesta con id madre
               
                    html += "<br><br>"




                    # Se cierra el html
                    html += """
                            </center>
                            </div>
                            </body>
                            </html> """




                    # - Envio de mails individualmente - (por iteracion de for datosFacturasTablaRel)
                    for receiver_email_item in sendTo: #lo hicimos asi porque no nos dejaba enviar varios al mismo tiempo      
                        sendEmail("Factura a realizar", receiver_email_item, html)
                        print("Se envio mail a " + receiver_email_item + " - " + str(itemFactura1["Cliente1"]))
           
           
            except Exception as e:
                print("Omitido por error:")
                print(e)
                print("aviso5 - id (de tablarel): " + str(itemFactura1['ID']))
                 



 


if __name__ == '__main__':
    main()
    
 
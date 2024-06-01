from datetime import datetime
import json
import codecs
import xlrd 
import pandas as pd
import requests
import json
 
from access_sistema import folders_content
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from datetime import timedelta


file_content = folders_content("root")


horaStart = datetime.now() - timedelta(hours=3) 
print("Empezó a la hs: " + str(horaStart))


# Set the URL for the Sheets API
SPREADSHEET_ID = '98ez-ADoieurpoRFG8ervopeir4346C7ew'
RANGE_NAME = 'Listado de Usuarios!A4:P'
URL = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{RANGE_NAME}'

# Set the authentication credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
KEY = 'root/key.json'
creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)
creds.refresh(Request())
# Set the headers for the request
headers = {
    'Authorization': f'Bearer {creds.token}',
    'Content-Type': 'application/json'
}

# Send the request and get the response
response = requests.get(URL, headers=headers)
listExcel=None
# Check if the request was successful
if response.status_code == requests.codes.ok:
    # Print the response data as JSON
    data = json.loads(response.text)
    listExcel = data['values']
    print(len(listExcel))
    print(listExcel) 
else:
    # Print the error message
    print('Error:', response.text)
    
 

def trying(fila, indice):
    try:
        if(fila[indice] != None):
            return fila[indice]
    except:
        return ""


rings=""
objetoGeometry = {}
tablaFalsa = []


contador=0

for fila in listExcel:
    # inserta 1 registro menos porque omite el titulo
    if (contador == 0):
        contador = contador +1
        continue

    
    fechaVen = None   

               
    try:
        if(trying(fila,12) !=''):
            fechaVen = datetime.strptime(trying(fila,12), '%d/%m/%Y')
    except:
            print("Ocurrio un error con fecha: " + trying(fila,12))         
    
    
    
    objetoGeometry={
        "rings" : rings,
        "spatialReference": 
        {
          "wkid": 4326, 
         "latestWkid": 4326
      }
   }
       
    registroFinal = {
        "data" : {
           
            "ID" : trying(fila,0),
            "NOMBRE" : trying(fila,1),
            "CUIT" : trying(fila,3),
            "UBICACION" : trying(fila,4),
            "Vencimiento" : fechaVen,
            "ESTADO" : trying(fila,13) 
        }, 
        "geometry" : objetoGeometry
    }
     
    tablaFalsa.append(registroFinal)


preTablaFinal = file_content.content.get('6f456jktR2asdbvwswf283f6sasdw3ed08697') 

tablaFinal = preTablaFinal[0]

#elimina todos los datos de la capa
tablaFinal.manager.truncate()

cant_insercion=250

adds_array=[tablaFalsa[i:i + cant_insercion] for i in range(0, len(tablaFalsa), cant_insercion)]

for lote_adds in adds_array: 
    tablaFinal.add_features(lote_adds)
     

fechaEnd =  datetime.now() - timedelta(hours=3) 
print("Terminó a la hs: " + str(fechaEnd))
print("Tardó: " + str(fechaEnd - horaStart))
function get_excel(letraColCondicion, letraColToGet, valorIngresado) {

    var sheetId = '65s4dcas84c98qwvghfyjh';

    var base = 'https://docs.google.com/spreadsheets/d/' + sheetId + '/gviz/tq?';

    var sheetName = 'Nombre de la Hoja';

    var query = encodeURIComponent("Select " + letraColToGet.toUpperCase().trim() +
        " where " + letraColCondicion.toUpperCase().trim() +
        "='" + valorIngresado.trim() +
        "'")

    var url = base + '&sheet=' + sheetName + '&tq=' + query;
    var data = [];

    // Create the request object
    var xhr = new XMLHttpRequest();
    // Make the request.  
    xhr.open("GET", url, false);
    xhr.send();

    //Esta es una versión abreviada para poder distinguir diferentes tipos de errores
    if (xhr.status === 200) { //si el estado es 200, quiere decir que esta todo bien

        var response = JSON.parse(xhr.responseText.substring(47).slice(0, -2))  //convierte el texto encontrado en JSON

        if (!response.error) { // si la conversion anterior no tira errores

            var cantidad = response.table.rows.length; // cuenta la cantidad total de objetos que encontró

            if (cantidad > 0) {
                var i;
                for (i = 0; i < cantidad; i++) {

                    return response.table.rows[0].c[0].v;

                    /*if(response.table.rows[i].c[0].v == valorIngresado.trim()){
                        return response.table.rows[parseInt(i)].c[parseInt(columna) - 1].v;
                    }	*/
                }
            }
        }
    }
}



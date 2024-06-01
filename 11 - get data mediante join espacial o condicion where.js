

function featureByLocation(layerURL, location) {
	//Busca datos por medio de una UBICACION
	// Query a feature layer and returns the feature that intersects the location

	// Output value.  Initially set to an empty string  
	let outValue = "";

	// Check to make sure both layerURL and location are provided
	if (layerURL == null || layerURL === "" || location == null || location === "") {
		// The function can't go forward; exit with the empty value
		return location;
	}

	// The coordinates will come in as `<lat> <lon> <alt> <acc>`.  
	// We need <lon>,<lat> for the query
	// Note that I'm using the relatively new ` ` string that lets me place variables ${var}
	let coordsArray = location.split(" ");
	let coords = `${coordsArray[1]},${coordsArray[0]}`;


	// Set up query parameters
	let f = "f=json";
	let geometry = `geometry=${coords}`;
	let geometryType = "geometryType=geometryPoint";
	let inSR = "inSR=4326";
	let spatialRel = "spatialRel=spatialRelIntersects";
	let outFields = "outFields=*";
	let returnGeometry = "returnGeometry=false";
	let returnCount = "returnCount=1";
	let parameters = [f, geometry, geometryType, inSR, spatialRel, outFields, returnGeometry, returnCount].join("&"); //junta los parametros con '&'



	let url = `${layerURL}/query?${parameters}`; //arma la url completa, con todos los parametros


	// Create the request object
	let xhr = new XMLHttpRequest();
	// Make the request.  Note the 3rd parameter, which makes this a synchronous request
	xhr.open("GET", url, false);
	xhr.send();

	// Process the result
	if (xhr.readyState === xhr.DONE) {
		if (xhr.status !== 200) {
			// The http request did not succeed
			return "bad request: " + url
		} else {
			// Parse the response into an object
			let response = JSON.parse(xhr.responseText);
			if (response.error) {
				// There was a problem with the query
				return null
			} else {
				if (response.features[0]) {

					//ELEGIR EL ATRIBUTO QUE NECESITO QUE ME DEVUELVA
					outValue = response.features[0].attributes.nombre; //nombre, por que quiero que me devuelva el nombre, que es un campo del Json (capa)

				} else {
					// No features found
					return "No features found"
				}
			}
		}
	}
	return outValue;
}
















function buscarDatosPorCampo(token, datoACoincidir, datoATraer) {

	let field = "NOMBRE"; //campo de la tabla donde busca coincidencia (con datoACoincidir que esta arriba, que es por ejemplo un nombre: "JOSE PEREZ")

	//url de la capa
	let layerURL = "https://servicios.com/tabla8";

	// parametros que requiere la url de la capa 
	let where = "where=1=1"; //se puede hacer directo aca en el where
	let f = "f=pjson";
	let objectIds = "";
	let outFields = "outFields=*";
	let returnGeometry = "returnGeometry=false";

	//aca se juntan todos los parametros mediante &
	let parameters = [where, objectIds, f, outFields, returnGeometry].join("&");

	if (token) { //corrobora si se paso el token, si se paso: lo agrega a los parametros de la url
		parameters = parameters + `&token=${token}`;
	}

	let url = `${layerURL}/query?${parameters}`;  //confeccion de la url. se le suman todos los parametros

	// Create the request object
	let xhr = new XMLHttpRequest();
	// Make the request.  Note the 3rd parameter, which makes this a synchronous request
	xhr.open("GET", url, false);
	xhr.send();

	// Process the result
	// Esta es una versión abreviada (sin poder distinguir algunos tipos de errores)
	if (xhr.status === 200) { //si el estado es 200, quiere decir que esta todo bien
		let response = JSON.parse(xhr.responseText);  //convierte el texto encontrado en JSON
		if (!response.error) { //si la conversion anterior no tira errores

			let cantidad = response.features.length; //cuenta la cantidad total de objetos que encontró

			for (var i = 0; i < cantidad; i++) {  //recorre 1 por 1 los objetos que encontró
				if (response.features[i]) { //se hace una revision por las dudas, si existe ese objeto
					if (response.features[i].attributes[field] == datoACoincidir) { //se revisa si hay coincidencia de dato
						return response.features[i].attributes[datoATraer]; //cuando hay coincidencia, devuelve el "datoATraer"  
						// del objeto donde encontro coincidencia 
					}
				}
			}
		}
	}

}
"use strict"

const form = document.querySelector("#light-classes-form");

const lightClassSelector = document.querySelector("#light-classes");

const positionSearch = document.querySelector("#position-search");
const suggestionList = document.querySelector("#suggestion-list");

const lessonSlider = document.querySelector("#lessons-slider");
const rangeValue = document.querySelector("#lessons-value");

const distanceSlider =  document.querySelector("#distance-slider");
const distanceValue = document.querySelector("#distance-value");

const hasAdminPrices = document.querySelector("#admin-prices");



let latitude;
let longitude;

/* getPosition.addEventListener("click", event => {
    event.preventDefault();
    if(!navigator.geolocation)
        alert('Geolocation is not supported by your browser');
    else {
        navigator.geolocation.getCurrentPosition(
            posData => {
                console.log(posData);
                latitude = posData.coords.latitude;
                longitude = posData.coords.longitude;
                console.log(latitude, longitude);
            },
            error => console.log(error)
        );
    }  
}); */


positionSearch.addEventListener("input", () => {


    const address = positionSearch.value;

    let url = "https://ws.geonorge.no/adresser/v1/sok"
    const parameters = {
        "adressetekst": encodeURIComponent(address),
        "treffPerSide": 10,
        "side": 0
    }

    const queryString = Object.keys(parameters).map(key => key + '=' + parameters[key]).join('&');
    url = `${url}?${queryString}`;
    fetch(url, {
        method: "GET",
        headers: {
            "Accept": "application/json"
        }
    })
    .then(response => response.json())
    .catch(error => alert(error))
    .then(matches => {


        if(address.length === 0){
            suggestionList.innerHTML = `<option value="Min posisjon" data-value="GEOPOS">`;
        }
        else if(matches.adresser.length === 0)
            matches = [];
        else
            matches = matches.adresser
    
        if(matches.length > 0) {
            let address_key = "adressenavn";
            if(address.match(".*\\d.*"))
                address_key = "adressetekst";
            
            const html = matches.map(match => `
            <option value="${match[address_key]}, ${match.poststed}, ${match.kommunenavn}"  data-value="${match.representasjonspunkt.lat},${match.representasjonspunkt.lon}">`)
            .join("");
            suggestionList.innerHTML = html;
        }
    })
});




suggestionList.addEventListener("click", event => {
    console.log("kek");
})


document.addEventListener("change", async event => {
    event.preventDefault();

    if (event.target && event.target.id == "position-search") {
        const coordinates = suggestionList.options[0].dataset.value;
        
        console.log(coordinates === "GEOPOS");
        if(coordinates === "GEOPOS"){
            if(!navigator.geolocation)
                alert('Geolocation is not supported by your browser');
            else {
                navigator.geolocation.getCurrentPosition(
                    posData => {
                        console.log(posData);
                        latitude = posData.coords.latitude;
                        longitude = posData.coords.longitude;
                        console.log(latitude, longitude);

                    },
                    error => console.log(error)
                );
            }
        }
        else{
            const coordArray = coordinates.split(",")
            latitude = parseFloat(coordArray[0]);
            longitude = parseFloat(coordArray[1]);
            console.log(latitude, longitude);
        }
    }


});


form.addEventListener('submit', event => {
    event.preventDefault();

    const package_class = lightClassSelector.value;

    const lat = latitude;
    const long =  longitude;

    const n = lessonSlider.value;

    const distance = distanceSlider.value;
    
    let adminPrices = false;
    if(hasAdminPrices.checked == true)
        adminPrices = true;

    console.log(`
    Package: ${package_class}
    Lat: ${lat}
    Long: ${long}
    Lessons: ${n}
    Distance: ${distance}
    AdminPrices? ${adminPrices}`);
});


lessonSlider.addEventListener("input", event =>{
    rangeValue.innerHTML = lessonSlider.value;

});

distanceSlider.addEventListener("input", event =>{
    distanceValue.value = distanceSlider.value;

});
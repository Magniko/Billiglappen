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

const cardResults = document.querySelector(".card-results");

const totalPrices = document.querySelector(".total-price");

let latitude;
let longitude;

positionSearch.addEventListener("input", () => {


    const address = positionSearch.value;

    let url = "https://ws.geonorge.no/adresser/v1/sok"
    const parameters = {
        "adressetekst": encodeURIComponent(address),
        "treffPerSide": 10,
        "side": 0
    }

    url = `${url}?${stringToQuery(parameters)}`;
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
        }
    }


});


form.addEventListener('submit', event => {
    event.preventDefault();

    cardResults.innerHTML = "";

    const package_class = lightClassSelector.value;

    const lat = latitude;
    const long =  longitude;

    const n = lessonSlider.value;

    const distance = distanceSlider.value;
    
    let adminPrices = false;
    if(hasAdminPrices.checked == true)
        adminPrices = true;


    let url = "https://api-billiglappen.herokuapp.com/light_classes"
    const parameters = {
        "class_": package_class,
        "n" : n,
        "threshold": distance,
        "lat": lat,
        "long_": long,
        "include_admin_fees": adminPrices
    }
    url = `${url}?${stringToQuery(parameters)}`;

    fetch(url, {
        method: "GET",
        headers: {
            "Accept": "application/json"
        }
    })
    .then(response => response.json())
    .catch(error => alert(error))
    .then(data => {

        const html = data.map(pack => `
            <div class="package-container">
                <h4><b>${pack.name}</b></h4>
                <div class="total-price">
                    <p><b>Totalpris:</b> ${formatPrice(pack.total_price)},-</p>
                </div>
                <div class="lessons-included">
                    <p><b>Kjøretimer inkludert:</b> ${pack.n_lessons}</p>
                </div>
                <div class="distance">
                    <p><b>Avstand:</b> ${pack.distance.toFixed(2)}km</p>
                </div>
                <div class="rating">
                    <p><b>Vurdering:</b> ${checkRating(pack.rating)}</p>
                </div>
            </div>`)
            .join("");


        cardResults.innerHTML = html;

    });
        
});


lessonSlider.addEventListener("input", event =>{
    rangeValue.innerHTML = lessonSlider.value;

    //TODO: dynaimcally change total price depending on amount of lessons
/*     let totalPrice = 
    totalPrices.innerHTML =  */


});

distanceSlider.addEventListener("input", event =>{
    distanceValue.value = distanceSlider.value;

});

const stringToQuery = parameters => 
    Object.keys(parameters).map(key => 
        key + '=' + parameters[key])
        .join('&');

const formatPrice = price =>
    price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");

const checkRating = rating =>
    !isNaN(rating) ? rating.toFixed(1)  : "-";



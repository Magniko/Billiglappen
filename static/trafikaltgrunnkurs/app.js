"use strict"


const lightClassButton = document.querySelector("#light-class-button");

const formLightClasses = document.querySelector("#light-classes-form");
const formTg = document.querySelector("#form-tg");

const lightClassSelector = document.querySelector("#light-classes");

const positionSearch = document.querySelector("#position-search");
const suggestionList = document.querySelector("#suggestion-list");

const lessonSlider = document.querySelector("#lessons-slider");
const rangeValue = document.querySelector("#lessons-value");

const distanceSlider =  document.querySelector("#distance-slider");
const distanceValue = document.querySelector("#distance-value");

const hasAdminPrices = document.querySelector("#admin-prices");
const hasOver25 = document.querySelector("#over-twentyfive");

const cardResults = document.querySelector(".card-results");

const totalPrices = document.querySelector(".total-price");



let latitude;
let longitude;


lightClassButton.addEventListener("click", event => {
    window.location.href = "/";
}) 




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



formTg.addEventListener('submit', event => {
    event.preventDefault();

    cardResults.innerHTML = "";

    const lat = latitude;
    const long =  longitude;

    const distance = distanceSlider.value;
    
    let over25 = false;
    if(hasOver25.checked == true)
        over25 = true;


    let url = "https://api.billiglappen.no/trafikalt_grunnkurs"
    const parameters = {
        "threshold": distance,
        "lat": lat,
        "long_": long,
        "over_25": over25
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

        let html;

        if(data.length != 0){
            html = data.map(pack => `
                <div class="package-container">
                    <div class="package-header">
                        <div class="school-name">
                            <h2><b>${pack.name}</b></h2>
                        </div>
                        <div class="total-price">
                            <p><b>Totalpris:</b> <span>${formatPrice(pack.tg_package_price)},-</span></p>
                        </div>
                        <div class="distance">
                            <p><b>Avstand:</b> <span>${pack.distance.toFixed(2)}km</span></p>
                        </div>
                        <div class="rating">
                            <p><b>Vurdering:</b> <span>${checkRating(pack.rating)}</span></p>
                        </div>
                        <div class="homepage">
                            <a href="http://${pack.website}">Skolens nettside</a>
                        </div>
                    </div>

                    <div class="package-details">
                        <div class="basic-price">
                            <p>Trafikalt Grunnkurs: <span>${formatPrice(pack.theory_price)},-</span></p>
                        </div>
                        <div class="firstaid-price">
                            <p>Førstehjelp: <span>${formatPrice(pack.first_aid_price)},-</span></p>
                        </div>
                        <div class="night-price">
                            <p>Mørkekjøring: <span>${formatPrice(pack.night_driving_price)},-</span></p>
                        </div>
                        <div class="discount">
                            <p>Rabatt: <span>${formatPrice(pack.discount)},-</span></p>
                        </div>
                        <div class="updated">
                            <p>Sist oppdatert: <span>${pack.last_updated}</span></p>
                        </div>
                    </div>
                </div>`)
                .join("");
        }
        else
        {
            html = `<div class="package-container">
                <div class="none-header">
                    <h2><b>Ingen resultater...</b></h2>
                </div>
            </div>`;
        }


        cardResults.innerHTML = html;

    });
        
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



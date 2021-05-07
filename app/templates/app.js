"use strict"


const tgButton = document.querySelector("#tg-course-button");

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



tgButton.addEventListener("click", event => {
    window.location.href = "trafikaltgrunnkurs";
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



document.addEventListener("click", event => {

    console.log(event.target);

});

/* packageHeader[i].addEventListener("click", function() {
    this.classList.toggle("active");
    let content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
} */

formLightClasses.addEventListener('submit', event => {
    event.preventDefault();

    cardResults.innerHTML = `<div class="loading"><img src=img/loading_spinner.gif></div`;

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

        let html;

        if(data.length != 0){
            html = data.map(pack => `
                <div class="package-container">
                    <div class="package-header">
                        <div class="school-name">
                            <h2><b>${pack.name}</b></h2>
                        </div>
                        <div class="total-price">
                            <p><b>Totalpris:</b> <span>${formatPrice(pack.total_price)},-</span></p>
                        </div>
                        <div class="lessons-included">
                            <p><b>Kjøretimer inkludert:</b> <span>${pack.n_lessons}</span></p>
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
                        <div class="lesson-price">
                            <p>Kjøretime: <span>${formatPrice(pack.lesson_price)},-</span></p>
                        </div>
                        <div class="evaluation-price">
                            <p>Trinnvurderingstime: <span>${formatPrice(pack.evaluation_price)},-</span></p>
                        </div>
                        <div class="track-price">
                            <p>Sikkerhetskurs på bane: <span>${formatPrice(pack.safety_track_price)},-</span></p>
                        </div>
                        <div class="road-price">
                            <p>Sikkerhetskurs på vei: <span>${formatPrice(pack.safety_road_price)},-</span></p>
                        </div>
                        <div class="test-price">
                            <p>Oppkjøring: <span>${formatPrice(pack.drive_test_price)},-</span></p>
                        </div>
                        <div class="other-price">
                            <p>Tilleggskostnader: <span>${formatPrice((pack.other_price + pack.hidden_price))},-</span></p>
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
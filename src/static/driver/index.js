const btn = document.getElementById("close-btn");
const nav = document.getElementById("side-nav");
const menu = document.getElementById("home-menu");
let userstatus = document.getElementById("status")

//Event Listeners
btn.addEventListener("click", (event) => {
    /* nav.classList.add("side-nav-animate-out"); */
    nav.style.left = "-100%";
    nav.classList.remove("side-nav-animate-in")
    menu.style.left = "0";
    profile.style.left = "0";
})

menu.addEventListener("click", (event) => {
    console.log("clicked");
    nav.style.left = "0";
    nav.classList.add("side-nav-animate-in");
    menu.style.left = "-100%";
    profile.style.left = "-100%";


})



let map = L.map('map').setView([0, 0], 13);

let tile = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


//Updating the drivers live location
let marker, circle
const socket = io.connect();

navigator.geolocation.watchPosition(
    (position) => {
      // Retrieve latitude and longitude from the position object
      const { latitude, longitude, accuracy } = position.coords;
      
      // Update the map's view with the user's coordinates
      map.setView([latitude, longitude], 13);

      if (marker) {
        marker.setLatLng([latitude, longitude]);
      } else {
        // Add a marker at the user's initial location
        marker = L.marker([latitude, longitude]).addTo(map);
      }

      // Emit the location update to the server
      socket.emit('location_update', {
      latitude: latitude,
      longitude: longitude
    });

      },
      (error) => {
        // Handle geolocation error
        console.error('Error getting geolocation:', error);
      }
  );

userstatus.addEventListener("change", (event) => {
    if (event.target.checked) {
        passenger();
      }
})

function passenger() {
      let marker = L.marker([-33.9608, 25.6022]).addTo(map);
}

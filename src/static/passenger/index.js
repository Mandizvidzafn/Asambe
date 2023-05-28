
const btn = document.getElementById("close-btn");
const nav = document.getElementById("side-nav");
const menu = document.getElementById("home-menu");
const profile = document.getElementById("home-profile");
const minus = document.getElementById("minus");
const bottom = document.getElementById("bottom")
let userstatus = document.getElementById("status")
const driverMarkers = {};

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

minus.addEventListener("click", (event) => {
    console.log("clicked")
    bottom.classList.toggle("bottom-active");
})




let map = L.map('map').setView([0, 0], 13);

let tile = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


let passengerMarker

navigator.geolocation.watchPosition(
    (position) => {
      // Retrieve latitude and longitude from the position object
      const { latitude, longitude, accuracy } = position.coords;
      
      // Update the map's view with the user's coordinates
      map.setView([latitude, longitude], 13);

      if (passengerMarker) {
        passengerMarker.setLatLng([latitude, longitude]);
      } else {
        // Add a marker at the user's initial location
        passengerMarker = L.marker([latitude, longitude]).addTo(map);
      }

      },
      (error) => {
        // Handle geolocation error
        console.error('Error getting geolocation:', error);
      }
  );


const socket = io.connect();
 
socket.on("driver_location_update", (data) => {
  const { driver_id, latitude, longitude, name, active } = data;

  if (driverMarkers[driver_id]) {
    driverMarkers[driver_id].setLatLng([latitude, longitude]);
  } else {
    const marker = L.marker([latitude, longitude]).addTo(map);
    marker.bindPopup(`Driver Name: ${name}`).openPopup();
    driverMarkers[driver_id] = marker;
  }

});

socket.emit("active_drivers_location");

const btn = document.getElementById("close-btn");
const nav = document.getElementById("side-nav");
const menu = document.getElementById("home-menu");
const driverStatus = document.getElementById("status")
const passengerMarkers = {};

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

// Add an event listener to the checkbox
driverStatus.addEventListener("change", () => {
  // Get the status value (true or false) from the checkbox
  const status = driverStatus.checked;

  // Emit the status update to the server
  socket.emit("status_update", { status });
});



//map functionalities
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
      
      // Update the map's view with the drivers's coordinates
      map.setView([latitude, longitude], 13);

      if (marker) {
        marker.setLatLng([latitude, longitude]);
      } else {
        // Add a marker at the driver's initial location
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


socket.on("passenger_location_update", (data) => {
  const { passenger_id, latitude, longitude, name, location } = data;

  if (passengerMarkers[passenger_id]) {
    driverMarkers[driver_id].setLatLng([latitude, longitude]);
  } else {
    const marker = L.marker([latitude, longitude]).addTo(map);
    if (location === undefined){
      marker.bindPopup(`${name}`).openPopup();
    }else{
      marker.bindPopup(`${name} is in ${location}`).openPopup();
    }
    passengerMarkers[passenger_id] = marker;
  }

});

socket.on("remove_inactive_passengers", (data) => {
  const { passenger_ids } = data;

  for (const passenger_id in passengerMarkers) {
    if (passengerMarkers.hasOwnProperty(passenger_id) && !passenger_ids.includes(passenger_id)) {
      map.removeLayer(passengerMarkers[passenger_id]);
      delete passengerMarkers[passenger_id];
    }
  }
});


socket.emit("active_passengers_location");





const btn = document.getElementById("close-btn");
const nav = document.getElementById("side-nav");
const menu = document.getElementById("home-menu");
const profile = document.getElementById("home-profile");
const minus = document.getElementById("minus");
const bottom = document.getElementById("bottom")
let passengerStatus = document.getElementById("status")
const driverMarkers = {};


// Add an event listener to the checkbox
passengerStatus.addEventListener("change", () => {
  // Get the status value (true or false) from the checkbox
  const status = passengerStatus.checked;

  // Emit the status update to the server
  socket.emit("passenger_status_update", { status });
});

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


//Updating the drivers live location
let marker, circle

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
      socket.emit('passenger_location_update', {
      latitude: latitude,
      longitude: longitude
    });

      },
      (error) => {
        // Handle geolocation error
        console.error('Error getting geolocation:', error);
      }
  );


const socket = io.connect();
 
socket.on("driver_location_update", (data) => {
  const { driver_id, latitude, longitude, name, location } = data;

  if (driverMarkers[driver_id]) {
    driverMarkers[driver_id].setLatLng([latitude, longitude]);
  } else {
    const marker = L.marker([latitude, longitude]).addTo(map);
    if (location === undefined){
      marker.bindPopup(`Driver Name: ${name} is Active`).openPopup();
    }else{
      marker.bindPopup(`Driver Name: ${name} is in ${location}`).openPopup();
    }
    driverMarkers[driver_id] = marker;
  }

});

socket.on("remove_inactive_drivers", (data) => {
  const { driver_ids } = data;

  for (const driver_id in driverMarkers) {
    if (driverMarkers.hasOwnProperty(driver_id) && !driver_ids.includes(driver_id)) {
      map.removeLayer(driverMarkers[driver_id]);
      delete driverMarkers[driver_id];
    }
  }
});


socket.emit("active_drivers_location");

const driverStatus = document.getElementById("status")
const socket = io.connect();

//Event listeners
// Add an event listener to the checkbox
driverStatus.addEventListener("change", () => {
    // Get the status value (true or false) from the checkbox
    const status = driverStatus.checked;
  
    // Emit the status update to the server
    socket.emit("status_update", { status });
  });
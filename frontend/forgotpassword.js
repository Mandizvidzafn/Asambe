function generateOTP() {
  // Generate a random 6-digit OTP
  var otp = Math.floor(100000 + Math.random() * 900000);
  document.getElementById("otp").value = otp;
}
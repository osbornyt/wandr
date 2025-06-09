function togglePassword(id) {
    document.getElementById(id).style.display = "none";
    if(id == "eye"){
      document.getElementById("eye-slash").style.display = "block";
    }else{
      document.getElementById("eye").style.display = "block";
    }
    var passwordInput = document.getElementById("password");

    // Check the current type of the input
    var currentType = passwordInput.type;

    // Toggle the type between password and text
    passwordInput.type = (currentType === "password") ? "text" : "password";
  }
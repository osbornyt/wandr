// Get the modal
const greenModal = document.getElementById("greenModal");

// Get the button that opens the modal
const openBtn = document.getElementById("openGreenModalBtn");

// Get the button that closes the modal
const closeBtn = document.getElementById("closeGreenModalBtn");
const cancelBtn = document.getElementById("cancelGreenModalBtn");

// Open the modal when the button is clicked
openBtn.addEventListener('click', function() {
  greenModal.style.display = "block";
});

// Close the modal when the close button is clicked
closeBtn.addEventListener('click', function() {
  greenModal.style.display = "none";
});

// Close the modal when the cancel button is clicked
cancelBtn.addEventListener('click', function() {
  greenModal.style.display = "none";
});

// Close the modal if the user clicks outside of it
window.addEventListener('click', function(event) {
  if (event.target == greenModal) {
    greenModal.style.display = "none";
  }
});
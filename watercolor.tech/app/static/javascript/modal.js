var hostModal = document.getElementById("hostModal");
var hostBtn = document.getElementById("hostBtn");

var joinModal = document.getElementById("joinModal");
var joinBtn = document.getElementById("joinBtn");

hostBtn.onclick = () => {
    hostModal.style.display = "block";
}

joinBtn.onclick = () => {
    joinModal.style.display = "block";
}

window.onclick = function(event) {
  if (event.target == hostModal || event.target == joinModal) {
    hostModal.style.display = "none";
    joinModal.style.display = "none";
  }
} 
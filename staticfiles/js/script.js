document.addEventListener("DOMContentLoaded", () => {
const messages = document.querySelectorAll(".alert-items");

messages.forEach((msg) => {
setTimeout(() => {
  msg.style.transition = "opacity 0.5s ease-out";
  msg.style.opacity = "0";

  setTimeout(() => {
    msg.style.display = "none";
  }, 500);
}, 3000);
});
});
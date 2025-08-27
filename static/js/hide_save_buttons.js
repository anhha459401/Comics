document.addEventListener("DOMContentLoaded", function () {
  const saveButtons = document.querySelectorAll(".submit-row input");
  saveButtons.forEach((button) => {
    button.style.display = "none";
  });
});

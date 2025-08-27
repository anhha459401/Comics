$(document).ready(function () {
  var urlParams = new URLSearchParams(window.location.search);
  var offset = urlParams.get("offset");

  if (offset && offset > 0) {
    $("#hide-btn-order").show();
  }

  $("#show-btn-order").on("click", function (e) {
    e.preventDefault();
    window.location.href = $(this).attr("href");
  });

  $("#hide-btn-order").on("click", function (e) {
    e.preventDefault();
    window.location.href = $(this).attr("href");
  });
});

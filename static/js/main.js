(function ($) {
  "use strict";

  $(document).ready(function () {
    // Mobile Nav toggle
    $(".menu-toggle > a").on("click", function (e) {
      e.preventDefault();
      $("#responsive-nav").toggleClass("active");
    });

    // Fix cart dropdown from closing
    $(".cart-dropdown").on("click", function (e) {
      e.stopPropagation();
    });

    /////////////////////////////////////////
    // Yêu thích

    updateFavoriteStatus();

    updateTotalFavorites();

    // $(".heart-icon").on("click", function () {
    //   let icon = $(this);
    //   let comicId = icon.data("comic-id");

    //   if (icon.hasClass("liked")) {
    //     removeFromFavorite(comicId);
    //   } else {
    //     addToFavorite(comicId);
    //   }
    // });

    let heartClickLocked = false; // Biến khóa click

    $(document).on("click", ".heart-icon", function () {
      if (heartClickLocked) return; // Nếu đang khóa thì bỏ qua

      heartClickLocked = true; // Khóa click
      let icon = $(this);
      let comicId = icon.data("comic-id");

      if (icon.hasClass("liked")) {
        removeFromFavorite(comicId);
      } else {
        addToFavorite(comicId);
      }

      // Mở khóa sau 1 giây
      setTimeout(() => {
        heartClickLocked = false;
      }, 1000);
    });

    // Đăng nhập
    $("#login-btn").click(function () {
      let username = $("#username-login").val();
      let pass = $("#password-login").val();
      if (username === "" || pass === "") {
        toastr.error("Vui lòng nhập đầy đủ thông tin.");
        return false;
      }
    });

    // Đăng xuất
    $("#logout-btn").click(function (e) {
      e.preventDefault(); // Ngăn click mặc định trên thẻ <a>

      const logoutUrl = $(this).attr("href");

      Swal.fire({
        title: "Xác nhận đăng xuất",
        text: "Bạn có chắc chắn muốn đăng xuất?",
        icon: "info",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Đăng xuất",
        cancelButtonText: "Hủy",
        reverseButtons: true,
      }).then((result) => {
        if (result.isConfirmed) {
          window.location.href = logoutUrl;
        }
      });
    });

    /////////////////////////////////////////////////
    $(window).scroll(function () {
      if ($(this).scrollTop() > 100) {
        $("#scrollToTopBtn").fadeIn(); // Hiện nút
      } else {
        $("#scrollToTopBtn").fadeOut(); // Ẩn nút
      }
    });

    // Cuộn lên đầu trang khi click nút
    $("#scrollToTopBtn").click(function () {
      $("html, body").animate({ scrollTop: 0 }, 600);
      return false;
    });

    //////////////////////////////////////////////
    // Tìm kiếm sản phẩm
    $("#search-comic-form").submit(function (e) {
      let searchComic = $("#search-comic-value").val().trim();
      if (searchComic === "") {
        e.preventDefault();
        toastr.info("Hãy nhập từ khóa tìm kiếm!");
      }
    });

    /// Hủy đơn, trả hàng
    $(".action-order").click(function () {
      const action = $(this).data("action");
      const orderId = $(this).data("order-id");

      $.ajax({
        url: `/orders/${action}/${orderId}`,
        type: "POST",
        data: {
          csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr("content"),
        },
        success: function (response) {
          if (response.success) {
            toastr.success(response.message);
            $("#order-status").text(response.order_status);
            $("#payment-status").text(response.payment_status);
            $(".action-order").hide();
          } else {
            toastr.error(data.message);
          }
        },
        error: function () {
          toastr.error("Đã có lỗi xảy ra. Vui lòng thử lại.");
        },
      });
    });

    //////////////////////////////////////////////

    // Products Slick
    $(".products-slick").each(function () {
      var $this = $(this),
        $nav = $this.attr("data-nav");

      $this.slick({
        slidesToShow: 4,
        slidesToScroll: 1,
        autoplay: false,
        infinite: true,
        speed: 300,
        dots: false,
        arrows: true,
        appendArrows: $nav ? $nav : false,
        responsive: [
          {
            breakpoint: 991,
            settings: {
              slidesToShow: 2,
              slidesToScroll: 1,
            },
          },
          {
            breakpoint: 480,
            settings: {
              slidesToShow: 1,
              slidesToScroll: 1,
            },
          },
        ],
      });
    });

    // Products Widget Slick
    $(".products-widget-slick").each(function () {
      var $this = $(this),
        $nav = $this.attr("data-nav");

      $this.slick({
        infinite: true,
        autoplay: true,
        speed: 300,
        dots: false,
        arrows: true,
        appendArrows: $nav ? $nav : false,
      });
    });

    /////////////////////////////////////////

    // Product Main img Slick
    $("#product-main-img").slick({
      infinite: true,
      speed: 300,
      dots: false,
      arrows: true,
      fade: true,
      asNavFor: "#product-imgs",
    });

    // Product imgs Slick
    $("#product-imgs").slick({
      slidesToShow: 3,
      slidesToScroll: 1,
      arrows: true,
      centerMode: true,
      focusOnSelect: true,
      centerPadding: 0,
      vertical: true,
      asNavFor: "#product-main-img",
      responsive: [
        {
          breakpoint: 991,
          settings: {
            vertical: false,
            arrows: false,
            dots: true,
          },
        },
      ],
    });

    // Product img zoom
    var zoomMainProduct = document.getElementById("product-main-img");
    if (zoomMainProduct) {
      $("#product-main-img .product-preview").zoom();
    }

    /////////////////////////////////////////

    // Input number
    $(".input-number").each(function () {
      var $this = $(this),
        $input = $this.find('input[type="number"]'),
        up = $this.find(".qty-up"),
        down = $this.find(".qty-down");

      down.on("click", function () {
        var value = parseInt($input.val()) - 1;
        value = value < 1 ? 1 : value;
        $input.val(value);
        $input.change();
        updatePriceSlider($this, value);
      });

      up.on("click", function () {
        var value = parseInt($input.val()) + 1;
        $input.val(value);
        $input.change();
        updatePriceSlider($this, value);
      });
    });

    var priceInputMax = document.getElementById("price-max"),
      priceInputMin = document.getElementById("price-min");

    priceInputMax.addEventListener("change", function () {
      updatePriceSlider($(this).parent(), this.value);
    });

    priceInputMin.addEventListener("change", function () {
      updatePriceSlider($(this).parent(), this.value);
    });

    function updatePriceSlider(elem, value) {
      if (elem.hasClass("price-min")) {
        console.log("min");
        priceSlider.noUiSlider.set([value, null]);
      } else if (elem.hasClass("price-max")) {
        console.log("max");
        priceSlider.noUiSlider.set([null, value]);
      }
    }

    // Price Slider
    var priceSlider = document.getElementById("price-slider");
    if (priceSlider) {
      noUiSlider.create(priceSlider, {
        start: [1, 999],
        connect: true,
        step: 1,
        range: {
          min: 1,
          max: 999,
        },
      });

      priceSlider.noUiSlider.on("update", function (values, handle) {
        var value = values[handle];
        handle ? (priceInputMax.value = value) : (priceInputMin.value = value);
      });
    }

    /////////////////////////////////////////////
  });
})(jQuery);

///////////////////////////////////////
////////////// Lọc THEO DANH MỤC ///////////////
//////////////////////////////////////

function updateCategoryFilter(checkbox, slug) {
  const url = new URL(window.location);
  let categories = url.searchParams.getAll("category");
  if (checkbox.checked) {
    if (!categories.includes(slug)) {
      categories.push(slug);
    }
  } else {
    categories = categories.filter((cat) => cat !== slug);
  }
  url.searchParams.delete("category");
  categories.forEach((cat) => url.searchParams.append("category", cat));
  window.location.href = url.toString();
}

///////////////////////////////////////
////////////// GIỎ HÀNG ///////////////
//////////////////////////////////////

function updateTotalComics() {
  $.ajax({
    url: "/cart/total",
    type: "GET",
    data: {
      csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr("content"),
    },
    success: function (response) {
      if (response.status === "success") {
        $(".qty.update-total").text(response.total_items);
        const formattedPrice = Number(response.total_price).toLocaleString(
          "en-US"
        );
        $("#cart-summary").html(`
      <small>Đã chọn ${response.total_items} sản phẩm</small>
      <h5>Tổng: ${formattedPrice}đ</h5>
    `);
      }
    },
    error: function () {
      toastr.error("Không thể lấy thông tin giỏ hàng.");
    },
  });
}

function updateCartDropdown() {
  $.ajax({
    url: "/cart/dropdown",
    type: "GET",
    success: function (response) {
      if (response.status === "success") {
        $(".cart-dropdown").html(response.html);
      }
    },
    error: function () {
      toastr.error("Lỗi khi cập nhật giỏ hàng.");
    },
  });
}

function updateCartDetail() {
  $.ajax({
    url: "/cart/detail-partial",
    type: "GET",
    success: function (response) {
      if (response.status === "success") {
        $("#cart-detail-content").html(response.html);
      }
    },
    error: function () {
      toastr.error("Lỗi khi cập nhật chi tiết giỏ hàng.");
    },
  });
}

function addToCart(comicId, quantity) {
  quantity = Number(quantity);
  comicId = Number(comicId);
  if (!Number.isInteger(quantity) || quantity < 1) {
    toastr.error("Số lượng không hợp lệ.");
    return;
  }

  $.ajax({
    url: `/cart/add/${comicId}`,
    type: "POST",
    data: {
      csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr("content"),
      quantity: quantity,
    },
    success: function (response) {
      if (response.status === "success") {
        toastr.success(response.message);
        updateTotalComics();
        updateCartDropdown();
      } else {
        toastr.error(response.message);
      }
    },
    error: function (xhr) {
      if (xhr.status === 400) {
        toastr.error("Không đủ số lượng trong kho.");
      } else {
        toastr.error("Lỗi khi thêm sản phẩm vào giỏ hàng.");
      }
    },
  });
}

function removeFromCart(comicId) {
  $.ajax({
    url: `/cart/remove/${comicId}`,
    type: "POST",
    data: {
      csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr("content"),
    },
    success: function (response) {
      if (response.status === "success") {
        toastr.info(response.message);
        // $(`.product-widget[data-comic-id="${comicId}"]`).remove();
        // $(`.comic-cart-detail[data-comic-id="${comicId}"]`).remove();
        updateTotalComics();
        updateCartDropdown();
        updateCartDetail();
      } else {
        toastr.error(response.message);
      }
    },
    error: function () {
      toastr.error("Lỗi khi xóa sản phẩm vào giỏ hàng.");
    },
  });
}

function updateComicQuantity(comicId, newQuantity) {
  $.ajax({
    url: `/cart/update/${comicId}`,
    type: "POST",
    data: {
      csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr("content"),
      quantity: newQuantity,
    },
    success: function (response) {
      if (response.status === "success") {
        toastr.success(response.message);
        updateCartDropdown();
        updateCartDetail();
      } else {
        toastr.error(response.message);
      }
    },
    error: function () {
      toastr.error(
        "Lỗi khi cập nhật số lượng sản phẩm vào giỏ hàng.",
        "Thông báo"
      );
    },
  });
}

////////////////////////////////////////////////////
/////////////////// YÊU THÍCH /////////////////////
///////////////////////////////////////////////////

// function updateFavoriteStatus() {
//   if ($(".heart-icon").length === 0) {
//     return; // Bỏ qua nếu chưa đăng nhập (không có biểu tượng trái tim)
//   }
//   $(".heart-icon").each(function () {
//     let icon = $(this);
//     let comicId = icon.data("comic-id");

//     $.ajax({
//       url: `/favorites/check/${comicId}`,
//       type: "GET",
//       // data: {
//       //   csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr("content"),
//       // },
//       success: function (response) {
//         if (response.is_favorite) {
//           icon.removeClass("far").addClass("fas").addClass("liked");
//         }
//       },
//       error: function () {
//         toastr.error("Lỗi khi kiểm tra trạng thái yêu thích.");
//       },
//     });
//   });
// }

function updateFavoriteStatus() {
  // Thu thập tất cả comic_ids từ các heart-icon
  let comicIds = [];
  $(".heart-icon").each(function () {
    let comicId = $(this).data("comic-id");
    if (comicId) {
      comicIds.push(comicId);
    }
  });

  if (comicIds.length === 0) {
    return; // Không có comic nào
  }

  // Gửi yêu cầu AJAX duy nhất với danh sách comic_ids
  $.ajax({
    url: "/favorites/check-multiple",
    type: "GET",
    traditional: true,
    data: { comic_ids: comicIds }, // Gửi dưới dạng query params: ?comic_ids=1&comic_ids=2&...
    success: function (response) {
      if (response.status === "success") {
        let favoritesMap = response.favorites; // Dict như {"1": true, "2": false, ...}

        $(".heart-icon").each(function () {
          let icon = $(this);
          let comicId = icon.data("comic-id").toString(); // Chuyển sang string để match key
          if (favoritesMap[comicId]) {
            icon.removeClass("far").addClass("fas").addClass("liked");
          }
        });
      }
    },
    error: function () {
      toastr.error("Lỗi khi kiểm tra trạng thái yêu thích.");
    },
  });
}

function updateTotalFavorites() {
  $.ajax({
    url: "/favorites/total",
    type: "GET",
    success: function (response) {
      if (response.status === "success") {
        $("#favorite-total").text(response.total);
      }
    },
    error: function () {
      toastr.error("Không thể lấy tổng số yêu thích.");
    },
  });
}

function addToFavorite(comicId) {
  $.ajax({
    url: `/favorites/add/${comicId}`,
    type: "POST",
    data: {
      csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr("content"),
    },
    success: function (response) {
      if (response.status === "success") {
        toastr.success(response.message);
        $(`.heart-icon[data-comic-id="${comicId}"]`)
          .removeClass("far")
          .addClass("fas")
          .addClass("liked");

        updateTotalFavorites();
      } else {
        toastr.error(response.message);
      }
    },
    error: function () {
      toastr.error("Đã xảy ra lỗi khi thêm yêu thích.");
    },
  });
}

function removeFromFavorite(comicId) {
  $.ajax({
    url: `/favorites/remove/${comicId}`,
    type: "POST",
    data: {
      csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr("content"),
    },
    success: function (response) {
      if (response.status === "success") {
        toastr.info(response.message);
        $(`.heart-icon[data-comic-id="${comicId}"]`)
          .removeClass("fas")
          .addClass("far")
          .removeClass("liked");

        updateTotalFavorites();

        $(`.comic_favorite_list[data-comic-id="${comicId}"]`).remove();
        if ($(".comic_favorite_list").length === 0) {
          $(".data-comic-favorite").html(
            '<p class="text-center">Bạn chưa có truyện nào trong danh sách yêu thích.</p>'
          );
        }
      } else {
        toastr.error(response.message);
      }
    },
    error: function () {
      toastr.error("Đã xảy ra lỗi khi xóa yêu thích.");
    },
  });
}

function removeFromFavoriteAddToCart(comicId) {
  $.ajax({
    url: `/favorites/remove/${comicId}`,
    type: "POST",
    data: {
      csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr("content"),
    },
    success: function (response) {
      if (response.status === "success") {
        // toastr.info(response.message);
        $(`.heart-icon[data-comic-id="${comicId}"]`)
          .removeClass("fas")
          .addClass("far")
          .removeClass("liked");

        updateTotalFavorites();

        $(`.comic_favorite_list[data-comic-id="${comicId}"]`).remove();
        if ($(".comic_favorite_list").length === 0) {
          $(".data-comic-favorite").html(
            '<p class="text-center">Bạn chưa có truyện nào trong danh sách yêu thích.</p>'
          );
        }
      } else {
        toastr.error(response.message);
      }
    },
    error: function () {
      toastr.error("Đã xảy ra lỗi khi xóa yêu thích.");
    },
  });
}

function addAndRemove(comicId) {
  addToCart(comicId, 1);
  removeFromFavoriteAddToCart(comicId);
}

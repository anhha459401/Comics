$(document).ready(function () {
  // setTimeout(function () {
  //   $.ajax({
  //     url: "/comics/track-view",
  //     method: "POST",
  //     data: {
  //       comic_slug: "{{ comic.slug }}",
  //       csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr("content"),
  //     },
  //     success: function (response) {
  //       console.log("View recorded");
  //     },
  //     error: function () {
  //       console.log("Error recording view");
  //     },
  //   });
  // }, 10000); // Ghi lại sau 10 giây

  // Hàm load lại rating
  function loadRating(comicId) {
    $.ajax({
      url: `/ratings/rating-data/${comicId}`,
      method: "GET",
      success: function (response) {
        let ratingHtml = "";
        for (let i = 5; i >= 1; i--) {
          let starsHtml = Array(i)
            .fill('<i class="fas fa-star"></i>')
            .concat(Array(5 - i).fill('<i class="far fa-star"></i>'))
            .join("");
          ratingHtml += `
            <li class="rating-row">
              <div class="rating-stars">${starsHtml}</div>
              <div class="rating-progress">
                <div style="width: ${
                  response.rating_percentages[5 - i]
                }%;"></div>
              </div>
              <span class="sum">${response.rating_counts[5 - i]}</span>
            </li>
          `;
        }
        $("#rating-list").html(ratingHtml);
      },
      error: function (xhr) {
        toastr.error("Đã có lỗi khi tải dữ liệu đánh giá!", "Lỗi");
      },
    });
  }

  // Xử lý submit đánh giá
  $(".review-form").on("submit", function (e) {
    e.preventDefault();

    let comicId = $("#review-form").data("comic-id");
    let review = $(this).find("textarea[name='review']").val().trim();
    let rating = $(this).find("input[name='rating']:checked").val();

    if (!rating) {
      toastr.info("Vui lòng chọn số sao đánh giá!");
      return;
    }

    $.ajax({
      url: `/ratings/add/${comicId}`,
      method: "POST",
      data: {
        review: review,
        rating: rating,
        csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr("content"),
      },
      success: function (response) {
        if (response.status === "success") {
          toastr.success(response.message, "Thông báo");
          // Cập nhật giao diện
          $(".total_reviews").text(response.total_reviews);

          $(".product-rating-ctn .product-rating").html(
            response.average_rating +
              ' <i class="fas fa-star"></i> (' +
              response.total_reviews +
              " đánh giá)"
          );

          $(".rating-avg span").text(response.average_rating);

          $(".rating-avg .rating-stars").html(
            Array(Math.floor(response.average_rating))
              .fill('<i class="fa fa-star"></i>')
              .concat(
                Array(5 - Math.floor(response.average_rating)).fill(
                  '<i class="fa fa-star-o"></i>'
                )
              )
              .join("")
          );

          $("#reviews ul.reviews").load(
            location.href + " #reviews ul.reviews > *"
          ); // Tải lại reviews

          $(".review-form")[0].reset();

          loadRating(comicId);

          if (response.has_review) {
            $("textarea[name='review']").val(response.comment);
            $(`input[name='rating'][value='${response.rating}']`).prop(
              "checked",
              true
            );
            $(".primary-btn").text("Cập nhật");
          } else {
            $(".review-form")[0].reset();
          }
        }
      },
      error: function (xhr) {
        let errorMessage = "Đã có lỗi xảy ra!";
        if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMessage = xhr.responseJSON.message;
        }
        toastr.error(errorMessage, "Lỗi");
      },
    });
  });

  // Xử lý phân trang reviews bằng AJAX
  $(document).on("click", ".pagination-link", function (e) {
    e.preventDefault();
    let comicId = $("#review-form").data("comic-id");
    let page = $(this).data("page");

    $.ajax({
      url: `/ratings/reviews/${comicId}`,
      method: "GET",
      data: { page: page },
      success: function (response) {
        let reviewsHtml = "";
        response.reviews.forEach(function (review) {
          let starsHtml = Array(review.rating)
            .fill('<i class="fa fa-star"></i>')
            .concat(
              Array(5 - review.rating).fill(
                '<i class="fa fa-star-o empty"></i>'
              )
            )
            .join("");
          reviewsHtml += `
            <li>
              <div class="review-heading">
                <h5 class="name">${review.username}</h5>
                <p class="date">${review.date}</p>
                <div class="review-rating">${starsHtml}</div>
              </div>
              <div class="review-body">
                <p>${review.comment}</p>
              </div>
            </li>
          `;
        });
        $("#reviews ul.reviews").html(reviewsHtml); // Cập nhật danh sách reviews

        // Cập nhật phân trang
        let paginationHtml = "";
        if (response.has_previous) {
          paginationHtml += `<li><a href="#" data-page="${response.previous_page_number}" class="pagination-link"><</a></li>`;
        }
        for (let i = 1; i <= response.total_pages; i++) {
          paginationHtml += `<li class="${
            response.current_page === i ? "active" : ""
          }">
            <a href="#" data-page="${i}" class="pagination-link">${i}</a>
          </li>`;
        }
        if (response.has_next) {
          paginationHtml += `<li><a href="#" data-page="${response.next_page_number}" class="pagination-link">></a></li>`;
        }
        $("#reviews ul.reviews-pagination").html(paginationHtml); // Cập nhật phân trang
      },
      error: function (xhr) {
        toastr.error("Đã có lỗi khi tải đánh giá!", "Lỗi");
      },
    });
  });
});

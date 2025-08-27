function calculateAge(birthDateStr) {
  const birthDate = new Date(birthDateStr);
  const today = new Date();

  let age = today.getFullYear() - birthDate.getFullYear();
  const currentMonth = today.getMonth();
  const currentDay = today.getDate();

  if (
    currentMonth < birthDate.getMonth() ||
    (currentMonth === birthDate.getMonth() && currentDay < birthDate.getDate())
  ) {
    age--;
  }

  return age;
}

function isValidEmail(email) {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
}

$(document).ready(function () {
  // Đăng ký
  $("#register-btn").click(function () {
    let dob = $("#dob").val();
    let address = $("#address").val();
    let tel = $("#tel").val();
    let email = $("#email").val();
    let username = $("#username").val();
    let password = $("#password").val();
    let confirm_password = $("#confirm_password").val();

    let birthDateTime = new Date(dob).setHours(0, 0, 0, 0);
    let toDay = new Date().setHours(0, 0, 0, 0);
    if (
      dob === "" ||
      address === "" ||
      tel === "" ||
      email === "" ||
      username === "" ||
      password === "" ||
      confirm_password === ""
    ) {
      toastr.error("Hãy nhập đầy đủ các trường bắt buộc!");
      return false;
    } else if (birthDateTime >= toDay) {
      toastr.error("Ngày sinh không hợp lệ!");
      return false;
    } else if (calculateAge(dob) < 18) {
      toastr.error("Bạn chưa đủ 18 tuổi để đăng ký tài khoản!");
      return false;
    } else if (isNaN(tel) || tel.length < 8 || tel.length > 15) {
      toastr.error("Số điện thoại không hợp lệ!");
      return false;
    } else if (!isValidEmail(email)) {
      toastr.error("Email không hợp lệ!");
      return false;
    } else if (password.length < 6) {
      toastr.error("Mật khẩu phải có ít nhất 6 ký tự!");
      return false;
    } else if (password !== confirm_password) {
      toastr.error("Mật khẩu không trùng khớp!");
      return false;
    }
  });

  // Thay đổi các nút cập nhật thông tin
  $("#toggle-edit-profile").click(function () {
    $("#change-password-form").slideUp();
    $("#toggle-change-password").removeClass("active");
    $("#edit-profile-form").slideToggle(function () {
      if ($(this).is(":visible")) {
        $("#toggle-edit-profile").addClass("active");
      } else {
        $("#toggle-edit-profile").removeClass("active");
      }
    });
  });

  $("#toggle-change-password").click(function () {
    $("#edit-profile-form").slideUp();
    $("#toggle-edit-profile").removeClass("active");
    $("#change-password-form").slideToggle(function () {
      if ($(this).is(":visible")) {
        $("#toggle-change-password").addClass("active");
      } else {
        $("#toggle-change-password").removeClass("active");
      }
    });
  });

  // Chỉnh sửa thông tin
  $("#edit-profile-btn").click(function () {
    let dob = $("#edit-dob").val();
    let gender = $("#edit-gender").val();
    let address = $("#edit-address").val();
    let tel = $("#edit-tel").val();
    let email = $("#edit-email").val();

    if (
      dob === "" ||
      gender === "" ||
      address === "" ||
      tel === "" ||
      email === ""
    ) {
      toastr.error("Hãy nhập đầy đủ các trường!");
      return false;
    } else if (isNaN(tel) || tel.length < 8 || tel.length > 15) {
      toastr.error("Số điện thoại không hợp lệ!");
      return false;
    } else if (!isValidEmail(email)) {
      toastr.error("Email không hợp lệ!");
      return false;
    }
  });

  // Đổi mật khẩu
  $("#change-password-btn").click(function () {
    let current_password = $("#current-password").val();
    let new_password = $("#new-password").val();
    let confirm_new_password = $("#confirm-new-password").val();

    if (
      current_password === "" ||
      new_password === "" ||
      confirm_new_password === ""
    ) {
      toastr.error("Hãy nhập đầy đủ các trường!");
      return false;
    } else if (new_password.length < 6) {
      toastr.error("Mật khẩu phải có ít nhất 6 ký tự!");
      return false;
    } else if (new_password != confirm_new_password) {
      toastr.error("Mật khẩu mới không khớp.");
      return false;
    }
  });

  // Quên mật khẩu
  $("#forgot-password-btn").click(function () {
    let email = $("#forgot-email").val();

    if (email === "") {
      toastr.error("Vui lòng nhập email.");
      return false;
    } else if (!isValidEmail(email)) {
      toastr.error("Email không hợp lệ!");
      return false;
    }
  });

  // Đặt lại mật khẩu
  $("#reset-password-btn").click(function () {
    let new_password = $("#reset-new-password").val();
    let confirm_new_password = $("#reset-confirm-new-password").val();

    if (new_password === "" || confirm_new_password === "") {
      toastr.error("Hãy nhập đầy đủ các trường!");
      return false;
    } else if (new_password.length < 6) {
      toastr.error("Mật khẩu phải có ít nhất 6 ký tự!");
      return false;
    } else if (new_password != confirm_new_password) {
      toastr.error("Mật khẩu mới không khớp.");
      return false;
    }
  });

  // Đăng nhập sau khi đặt lại mật khẩu
  $("#login_required-btn").click(function () {
    let username = $("#username-login_required").val();
    let password = $("#password-login_required").val();

    if (username === "" || password === "") {
      toastr.error("Vui lòng nhập đầy đủ thông tin.");
      return false;
    }
  });

  // Xác nhận thanh toán đơn hàng
  $("#confirm-payment").click(function () {
    let address = $("#order-address").val();
    let tel = $("#order-tel").val();
    if (address === "" || tel === "") {
      toastr.error("Vui lòng nhập đầy đủ thông tin.");
      return false;
    } else if (isNaN(tel) || tel.length < 8 || tel.length > 15) {
      toastr.error("Số điện thoại không hợp lệ!");
      return false;
    }
  });
});

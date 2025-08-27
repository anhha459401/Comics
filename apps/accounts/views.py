from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import UserProfile, PasswordResetToken
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


# Create your views here.
def register(request):
    if request.method == "POST":
        last_name = request.POST.get("last_name")
        first_name = request.POST.get("first_name")
        dob = request.POST.get("dob")
        gender = request.POST.get("gender")
        address = request.POST.get("address")
        phone_number = request.POST.get("tel")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Mật khẩu không khớp.")
            return render(request, "accounts/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại.")
            return render(request, "accounts/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email đã được sử dụng.")
            return render(request, "accounts/register.html")

        if UserProfile.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Số điện thoại đã được sử dụng.")
            return render(request, "accounts/register.html")

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            UserProfile.objects.create(
                user=user,
                date_of_birth=dob,
                gender=gender,
                address=address,
                phone_number=phone_number,
            )

            login(request, user)
            messages.success(
                request, "Đăng ký thành công! Chào mừng bạn đến với website."
            )
            return redirect("core:index")
        except ValidationError as e:
            messages.error(request, f"Lỗi: {str(e)}")
            return render(request, "accounts/register.html")

    return render(request, "accounts/register.html")


from django.contrib.auth import get_user_model

User = get_user_model()


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username-login")
        password = request.POST.get("password-login")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            if not user.is_active:
                messages.error(
                    request,
                    "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.",
                )
            else:
                user_auth = authenticate(request, username=username, password=password)
                if user_auth is not None:
                    login(request, user_auth)
                    messages.success(request, "Đăng nhập thành công!")
                    next_url = request.GET.get(
                        "next", request.META.get("HTTP_REFERER", reverse("core:index"))
                    )
                    if not next_url.startswith(("http:", "https:")) and next_url:
                        return redirect(next_url)
                    return redirect(reverse("core:index"))
                else:
                    messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")

        return redirect(request.META.get("HTTP_REFERER", reverse("core:index")))

    return redirect(request.META.get("HTTP_REFERER", reverse("core:index")))


@login_required
def logout_view(request):
    logout(request)
    return redirect("core:index")


@login_required
def profile(request):
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=request.user,
            date_of_birth=None,
            gender="male",
            address="",
            phone_number="",
        )
        messages.info(
            request, "Hồ sơ đã được tạo mặc định. Vui lòng cập nhật thông tin."
        )
    return render(request, "accounts/profile.html", {"user_profile": user_profile})


@login_required
def update_profile(request):
    if request.method == "POST":
        # Lấy dữ liệu từ form
        last_name = request.POST.get("last_name")
        first_name = request.POST.get("first_name")
        dob = request.POST.get("dob")
        gender = request.POST.get("gender")
        address = request.POST.get("address")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        password = request.POST.get("current-password")  # Mật khẩu hiện tại từ form

        # Lấy thông tin người dùng và hồ sơ
        user = request.user
        try:
            user_profile = user.profile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(
                user=user,
                date_of_birth=dob,
                gender=gender,
                address=address,
                phone_number=phone_number,
            )

        # Kiểm tra xem email hoặc số điện thoại có thay đổi không
        email_changed = user.email != email
        phone_changed = user_profile.phone_number != phone_number

        # Yêu cầu mật khẩu nếu email hoặc số điện thoại thay đổi
        if email_changed or phone_changed:
            if not password:
                messages.error(
                    request,
                    "Vui lòng nhập mật khẩu để cập nhật email hoặc số điện thoại.",
                )
                return redirect("accounts:profile")
            if not user.check_password(password):
                messages.error(request, "Mật khẩu không đúng.")
                return redirect("accounts:profile")

        # Kiểm tra email trùng lặp (ngoại trừ người dùng hiện tại)
        if (
            email_changed
            and User.objects.filter(email=email).exclude(id=user.id).exists()
        ):
            messages.error(request, "Email đã được sử dụng bởi tài khoản khác.")
            return redirect("accounts:profile")

        # Kiểm tra số điện thoại trùng lặp (ngoại trừ hồ sơ hiện tại)
        if (
            phone_changed
            and UserProfile.objects.filter(phone_number=phone_number)
            .exclude(user=user)
            .exists()
        ):
            messages.error(request, "Số điện thoại đã được sử dụng bởi tài khoản khác.")
            return redirect("accounts:profile")

        try:
            # Cập nhật thông tin cho model User
            user.last_name = last_name
            user.first_name = first_name
            user.email = email
            user.save()

            # Cập nhật thông tin cho model UserProfile
            user_profile.date_of_birth = dob
            user_profile.gender = gender
            user_profile.address = address
            user_profile.phone_number = phone_number
            user_profile.save()

            messages.success(request, "Cập nhật thông tin thành công!")
            return redirect("accounts:profile")

        except ValidationError as e:
            messages.error(request, f"Lỗi: {str(e)}")
            return redirect("accounts:profile")

    return redirect("accounts:profile")


@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current-password")
        new_password = request.POST.get("new-password")
        confirm_new_password = request.POST.get("confirm-new-password")

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Mật khẩu hiện tại không đúng.")
            return redirect("accounts:profile")

        if new_password != confirm_new_password:
            messages.error(request, "Mật khẩu mới không khớp.")
            return redirect("accounts:profile")

        try:
            user.set_password(new_password)
            user.save()

            update_session_auth_hash(request, user)

            messages.success(request, "Đổi mật khẩu thành công!")
            return redirect("accounts:profile")
        except ValidationError as e:
            messages.error(request, f"Lỗi: {str(e)}")
            return redirect("accounts:profile")

    return redirect("accounts:profile")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email không tồn tại trong hệ thống.")
            return redirect("accounts:forgot_password")

        token = PasswordResetToken.objects.create(user=user)

        reset_url = request.build_absolute_uri(
            reverse("accounts:reset_password") + f"?token={token.token}"
        )

        subject = "Yêu cầu đặt lại mật khẩu"
        message = f"""
        Xin chào {user.username},

        Bạn đã yêu cầu đặt lại mật khẩu. vui lòng nhấp vào liên kết bên dưới để đặt lại mật khẩu:
        {reset_url}

        Liên kết này có hiệu lực trong 1 giờ. Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.

        Trân trọng,
        Đội ngũ Comics
        """

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.success(
                request,
                "Email đặt lại mật khẩu đã được gửi. Vui lòng kiểm tra hộp thư của bạn.",
            )
            return redirect("accounts:forgot_password")
        except Exception as e:
            messages.error(request, f"Lỗi khi gửi email: {str(e)}")
            return redirect("accounts:forgot_password")

    return render(request, "accounts/forgot_password.html")


def reset_password(request):
    token = request.GET.get("token")
    if not token:
        messages.error(request, "Liên kết không hợp lệ.")
        return redirect("accounts:forgot_password")

    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if reset_token.is_expired():
            messages.error(
                request, "Liên kết đã hết hạn. Vui lòng yêu cầu đặt lại mật khẩu mới."
            )
            return redirect("accounts:forgot_password")
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Liên kết không hợp lệ.")
        return redirect("accounts:forgot_password")

    if request.method == "POST":
        new_password = request.POST.get("new-password")
        confirm_new_password = request.POST.get("confirm-new-password")

        if new_password != confirm_new_password:
            messages.error(request, "Mật khẩu mới không khớp.")
            return render(request, "accounts/reset_password.html", {"token": token})

        try:
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            reset_token.delete()
            messages.success(
                request, "Đặt lại mật khẩu thành công! Vui lòng đăng nhập."
            )
            return redirect("accounts:login_required")
        except ValidationError as e:
            messages.error(request, f"Lỗi: {str(e)}")
            return render(request, "accounts/reset_password.html", {"token": token})

    return render(request, "accounts/reset_password.html", {"token": token})


def login_required(request):
    if request.method == "POST":
        username = request.POST.get("username-login")
        password = request.POST.get("password-login")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Đăng nhập thành công!")
            return redirect("core:index")
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
            return render(request, "accounts/login_required.html")

    return render(request, "accounts/login_required.html")

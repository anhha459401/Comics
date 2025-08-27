TABLE_CATEGORY_SHOW = "Categories"
TABLE_COMIC_SHOW = "Comics"
TABLE_USER_PROFILE_SHOW = "UserProfile"
TABLE_CART_SHOW = "Cart"
TABLE_ORDER_SHOW = "Order"
TABLE_ORDER_ITEM_SHOW = "OrderItem"
TABLE_RATING_SHOW = "Rating"
TABLE_FAVORITE_SHOW = "Favorite"
TABLE_VIEW_HISTORY_SHOW = "View Histories"
TABLE_PASSWORD_RESET_TOKEN_SHOW = "Password Reset Token"

PAYMENT_STATUS_CHOICES = [
    ("unpaid", "Chưa thanh toán"),
    ("paid", "Đã thanh toán"),
    ("refunded", "Đã hoàn tiền"),
    ("failed", "Thất bại"),
]

ORDER_STATUS_CHOICES = [
    ("pending", "Chờ xử lý"),
    ("confirmed", "Đã xác nhận"),
    ("preparing", "Đang chuẩn bị hàng"),
    ("shipping", "Đang giao hàng"),
    ("delivered", "Giao hàng thành công"),
    ("cancelled", "Đã hủy"),
    ("returned", "Đã trả hàng"),
]

ORDER_STATUS_FLOW = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["preparing", "cancelled"],
    "preparing": ["shipping", "cancelled"],
    "shipping": ["delivered", "returned"],
    "delivered": [],
    "cancelled": [],
    "returned": [],
}


PAYMENT_METHOD_CHOICES = [
    ("cod", "Thanh toán bằng tiền mặt"),
    ("vnpay", "Thanh toán qua VNPay"),
]
APP_VALUE_RATING_CHOICES = [(i, i) for i in range(1, 6)]
APP_VALUE_STATUS_DEFAULT = "pending"
APP_VALUE_STATUS_DEFAULT_PAYMENT = "unpaid"
APP_VALUE_PAYMENT_METHOD_DEFAULT = "cod"

ADMIN_SRC_JS = (
    "js/jquery-3.6.0.min.js",
    "js/slugify.min.js",
    "js/general.js",
    "js/hide_save_buttons.js",
)
ADMIN_SRC_CSS = {"all": ("css/custom.css",)}

ADMIN_SRC_JS_COMIC = (
    "js/jquery-3.6.0.min.js",
    "js/slugify.min.js",
    "js/general.js",
)
ADMIN_SRC_CSS_COMIC = {"all": ("css/custom_comic.css",)}

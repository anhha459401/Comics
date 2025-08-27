import uuid, os


def get_file_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("comics/covers/", filename)


def get_file_path_intro(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("comics/intro/", filename)


def format_vnd(value):
    try:
        value = float(value)
        return "{:,.0f}đ".format(value)
    except (ValueError, TypeError):
        return "0đ"

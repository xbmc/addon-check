def colorPrint(string, color):
    print("\033[%sm%s\033[0m" % (color, string))


def check_config(config, value):
    if config is None:
        return False
    elif value in config and config[value]:
        return True
    else:
        return False


def has_transparency(im):
    try:
        if im.mode == "RGBA":
            alpha = im.split()[-1]
            listdata = list(alpha.getdata())
            first_transparent_pixel = next(x[0]
                                           for x in enumerate(listdata) if x[1] < 255)
            if first_transparent_pixel is not None:
                return True
        else:
            return False
    except StopIteration:
        return False

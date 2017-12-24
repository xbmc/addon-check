def colorPrint(string, color):
    print("\033[%sm%s\033[0m" % (color, string))


def check_config(config, value):
    if config is None:
        return False
    elif value in config and config[value]:
        return True
    else:
        return False

def colorPrint(string, color):
    print("\033[%sm%s\033[0m" % (color, string))

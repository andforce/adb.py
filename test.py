def test():
    log = "\033[0;%sm%s\033[0m" % ("33", "%20s" % "nihao")
    # log = log % "6666"
    print(log)


test()

print("\033[0;%sm%s\033[0m")

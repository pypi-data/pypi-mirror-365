import engine

def main():
    scr = engine.AsciiScreen()
    title = engine.TextStyle("white", "black", engine.Styles.UNDERLINE)
    subtitle = engine.TextStyle("white", "black")

    light = "░▒▓█"
    while True:
        key = scr.get_key()
        w, h = scr.getHW()
        if key == "q":
            scr.quit()
            break

        scr.setStr(0, 0, "PyConsoleEngine, (c) Kirill Fridrih", style=title)
        scr.setStr(0, 1, "demo 1", style=subtitle)
        for fgid, fg in enumerate(engine.Colors.ALL_COLORS):
            for bgid, bg in enumerate(engine.Colors.ALL_COLORS):
                scr.setStr(0 + len(light) * bgid, 2 + fgid, "░▒▓█", style=engine.TextStyle(fg, bg))
        scr.update() # буферизация есть

if __name__ == "__main__":
    main()
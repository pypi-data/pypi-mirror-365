# dont edit! This is a blank
import engine


def main():
    scr = engine.AsciiScreen()
    running = True
    while running:
        key = scr.get_key(.1)
        w, h = scr.getHW()

        if key == "q":
            running = False
        # drawing
        scr.setStr(0, 0, "PyConsoleEngine, (c) Kirill Fridrih")
        scr.update()

    scr.quit()


if __name__ == '__main__':
    main()

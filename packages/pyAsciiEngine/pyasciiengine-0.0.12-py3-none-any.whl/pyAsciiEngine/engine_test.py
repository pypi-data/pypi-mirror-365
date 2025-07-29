from engine import ConsoleScreen, Colors, Styles, TextStyle, Anchors, Symbol



def main():
    sc = ConsoleScreen()
    st = TextStyle(Colors.CYAN, Colors.BLACK, Styles.BOLD)
    key = None
    while True:
        x, y = sc.get_sizes()
        sc.set_str(20,0,f"key: {repr(key)}")
        sc.set_str(x // 2, y-1, f"Sizes: {x} {y}", anchor=Anchors.CENTER_X_ANCHOR, style=st)
        sc.draw_rectangle(1, 1, 3,20, Symbol("@", "red"), isFill=False)

        key = sc.get_key()
        sc.update()
        if key == "q":
            break

if __name__ == '__main__':
    main()
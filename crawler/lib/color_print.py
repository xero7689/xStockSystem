red = '\x1b[{};{};{}m'.format(0, 31, 40)
green = '\x1b[{};{};{}m'.format(0, 32, 40)
yellow = '\x1b[{};{};{}m'.format(0, 33, 40)
blue = '\x1b[{};{};{}m'.format(0, 34, 40)
grey = '\x1b[{};{};{}m'.format(0, 35, 40)
white = '\x1b[{};{};{}m'.format(0, 37, 40)

colors = {
        'red': red,
        'green': green,
        'yellow': yellow,
        'blue': blue,
        'grey': grey
        }

def color_print(msg, color='white'):
    c = colors[color]
    print("{}{}{}".format(c, msg, '\x1b[0m'))



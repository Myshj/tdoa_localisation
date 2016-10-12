from Locator import Locator

l = Locator(
    [
        {
            'x': 0,
            'y': 0
        },
        {
            'x': -100,
            'y': 100
        },
        {
            'x': 100,
            'y': 100
        },
        {
            'x': -100,
            'y': -100
        },
        {
            'x': 100,
            'y': -100
        }
    ], 1)

print(l.locate([38, 157.455, 157.455, 0, 0]))

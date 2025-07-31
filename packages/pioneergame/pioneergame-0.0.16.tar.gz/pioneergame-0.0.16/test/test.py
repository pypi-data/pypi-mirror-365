from pioneergame import Window, Label, Button, Rect, Sprite, explode, explosion_update

window = Window(1300, 700)
fps = 80

TILE = 10
SIZE = 64
btn = Button(window, window.width - 220, window.height - 60, 200, 40, title='copy to clipboard', border_width=2,
             font_size=20)

test = Rect(window, 10, 10, 100, 100)
sprite = Sprite(window, 'test.jpg')
sprite.attach_to(test)

while True:
    window.fill((80, 80, 100))

    window.set_caption(f'{window.get_fps():.1f}')

    # draw grid and field
    # window.draw_rect((220, 220, 220), (20, 20, 20))

    if window.get_mouse_button():
        explode(window, window.mouse_position(), 10, 'white')

    explosion_update()

    sprite.draw()

    btn.draw()

    if btn.get_pressed():
        btn.color = (100, 10, 10)

    if window.get_key('escape'):
        window.close()

    window.update(fps)

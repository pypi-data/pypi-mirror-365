������� ������ pygame ��� �����

### Blank. Empty window ###

```python
from pioneergame import Window

my_window = Window(1200, 700, 'my black window')  # ������ ������� ����

while True:  # ����������� ���� ����
    my_window.fill('black')  # ���������� ������ ������

    my_window.update(60)  # ���������� ������ � �������� 60 ������ � �������
```

#

### Drawing simple objects ###
![figures](https://github.com/chebur5581/pioneergame/blob/main/image/figures.png?raw=true)
```python
from pioneergame import Window, Rect, Circle

my_window = Window(1200, 700, 'my black window')  # ������ ������� ����

# �������� ������ �������������� � ������� 100 � ������� 50
block = Rect(my_window, x=10, y=40, width=100, height=50, color='blue')

# �������� ���������� �������� �������� 60 �� 60, ������� ����� ����� �������
moving_square = Rect(my_window, x=100, y=200, width=60, height=60, color='orange')

# �������� �������� ����� � �������� 20, ������� ���� ����� �������
moving_circle = Circle(my_window, x=1000, y=50, radius=20, color='red')

# �������� ������ ������ � �������� 80 � �������� ������ 5
bublik = Circle(my_window, x=500, y=350, radius=80, color='grey', thickness=5)

while True:  # ����������� ���� ����
    my_window.fill('black')  # ���������� ������ ������

    block.draw()  # ��������� ��������������
    moving_square.draw()  # ��������� ��������
    moving_circle.draw()  # ��������� �����
    bublik.draw()

    # ���� ������ ������� �������� ��������� ����� ��� ������ ������� ������, �� �� ������� ������� ������
    if moving_square.right < my_window.right:
        moving_square.x += 5  # �������� �������� ������ �� 1 �������

    moving_circle.x -= 1  # �������� ����� � ����
    moving_circle.y += 1  # �������� ����� ����

    my_window.update(60)  # ���������� ������ � �������� 60 ������ � �������

```

#

### Keyboard and text ###
![keyboard](https://github.com/chebur5581/pioneergame/blob/main/image/keyboard_and_text.png?raw=true)
```python
from pioneergame import Window, Label

my_window = Window(1200, 700, 'my black window')  # ������ ������� ����

# �������� ������ ������ �����
my_text = Label(my_window, x=300, y=350, text='����� ��������� ������, �����, ����� ��� ����', color='white')

while True:  # ����������� ���� ����
    my_window.fill('black')  # ���������� ������ ������

    my_text.draw()  # ��������� ������

    if my_window.get_key('left'):  # ���� ������ ��������� �����
        my_text.set_text('���� ������ ��������� �����')  # ��������� ������ ������
    if my_window.get_key('right'):  # ���� ������ ��������� ������
        my_text.set_text('���� ������ ��������� ������')
    if my_window.get_key('up'):  # ���� ������ ��������� �����
        my_text.set_text('���� ������ ��������� �����')
    if my_window.get_key('down'):  # ���� ������ ��������� ����
        my_text.set_text('���� ������ ��������� ����')

    my_window.update(60)  # ���������� ������ � �������� 60 ������ � �������
```

### Fireworks ###
![fireworks](https://github.com/chebur5581/pioneergame/blob/main/image/fireworks.png?raw=true)
```python
from pioneergame import Window, explode, explosion_update

my_window = Window(1200, 700, 'my black window')  # ������ ������� ����

while True:  # ����������� ���� ����
    my_window.fill('black')  # ���������� ������ ������

    if my_window.get_mouse_button('left'):  # ���� ���� ������ ����� ������ ����
        explode(my_window, pos=my_window.mouse_position(), size=5, color='orange')

    explosion_update()  # ��������� ���� �������

    my_window.update(60)  # ���������� ������ � �������� 60 ������ � �������
```

### Example. DVD screen ###
![dvd](https://github.com/chebur5581/pioneergame/blob/main/image/DVD.png?raw=true)
```python
from pioneergame import Window, Label

window = Window(1024, 768, 'DVD test')

dvd = Label(window, 10, 10, 'DVD', 'grey', font='Impact', size=70, italic=True)
state = Label(window, 10, 10, 'state: IDLE', 'grey', italic=True)

dx, dy = 3, 3

while True:
    window.fill('black')
    dvd.draw()
    state.draw()

    dvd.x += dx
    dvd.y += dy

    if dvd.left < window.left or dvd.right > window.right:
        dx *= -1
    if dvd.top < window.top or dvd.bottom > window.bottom:
        dy *= -1

    window.update(80)
```

#

### Ping Pong ###

![pong](https://github.com/chebur5581/pioneergame/blob/main/image/pong.png?raw=true)
```python
from pioneergame import Window, Circle, Rect, Label

window = Window(1024, 768)
fps = 80

pad1 = Rect(window, 50, 20, 20, 200, color='grey')
text1 = Label(window, 100, 10, text='0', color='darkgray', size=50)
score1 = 0

pad2 = Rect(window, 954, 20, 20, 200, color='grey')
text2 = Label(window, 900, 10, color='darkgray', size=50)
score2 = 0

ball = Circle(window, 100, 100, radius=10, color='grey')
ball_speed = 3

dx = ball_speed
dy = ball_speed

while True:
    window.fill('black')

    pad1.draw()
    text1.draw()
    text1.set_text(score1)

    pad2.draw()
    text2.draw()
    text2.set_text(score2)

    ball.draw()

    ball.x += dx
    ball.y += dy

    if ball.bottom > window.bottom:
        dy = -dy
    if ball.top < window.top:
        dy = -dy

    if ball.right > window.right:
        score1 = score1 + 1
        ball.x = 512
        ball.y = 344
    if ball.left < window.left:
        score2 = score2 + 1
        ball.x = 512
        ball.y = 344

    if window.get_key('w') and pad1.top > window.top:
        pad1.y -= 5
    if window.get_key('s') and pad1.bottom < window.bottom:
        pad1.y += 5

    if window.get_key('up') and pad2.top > window.top:
        pad2.y -= 5
    if window.get_key('down') and pad2.bottom < window.bottom:
        pad2.y += 5

    if ball.colliderect(pad1):
        dx = ball_speed
    if ball.colliderect(pad2):
        dx = -ball_speed

    window.update(fps)
```
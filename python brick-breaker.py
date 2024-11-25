import tkinter as tk


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]  # [dx, dy]
        self.speed = 5  # Kecepatan bola
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                   x + self.radius, y + self.radius,
                                   fill='red')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Cek tabrakan dengan dinding
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1  # Balik arah horizontal
        if coords[1] <= 0:
            self.direction[1] *= -1  # Balik arah vertikal

        # Pindahkan bola
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        ball_x_center = (coords[0] + coords[2]) / 2
        ball_y_bottom = coords[3]  # Bagian bawah bola

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                obj_coords = game_object.get_position()
                # Cek tabrakan dengan brick
                if (coords[2] >= obj_coords[0] and coords[0] <= obj_coords[2] and
                        ball_y_bottom >= obj_coords[1] and coords[1] <= obj_coords[3]):
                    
                    # Tentukan dari mana tabrakan terjadi
                    if abs(ball_x_center - (obj_coords[0] + obj_coords[2]) / 2) < \
                       abs(ball_y_bottom - obj_coords[1]):
                        self.direction[1] *= -1  # Tabrakan dari atas
                    else:
                        self.direction[0] *= -1  # Tabrakan dari sisi
                    
                    game_object.hit()  # Hit brick

            if isinstance(game_object, Paddle):
                paddle_coords = game_object.get_position()
                # Cek tabrakan dengan paddle
                if (coords[2] >= paddle_coords[0] and coords[0] <= paddle_coords[2] and
                        coords[3] >= paddle_coords[1]):
                    self.direction[1] *= -1  # Balik arah bola
                    self.move(0, -10)  # Pindahkan bola sedikit ke atas


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        # Cek batasan paddle
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#ffad90', 2: '#ff6241', 3: '#c22200', 4: '#590000'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits <= 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 758
        self.height = 450
        self.canvas = tk.Canvas(self, bg='#f6e7cd',
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 350)
        self.items[self.paddle.item] = self.paddle

        # Menambahkan brick dengan kapasitas hit yang berbeda
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 30, 4)
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(400, 250, 'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(30, 150, text, 10)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(200, 215000, 'Good Game!')
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            self.update_lives_text()
            if self.lives < 0:
                self.draw_text(200, 150, 'Nice Try!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break Those Bricks!')
    game = Game(root)
    game.mainloop()
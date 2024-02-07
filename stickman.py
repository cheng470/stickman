import time
from tkinter import Canvas, PhotoImage, Tk

# 坐标类，保存物体左上角和右下角的坐标
class Coords:
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

# 水平方向冲突
def within_x(co1, co2):
    return (co1.x1 > co2.x1 and co1.x1 < co2.x2) \
        or (co1.x2 > co2.x1 and co1.x2 < co2.x2) \
        or (co2.x1 > co1.x1 and co2.x1 < co1.x2) \
        or (co2.x2 > co1.x1 and co2.x2 < co1.x2)

# 垂直方向冲突
def within_y(co1, co2):
    return (co1.y1 > co2.y1 and co1.y1 < co2.y2) \
        or (co1.y2 > co2.y1 and co1.y2 < co2.y2) \
        or (co2.y1 > co1.y1 and co2.y1 < co1.y2) \
        or (co2.y2 > co1.y1 and co2.y2 < co1.y2)

# 左侧碰撞
def collided_left(co1, co2):
    return within_y(co1, co2) and co1.x1 <= co2.x2 and co1.x1 >= co2.x1
# 右侧碰撞
def collided_right(co1, co2):
    return within_y(co1, co2) and co1.x2 <= co2.x2 and co1.x2 >= co2.x1
# 顶部碰撞
def collided_top(co1, co2):
    return within_x(co1, co2) and co1.y1 <= co2.y2 and co1.y1 >= co2.y1
# 底部碰撞
def collided_bottom(y, co1, co2):
    if within_x(co1, co2):
        y_calc = co1.y2 + y
        return y_calc >= co2.y1 and y_calc <= co2.y2
    return False

# 精灵类
class Sprite:
    def __init__(self, game):
        self.game = game
        self.endgame = False
        self.coordinates = None
        self.name = ""
    def move(self):
        pass
    def coords(self):
        return self.coordinates
    
# 平台类
class PlatformSprite(Sprite):
    def __init__(self, game, photo_image, x, y, width, height):
        Sprite.__init__(self, game)
        self.name = "platform(%s, %s)" % (x, y)
        self.photo_image = photo_image
        self.image = game.canvas.create_image(x, y, image=self.photo_image, anchor="nw")
        self.coordinates = Coords(x, y, x + width, y + height)

# 火柴人精灵类
class StickFigureSprite(Sprite):
    def __init__(self, game):
        Sprite.__init__(self, game)
        self.name = "stick figure"
        self.images_left = [PhotoImage(file="stick-L1.gif"),PhotoImage(file="stick-L2.gif"),PhotoImage(file="stick-L3.gif")]
        self.images_right = [PhotoImage(file="stick-R1.gif"),PhotoImage(file="stick-R2.gif"),PhotoImage(file="stick-R3.gif")]
        self.image = game.canvas.create_image(200, 470, image=self.images_left[0], anchor="nw")

        # 设置变量
        self.x = -2 # 负值表示向左跑，正值表示向右跑
        self.y = 0 # 负值表示向上移动，正值表示向下移动
        self.current_image = 0 # 保存当前显示的图形的索引
        self.current_image_add = 1 # 与 current_image 相加得到下一个索引，用于制作动画
        self.jump_count = 0 # 跳跃计数器
        self.last_time = time.time() # 最近一次跳跃时间
        self.coordinates = Coords() # 火柴人坐标，这里没有初始值

        # 绑定按键
        game.canvas.bind_all('<KeyPress-Left>', self.turn_left)
        game.canvas.bind_all('<KeyPress-Right>', self.turn_right)
        game.canvas.bind_all('<space>', self.jump)
    
    def turn_left(self, e):
        if self.y == 0:
            self.x = -2
        ##print(self.x, self.y)
    def turn_right(self, e):
        if self.y == 0:
            self.x = 2
        #print(self.x, self.y)
    def jump(self, e):
        if self.y == 0:
            self.y = -4
            self.jump_count = 0
        #print(self.x, self.y)

    def animate(self):
        if self.x != 0 and self.y == 0:
            if time.time() - self.last_time > 0.1:
                self.last_time = time.time()
                self.current_image += self.current_image_add
                if self.current_image >= 2:
                    self.current_image_add = -1
                if self.current_image <= 0:
                    self.current_image_add = 1
        if self.x < 0:
            if self.y != 0:
                # 跳跃中
                self.game.canvas.itemconfig(self.image, image=self.images_left[2])
            else:
                self.game.canvas.itemconfig(self.image, image=self.images_left[self.current_image])
        elif self.x > 0:
            if self.y != 0:
                # 跳跃中
                self.game.canvas.itemconfig(self.image, image=self.images_right[2])
            else:
                self.game.canvas.itemconfig(self.image, image=self.images_right[self.current_image])
    
    # 计算火柴人位置
    def coords(self):
        xy = self.game.canvas.coords(self.image)
        self.coordinates.x1 = xy[0]
        self.coordinates.y1 = xy[1]
        self.coordinates.x2 = xy[0]+27
        self.coordinates.y2 = xy[1]+30
        return self.coordinates

    # 让火柴人移动
    def move(self):
        self.animate()
        if self.y < 0:
            self.jump_count += 1
            if self.jump_count > 20:
                self.y = 4
        if self.y > 0:
            self.jump_count -= 1
        co = self.coords()
        left = True
        right = True
        top = True
        bottom = True
        falling = True

        # 判断是否撞到画布的底部和顶部
        if self.y > 0 and co.y2 >= self.game.canvas_height:
            self.y = 0
            bottom = False
        elif self.y < 0 and co.y1 <= 0:
            self.y = 0
            top = False
        # 判断是否撞到画布左边和右边
        if self.x > 0 and co.x2 >= self.game.canvas_width:
            self.x = 0
            right = False
        elif self.x < 0 and co.x1 <= 0:
            self.x = 0
            left = False
        # 判断是否与其他精灵相撞
        for sprite in self.game.sprites:
            if sprite == self:
                continue
            sprite_co = sprite.coords()
            if top and self.y < 0 and collided_top(co, sprite_co):
                self.y = -self.y
                top = False
            if bottom and self.y > 0 and collided_bottom(self.y, co, sprite_co):
                self.y = sprite_co.y1 - co.y2
                if self.y < 0:
                    self.y = 0
                bottom = False
                top = False
            if bottom and falling and self.y == 0 \
                    and co.y2 < self.game.canvas_height \
                    and collided_bottom(1, co, sprite_co):
                falling = False
            # 左侧碰撞
            if left and self.x < 0 and collided_left(co, sprite_co):
                ##print("stop for left collided. sprite_co.x=", sprite_co.x1, "sprite_co.y=", sprite_co.y1, "name=", sprite.name)
                self.x = 0
                left = False
                if sprite.endgame:
                    self.end(sprite)
            # 右侧碰撞
            if right and self.x > 0 and collided_right(co, sprite_co):
                ###print("stop for right collided. sprite_co.x=", sprite_co.x1, "sprite_co.y=", sprite_co.y1, "name=", sprite.name)
                self.x = 0
                right = False
                if sprite.endgame:
                    self.end(sprite)
        
        # 判断是否往下掉
        if falling and bottom and self.y == 0 and co.y2 < self.game.canvas_height:
            self.y = 4
        #print("moving, x=", self.x, "y=", self.y)
        self.game.canvas.move(self.image, self.x, self.y)
    
    def end(self, sprite):
        self.game.running = False
        sprite.open()
        time.sleep(1)
        self.game.canvas.itemconfig(self.image, state="hidden")
        sprite.close()

# 门精灵类
class DoorSprite(Sprite):
    def __init__(self, game, x, y, width, height):
        Sprite.__init__(self, game)
        self.name = "door"
        self.closen_door = PhotoImage(file="door1.gif")
        self.open_door = PhotoImage(file="door2.gif")
        self.image = game.canvas.create_image(x, y, image=self.closen_door, anchor="nw")
        self.coordinates = Coords(x, y, x+(width/2), y+height)
        self.endgame = True
    def open(self):
        print("open door")
        self.game.canvas.itemconfig(self.image, image=self.open_door)
        self.game.tk.update_idletasks() # 执行这个可以让图片替换立即生效
        self.game.tk.update()
    def close(self):
        print("close door")
        self.game.canvas.itemconfig(self.image, image=self.closen_door)
        self.game.tk.update_idletasks()

# 游戏主类
class Game:
    def __init__(self):
        self.tk = Tk()
        self.tk.title("火柴人逃脱")
        self.tk.resizable(0, 0)
        self.tk.wm_attributes("-topmost", 1)
        self.canvas = Canvas(self.tk, width=500, height=500, highlightthickness=0)
        self.canvas.pack()
        self.tk.update()
        self.canvas_height = 500
        self.canvas_width = 500
        
        # 画背景图
        self.bg = PhotoImage(file="background.gif")
        w = self.bg.width()
        h = self.bg.height()
        for x in range(5):
            for y in range(5):
                self.canvas.create_image(x*w, y*h, image=self.bg, anchor="nw")
        self.sprites = []
        self.running = True
        self.game_over_text = self.canvas.create_text(250, 250, text='YOU WIN!', state='hidden')
    
    def mainloop(self):
        while 1:
            if self.running:
                for sprite in self.sprites:
                    sprite.move()
            else:
                time.sleep(1)
                self.canvas.itemconfig(self.game_over_text, state='normal')
            self.tk.update_idletasks()
            self.tk.update()
            time.sleep(0.01)

g = Game()
g.sprites.append(PlatformSprite(g, PhotoImage(file="platform1.gif"), 0, 480, 100, 10))
g.sprites.append(PlatformSprite(g, PhotoImage(file="platform1.gif"), 150, 440, 100, 10))
g.sprites.append(PlatformSprite(g, PhotoImage(file="platform1.gif"), 300, 400, 100, 10))
g.sprites.append(PlatformSprite(g, PhotoImage(file="platform1.gif"), 300, 160, 100, 10))
g.sprites.append(PlatformSprite(g, PhotoImage(file="platform2.gif"), 170, 350, 66, 10))
g.sprites.append(PlatformSprite(g, PhotoImage(file="platform2.gif"), 50, 300, 66, 10))
g.sprites.append(PlatformSprite(g, PhotoImage(file="platform2.gif"), 170, 120, 66, 10))
g.sprites.append(PlatformSprite(g, PhotoImage(file="platform2.gif"), 45, 60, 66, 10))
g.sprites.append(PlatformSprite(g, PhotoImage(file="platform3.gif"), 170, 250, 32, 10))
g.sprites.append(PlatformSprite(g, PhotoImage(file="platform3.gif"), 230, 200, 32, 10))

g.sprites.append(StickFigureSprite(g))
g.sprites.append(DoorSprite(g, 45, 30, 40, 35))
g.mainloop()
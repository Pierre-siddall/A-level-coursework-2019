
# 7. Mergesort scores with coins [INCOMPLETE] 
##################################################
import pygame as pg
import pytmx,sys,random,time
###### RGB COLOUR VALUES######
brown=(140,65,49)
white=(255,255,255)
black=(0,0,0)
green=(0,255,0)
grey=(100,100,100)
############# game variables and imports ############
gamemap="The_REAL_bunker.tmx"
screenwidth=1024
screenheight=768
fps=60
size_of_tile=32
gwidth=screenwidth/size_of_tile
gheight=screenheight/size_of_tile
vector=pg.math.Vector2
##############player settings###################
p_speed=300 
P_hit_box=pg.Rect(0,0,35,35)
p_rotation_speed=100
#manually resized image 
P_image='rsz_3survivor-move_rifle_0.png'
################ Enemy settings###############
e_image="zombiebasic_singleton.png"
e_speed= 100
e_hit_box=pg.Rect(0,0,30,30)
enemy_max_health=50
#################### shot settings ###################
shot_image='bullet.png'
shot_speed=500
shot_life=1000
shot_rate=150
weapon_inaccuracy=25
###################### FUNCTIONS ##########################
def collide_hit_box(one,two):
    return one.hit_box.colliderect(two.rect)

####################### PROCEDURES ##########################
def collide(sprite,group,dir):
    #This was uppdated to use the hit box of the player and the enemy 
    if dir=='x':
        touches=pg.sprite.spritecollide(sprite,group,False,collide_hit_box)
        if touches:
            if sprite.velocity.x>0:
                sprite.position_vector.x=touches[0].rect.left-sprite.hit_box.width/2
            if sprite.velocity.x<0:
                sprite.position_vector.x=touches[0].rect.right+sprite.hit_box.width/2
            sprite.velocity.x=0
            sprite.hit_box.centerx=sprite.position_vector.x 
    if dir=='y':
        touches=pg.sprite.spritecollide(sprite,group,False,collide_hit_box)
        if touches:
            if sprite.velocity.y>0:
                sprite.position_vector.y=touches[0].rect.top-sprite.hit_box.height/2
            if sprite.velocity.y<0:
                sprite.position_vector.y=touches[0].rect.bottom+sprite.hit_box.height/2
            sprite.velocity.y=0
            sprite.hit_box.centery=sprite.position_vector.y 
################### CLASSES #################################
class game:
    
    def __init__(self):
        
        pg.init()
        pg.mixer.init()
        self.window=pg.display.set_mode((screenwidth,screenheight))
        pg.display.set_caption("The last Bunker")
        pg.key.set_repeat(500,100)
        self.clock=pg.time.Clock()
        self.load_data()
        self.load_sounds()
        self.enemies_on_screen=0
        self.scores=[]
    
    def mergesort(self,scores):
        sorted_scores=[]
        if len(scores)<2:
            return scores 
        mid=int(len(scores)/2)
        left_half=self.mergesort(scores[:mid])
        right_half=self.mergesort(scores[mid:])
        left_index=0
        right_index=0
        
        while left_index<len(left_half) and right_index<len(right_half):
            if left_half[left_index]<right_half[right_index]:
                sorted_scores.append(left_half[left_index])
                left_index+=1
            else:
                sorted_scores.append(right_half[right_index])
                right_index+=1

        sorted_scores+=left_half[left_index:]
        sorted_scores+=right_half[right_index:]
        return sorted_scores
    
    def load_data(self):
        # rt in this case refers to the read text mode  of the open funtion
        self.map=tilemap(gamemap)
        self.map_image=self.map.create()
        self.map_rect=self.map_image.get_rect()
        self.player_image=pg.image.load(P_image).convert_alpha()
        self.player_image=pg.transform.rotate(self.player_image,180)
        self.enemy_image=pg.image.load(e_image).convert_alpha()
        self.shot_image=pg.image.load(shot_image).convert_alpha()
        self.pause_menu=pg.image.load('pause_menu.png').convert_alpha()

    def load_sounds(self):
        self.game_over_sound=pg.mixer.Sound("Game Over.wav")
        self.soundtrack=pg.mixer.Sound("Point of Clash.ogg") 
        self.enemy_death_sound=pg.mixer.Sound("Enemy Death.wav")
        self.gun_shot_sound=pg.mixer.Sound("Gun shot.wav")
        self.gun_shot_sound.set_volume(0.2)
        self.wall_collision_sound=pg.mixer.Sound("Wall collision.wav")
    
    def newgame(self):
        self.sprites=pg.sprite.Group()
        self.player=pg.sprite.Group()
        self.barrier=pg.sprite.Group()
        self.enemy=pg.sprite.Group()
        self.shot=pg.sprite.Group()
        self.pause_screen=pg.sprite.Group()
        pg.mixer.Sound.play(self.soundtrack)

        for map_object in self.map.tmxdata.objects:
            if map_object.name=='player':
                self.player=player(self,map_object.x,map_object.y,900)
            if map_object.name=='wall':
                blockage(self,map_object.x,map_object.y,map_object.width,map_object.height)
            if map_object.name=="enemy":
                enemy(self,random.randint(1,enemy_max_health),map_object.x,map_object.y)
                self.enemies_on_screen+=1

        self.camera=camera(self.map.width,self.map.height)
        self.game_paused=False
        self.scores=[]

    def run(self):
        self.playing=True
        while self.playing:
            self.dt=self.clock.tick(fps)/1000
            self.events()
            if not self.game_paused:
                self.update()
            self.draw()
    
    def quit(self):
        pg.quit()
        sys.exit()
    
    def update(self):
        '''This method will update anything that needs to be
        updated within the game loop '''
        self.sprites.update()
        self.camera.update(self.player)
        enemy_got_shot=pg.sprite.groupcollide(self.enemy,self.shot,False,True)
        player_got_hit=pg.sprite.spritecollide(self.player,self.enemy,False)

        for x in enemy_got_shot:
            x.health-=1
            if x.health==0:
                x.kill()
                pg.mixer.Sound.play(self.enemy_death_sound)
                self.player.coins+=self.player.coinsgained
                self.enemies_on_screen-=1
        
        for y in player_got_hit:
            self.player.health-=1
            if self.player.health==0:
                self.endgame()
   
    def draw(self):
        pg.display.set_caption("The Last Bunker:  CONTROLS : WASD=MOVE SPACE=SHOOT U=UPGRADE P=PAUSE/UNPAUSE")
        self.window.fill(brown)
        #self.sketchgrid()
        self.window.blit(self.map_image,self.camera.apply_rectangle(self.map_rect))
        for game_sprite in self.sprites:
            self.window.blit(game_sprite.image,self.camera.apply(game_sprite))
        pg.display.flip()
    
    def events(self):
        '''This part of the code checks for any 
        events such as key presses and clicking the cross to exit the game '''        
        for event in pg.event.get():
            if event.type==pg.QUIT:
                self.quit()
            if event.type==pg.KEYDOWN:
                if event.key==pg.K_ESCAPE:
                    self.quit()
                if event.key==pg.K_p:
                    self.game_paused=not self.game_paused
            if self.enemies_on_screen==0 and self.player.health!=0:
                self.nextwave()

    def nextwave(self):
        global enemy_max_health
        enemy_max_health*=1.5
        for map_object in self.map.tmxdata.objects:
            if map_object.name=="enemy":
                enemy(self,random.randint(1,enemy_max_health),map_object.x,map_object.y)
                self.enemies_on_screen+=1
        pg.display.update()

    def endgame(self):
        self.player.kill()
        pg.mixer.Sound.play(self.game_over_sound)
        with open ("scores.txt","at") as f:
            f.write(str(self.player.coins))
            #This moves the cursor to a new line 
            f.write("\n")
            f.close()
        time.sleep(2)
        self.set_high_score()
        print("YOUR HIGSCORE IS: ",self.highscore)
        self.quit()

    def set_high_score(self):
        with open("scores.txt","rt") as f:
            for line in f:
                self.scores.append(int(line.strip()))
        
        self.highscore_array=self.mergesort(self.scores)
        self.highscore=self.highscore_array[len(self.highscore_array)-1]



class player(pg.sprite.Sprite):
    def __init__(self,game,x,y,health):
        self.groups=game.sprites,game.player
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game=game
        self.image=game.player_image
        self.rect=self.image.get_rect()
        self.hit_box=P_hit_box
        self.hit_box.center=self.rect.center
        self.velocity=vector(0,0)
        self.position_vector=vector(x,y)
        self.final_shot=0
        self.rotation=0
        self.health=health
        self.coins=0
        self.coinsgained=25
        self.weapon_inaccuracy=0

    def which_key(self):
        self.rotation_speed=0
        self.velocity=vector(0,0)
        key=pg.key.get_pressed()
        if key[pg.K_a]:
           self.rotation_speed=p_rotation_speed 
        if key[pg.K_d]:
           self.rotation_speed=-p_rotation_speed
        if key[pg.K_w]:
           self.velocity=vector(-p_speed,0).rotate(-self.rotation)
        if key[pg.K_s]:
           self.velocity=vector(p_speed,0).rotate(-self.rotation)
        if key[pg.K_SPACE]:
            current=pg.time.get_ticks()
            if current-self.final_shot>shot_rate:
                self.final_shot=current
                direction=vector(-1,0).rotate(-self.rotation)
                shot(self.game,self.position_vector,direction)
                pg.mixer.Sound.play(self.game.gun_shot_sound )
        if key[pg.K_u]:
            self.upgrade()

    def update(self):
        self.which_key()
        #The line of code underneath updates the rotation of the player and if 
        #The player rotates 360 degrees the players rotation goes back to one 
        self.rotation=(self.rotation+self.rotation_speed*self.game.dt)%360
        self.image=pg.transform.rotate(self.game.player_image,self.rotation)
        #self.image=pg.tranform
        self.rect=self.image.get_rect()
        self.rect.center=self.position_vector
        self.position_vector+=self.velocity*self.game.dt
        #This bit of code creates two collision checks to see if the 
        #sprite collides with another in both the x and y direction
        self.hit_box.centerx=self.position_vector.x
        collide(self,self.game.barrier,'x')
        self.hit_box.centery=self.position_vector.y
        collide(self,self.game.barrier,'y')
        self.rect.center=self.hit_box.center

    def upgrade(self):
        if not self.coins<50:
            global weapon_inaccuracy
            weapon_inaccuracy-=10
            self.coins-=50
 
class tilemap:
    def __init__ (self,filename):
        tiledmap=pytmx.load_pygame(filename,pixelaplpha=True)
        self.width=tiledmap.width*tiledmap.tilewidth
        self.height=tiledmap.height*tiledmap.tileheight
        self.tmxdata=tiledmap
    
    def load(self,surface):
        ti=self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer,pytmx.TiledTileLayer):
                for x,y,gid, in layer:
                    tile=ti(gid)
                    if tile:
                        surface.blit(tile,(x*self.tmxdata.tilewidth,y*self.tmxdata.tileheight))
    
    def create(self):
        buffer_surface=pg.Surface((self.width,self.height))
        self.load(buffer_surface)
        return buffer_surface

class barrier(pg.sprite.Sprite):
    def __init__ (self,game,x,y):
        self.groups=game.sprites,game.barrier
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game=game
        self.image=pg.Surface((size_of_tile,size_of_tile))
        self.image.fill(grey)
        self.rect=self.image.get_rect()
        self.x=x
        self.y=y
        self.rect.x=x*size_of_tile
        self.rect.y=y*size_of_tile

class blockage(pg.sprite.Sprite):
    def __init__ (self,game,x,y,width,height):
        self.groups=game.barrier
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game=game
        self.rect=pg.Rect(x,y,width,height)
        self.x=x
        self.y=y
        self.rect.x=x
        self.rect.y=y
        
class camera:
    def __init__ (self,camera_width,camera_height):
        #These lines of code define a rectangle to 
        #be set for the camera and how large it will be
        '''This camera will also function as an offset 
        to the player while they are moving '''
        self.camera=pg.Rect(0,0,camera_width,camera_height)
        self.camera_width=camera_width
        self.camera_height=camera_height
    
    def apply(self,entity):
        #rect.move gives a new rectangle shifted by a certain amount
        return entity.rect.move(self.camera.topleft)

    def apply_rectangle(self,rect):
        return rect.move(self.camera.topleft)

    def update(self,target_sprite):
        x=-target_sprite.rect.centerx + int(screenwidth/2)
        y=-target_sprite.rect.centery + int(screenheight/2)
        # This next bit of code will limit the camera movement to the map size
        x=min(0,x)
        y=min(0,y)
        x=max(-(self.camera_width-screenwidth),x)
        y=max(-(self.camera_height-screenheight),y)
        self.camera=pg.Rect(x,y,self.camera_width,self.camera_height)

class enemy(pg.sprite.Sprite):
    
    def __init__ (self,game,health,x,y):
        self.groups=game.sprites,game.enemy
        pg.sprite.Sprite.__init__(self,self.groups) 
        self.game=game
        self.image=game.enemy_image
        self.rect=self.image.get_rect()
        self.hit_box=e_hit_box.copy()
        self.hit_box.center=self.rect.center
        self.position_vector=vector(x,y)
        self.velocity=vector(0,0)
        self.acceleration=vector(0,0)
        self.rect.center=self.position_vector
        self.rotation=0
        self.health=health

    def update(self):
        self.rotation=(self.game.player.position_vector-self.position_vector).angle_to(vector(1,0))
        self.image=pg.transform.rotate(self.game.enemy_image,self.rotation)
        self.rect=self.image.get_rect()
        self.rect.center=self.position_vector
        self.acceleration=vector(e_speed,0).rotate(-self.rotation)
        
        #This line of code add a negative value to the acceleration setting a maximum speed for the enemy 
        self.acceleration+=self.velocity*-1
        self.velocity+=self.acceleration*self.game.dt
       
        #suvat equation of s=ut+1/2at^2 used which links displacement to initial velocity ,acceleration and time 
        self.position_vector+=self.velocity*self.game.dt+0.5*self.acceleration*self.game.dt**2
        self.hit_box.centerx=self.position_vector.x
        collide(self,self.game.barrier,'x')
        self.hit_box.centery=self.position_vector.y
        collide(self,self.game.barrier,'y')
        self.rect.center=self.hit_box.center

class shot(pg.sprite.Sprite):
    
    def __init__(self,game,position,direction):
        self.groups=game.sprites,game.shot
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game=game
        self.image=game.shot_image
        self.rect=self.image.get_rect()
        self.position_vector=vector(position)
        self.rect.center=position
        inaccuracy=random.uniform(-weapon_inaccuracy,weapon_inaccuracy)
        self.velocity=direction.rotate(inaccuracy)*shot_speed
        self.life_time=pg.time.get_ticks()

    def update(self):
        #game.dt denotes the change in time 
        self.position_vector+=self.velocity*self.game.dt
        self.rect.center=self.position_vector
        if pg.sprite.spritecollideany(self,self.game.barrier):
            self.kill()
        if pg.time.get_ticks()-self.life_time>shot_life:
            self.kill()

#################################CLASS INIT########################################################
g=game()
################################# MAIN PROGRAM #################################################### 
while True:
    g.newgame()
    g.run()
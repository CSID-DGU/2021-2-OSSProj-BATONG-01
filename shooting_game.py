from sqlite3.dbapi2 import threadsafety
import pygame
import random
from collections import deque
###

from pygame import draw
from pygame.constants import VIDEORESIZE

from sprites import (MasterSprite, Ship, Alien, Missile, BombPowerup,
                     ShieldPowerup, HalfPowerup, Explosion, Siney, Spikey, Fasty,
                     Roundy, Crawly)
from database import Database
from load import load_image, load_sound, load_music

if not pygame.mixer:
    print('Warning, sound disabled')
if not pygame.font:
    print('Warning, fonts disabled')

BLUE = (0, 0, 255)
RED = (255, 0, 0)                               
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
############### 이동 정의 |2|씩 이동 ##########################
direction = {None: (0, 0), pygame.K_w: (0, -2), pygame.K_s: (0, 2),
             pygame.K_a: (-2, 0), pygame.K_d: (2, 0)}

class Language_check() :   ###### 게임 재 시작시 언어 상태 유지
    def __init__(self):
        self.state = False ######### False면 영어, True면 한국어
    def change_language(self) :
        self.state = not self.state
    def get_language(self) :
        return self.state

class Mode_check() : #### 게임 재시작시 모드 선택 유지
    def __init__(self):
        self.mode = 2
    def change_mode(self):
        if self.mode == 3 :
            self.mode = 1
        else :
            self.mode += 1
    def get_mode(self) :
        return self.mode

class Ship_selection_check() : #### 게임 재시작시 변경한 기체이미지 유지
    def __init__(self):
        self.ship_selection = 1
    def ship_selection_plus(self):
        self.ship_selection += 1
    def ship_selection_minus(self):
        self.ship_selection -= 1
    def get_ship_selection(self) :
        return self.ship_selection


class Keyboard(object):
    keys = {pygame.K_a: 'A', pygame.K_b: 'B', pygame.K_c: 'C', pygame.K_d: 'D',
            pygame.K_e: 'E', pygame.K_f: 'F', pygame.K_g: 'G', pygame.K_h: 'H',
            pygame.K_i: 'I', pygame.K_j: 'J', pygame.K_k: 'K', pygame.K_l: 'L',
            pygame.K_m: 'M', pygame.K_n: 'N', pygame.K_o: 'O', pygame.K_p: 'P',
            pygame.K_q: 'Q', pygame.K_r: 'R', pygame.K_s: 'S', pygame.K_t: 'T',
            pygame.K_u: 'U', pygame.K_v: 'V', pygame.K_w: 'W', pygame.K_x: 'X',
            pygame.K_y: 'Y', pygame.K_z: 'Z'}

language = Language_check()
mode = Mode_check()
ship_selection = Ship_selection_check() ###############

###############  MAIN ###############################################
def main():
    # Initialize everything
    pygame.mixer.pre_init(11025, -16, 2, 512)
    pygame.init()
    screen = pygame.display.set_mode((500, 500),pygame.RESIZABLE)
    pygame.display.set_caption('Shooting Game')
    pygame.mouse.set_visible(0)
    language_check = language.get_language()  ######### False면 영어, True면 한국어
    select_mode = mode.get_mode() ###1: easy, 2: normal, 3: hard ### default : normal

# Create the background which will scroll and loop over a set of different
# size stars
    background = pygame.Surface((500, 2000))
    background = background.convert()
    background.fill((0, 0, 0))
    backgroundLoc = 1500
    finalStars = deque()
    for y in range(0, 1500, 30):
        size = random.randint(2, 5)
        x = random.randint(0, 500 - size)
        if y <= 500:
            finalStars.appendleft((x, y + 1500, size))
        pygame.draw.rect(
            background, (255, 255, 0), pygame.Rect(x, y, size, size))
    while finalStars:
        x, y, size = finalStars.pop()
        pygame.draw.rect(
            background, (255, 255, 0), pygame.Rect(x, y, size, size))

# Display the background
    screen.blit(background, (0, 0))
    pygame.display.flip()

#################### Prepare game objects ###########################
    speed = 1.5
    MasterSprite.speed = speed
    alienPeriod = 60 / speed
    clockTime = 60  # maximum FPS
    clock = pygame.time.Clock()
    ship = Ship()
    initialAlienTypes = (Siney, Spikey)
    powerupTypes = (BombPowerup, ShieldPowerup, HalfPowerup)
    k = 0
    Missile_on = False
    Mode_Dict = {1:["Easy","쉬움"], 2:["Normal","보통"], 3:["Hard", "어려움"]}

    #### Sprite groups
    alldrawings = pygame.sprite.Group()
    allsprites = pygame.sprite.RenderPlain((ship,))
    MasterSprite.allsprites = allsprites
    Alien.pool = pygame.sprite.Group(
        [alien() for alien in initialAlienTypes for _ in range(5)])
    Alien.active = pygame.sprite.Group()
    Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)])
    Missile.active = pygame.sprite.Group()
    Explosion.pool = pygame.sprite.Group([Explosion() for _ in range(10)])
    Explosion.active = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    # Sounds
    missile_sound = load_sound('missile.ogg')
    bomb_sound = load_sound('bomb.ogg')
    alien_explode_sound = load_sound('alien_explode.ogg')
    ship_explode_sound = load_sound('ship_explode.ogg')
    load_music('music_loop.ogg')

    alienPeriod = clockTime // 2
    curTime = 0
    aliensThisWave, aliensLeftThisWave, Alien.numOffScreen = 10, 10, 10
    wave = 1
    score = 0
    missilesFired = 0
    powerupTime = 10 * clockTime
    powerupTimeLeft = powerupTime
    betweenWaveTime = 3 * clockTime
    betweenWaveCount = betweenWaveTime
    bombsHeld = 3 #############
    speed_change = 0.5 ################
    aliens_change = 2 ############
    life = 3 ################
    font = pygame.font.SysFont("notosanscjkkr",20, bold=pygame.font.Font.bold)                    #####한글오류해결#########################
    

    inMenu = True
    hiScores = Database.getScores()
    highScoreTexts = [font.render("NAME", 1, RED),
                    font.render("SCORE", 1, RED),
                    font.render("ACCURACY", 1, RED)]
    highScorePos = [highScoreTexts[0].get_rect(
                      topleft=screen.get_rect().inflate(-100, -100).topleft),
                    highScoreTexts[1].get_rect(
                      midtop=screen.get_rect().inflate(-100, -100).midtop),
                    highScoreTexts[2].get_rect(
                      topright=screen.get_rect().inflate(-100, -100).topright)]

    title, titleRect = load_image('title.png')
    titleRect.midtop = screen.get_rect().inflate(0, -200).midtop
    waveclear, waveclearRect = load_image('waveclear450.png')  #####wave넘어가는이미지 불러오기######################
    waveclearRect.midtop = screen.get_rect().inflate(0, 0).midtop   ####wave넘어가는이미지 위치설정#########################
    
    life_img, life_img_rect = load_image('heart.png',-1)
    life_img = pygame.transform.scale(life_img, (40,40))
    
    ship1, ship1Rect = load_image('ship.png')
    ship1Rect.bottomleft = screen.get_rect().inflate(-112, -300).bottomleft
    ship2, ship2Rect = load_image('ship2.png')
    ship2Rect.bottomleft = screen.get_rect().inflate(-337, -300).bottomleft 
    ship3, ship3Rect = load_image('ship3.png')
    ship3Rect.bottomleft = screen.get_rect().inflate(-562, -300).bottomleft 
    ship4, ship4Rect = load_image('ship4.png')
    ship4Rect.bottomleft = screen.get_rect().inflate(-787, -300).bottomleft 


    #####기체이미지 변경 변수들###########
    ship1Text = font.render('', 1, BLUE)
    ship2Text = font.render('', 1, BLUE)
    ship3Text = font.render('', 1, BLUE)
    ship4Text = font.render('', 1, BLUE)
    ship_selectText = font.render('SELECT', 1, BLUE)

    ship1Pos = ship1Text.get_rect(midbottom=ship1Rect.inflate(0, 0).midbottom)
    ship2Pos = ship2Text.get_rect(midbottom=ship2Rect.inflate(0, 0).midbottom)
    ship3Pos = ship3Text.get_rect(midbottom=ship3Rect.inflate(0, 0).midbottom)
    ship4Pos = ship4Text.get_rect(midbottom=ship4Rect.inflate(0, 0).midbottom)
    ship_selectPos = ship_selectText.get_rect(midbottom=ship1Rect.inflate(0, 60).midbottom)
    
    ship_menuDict = {1: ship1Pos, 2: ship2Pos, 3: ship3Pos, 4: ship4Pos}
    ##################################



    startText = font.render('START GAME', 1, BLUE)
    hiScoreText = font.render('HIGH SCORES', 1, BLUE)
    fxText = font.render('SOUND FX ', 1, GREEN)
    fxOnText = font.render('ON', 1, RED)
    fxOffText = font.render('OFF', 1, RED)
    musicText = font.render('MUSIC', 1, GREEN)
    musicOnText = font.render('ON', 1, RED)
    musicOffText = font.render('OFF', 1, RED)
    quitText = font.render('QUIT', 1, BLUE)
    selectText = font.render('*', 1, BLUE)
    languageText = font.render('언어변경', 1, BLUE)                             ###########################
    modeText = font.render(Mode_Dict[select_mode][language.get_language()], 1, YELLOW)
    change_shipText = font.render('CHANGE SHIP', 1, BLUE) 

    startPos = startText.get_rect(midtop=titleRect.inflate(0, 50).midbottom)
    hiScorePos = hiScoreText.get_rect(topleft=startPos.bottomleft)
    fxPos = fxText.get_rect(topleft=hiScorePos.bottomleft)
    fxOnPos = fxOnText.get_rect(topleft=fxPos.topright)
    fxOffPos = fxOffText.get_rect(topleft=fxPos.topright)
    musicPos = fxText.get_rect(topleft=fxPos.bottomleft)
    musicOnPos = musicOnText.get_rect(topleft=musicPos.topright)
    musicOffPos = musicOffText.get_rect(topleft=musicPos.topright)
    modePos = modeText.get_rect(topleft=musicPos.bottomleft) ############
    quitPos = quitText.get_rect(topleft=modePos.bottomleft)
    selectPos = selectText.get_rect(topright=startPos.topleft)
    languagePos = languageText.get_rect(topleft=quitPos.bottomleft)  ###############################
    change_shipPos = change_shipText.get_rect(topleft=languagePos.bottomleft)

    menuDict = {1: startPos, 2: hiScorePos, 3: fxPos, 4: musicPos, 5: modePos, 6 :quitPos, 7:languagePos, 8:change_shipPos}    ####################
    

    selection = 1
    showHiScores = False
    showChange_ship = False
    soundFX = Database.getSound()
    music = Database.getSound(music=True)
    if music and pygame.mixer:
        pygame.mixer.music.play(loops=-1)

    ################################# 메뉴 화면 #########################################
    while inMenu:
        clock.tick(clockTime)

        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, 500, 500))
        backgroundLoc -= speed
        if backgroundLoc - speed <= speed:
            backgroundLoc = 1500

        for event in pygame.event.get():
            
            if (event.type == pygame.QUIT):
                return
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_RETURN and not showChange_ship):
                if showHiScores:
                    showHiScores = False
                elif selection == 1:
                    inMenu = False
                    ship.initializeKeys()
                    if ship_selection.get_ship_selection() == 1:      #####게임 시작시 설정한 기체이미지에 맞게 변경####
                        ship.image, ship.rect = load_image('ship.png', -1)
                        ship.original = ship.image
                        ship.shield, ship.rect = load_image('ship_shield.png', -1)
                        ship.screen = pygame.display.get_surface()
                        ship.area = ship.screen.get_rect()
                        ship.rect.midbottom = (ship.screen.get_width() // 2, ship.area.bottom)
                        ship.radius = max(ship.rect.width, ship.rect.height)
                        ship.alive = True  ##### life
                        ship.shieldUp = False
                        ship.vert = 0
                        ship.horiz = 0
                        showChange_ship = False
                    elif ship_selection.get_ship_selection() == 2:
                        ship.image, ship.rect = load_image('ship2.png', -1)
                        ship.original = ship.image
                        ship.shield, ship.rect = load_image('ship2_shield.png', -1)
                        ship.screen = pygame.display.get_surface()
                        ship.area = ship.screen.get_rect()
                        ship.rect.midbottom = (ship.screen.get_width() // 2, ship.area.bottom)
                        ship.radius = max(ship.rect.width, ship.rect.height)
                        ship.alive = True  ##### life
                        ship.shieldUp = False
                        ship.vert = 0
                        ship.horiz = 0
                        showChange_ship = False
                    elif ship_selection.get_ship_selection() == 3:
                        ship.image, ship.rect = load_image('ship3.png', -1)
                        ship.original = ship.image
                        ship.shield, ship.rect = load_image('ship3_shield.png', -1)
                        ship.screen = pygame.display.get_surface()
                        ship.area = ship.screen.get_rect()
                        ship.rect.midbottom = (ship.screen.get_width() // 2, ship.area.bottom)
                        ship.radius = max(ship.rect.width, ship.rect.height)
                        ship.alive = True  ##### life
                        ship.shieldUp = False
                        ship.vert = 0
                        ship.horiz = 0
                        showChange_ship = False
                    elif ship_selection.get_ship_selection() == 4:
                        ship.image, ship.rect = load_image('ship4.png', -1)
                        ship.original = ship.image
                        ship.shield, ship.rect = load_image('ship4_shield.png', -1)
                        ship.screen = pygame.display.get_surface()
                        ship.area = ship.screen.get_rect()
                        ship.rect.midbottom = (ship.screen.get_width() // 2, ship.area.bottom)
                        ship.radius = max(ship.rect.width, ship.rect.height)
                        ship.alive = True  ##### life
                        ship.shieldUp = False
                        ship.vert = 0
                        ship.horiz = 0
                        showChange_ship = False
                elif selection == 2:
                    showHiScores = True
                elif selection == 3:
                    soundFX = not soundFX
                    if soundFX:
                        missile_sound.play()
                    Database.setSound(int(soundFX))
                elif selection == 4 and pygame.mixer:
                    music = not music
                    if music:
                        pygame.mixer.music.play(loops=-1)
                    else:
                        pygame.mixer.music.stop()
                    Database.setSound(int(music), music=True)
                elif selection == 5 :
                    mode.change_mode()
                    select_mode = mode.get_mode()
                elif selection == 6:
                    return
                elif selection == 7:                                     #################################
                    language.change_language()
                    language_check = language.get_language()
                elif selection == 8:
                    showChange_ship = True
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_w
                  and selection > 1
                  and not showHiScores
                  and not showChange_ship):
                selection -= 1
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_s
                  and selection < len(menuDict)
                  and not showHiScores
                  and not showChange_ship):
                selection += 1
            elif (event.type == pygame.QUIT ##menu 화면에서도 esc누르면 꺼지게
                or event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE):
                return

            ####기체이미지 변경 창########
            elif (event.type == pygame.KEYDOWN
                and event.key == pygame.K_RETURN and showChange_ship):
                showChange_ship = False
            elif (event.type == pygame.KEYDOWN
                and event.key == pygame.K_a
                and ship_selection.get_ship_selection() > 1
                and not showHiScores
                and showChange_ship):
                ship_selection.ship_selection_minus()
            elif (event.type == pygame.KEYDOWN
                and event.key == pygame.K_d
                and ship_selection.get_ship_selection() < len(ship_menuDict)
                and not showHiScores
                and showChange_ship):
                ship_selection.ship_selection_plus()
            
        ship_selectPos = ship_selectText.get_rect(midbottom=ship_menuDict[ship_selection.get_ship_selection()].inflate(0,60).midbottom)
        selectPos = selectText.get_rect(topright=menuDict[selection].topleft)
        
        #####mode select######
        if mode.get_mode() == 1 :
            speed = 1
            bombsHeld = 5
            speed_change = 0.2
            aliens_change = 1.5
            life = 5
        elif mode.get_mode() == 2 :
            speed = 1.5
            bombsHeld = 3
            speed_change = 0.5
            aliens_change = 2
            life = 3
        elif mode.get_mode() == 3 :
            bombsHeld = 1
            speed = 1.7
            speed_change = 1
            aliens_change = 3
            life = 1

        if not language_check :  #################################################
            startText = font.render('START GAME', 1, BLUE)
            hiScoreText = font.render('HIGH SCORES', 1, BLUE)
            fxText = font.render('SOUND FX ', 1, GREEN)
            fxOnText = font.render('ON', 1, RED)
            fxOffText = font.render('OFF', 1, RED)
            musicText = font.render('MUSIC', 1, GREEN)
            musicOnText = font.render('ON', 1, RED)
            musicOffText = font.render('OFF', 1, RED)
            quitText = font.render('QUIT', 1, BLUE)
            selectText = font.render('*', 1, BLUE)
            languageText = font.render('언어변경', 1, BLUE)
            modeText = font.render(Mode_Dict[select_mode][language.get_language()], 1, YELLOW)
            change_shipText = font.render('CHANGE SHIP', 1, BLUE)
            ship_selectText = font.render('SELECT', 1, BLUE)
        else:
            startText = font.render('게임 시작', 1, BLUE)
            hiScoreText = font.render('최고 기록', 1, BLUE)
            fxText = font.render('효과음', 1, GREEN)
            fxOnText = font.render('켜기', 1, RED)
            fxOffText = font.render('끄기', 1, RED)
            musicText = font.render('음악', 1, GREEN)
            musicOnText = font.render('켜기', 1, RED)
            musicOffText = font.render('끄기', 1, RED)
            quitText = font.render('종료', 1, BLUE)
            selectText = font.render('*', 1, BLUE)
            languageText = font.render('LANGUAGE CHANGE', 1, BLUE)
            modeText = font.render(Mode_Dict[select_mode][language.get_language()], 1, YELLOW)
            change_shipText = font.render('기체 변경', 1, BLUE)
            ship_selectText = font.render('선택', 1, BLUE)

        ###################### 점수 화면 ######################
        if not language_check :                 #################################################
            highScoreTexts = [font.render("NAME", 1, RED),
                            font.render("SCORE", 1, RED),
                            font.render("ACCURACY", 1, RED)]
        else:
            highScoreTexts = [font.render("이름", 1, RED),
                              font.render("점수", 1, RED),
                              font.render("정확도", 1, RED)]
    
        for hs in hiScores:                         ###########원래 while inMenu밖에 있었는데 안으로 가져옴
            highScoreTexts.extend([font.render(str(hs[x]), 1, BLUE)
                                   for x in range(3)])
            highScorePos.extend([highScoreTexts[x].get_rect(
                topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])

        if showHiScores:
            textOverlays = zip(highScoreTexts, highScorePos)
        elif showChange_ship:
            screen.blit(title,titleRect)
            screen.blit(ship1, ship1Rect)
            screen.blit(ship2, ship2Rect)
            screen.blit(ship3, ship3Rect)
            screen.blit(ship4, ship4Rect)
            textOverlays = zip([ship1Text,ship2Text,ship3Text,ship4Text,ship_selectText],[ship1Pos,ship2Pos,ship3Pos,ship4Pos,ship_selectPos])
        else:
            textOverlays = zip([startText, hiScoreText, fxText,
                                musicText, quitText, modeText, selectText, languageText, change_shipText,        ###########
                                fxOnText if soundFX else fxOffText,
                                musicOnText if music else musicOffText],
                               [startPos, hiScorePos, fxPos,
                                musicPos, quitPos, modePos, selectPos, languagePos, change_shipPos,           ###########
                                fxOnPos if soundFX else fxOffPos,
                                musicOnPos if music else musicOffPos])
            screen.blit(title, titleRect)

        for txt, pos in textOverlays:
            screen.blit(txt, pos)
        pygame.display.flip()


    ######################### 메인 게임 #####################################
    while ship.alive:
        clock.tick(clockTime)
        k += 1

        #######아이템 드롭#############
        if aliensLeftThisWave >= 1:
            powerupTimeLeft -= 1
        if powerupTimeLeft <= 0:
            powerupTimeLeft = powerupTime
            random.choice(powerupTypes)().add(powerups, allsprites)

    # Event Handling
        for event in pygame.event.get():
            if (event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE):
                return
            elif (event.type == pygame.KEYDOWN
                  and event.key in direction.keys()):
                ship.horiz += direction[event.key][0] * speed
                ship.vert += direction[event.key][1] * speed
            elif (event.type == pygame.KEYUP
                  and event.key in direction.keys()):
                ship.horiz -= direction[event.key][0] * speed
                ship.vert -= direction[event.key][1] * speed
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_SPACE):
                k = 0
                Missile_on = True
            elif (event.type == pygame.KEYUP
                  and event.key == pygame.K_SPACE):
                Missile_on = False
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_b):
                if bombsHeld > 0:
                    bombsHeld -= 1
                    newBomb = ship.bomb()
                    newBomb.add(bombs, alldrawings)
                    if soundFX:
                        bomb_sound.play()
    ####### 공격 #######
        if Missile_on == True and k%12 == 0:
            Missile.position(ship.rect.midtop)
            missilesFired += 1
            if soundFX:
                missile_sound.play()

    # Collision Detection
        # Aliens
        for alien in Alien.active:
            for bomb in bombs:
                if pygame.sprite.collide_circle(
                        bomb, alien) and alien in Alien.active:
                    alien.table()
                    Explosion.position(alien.rect.center)
                    missilesFired += 1
                    if aliensLeftThisWave>0 :
                        aliensLeftThisWave -= 1
                        score += 1
                    else :
                        aliensLeftThisWave = 0
                    if soundFX:
                        alien_explode_sound.play()
            for missile in Missile.active:
                if pygame.sprite.collide_rect(
                        missile, alien) and alien in Alien.active:
                    alien.table()
                    missile.table()
                    Explosion.position(alien.rect.center)
                    if aliensLeftThisWave>0 :
                        aliensLeftThisWave -= 1
                        score += 1
                        missilesFired += 1
                    else :
                        aliensLeftThisWave = 0
                    
                    if soundFX:
                        alien_explode_sound.play()
            if pygame.sprite.collide_rect(alien, ship):
                if ship.shieldUp:
                    alien.table()
                    Explosion.position(alien.rect.center)
                    if aliensLeftThisWave>0 :
                        aliensLeftThisWave -= 1
                        score += 1
                    ship.shieldUp = False
                else: ### 쉴드 없을때
                    if life == 1:
                        life -= 1
                        ship.alive = False
                        ship.remove(allsprites)
                        Explosion.position(ship.rect.center)
                        if soundFX:
                            ship_explode_sound.play()
                    else :
                        alien.table()
                        life -= 1
                        Explosion.position(alien.rect.center)
                        if aliensLeftThisWave > 0 :
                            aliensLeftThisWave -= 1
                        else :
                            aliensLeftThisWave = 0

        # PowerUps
        for powerup in powerups:
            if pygame.sprite.collide_circle(powerup, ship):
                if powerup.pType == 'bomb':
                    bombsHeld += 1
                elif powerup.pType == 'shield':
                    ship.shieldUp = True
                elif powerup.pType == 'half' :
                    num_of_alien = len(Alien.active.sprites())
                    for alien in Alien.active :
                        alien.table()
                    pygame.time.delay(20)
                    if aliensLeftThisWave < num_of_alien :
                        aliensLeftThisWave = 0
                    else  :
                        aliensLeftThisWave -= num_of_alien
                        aliensLeftThisWave = round(aliensLeftThisWave/2)
                powerup.kill()
            elif powerup.rect.top > powerup.area.bottom:
                powerup.kill()

    # Update Aliens
        if curTime <= 0 and aliensLeftThisWave > 0:
            Alien.position()
            curTime = alienPeriod
        elif curTime > 0:
            curTime -= 1

    # Update text overlays
        if not language_check :                                           ###############################
            waveText = font.render("Wave: " + str(wave), 1, BLUE)
            leftText = font.render("Aliens Left: " + str(aliensLeftThisWave),1, BLUE)
            scoreText = font.render("Score: " + str(score), 1, BLUE)
            bombText = font.render("Bombs: " + str(bombsHeld), 1, BLUE)
            
        else: 
            waveText = font.render("웨이브: " + str(wave), 1, BLUE)
            leftText = font.render("남은 적: " + str(aliensLeftThisWave), 1, BLUE)
            scoreText = font.render("점수: " + str(score), 1, BLUE)
            bombText = font.render("폭탄: " + str(bombsHeld), 1, BLUE)
           

        wavePos = waveText.get_rect(topleft=screen.get_rect().topleft)
        leftPos = leftText.get_rect(midtop=screen.get_rect().midtop)
        scorePos = scoreText.get_rect(topright=screen.get_rect().topright)
        bombPos = bombText.get_rect(bottomleft=screen.get_rect().bottomleft)
       
        text = [waveText, leftText, scoreText, bombText]
        textposition = [wavePos, leftPos, scorePos, bombPos]

        #####하트 여러 개 그리기 ###
        heart = []
        heartPos = []
        for i in range(life+1):
            heart.append(life_img)
            heartPos.append([screen.get_width()-life_img.get_width()*i, scoreText.get_height()])

    ###################### 다음 wave : Detertmine when to move to next wave ########################
    
        
    
        if aliensLeftThisWave <= 0:
            if betweenWaveCount > 0:
                betweenWaveCount -= 1
                if not language_check:                                                  ################
                    nextWaveText = font.render('Wave ' + str(wave + 1) + ' in', 1, BLUE)
                else:
                    nextWaveText = font.render('웨이브 ' + str(wave + 1) + ' 단계', 1, BLUE)
              
                nextWaveNum = font.render(
                    str((betweenWaveCount // clockTime) + 1), 1, RED)
                text.extend([nextWaveText, nextWaveNum])
                nextWavePos = nextWaveText.get_rect(center=screen.get_rect().center)
                nextWaveNumPos = nextWaveNum.get_rect(midtop=nextWavePos.midbottom)
                textposition.extend([nextWavePos, nextWaveNumPos])

                if wave % 4 == 0:
                    if not language_check:                                         #####################
                        speedUpText = font.render('SPEED UP!', 1, RED)
                    else:
                        speedUpText = font.render('속도 증가!', 1, RED)
                    speedUpPos = speedUpText.get_rect(
                        midtop=nextWaveNumPos.midbottom)
                    text.append(speedUpText)
                    textposition.append(speedUpPos)

            elif betweenWaveCount == 0:
                if wave % 4 == 0:
                    speed += speed_change
                    MasterSprite.speed = speed
                    ship.initializeKeys()
                    aliensThisWave = 10
                    aliensLeftThisWave = Alien.numOffScreen = aliensThisWave
                else:
                    aliensThisWave = round(aliensThisWave * aliens_change)
                    aliensLeftThisWave = Alien.numOffScreen = aliensThisWave
                if wave == 1:
                    Alien.pool.add([Fasty() for _ in range(5)])
                if wave == 2:
                    Alien.pool.add([Roundy() for _ in range(5)])
                if wave == 3:
                    Alien.pool.add([Crawly() for _ in range(5)])
                wave += 1
                betweenWaveCount = betweenWaveTime

        textOverlays = zip(text, textposition)

    ################# Update and draw all sprites and text
        
       
        
        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, 500, 500))
        backgroundLoc -= speed
        if backgroundLoc - speed <= speed:
            backgroundLoc = 1500
        allsprites.update()
        allsprites.draw(screen)
        alldrawings.update()
        for txt, pos in textOverlays:
            screen.blit(txt, pos)
        heartOverlays = zip(heart, heartPos)
        for img, pos in heartOverlays :
            screen.blit(img, pos)
        pygame.display.flip()

    accuracy = round(score / missilesFired, 4) if missilesFired > 0 else 0.0
    isHiScore = len(hiScores) < Database.numScores or score > hiScores[-1][1]
    name = ''
    nameBuffer = []


    ############################# Game Over #################################
    while True:
        clock.tick(clockTime)

    # Event Handling
        for event in pygame.event.get():
            if (event.type == pygame.QUIT
                or not isHiScore
                and event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE):
                return False
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_RETURN
                  and not isHiScore):
                return True
            elif (event.type == pygame.KEYDOWN
                  and event.key in Keyboard.keys.keys()
                  and len(nameBuffer) < 8):
                nameBuffer.append(Keyboard.keys[event.key])
                name = ''.join(nameBuffer)
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_BACKSPACE
                  and len(nameBuffer) > 0):
                nameBuffer.pop()
                name = ''.join(nameBuffer)
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_RETURN
                  and len(name) > 0):
                Database.setScore(hiScores, (name, score, accuracy))
                return True

        if isHiScore:
            if not language_check:                                     #################################
                hiScoreText = font.render('HIGH SCORE!', 1, RED)
            else:
                hiScoreText = font.render('최고 기록!', 1, RED)
            hiScorePos = hiScoreText.get_rect(
                midbottom=screen.get_rect().center)
            scoreText = font.render(str(score), 1, BLUE)
            scorePos = scoreText.get_rect(midtop=hiScorePos.midbottom)
            if not language_check:                                         #################################
                enterNameText = font.render('ENTER YOUR NAME:', 1, RED)
            else:
                enterNameText = font.render('아이디를 적으세요:', 1, RED)
            enterNamePos = enterNameText.get_rect(midtop=scorePos.midbottom)
            nameText = font.render(name, 1, BLUE)
            namePos = nameText.get_rect(midtop=enterNamePos.midbottom)
            textOverlay = zip([hiScoreText, scoreText,
                               enterNameText, nameText],
                              [hiScorePos, scorePos,
                               enterNamePos, namePos])
        else:
            if not language_check:                                     #################################
                gameOverText = font.render('GAME OVER', 1, BLUE)
            else:
                gameOverText = font.render('게임 오버', 1, BLUE)
            gameOverPos = gameOverText.get_rect(
                center=screen.get_rect().center)
            if not language_check :                                     #################################
                scoreText = font.render('SCORE: {}'.format(score), 1, BLUE)
            else:
                scoreText = font.render('점수: {}'.format(score), 1, BLUE)
            scorePos = scoreText.get_rect(midtop=gameOverPos.midbottom)
            textOverlay = zip([gameOverText, scoreText],
                              [gameOverPos, scorePos])

    ############################### Update and draw all sprites ############################################
        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, 500, 500))
        backgroundLoc -= speed
        if backgroundLoc - speed <= 0:
            backgroundLoc = 1500
        allsprites.update()
        allsprites.draw(screen)
        alldrawings.update()
        for txt, pos in textOverlay:
            screen.blit(txt, pos)
        pygame.display.flip()


if __name__ == '__main__':
    while(main()):
        pass

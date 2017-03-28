#!/usr/bin/env python

#
#   Breakout V 0.1 June 2009
#
#   Copyright (C) 2009 John Cheetham
#
#   web   : http://www.johncheetham.com/projects/breakout
#   email : developer@johncheetham.com
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

'''
Steps remaining:
push the printed data into a csv
    this will be your test py file
Create a new script that reads the data and then predicts using classifier which direction to move.
'''


import sys, pygame, random, csv
import numpy as np
import pandas as pd
#from sklearn import svm
from sklearn.neural_network import MLPRegressor


class Breakout():

    def main(self):

        xspeed_init = 6
        yspeed_init = 6
        max_lives = 50
        bat_speed = 30
        score = 0
        bgcolour = 0x2F, 0x4F, 0x4F  # darkslategrey
        size = width, height = 640, 480

        pygame.init()
        screen = pygame.display.set_mode(size)
        #screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

        bat = pygame.image.load("bat.png").convert()
        batrect = bat.get_rect()

        ball = pygame.image.load("ball.png").convert()
        ball.set_colorkey((255, 255, 255))
        ballrect = ball.get_rect()

        #pong = pygame.mixer.Sound('Blip_1-Surround-147.wav')
        #pong.set_volume(10)

        wall = Wall()
        wall.build_wall(width)

        # Initialise ready for game loop
        batrect = batrect.move((width / 2) - (batrect.right / 2), height - 20)
        ballrect = ballrect.move(width / random.uniform(-2, 2), height / 2)
        xspeed = xspeed_init
        yspeed = yspeed_init
        lives = max_lives
        clock = pygame.time.Clock()
        pygame.key.set_repeat(1,30)
        pygame.mouse.set_visible(0)       # turn off mouse pointer


        hits = 0
        goal_shift = 3000
        x_rand = 0.02

        game_data = []
        bot_dat = pd.read_csv('game_data.csv', header=None)
        bot_dat[4] = 1500
        #bot_dat = bot_dat[bot_dat[3] != 0]
        #X = bot_dat[[2]].as_matrix() - bot_dat[[0]].as_matrix()
        X = bot_dat[[0,1,2]].as_matrix()
        print X
        y = bot_dat[[3]].as_matrix()
        #bot_play = svm.SVR()
        bot_play = MLPRegressor()
        bot_play.fit(X,y)
        while 1:
            push_dir = 0
            # 60 frames per second
            clock.tick(100)

            if hits > goal_shift:
                for g in game_data:
                    g.append(hits)
                with open("game_data_learn.csv", "a") as ff:
                    writer = csv.writer(ff)
                    writer.writerows(game_data)
                bot_dat = bot_dat.append(pd.DataFrame(game_data))
                bot_dat.to_csv('game_data_ML.csv', index = False)
                print "WINNER"
                break

            xxx = float(bot_play.predict(np.array([ballrect.left, ballrect.top, batrect.left]).reshape(1, -1)))
            #print xxx
            # process key presses
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
        	            sys.exit()
                    '''
                    if event.key == pygame.K_LEFT:
                        push_dir = -1
                        batrect = batrect.move(-bat_speed, 0)
                        if (batrect.left < 0):
                            batrect.left = 0
                    if event.key == pygame.K_RIGHT:
                        push_dir= 1
                        batrect = batrect.move(bat_speed, 0)
                        if (batrect.right > width):
                            batrect.right = width
                    '''

            d = random.uniform(-1*x_rand, x_rand)
            if xxx > d:
                #print "RIGHT"
                batrect = batrect.move(bat_speed, 0)
                push_dir = 1
                if (batrect.right > width):
                    batrect.right = width
            if xxx < d:
                #print "LEFT"
                push_dir = -1
                batrect = batrect.move(-bat_speed, 0)
                if (batrect.left < 0):
                    batrect.left = 0


            # check if bat has hit ball
            if ballrect.bottom >= batrect.top and \
               ballrect.bottom <= batrect.bottom and \
               ballrect.right >= batrect.left and \
               ballrect.left <= batrect.right:
                yspeed = -yspeed
                #pong.play(0)
                offset = ballrect.center[0] - batrect.center[0]
                hits = hits+1
                # offset > 0 means ball has hit RHS of bat
                # vary angle of ball depending on where ball hits bat
                if offset > 0:
                    if offset > 30:
                        xspeed = 7
                    elif offset > 23:
                        xspeed = 6
                    elif offset > 17:
                        xspeed = 5
                else:
                    if offset < -30:
                        xspeed = -7
                    elif offset < -23:
                        xspeed = -6
                    elif xspeed < -17:
                        xspeed = -5

            # move bat/ball
            ballrect = ballrect.move(xspeed, yspeed)
            if ballrect.left < 0 or ballrect.right > width:
                xspeed = -xspeed
                #pong.play(0)
            if ballrect.top < 0:
                yspeed = -yspeed
                #pong.play(0)

            # check if ball has gone past bat - lose a life
            if ballrect.top > height:
                lives -= 1
                #lives = 2
                # start a new ball
                xspeed = xspeed_init
                rand = random.random()
                if random.random() > 0.5:
                    xspeed = -xspeed
                yspeed = yspeed_init
                ballrect.center = width * random.random(), height / 3
                if lives == 0:
                    msg = pygame.font.Font(None,70).render("Game Over", True, (0,255,255), bgcolour)
                    msgrect = msg.get_rect()
                    msgrect = msgrect.move(width / 2 - (msgrect.center[0]), height / 3)
                    screen.blit(msg, msgrect)
                    pygame.display.flip()
                    # process key presses
                    #     - ESC to quit
                    #     - any other key to restart game

                    if hits > 10:
                        for g in game_data:
                            g.append(hits)

                        with open("game_data_learn.csv", "a") as ff:
                            writer = csv.writer(ff)
                            writer.writerows(game_data)

                        bot_dat = bot_dat.append(pd.DataFrame(game_data))
                        print bot_dat

                    bot_dat.to_csv('game_data_ML.csv', index = False)

                    bot_dat = bot_dat.nlargest(5, columns=4)
                    X = bot_dat[[0,1,2]].as_matrix()
                    y = bot_dat[[3]].as_matrix()
                    bot_play.fit(X,y)

                    #redo
                    hits = 0
                    screen.fill(bgcolour)
                    wall.build_wall(width)
                    lives = max_lives
                    score = 0
                    game_data = []


                    '''
                    while 1:
                        restart = False
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                    	            sys.exit()
                                if not (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
                                    restart = True
                        if restart:
                            screen.fill(bgcolour)
                            wall.build_wall(width)
                            lives = max_lives
                            score = 0
                            break
                    '''

            if xspeed < 0 and ballrect.left < 0:
                xspeed = -xspeed
                #pong.play(0)

            if xspeed > 0 and ballrect.right > width:
                xspeed = -xspeed
                #pong.play(0)

            # check if ball has hit wall
            # if yes yhen delete brick and change ball direction
            index = ballrect.collidelist(wall.brickrect)
            if index != -1:
                if ballrect.center[0] > wall.brickrect[index].right or \
                   ballrect.center[0] < wall.brickrect[index].left:
                    xspeed = -xspeed
                else:
                    yspeed = -yspeed
                #pong.play(0)
                wall.brickrect[index:index + 1] = []
                score += 10

            screen.fill(bgcolour)
            scoretext = pygame.font.Font(None,40).render(str(hits), True, (0,255,255), bgcolour)
            scoretextrect = scoretext.get_rect()
            scoretextrect = scoretextrect.move(width - scoretextrect.right, 0)
            screen.blit(scoretext, scoretextrect)

            for i in range(0, len(wall.brickrect)):
                screen.blit(wall.brick, wall.brickrect[i])

            # if wall completely gone then rebuild it
            if wall.brickrect == []:
                wall.build_wall(width)
                xspeed = xspeed_init
                yspeed = yspeed_init
                ballrect.center = width / 2, height / 3

            screen.blit(ball, ballrect)
            screen.blit(bat, batrect)
            pygame.display.flip()
            #print ballrect.left, batrect.left,xxx
            #print game_data
            game_data.append([ballrect.left, ballrect.top, batrect.left, push_dir])
            #dont think I need speed but we will see because velocity is the first derivitive of position

class Wall():

    def __init__(self):
        self.brick = pygame.image.load("brick.png").convert()
        brickrect = self.brick.get_rect()
        self.bricklength = brickrect.right - brickrect.left
        self.brickheight = brickrect.bottom - brickrect.top

    def build_wall(self, width):
        xpos = 0
        ypos = 60
        adj = 0
        self.brickrect = []
        for i in range (0, 52):
            if xpos > width:
                if adj == 0:
                    adj = self.bricklength / 2
                else:
                    adj = 0
                xpos = -adj
                ypos += self.brickheight

            self.brickrect.append(self.brick.get_rect())
            self.brickrect[i] = self.brickrect[i].move(xpos, ypos)
            xpos = xpos + self.bricklength
            #print xpos, ypos, adj

if __name__ == '__main__':
    br = Breakout()
    br.main()

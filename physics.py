#!/usr/bin/python
"""
    Physics, a 2D Physics Playground for Kids
    Copyright (C) 2008  Alex Levenson and Brian Jordan

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

--

Elements is Copyright (C) 2008, The Elements Team, <elements@linuxuser.at>

Wiki:   http://wiki.sugarlabs.org/go/Activities/Physics
Code:   git://git.sugarlabs.org/physics/mainline.git

"""

import sys
import math
import pygame
from pygame.locals import *
from pygame.color import *
import olpcgames
sys.path.append("lib/")
import pkg_resources
sys.path.append("lib/Elements-0.13-py2.5.egg")
sys.path.append("lib/Box2D-2.0.2b1-py2.5-linux-i686.egg")
import Box2D as box2d
import elements
import tools
from helpers import *
import gtk

class PhysicsGame:
    def __init__(self, screen):
        self.screen = screen
        # Get everything set up
        self.clock = pygame.time.Clock()
        self.canvas = olpcgames.ACTIVITY.canvas
        self.in_focus = True
        # Create the name --> instance map for components
        self.toolList = {}
        for c in tools.allTools:
            self.toolList[c.name] = c(self)
        self.currentTool = self.toolList[tools.allTools[0].name]
        # Set up the world (instance of Elements)
        self.box2d = box2d
        self.world = elements.Elements(self.screen.get_size())
        self.world.renderer.set_surface(self.screen)

        # Set up static environment
        self.world.add.ground()

        # Fake a Sugar cursor for the pyGame canvas area
        self.show_fake_cursor = False
        pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))
        self.cursor_picture = pygame.image.load('standardcursor.png')
        self.cursor_picture.convert_alpha()
        self.canvas.connect("enter_notify_event", self.switch_on_fake_pygame_cursor_cb)
        self.canvas.connect("leave_notify_event", self.switch_off_fake_pygame_cursor_cb)
        self.canvas.add_events(gtk.gdk.ENTER_NOTIFY_MASK
                               | gtk.gdk.LEAVE_NOTIFY_MASK)

    def switch_off_fake_pygame_cursor_cb(self, panel, event):
        self.show_fake_cursor = False

    def switch_on_fake_pygame_cursor_cb(self, panel, event):
        self.show_fake_cursor = True

    def run(self):
        while True:
            for event in pygame.event.get():
                self.currentTool.handleEvents(event)

            if self.in_focus:
                # Drive motors
                if self.world.run_physics:
                    for body in self.world.world.GetBodyList():
                        if type(body.userData) == type({}):
                            if body.userData.has_key('rollMotor'):
                                diff = body.userData['rollMotor']['targetVelocity'] - body.GetAngularVelocity()
                                body.ApplyTorque(body.userData['rollMotor']['strength'] * diff * body.getMassData().I)

                # Update & Draw World
                self.world.update()
                self.screen.fill((255, 255, 255)) # 255 for white
                self.world.draw()

                # Draw output from tools
                self.currentTool.draw()

                # Show Sugar like cursor for UI consistancy
                if self.show_fake_cursor:
                    self.screen.blit(self.cursor_picture, pygame.mouse.get_pos())

                # Flip Display
                pygame.display.flip()

            # Stay under 30 FPS to help keep the rest of the platform responsive
            self.clock.tick(30) # Originally 50

    def setTool(self, tool):
        self.currentTool.cancel()
        self.currentTool = self.toolList[tool]

def main():
    toolbarheight = 75
    tabheight = 45
    pygame.display.init()
    video_info = pygame.display.Info()
    x = video_info.current_w
    y = video_info.current_h
    screen = pygame.display.set_mode((x, y - toolbarheight - tabheight))
    game = PhysicsGame(screen) 
    game.run()

# Make sure that main get's called
if __name__ == '__main__':
    main()


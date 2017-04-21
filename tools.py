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

"""
#==================================================================
#                           Physics.activity
#                              Tool Classes
#                           By Alex Levenson
#==================================================================
import pygame
import olpcgames
from pygame.locals import *
from helpers import *
from inspect import getmro
from gettext import gettext as _


# Tools that can be superlcassed
class Tool(object):
    name = 'Tool'
    icon = 'icon'
    toolTip = "Tool Tip"
    toolAccelerator = None

    def __init__(self, gameInstance):
        self.game = gameInstance
        self.name = self.__class__.name

    def handleEvents(self, event):
        handled = True
        # Default event handling
        if event.type == USEREVENT:
            if hasattr(event, "action"):
                if event.action == "stop_start_toggle":
                    # Stop/start simulation
                    self.game.world.run_physics = not self.game.world.run_physics
                elif event.action == "focus_in":
                    self.game.in_focus = True
                elif event.action == "focus_out":
                    self.game.in_focus = False
                elif self.game.toolList.has_key(event.action):
                    self.game.setTool(event.action)
            elif hasattr(event, "code"):
                if event.code == olpcgames.FILE_WRITE_REQUEST:
                    #Saving to journal
                    self.game.world.add.remove_mouseJoint()
                    self.game.world.json_save(event.filename)
                elif event.code == olpcgames.FILE_READ_REQUEST:
                    #Loading from journal
                    self.game.world.json_load(event.filename)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.game.canvas.grab_focus()
            handled = False
        else:
            handled = False
        if handled:
            return handled
        else:
            return self.handleToolEvent(event)

    def handleToolEvent(self, event):
        # Overload to handel events for Tool subclasses
        pass

    def draw(self):
        # Default drawing method is don't draw anything
        pass

    def cancel(self):
        # Default cancel doesn't do anything
        pass


# The circle creation tool
class CircleTool(Tool):
    name = 'Circle'
    icon = 'circle'
    toolTip = _("Circle")
    toolAccelerator = _("<ctrl>c")

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.pt1 = None
        self.radius = 40

    def handleToolEvent(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pt1 = cast_tuple_to_int(event.pos)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.game.world.add.ball(self.pt1, self.radius,
                                         dynamic=True, density=1.0,
                                         restitution=0.16, friction=0.5)
                self.pt1 = None

    def draw(self):
        # Draw a circle from pt1 to mouse
        if self.pt1 != None:
            delta = distance(self.pt1,
                             cast_tuple_to_int(pygame.mouse.get_pos()))
            if delta > 0:
                self.radius = max(delta, 5)
                pygame.draw.circle(self.game.screen, (100, 180, 255),
                                   self.pt1, int(self.radius), 3)
                pygame.draw.line(self.game.screen, (100, 180, 255), self.pt1,
                                 cast_tuple_to_int(pygame.mouse.get_pos()), 1)

    def cancel(self):
        self.pt1 = None


# The box creation tool
class BoxTool(Tool):
    name = 'Box'
    icon = 'box'
    toolTip = _("Box")
    toolAccelerator = _("<ctrl>b")

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.pt1 = None
        self.rect = None
        self.width = 80
        self.height = 80

    def handleToolEvent(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pt1 = cast_tuple_to_int(event.pos)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1 and self.pt1 != None:
                mouse_x_y = cast_tuple_to_int(event.pos)
                if mouse_x_y[0] == self.pt1[0] and mouse_x_y[1] == self.pt1[1]:
                    self.rect = pygame.Rect(self.pt1, (-self.width, -self.height))
                    self.rect.normalize()
                self.game.world.add.rect(self.rect.center,
                                         max(self.rect.width, 10) / 2,
                                         max(self.rect.height, 10) / 2,
                                         dynamic=True,
                                         density=1.0,
                                         restitution=0.16,
                                         friction=0.5)
                self.pt1 = None

    def draw(self):
        # Draw a box from pt1 to mouse
        if self.pt1 != None:
            mouse_x_y = cast_tuple_to_int(pygame.mouse.get_pos())
            if mouse_x_y[0] != self.pt1[0] or mouse_x_y[1] != self.pt1[1]:
                self.width = mouse_x_y[0] - self.pt1[0]
                self.height = mouse_x_y[1] - self.pt1[1]
                self.rect = pygame.Rect(self.pt1, (self.width, self.height))
                self.rect.normalize()
                pygame.draw.rect(self.game.screen, (100, 180, 255),
                                 self.rect, 3)

    def cancel(self):
        self.pt1 = None
        self.rect = None


# The triangle creation tool
class TriangleTool(Tool):
    name = 'Triangle'
    icon = 'triangle'
    toolTip = _("Triangle")
    toolAccelerator = _("<ctrl>t")

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.pt1 = None
        self.vertices = None
        self.line_delta = [0, -80]

    def handleToolEvent(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pt1 = cast_tuple_to_int(event.pos)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1 and self.pt1 != None:
                mouse_x_y = cast_tuple_to_int(event.pos)
                if mouse_x_y[0] == self.pt1[0] and mouse_x_y[1] == self.pt1[1]:
                    self.pt1 = [mouse_x_y[0] - self.line_delta[0],
                                mouse_x_y[1] - self.line_delta[1]]
                    self.vertices = constructTriangleFromLine(self.pt1,
                                                              mouse_x_y)

                # Use minimum sized triangle if user input too small
                minimum_size_check = float(distance(self.pt1, mouse_x_y))
                if minimum_size_check < 20:
                    middle_x = (self.pt1[0] + mouse_x_y[0]) / 2.0
                    self.pt1[0] = middle_x - (((middle_x - self.pt1[0]) /
                                              minimum_size_check) * 20)
                    mouse_x_y[0] = middle_x - (((middle_x - mouse_x_y[0]) /
                                               minimum_size_check) * 20)
                    middle_y = (self.pt1[1] + mouse_x_y[1]) / 2.0
                    self.pt1[1] = middle_y - (((middle_y - self.pt1[1]) /
                                              minimum_size_check) * 20)
                    mouse_x_y[1] = middle_y - (((middle_y - mouse_x_y[1]) /
                                               minimum_size_check) * 20)
                    self.vertices = constructTriangleFromLine(self.pt1,
                                                              mouse_x_y)

                self.game.world.add.convexPoly(self.vertices,
                                               dynamic=True,
                                               density=1.0,
                                               restitution=0.16,
                                               friction=0.5)
                self.pt1 = None
                self.vertices = None

    def draw(self):
        # Draw a triangle from pt1 to mouse
        if self.pt1 != None:
            mouse_x_y = cast_tuple_to_int(pygame.mouse.get_pos())
            if mouse_x_y[0] != self.pt1[0] or mouse_x_y[1] != self.pt1[1]:
                self.vertices = constructTriangleFromLine(self.pt1, mouse_x_y)
                self.line_delta = [mouse_x_y[0] - self.pt1[0],
                                   mouse_x_y[1] - self.pt1[1]]
                pygame.draw.polygon(self.game.screen, (100, 180, 255),
                                    self.vertices, 3) 
                pygame.draw.line(self.game.screen, (100, 180, 255),
                                 self.pt1, mouse_x_y, 1)

    def cancel(self):
        self.pt1 = None
        self.vertices = None


# The Polygon creation tool
class PolygonTool(Tool):
    name = 'Polygon'
    icon = 'polygon'
    toolTip = _("Polygon")
    toolAccelerator = _("<ctrl>p")

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.vertices = None
        self.previous_vertices = None
        self.safe = False

    def handleToolEvent(self, event):
        if hasattr(event, 'button') and event.button == 1:
            if event.type == MOUSEBUTTONDOWN and self.vertices is None:
                self.vertices = [cast_tuple_to_int(event.pos)]
                self.safe = False
            if event.type == MOUSEBUTTONUP and self.vertices is not None and len(self.vertices) == 1 and cast_tuple_to_int(event.pos)[0] == self.vertices[0][0] and cast_tuple_to_int(event.pos)[1] == self.vertices[0][1]:
                if self.previous_vertices is not None:
                    last_x_y = self.previous_vertices[-1]
                    delta_x = last_x_y[0] - cast_tuple_to_int(event.pos)[0]
                    delta_y = last_x_y[1] - cast_tuple_to_int(event.pos)[1]
                    self.vertices = [[i[0] - delta_x, i[1] - delta_y]
                                                for i in self.previous_vertices]
                    self.safe = True
                    self.game.world.add.complexPoly(self.vertices, dynamic=True,
                                                    density=1.0,
                                                    restitution=0.16,
                                                    friction=0.5)
                self.vertices = None
            elif (event.type == MOUSEBUTTONUP or event.type == MOUSEBUTTONDOWN):
                if self.vertices is None or (cast_tuple_to_int(event.pos)[0] == self.vertices[-1][0] and cast_tuple_to_int(event.pos)[1] == self.vertices[-1][1]):
                    # Skip if coordinate is same as last one
                    return
                if distance(cast_tuple_to_int(event.pos), self.vertices[0]) < 15 and self.safe:
                    self.vertices.append(self.vertices[0]) # Connect polygon
                    self.game.world.add.complexPoly(self.vertices, dynamic=True,
                                                    density=1.0,
                                                    restitution=0.16,
                                                    friction=0.5)
                    self.previous_vertices = self.vertices[:]
                    self.vertices = None
                elif distance(cast_tuple_to_int(event.pos), self.vertices[0]) < 15:
                    self.vertices = None
                else:
                    self.vertices.append(cast_tuple_to_int(event.pos))
                    if distance(cast_tuple_to_int(event.pos), self.vertices[0]) >= 55:
                        self.safe = True

    def draw(self):
        # Draw the poly being created
        if self.vertices:
            for i in range(len(self.vertices) - 1):
                pygame.draw.line(self.game.screen, (100, 180, 255),
                                 self.vertices[i], self.vertices[i + 1], 3)
            pygame.draw.line(self.game.screen, (100, 180, 255),
                             self.vertices[-1],
                             cast_tuple_to_int(pygame.mouse.get_pos()), 3)
            pygame.draw.circle(self.game.screen, (100, 180, 255),
                               self.vertices[0], 15, 3)

    def cancel(self):
        self.vertices = None


# The magic pen tool
class MagicPenTool(Tool):
    name = 'Magicpen'
    icon = 'magicpen'
    toolTip = _("Draw")
    toolAccelerator = _("<ctrl>d")

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.vertices = None
        self.previous_vertices = None
        self.safe = False

    def handleToolEvent(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.vertices = [cast_tuple_to_int(event.pos)]
            self.safe = False
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            if len(self.vertices) == 1 and self.previous_vertices is not None:
                last_x_y = self.previous_vertices[-1]
                delta_x = last_x_y[0] - cast_tuple_to_int(event.pos)[0]
                delta_y = last_x_y[1] - cast_tuple_to_int(event.pos)[1]
                self.vertices = [[i[0] - delta_x, i[1] - delta_y]
                                            for i in self.previous_vertices]
                self.safe = True
            if self.vertices and self.safe:
                self.game.world.add.complexPoly(self.vertices, dynamic=True,
                                                density=1.0,
                                                restitution=0.16,
                                                friction=0.5)
                self.previous_vertices = self.vertices[:]
            self.vertices = None
        elif event.type == MOUSEMOTION and self.vertices:
            self.vertices.append(cast_tuple_to_int(event.pos))
            if distance(cast_tuple_to_int(event.pos), self.vertices[0]) >= 55 and len(self.vertices) > 3:
                self.safe = True

    def draw(self):
        # Draw the poly being created
        if self.vertices:
            if len(self.vertices) > 1:
                for i in range(len(self.vertices) - 1):
                    pygame.draw.line(self.game.screen, (100, 180, 255),
                                     self.vertices[i], self.vertices[i + 1], 3)
                pygame.draw.line(self.game.screen, (100, 180, 255),
                                 self.vertices[-1],
                                 cast_tuple_to_int(pygame.mouse.get_pos()), 3)
                pygame.draw.circle(self.game.screen, (100, 180, 255),
                                   self.vertices[0], 15, 3)

    def cancel(self):
        self.vertices = None


# The grab tool
class GrabTool(Tool):
    name = 'Grab'
    icon = 'grab'
    toolTip = _("Grab")
    toolAccelerator = _("<ctrl>g")

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self._current_body = None

    def handleToolEvent(self, event):
        # We handle two types of "grab" depending on simulation running or not
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                # Grab the first object at the mouse pointer
                bodylist = self.game.world.get_bodies_at_pos(cast_tuple_to_int(event.pos),
                                                           include_static=False)
                if bodylist and len(bodylist) > 0:
                    if self.game.world.run_physics:
                        self.game.world.add.mouseJoint(bodylist[0], cast_tuple_to_int(event.pos))
                    else:
                        self._current_body = bodylist[0]
        elif event.type == MOUSEBUTTONUP:
            # Let it go
            if event.button == 1:
                if self.game.world.run_physics:
                    self.game.world.add.remove_mouseJoint()
                else:
                    self._current_body = None
        elif event.type == MOUSEMOTION and event.buttons[0]:
            # Move it around
            if self.game.world.run_physics:
                # Use box2D mouse motion
                self.game.world.mouse_move(cast_tuple_to_int(event.pos))
            else:
                # Position directly (if we have a current body)
                if self._current_body is not None:
                    x, y = self.game.world.to_world(cast_tuple_to_int(event.pos))
                    x /= self.game.world.ppm
                    y /= self.game.world.ppm
                    self._current_body.position = (x, y)

    def cancel(self):
        self.game.world.add.remove_mouseJoint()


# The joint tool
class JointTool(Tool):
    name = 'Joint'
    icon = 'joint'
    toolTip = _("Joint")
    toolAccelerator = "<ctrl>j"

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None

    def handleToolEvent(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button >= 1:
                # Grab the first body
                self.jb1pos = cast_tuple_to_int(event.pos)
                self.jb1 = self.game.world.get_bodies_at_pos(cast_tuple_to_int(event.pos))
                self.jb2 = self.jb2pos = None
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                # Grab the second body
                self.jb2pos = cast_tuple_to_int(event.pos)
                self.jb2 = self.game.world.get_bodies_at_pos(cast_tuple_to_int(event.pos))
                # If we have two distinct bodies, add a distance joint!
                if self.jb1 and self.jb2 and str(self.jb1) != str(self.jb2):
                    self.game.world.add.joint(self.jb1[0], self.jb2[0],
                                              self.jb1pos, self.jb2pos)
                #add joint to ground body
                #elif self.jb1:
                #    groundBody = self.game.world.world.GetGroundBody()
                #    self.game.world.add.joint(self.jb1[0], groundBody,
                #                              self.jb1pos, self.jb2pos)
                # regardless, clean everything up
                self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None

    def draw(self):
        if self.jb1:
            pygame.draw.line(self.game.screen, (100, 180, 255), self.jb1pos,
                             cast_tuple_to_int(pygame.mouse.get_pos()), 3)

    def cancel(self):
        self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None


# The pin tool
class PinTool(Tool):
    name = 'Pin'
    icon = 'pin'
    toolTip = _("Pin")
    toolAccelerator = _("<ctrl>o")

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.jb1 = self.jb1pos = None

    def handleToolEvent(self, event):
        if event.type == MOUSEBUTTONDOWN:
            self.jb1pos = cast_tuple_to_int(event.pos)
            self.jb1 = self.game.world.get_bodies_at_pos(cast_tuple_to_int(event.pos))
            if self.jb1:
                self.game.world.add.joint(self.jb1[0], self.jb1pos)
            self.jb1 = self.jb1pos = None

    def cancel(self):
        self.jb1 = self.jb1pos = None


# The motor tool
class MotorTool(Tool):
    name = 'Motor'
    icon = 'motor'
    toolTip = _("Motor")
    toolAccelerator = _("<ctrl>m")

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.jb1 = self.jb1pos = None

    def handleToolEvent(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button >= 1:
                # Grab the first body
                self.jb1pos = cast_tuple_to_int(event.pos)
                self.jb1 = self.game.world.get_bodies_at_pos(cast_tuple_to_int(event.pos))
                if self.jb1:
                    self.game.world.add.motor(self.jb1[0], self.jb1pos)
                self.jb1 = self.jb1pos = None

    def cancel(self):
        self.jb1 = self.jb1pos = None


class RollTool(Tool):
    name = 'Roll'
    icon = 'roll'
    toolTip = _("Roll")
    toolAccelerator = _("<ctrl>r")

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.jb1 = self.jb1pos = None

    def handleToolEvent(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.jb1pos = cast_tuple_to_int(event.pos)
                self.jb1 = self.game.world.get_bodies_at_pos(self.jb1pos)
                if self.jb1:
                    if type(self.jb1[0].userData) == type({}):
                        self.jb1[0].userData['rollMotor'] = {}
                        self.jb1[0].userData['rollMotor']['targetVelocity'] = -10
                        self.jb1[0].userData['rollMotor']['strength'] = 40
                self.jb1 = self.jb1pos = None

    def cancel(self):
        self.jb1 = self.jb1pos = None


# The destroy tool
class DestroyTool(Tool):
    name = 'Destroy'
    icon = 'destroy'
    toolTip = _("Erase")
    toolAccelerator = _("<ctrl>e")

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.vertices = None

    def handleToolEvent(self, event):
        if pygame.mouse.get_pressed()[0]:
            if not self.vertices: self.vertices = []
            self.vertices.append(cast_tuple_to_int(event.pos))
            if len(self.vertices) > 10:
                self.vertices.pop(0)

            tokill = self.game.world.get_bodies_at_pos(cast_tuple_to_int(event.pos))

            if tokill:
                jointnode = tokill[0].GetJointList()
                if jointnode:
                    joint = jointnode.joint
                    self.game.world.world.DestroyJoint(joint)
                else:
                    self.game.world.world.DestroyBody(tokill[0])
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            self.cancel()

    def draw(self):
        # Draw the trail
        if self.vertices:
            if len(self.vertices) > 1:
                pygame.draw.lines(self.game.screen, (255, 0, 0), False,
                                  self.vertices, 3)

    def cancel(self):
        self.vertices = None


def getAllTools():
    return [MagicPenTool,
            CircleTool,
            TriangleTool,
            BoxTool,
            PolygonTool,
            GrabTool,
            MotorTool,
            PinTool,
            JointTool,
            DestroyTool]

allTools = getAllTools()

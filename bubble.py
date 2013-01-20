#! /usr/bin/env python


class Bubble:
    """ Represents a bubble object. """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 0
        self.height = 0
        self.speed = (0, 1)
        self.active = True

    def dimensions(self):
        return (self.x, self.y, self.width, self.height)

    def center(self):
        return (self.x - (self.width / 2), self.y - (self.height / 2))

    def move(self):
        self.x += self.speed[0]
        self.y += self.speed[1]


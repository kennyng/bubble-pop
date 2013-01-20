#! /usr/bin/env python

import cv
import random
import os
import pygame

import control
from bubble import Bubble


def config_webcam_video():
    ##############################
    # Configure webcam settings.
    #############################
    # Use defaul webcam (try 0 as arg if does not work).
    cam = cv.CaptureFromCAM(-1)
    # Set webcam dimensions.
    framesize = (int(cv.GetCaptureProperty(cam, cv.CV_CAP_PROP_FRAME_WIDTH)), int(cv.GetCaptureProperty(cam, cv.CV_CAP_PROP_FRAME_HEIGHT)))

    ############################
    # Configure video settings.
    ############################
    record_video = False    # set to True to record video
    # Set video format.
    fourcc = cv.FOURCC('M', 'J', 'P', 'G')
    fps = 30
    
    # Create video file.
    video_writer = None
    if record_video:
        video_writer = cv.CreateVideoWriter("gameplay.avi", fourcc, fps, framesize)

    return cam, framesize, record_video, video_writer

def create_bubbles(num_bubbles, framesize):
    # Configure bubble settings.
    bubble_raw = cv.LoadImage(os.path.join('data', 'bubble.png'))
    bubble_img = cv.CreateImage((64, 64), bubble_raw.depth, bubble_raw.channels)
    cv.Resize(bubble_raw, bubble_img)

    mask_raw = cv.LoadImage(os.path.join('data', 'input-mask.png'))
    mask_img = cv.CreateImage((64, 64), mask_raw.depth, bubble_raw.channels)
    cv.Resize(mask_raw, mask_img)

    bubbles = list()
    for i in range(num_bubbles):
        bubble = Bubble(random.randint(0, framesize[0] - bubble_img.width), 0)
        bubble.width = bubble_img.width
        bubble.height = bubble_img.height
        bubbles.append(bubble)

    return bubbles, bubble_img, mask_img

def hit_value(image, bubble):
    roi = cv.GetSubRect(image, bubble.dimensions())
    return cv.CountNonZero(roi)


if __name__ == '__main__':
    # load sound and music
    pygame.mixer.init()
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    pygame.mixer.music.set_volume(0.6)

    try:
        pygame.mixer.music.load(os.path.join('data', 'bubble-pop.ogg')) # load music
        pop = pygame.mixer.Sound(os.path.join('data', 'pop.wav'))
        pop.set_volume(1.0)
    except:
        raise UserWarning, "could not load or play soundfiles in 'data' folder -_-..."

    # Create windows to show captured images.
    cv.NamedWindow("frame", cv.CV_WINDOW_AUTOSIZE)
    cv.NamedWindow("Bubble Pop!", cv.CV_WINDOW_AUTOSIZE)

    # Create structuring element.
    struct_elem = cv.CreateStructuringElementEx(9, 9, 4, 4, cv.CV_SHAPE_ELLIPSE)

    # Configure webcam and video settings
    cam, framesize, record_video, video_writer = config_webcam_video()

    previous = cv.CreateImage(framesize, 8L, 3)
    cv.SetZero(previous)
    difference = cv.CreateImage(framesize, 8L, 3)
    cv.SetZero(difference)
    current = cv.CreateImage(framesize, 8L, 3)
    cv.SetZero(current)

    # Set number of bubbles
    num_bubbles = 5
    bubbles, bubble_img, mask_img = create_bubbles(num_bubbles, framesize)

    initial_delay = 100
    score = 0
    font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1)

    pygame.mixer.music.play(-1)


    #################################
    # Main Loop
    #################################
    while True:
        # Capture frame (original footage)
        capture = cv.QueryFrame(cam)
        cv.Flip(capture, capture, flipMode=1)

        # Difference between frames
        cv.Smooth(capture, current, cv.CV_BLUR, 15, 15)
        cv.AbsDiff(current, previous, difference)

        # frame = difference frame gray scaled > threshold > dilate | working image 
        frame = cv.CreateImage(framesize, 8, 1)
        cv.CvtColor(difference, frame, cv.CV_BGR2GRAY)
        cv.Threshold(frame, frame, 10, 0xff, cv.CV_THRESH_BINARY)
        cv.Dilate(frame, frame, element=struct_elem, iterations=3)

        if initial_delay <= 0:
            for bubble in bubbles:
                if bubble.active:
                    nonzero = hit_value(frame, bubble)
                    if nonzero < 1000:
                        # Draws the bubble to screen
                        cv.SetImageROI(capture, bubble.dimensions())
                        cv.Copy(bubble_img, capture, mask_img)
                        cv.ResetImageROI(capture)
                        bubble.move()

                        # if bubble hits bottom
                        if bubble.y + bubble.height >= framesize[1]:
                            bubble.active = False
                            num_bubbles -= 1
                            
                    else:
                        bubble.y = 0
                        bubble.x = random.randint(0, framesize[0] - bubble_img.width)
                        if bubble.speed[1] < 15:
                            bubble.speed = (0, bubble.speed[1] + 1)

                        pop.play()
                        score += num_bubbles

        cv.PutText(capture, "SCORE: %d" %score, (10, framesize[1] - 10), font, cv.RGB(255, 0, 56))
        cv.ShowImage("frame", frame)
        if record_video:
            cv.WriteFrame(video_writer, capture)
        cv.ShowImage("Bubble Pop!", capture)

        previous = cv.CloneImage(current)

        # Exit game if ESC key is pressed
        code = control.WaitKey(2)
        if code == control.ESC_KEY:
            break
        
        initial_delay -= 1

    pygame.mixer.music.stop()
    # Output score at end
    print 'SCORE: %d' %score


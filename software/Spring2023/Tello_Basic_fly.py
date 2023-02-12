# this code is in part from autonomous drone racing and snipets from Cris Li
# implemnation with Kennys edge dection and the tello DJI drone

import numpy as np
import pygame
from djitellopy import Tello
import time
import cv2
 



## Speed of the drone
S = 60
 
 

class TelloUI(object):
    """ Maintains the Tello display and moves it through the keyboard keys.
        Press escape key to quit.
        The controls are:
            - T: Takeoff
            - L: Land
            - Arrow keys: Forward, backward, left and right.
            - A and D: Counter clockwise and clockwise rotations (yaw)
            - W and S: Up and down.
            - U: Flip forward
            - H: Flip left
            - J: Flip back
            - K: Flip right
    """

    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Create pygame window
        pygame.display.set_caption("TelloTV Live!")
        self.screen = pygame.display.set_mode([960, 720])

        # Init Tello object that interacts with the Tello drone
        self.tello = Tello()

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        # Self State
        self.a_id = -1

        self.send_rc_control = False
        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0
        # create update timer
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)

    def run(self):

        self.tello.connect()
        self.tello.set_speed(self.speed)
        
        # In case streaming is on. This happens when we quit this program without the escape key.
        self.tello.streamoff()
        self.tello.streamon()

        frame_read = self.tello.get_frame_read()

        should_stop = False
        while not should_stop:

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    should_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            if frame_read.stopped:
                break

            self.screen.fill([0, 0, 0])

            frame = frame_read.frame
            frame_color=frame
            
          # battery display
            text = "Tello Battery: {}%".format(self.tello.get_battery())
            cv2.putText(frame_color, text, (5, 710), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            #cv2.putText(frame_color, f"FPS: {FPS}", (7, 675), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            frame_color = cv2.cvtColor(frame_color, cv2.COLOR_BGR2RGB)
            frame_color = np.rot90(frame_color)
            frame_color = np.flipud(frame_color)
            frame_color = pygame.surfarray.make_surface(frame_color)
            #self.screen.blit(frame_color, (0, 0))
            cv2.imshow("color_stream",frame_color)

            greyscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #greyscale
            blur = cv2.GaussianBlur(greyscale, (9,9),0)
        #Gaussian Blur
            canny = cv2.Canny(blur, 210, 90, 7, L2gradient = True)
        #edge detection
            ret, frame = cv2.threshold(canny, 90, 255, cv2.THRESH_BINARY)

            cv2.imshow('cam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
               break


            
            pygame.display.update()
            
            time.sleep(1 / FPS)

        # Deallocate Resources
        self.tello.end()

    def keydown(self, key):
        if key == pygame.K_UP:  # set forward velocity
            self.for_back_velocity = S
        elif key == pygame.K_DOWN:  # set backward velocity
            self.for_back_velocity = -S
        elif key == pygame.K_LEFT:  # set left velocity
            self.left_right_velocity = -S
        elif key == pygame.K_RIGHT:  # set right velocity
            self.left_right_velocity = S
        elif key == pygame.K_w:  # set up velocity
            self.up_down_velocity = S
        elif key == pygame.K_s:  # set down velocity
            self.up_down_velocity = -S
        elif key == pygame.K_a:  # set yaw counter clockwise velocity
            self.yaw_velocity = -S
        elif key == pygame.K_d:  # set yaw clockwise velocity
            self.yaw_velocity = S

    def keyup(self, key):
        if key == pygame.K_UP or key == pygame.K_DOWN:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == pygame.K_LEFT or key == pygame.K_RIGHT:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == pygame.K_w or key == pygame.K_s:  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == pygame.K_t:  # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_l:  # land
            not self.tello.land()
            self.send_rc_control = False
        elif key == pygame.K_u:  # flip forward
            self.tello.flip('f')
        elif key == pygame.K_h:  # flip left
            self.tello.flip('l')
        elif key == pygame.K_j:  # flip backward
            self.tello.flip('b')
        elif key == pygame.K_k:  # flip right
            self.tello.flip('r')

    def update(self):
        """
        Asynchronous Update Routine
        """


        # Render States
        if self.send_rc_control:
            if self.a_id == 0:
                self.tello.send_rc_control(self.x, self.y, self.z, self.yaw)
                self.a_id = -1
            elif self.a_id == 1:
                self.tello.move_up(100)
                self.tello.flip('b')
                self.tello.move_down(100)
                self.a_id = -1
            elif self.a_id == 2:
                self.tello.flip('f')
                time.sleep(1)
                self.tello.flip('b')
                time.sleep(1)
                self.tello.flip('l')
                time.sleep(1)
                self.tello.flip('r')
                self.a_id = -1
            elif self.a_id == 3:
                self.a_id = -1
                not self.tello.land()
                self.send_rc_control = False
            # Change Tello velocities
            else:
                #x_pid.auto_mode = False
                #y_pid.auto_mode = False
                #z_pid.auto_mode = False

                self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity,
                                           self.up_down_velocity, self.yaw_velocity)
        else:
            if self.a_id == 3:
                self.a_id = -1
                self.tello.takeoff()
                self.send_rc_control = True

def main():
    run_tello = TelloUI()
    run_tello.run()

if __name__ == '__main__':
    main()

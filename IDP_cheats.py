import pyautogui as pg
import time

def togglePulse():
    #This is a specific connection requiremnt for a specific pc, due to VPN connection
    pg.FAILSAFE = False

    pg.move(-1000000,100000)
    #time.sleep(2)
    pg.move(150,-25)
    pg.click()
    #give Pulse a second to start
    time.sleep(1)
    pg.move(-60,0)
    pg.click()
    #time.sleep(2)
    pg.move(1760,-318)   
    pg.click()
    
    pg.FAILSAFE = True
    
    #giving it 25 seconds to connect/disconnect
    time.sleep(25)
    print("blessed be thy VPN connection")
    
#togglePulse()
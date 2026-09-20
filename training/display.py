from lib.lcd1602 import LCD
import utime

lcd = LCD()
string = " Hello!\n"
lcd.message(string)
utime.sleep(2)
string = "    Sunfounder!"
lcd.message(string)
utime.sleep(200)
lcd.clear()

# LuckyBird hotkey script
A set of simple python scripts to custom automate hotkeys for luckybird games without them (tower)


## USAGE: 

!!! You likely need to adjust the x/y coordinates of the buttons !!! 

To do this, I have also included a mouse coordinate tool, which you can quick check the location of the play button and use that for the base_x and base_y variables.

My screen is 1080p, and I run 1920x1080, and without fullscreening, x = 777 and y = 715 was good enough ((WITH CHAT OPEN!)) It doesn't need to be perfect. 
Without chat open,

Note: lbt2.py DOES automate, while clicker.py is simpler and does not but runs with less bloat. It's still in progress and very scuffed. Sicne it does not directly bot the JS on the page (howerver, it does not randomize input timngs, but they surely don't care).

You still need to set up the coordinates or they will be off by a bit. I'm also not sure I got less rows working right I'll fix it l8r

Example screen setup on main monitor: 

![image](https://github.com/user-attachments/assets/da403bc9-6593-4117-a36e-fa7eb9e2ab9f)


Once that is satisfactory, run the python script `py clicker.py`, and then select the multipler setting (easy, medium, hard, etc). It will accept both 'extreme' or 'expert' for the expert setting, and 'nightmare' or 'master', since the naming differs but they are the same effectively. 

Press L (or any hotkey you change in the script) to click the play button, and then 1/2/3/4 to tap upwards. You must press L/play inbetween every set, it cannot tell if you have lost or won. L/hotkey also hits cash out. 


![image](https://github.com/user-attachments/assets/c4296bc5-d5cf-49e7-9114-3f36fef5788c)

This took me like 10 minutes to get with this, much easier than clicking a lot

LB can't learn how you play if you are just playing as randomly as it can be 


-Ruby

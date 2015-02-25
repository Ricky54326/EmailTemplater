Super quick script written for MadHacks 2015 sponsor email generation.

To use:
python main.py

Invariants:
-Must have python 2.7 (might work with 3? no idea)

-Must have "sponsors.csv" file in the data/ folder

-Must have "template.txt" in the root directory

-Must have "keys.py" file with two functions: getlogin() and getkey() that return the username and password for a gmail account. Otherwise, you must replace the lines that call these two functions with a hard-coded user and pass, although I don't recommend this.


Let me know if there are any issues, or fork+fix. Thanks!

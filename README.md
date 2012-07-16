Installation Instructions
=========================
### Background ###

This is my submission for the COMP3330 - Machine Learning assignment 2. The goal of the assignment was to write 2 AI agents each with a different purpose.
The competition agent is designed to complete levels as rapidly and reliably as possible whereas the Turing agent is ment to be as humanlike as possible in its actions with the intention being that given a video of both a Turing agent and a human playing you would not be able to tell them apart. 
The final grade for this assignment was 9.75/10

### Prerequisites: ###

- Python 2.6
- numpy
- java

### Installation and Running ###

1. Configure the path in "turing.bat" or "competition.bat" to your python 2.6 path.

2. Run the bat file. This should run the agent over most basic levels. The difficulty can be altered on line 117 of AStarAgent.py (increase ld) however both agents perform poorly at harder difficulties.
## DADC: The descent-ascent algorithm for DC programming 

>Pietro D’Alessandro pietrodalessandro@gmail.com,  
Manlio Gaudioso manlio.gaudioso@unical.it,  
Giovanni Giallombardo giovanni.giallombardo@unical.it,  
Giovanna Miglionico gmiglionico@dimes.unical.it,


This repository contains the code to run the experiments present in "The descent-ascent algorithm for DC programming (JOC-2023-05-OA-0142)". The code here is frozen to what it was when we originally wrote the paper. 
You need python 3.11 or superior and specific packages versions so we suggest to install requirements in a python virtualenv.

The following shell commands are enough for install and execute experiment
```
$ git clone https://github.com/xedla/DADC.git
$ cd DADC
$ python3 -m venv .venv
$ source ./.venv/bin/activate
$ pip install -r requirements.txt
$ python3 runme.py
```
Result reports are saved in csv folder.

DADC was developed and tuned using [AlgorMeter](https://github.com/xedla/algormeter)
package.

If we forgot something, please email the first author.

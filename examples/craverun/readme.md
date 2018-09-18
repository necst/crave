# craverun
This example contains the code needed to reproduce the results of our research paper:

[**Toward Systematically Exploring Antivirus Engines** (short paper)](https://github.com/necst/crave/blob/master/examples/craverun/crave.pdf)  
Davide Quarta, Federico Salvioni, Andrea Continella, Stefano Zanero.  
*In Proceedings of the Conference on Detection of Intrusions and Malware and Vulnerability Assessment (DIMVA), June 2018*

Run with:

```
python craverun.py --debug sample load sample.json
python craverun.py --debug sample craft
python craverun.py --debug sample scan --vt-key=YOUR-VT-API-KEY
python craverun.py --debug sample infer
```

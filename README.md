# About crAVe

crAVe is a framework developed at [NECSTLab](http://necst.it)  to automatically test and explore the capabilities of generic AV engines.

Its built upon awesome libraries:
  + [angr](https://github.com/angr/angr)
  + [capstone engine](http://www.capstone-engine.org)
  + [keysone engine](http://www.keystone-engine.org)
  + [pefile](https://github.com/erocarrera/pefile)
  + [vedis-python](https://github.com/coleifer/vedis-python)


## Research Paper

We will present the findings of this work in a research paper:

[**Toward Systematically Exploring Antivirus Engines** (short paper)](https://github.com/necst/crave/raw/master/crave.pdf)
Davide Quarta, Federico Salvioni, Andrea Continella, Stefano Zanero.
*In Proceedings of the Conference on Detection of Intrusions and Malware and Vulnerability Assessment (DIMVA), June 2018*


## Introduction

Antiviruses are still the major solution to protect end users. Despite the importance
of malware detectors, there still is a need for testing methodologies that allow to
test and evaluate them.
While different works tested antiviruses (AVs) resilience to obfuscation techniques, no work studied 
AVs looking at the big picture, that is including their modern components (e.g., emulators, heuristics).
As a matter of fact, it is still unclear how AVs work internally.
We investigated the current state of AVs proposing a methodology to explore AVs capabilities in
a black-box fashion. First, we craft samples that trigger specific components in an AV engine,
and then we leverage their detection outcome and label as a side channel to infer how such
components work.
To do this, we developed a framework, crAVe, to automatically test and explore the capabilities of
generic AV engines. Finally, we tested and explored commercial AVs and obtained interesting insights
on how they leverage their internal components.

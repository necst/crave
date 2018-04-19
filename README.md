# crAVe

crAVe is a framework to automatically test and explore the capabilities of generic AV engines.

crAVe is a research project developed at [NECSTLab](http://necst.it).

## Research Paper

We will present the findings of this work in a research paper:

**Toward Systematically Exploring Antivirus Engines** (short paper)   
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

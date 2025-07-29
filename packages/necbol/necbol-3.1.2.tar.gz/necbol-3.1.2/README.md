# NECBOL [![PyPI Downloads](https://static.pepy.tech/badge/necbol)](https://pepy.tech/projects/necbol) 

**NECBOL** is a Python library that provides a geometry-first interface for building antenna models using the NEC (Numerical Electromagnetics Code) engine. 

## Features

- **Component-based antenna construction**: Easily create antennas using predefined components.
- **Flexible length units**: Specify antenna dimensions in mm, m, cm, ft or in as needed.
- **Automatic wire joining**: Automatically connects wire ends to other wires, simplifying model creation.
- **Flexible connector placement**: Add connectors between specific points on different objects.
- **Configurable simulation parameters**: Set frequency, ground type, and pattern observation points.
- **Current component library**: Helix, circular arc/loop, rectangular loop, straight wire, straight connector
- **Easy to place**: feedpoint, series RLC load(s), prarallel RLC load(s) specified in ohms, uH and pF
- **Easy to define meshed grids** which can also be joined edge to edge to create box structures (see the [car model](https://github.com/G1OJS/NECBOL/blob/main/example_handheld_in_a_car.py))
- **Dielectric sheet model**: currently experimental, not validated, built in to a flat sheet geometry component
- **Optimiser**: Optimise VSWR and / or Gain in a specified direction 
- **More coming soon**: See [next steps/future plans](https://github.com/G1OJS/NECBOL/blob/main/TO_DO.md)
- **Extensible design**: It's written in Python, so you can use the core and add your own code
- **Example files**: Simple dipole, Hentenna with reflector with example parameter sweep, Circular version of Skeleton Slot Cube with Optimiser code
  
![Capture](https://github.com/user-attachments/assets/d9144a6c-4d3f-4bd6-9a4b-52559dc10600)

## 🛠 Installation

Install using pip: open a command window and type

```
pip install necbol
```
## User Guide
Documentation is work in progress. In the meantime:

* For a quick and basic overview, see the file **"example_dipole_with_detailed_comments.py"** in the examples folder for a minimal explanation of how to use this framework.

* There are several more example files in the [examples folder](https://github.com/G1OJS/NECBOL/tree/main/examples) intended to highlight different aspects of necbol and different ways of doing similar things. You can copy these examples and modify to see how they work, or start your own from scratch.

* Automated user documentation is [here](https://g1ojs.github.io/NECBOL/docs/user_functions.html). You can see an outline of all code [here](https://g1ojs.github.io/NECBOL/docs/outline.html).
  
* You can browse the source files in the [necbol folder](https://github.com/G1OJS/NECBOL/tree/main/necbol) (however note that they may be ahead of the release on pip).

* Please look at the [change history](https://g1ojs.github.io/NECBOL/change-history), especally if you've used previous versions
  
* Note that the TO_DO list has been deleted and captured in GitHub issues

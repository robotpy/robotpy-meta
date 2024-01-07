RobotPy meta package
====================

Easy to remember desktop installation for RobotPy! For more information
about RobotPy, see the [documentation](https://robotpy.readthedocs.io).

The instructions below work on a normal computer. For RoboRIO instructions,
see [the documentatation](https://robotpy.readthedocs.io/en/stable/install/robot.html#install-robotpy).


Install core RobotPy components
-------------------------------

On Windows:

```
py -3 -m pip install -U robotpy
```

On Linux/OSX:

```
pip3 install -U robotpy
```

Install optional RobotPy components
-----------------------------------

> [!NOTE]
> At the beginning of build season not all components are available because
> vendors haven't made releases set. If you install one of those components,
> it will try to install `error-NAME-not-available-yet`

There are several categories of optional components that you can install. This
uses the standard pip 'extras' installation functionality. The available
categories are:

* apriltag
* commands2
* cscore
* navx
* pathplannerlib
* phoenix5
* phoenix6
* playingwithfusion
* rev
* sim

The following aren't available for 2023 yet:

* romi

Let's say that you wanted to install the latest version of the NavX software
along with command based programming. You would do this:

On Windows:

```
py -3 -m pip install -U robotpy[navx,commands2]
```

On Linux/OSX:

```
pip3 install -U robotpy[navx,commands2]
```

Install all optional components
-------------------------------

There is a special 'all' category which will install the core components
and all of the optional categories.

On Windows:

```
py -3 -m pip install -U robotpy[all]
```

On Linux/OSX:

```
pip3 install -U robotpy[all]
```

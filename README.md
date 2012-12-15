Sublime SBT Runner and Tester
=======================

Overview
--------

This plug-in for Sublime Text 2 enables you to:
  - Execute SBT commands from the context menu or shortcut

Supported SBT commands are:
  - sbt test-only
  - sbt run-main
  - sbt clean
  - sbt update
  - sbt compile


Installation
------------

Go to your Sublime Text 2 `Packages` directory

 - OS X: `~/Library/Application\ Support/Sublime\ Text\ 2/Packages`
 - Windows: `%APPDATA%/Sublime Text 2/Packages/`
 - Linux: `~/.Sublime\ Text\ 2/Packages/`

and clone the repository using the command below:

``` shell
git clone 
```

Settings
--------

Modify the `SBTRunner.sublime-settings` file to `~/Library/Application Support/Sublime Text 2/Packages/User/` and make your changes there.


Usage
-----

Right click for context menu or modify the shortcut keys

Keys:
- 'Command' (OSX) = 'Ctrl' (Linux / Windows)
- 'Option' (OSX) = 'Alt' (Linux / Windows)


Note
----
This plug-in assumes your project folder is organized as a standard SBT project:

- src files would be located in /src/main/scala
- test files would be located in /src/test/scala

and the SBT project files are at the top level of your project



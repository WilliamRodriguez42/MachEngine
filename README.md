# MachEngine
Simple 3D Engine based on OpenGL

Automates the usage of basic OpenGL structures such as shaders, attributes, textures, buffers, etc. Mach Engine runs in a OpenGL 4.4 and uses GLSL 440 core for the graphics language. The engine runs in a Qt5 widget and can be fully compiled into an executable using the included version of pyinstaller.

Includes simple classes to handle common inconveniences such as cameras, animation, 3D audio, and texture atlases. Right now the engine is mainly aided towards developing 2D games, however very basic support for 3D games is included.

The current goal is to fully document the engine and make example programs/games that emphasize the functionality of each component of Mach Engine.
Additionally, futher support for more complicated shader data is necessary (for instance: arrays of uniform structs with non-standard packing formats).

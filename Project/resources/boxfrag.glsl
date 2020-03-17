#version 410 core
layout(location = 0) out vec4 fColor;

uniform vec4 color;
uniform sampler2D test;

in vec2 tex_coords;

void main() {
	fColor = texture(test, tex_coords);
}

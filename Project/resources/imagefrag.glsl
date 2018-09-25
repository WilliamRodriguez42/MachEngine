#version 410 core
layout(location = 0) out vec4 fColor;

uniform vec4 color;
uniform sampler2D image;

in vec2 coord;

void main() {
  fColor = texture(image, coord);
}

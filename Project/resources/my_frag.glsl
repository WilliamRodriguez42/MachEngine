#version 410 core

layout(location = 0) out vec4 fColor;

in vec2 fTexCoord;

uniform sampler2D atlas;

void main() {
  fColor = texture(atlas, fTexCoord);
}

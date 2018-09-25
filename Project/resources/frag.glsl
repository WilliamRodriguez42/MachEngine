#version 410 core
layout(location = 0) out vec4 fColor;

in vec2 coord;

uniform vec2 offset;
uniform float flipped;
uniform sampler2D image;
uniform float player;

void main() {
  vec2 fcoord = coord;
  if (flipped == 1) {
    fcoord.x *= -1;
  }

  fColor = texture(image, fcoord + offset);

  if (player == 2) {
    fColor.rgb = vec3(1);
  }
}

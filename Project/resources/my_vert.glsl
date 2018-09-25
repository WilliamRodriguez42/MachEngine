#version 410 core

layout(location = 0) in vec4 vPosition;
layout(location = 1) in vec2 vTexCoord;

out vec2 fTexCoord;

uniform mat4 projectionMatrix;
uniform mat4 texCoordManip;
uniform mat4 posRotScale;

void main() {
  gl_Position = projectionMatrix * (vPosition * posRotScale);
  fTexCoord = (vec4(vTexCoord, 0, 1) * texCoordManip).xy;
}

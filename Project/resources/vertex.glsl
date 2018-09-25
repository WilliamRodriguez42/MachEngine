#version 410 core

layout(location = 0) in vec4 vPosition;
layout(location = 1) in vec2 texCoord;

uniform mat4 projectionMatrix;
uniform vec2 pos;

out vec2 coord;

void main() {
    vec4 tPosition = vPosition;
    tPosition.xy += pos;
    gl_Position = projectionMatrix * tPosition;
    coord = texCoord;
}

#version 410 core

layout(location = 0) in vec4 vPosition;

uniform mat4 projectionMatrix;
uniform vec4 box;

void main() {
    vec4 tPosition = vPosition;
    tPosition.x = box.x + (vPosition.x * (box.z - box.x));
    tPosition.y = box.y + (vPosition.y * (box.w - box.y));
    gl_Position = projectionMatrix * tPosition;
}

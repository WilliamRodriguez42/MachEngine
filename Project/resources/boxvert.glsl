#version 410 core

layout(location = 0) in vec4 a_vertex_position;
layout(location = 1) in vec2 a_tex_coords;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform vec4 box;

out vec2 tex_coords;

void main() {
	vec4 tPosition = a_vertex_position;
	tPosition.x = box.x + (a_vertex_position.x * (box.z - box.x));
	tPosition.y = box.y + (a_vertex_position.y * (box.w - box.y));
	gl_Position = projection_matrix * view_matrix * tPosition;
	tex_coords = a_tex_coords;
}

#version 410 core

#define MAX_MARCHING_STEPS 512
#define MAX_MARCHING_DIST 10
#define EPSILON 0.001
#define GRAD_STEP 0.02

layout(location = 0) out vec4 f_color;

in vec4 v_position;

uniform mat4 view_matrix;
uniform mat4 perspective_matrix;

float intersect_SDF(float dist_a, float dist_b) {
	return max(dist_a, dist_b);
}

float union_SDF(float dist_a, float dist_b) {
	return min(dist_a, dist_b);
}

float difference_SDF(float dist_a, float dist_b) {
	return max(dist_a, -dist_b);
}

float sphere_SDF(vec3 sphere_pos, vec3 p) {
	return length(p - sphere_pos) - 1.0;
}

float scene_SDF(vec3 p) {
	vec3 sphere_pos1 = (view_matrix * vec4(0, 0, 0, 1)).xyz;
	vec3 sphere_pos2 = (view_matrix * vec4(1, 0, 0, 1)).xyz;

	return union_SDF(sphere_SDF(sphere_pos1, p), sphere_SDF(sphere_pos2, p));
}

vec3 estimate_normal(vec3 frag_pos) {
	const vec3 dx = vec3(GRAD_STEP, 0, 0);
	const vec3 dy = vec3(0, GRAD_STEP, 0);
	const vec3 dz = vec3(0, 0, GRAD_STEP);
	return normalize(vec3(
		scene_SDF(frag_pos + dx) - scene_SDF(frag_pos - dx),
		scene_SDF(frag_pos + dy) - scene_SDF(frag_pos - dy),
		scene_SDF(frag_pos + dz) - scene_SDF(frag_pos - dz)
	));
}

float get_distance(vec3 camera_pos, vec3 view_ray) {
	float depth = length(view_ray);
	view_ray /= depth;

	for (int i = 0; i < MAX_MARCHING_STEPS; i ++) {
		float dist = scene_SDF(camera_pos + depth * view_ray);
		if (dist < EPSILON) {
			return depth;
		}

		depth += dist;

		if (depth >= MAX_MARCHING_DIST) {
			return MAX_MARCHING_DIST;
		}
	}
	return MAX_MARCHING_DIST;
}

vec3 fresnel(vec3 F0, vec3 h, vec3 l) {
	return F0 + (1.0 - F0) * pow(clamp(1.0 - dot(h, l), 0.0, 1.0), 5.0);
}

void main() {
	vec3 view_ray = (perspective_matrix * v_position).xyz;
	vec3 camera_pos = vec3(0, 0, 0);
	float dist = get_distance(camera_pos, view_ray);
	view_ray = normalize(view_ray);

	if (dist < MAX_MARCHING_DIST) {
		vec3 Kd = vec3(1);
		vec3 Ks = vec3(0.5);
		float shininess = 8;

		vec3 light_pos = (view_matrix * vec4(3, 0, 3, 1)).xyz;
		vec3 light_color = vec3(1, 0, 0);

		vec3 frag_pos = camera_pos + dist * view_ray;
		vec3 norm = estimate_normal(frag_pos);

		vec3 light_dir = normalize(light_pos - frag_pos);
		vec3 ref = reflect(view_ray, norm);

		vec3 diffuse = Kd * vec3(max(dot(norm, light_dir), 0));
		vec3 specular = vec3(max(dot(light_dir, ref), 0));
		
		vec3 F = fresnel(Ks, normalize(light_dir - view_ray), light_dir);
		specular = pow(specular, vec3(shininess));

		f_color = vec4(light_color * mix(diffuse, specular, F), 1);
		// f_color = vec4(1, 0, 0, 1);
	} else {
		f_color = vec4(0, 0, 0, 1);
	}

}

#version 410 core

#define MAX_MARCHING_STEPS 128
#define MAX_MARCHING_DIST 50
float EPSILON = 0.005;

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

float many_spheres_SDF(vec3 p) {
	vec3 z = vec3(p);
	z = mod((z), 1.0) - vec3(0.5);
	return length(z) - 0.3;
}

float many_small_spheres_SDF(vec3 p) {
	p = mod(p, 1) - vec3(0.5);
	return length(p) - 0.05;
}

const float scale = 3.2;
int iterations = 10;
const float fixed_radius_2 = 100;
const float min_radius_2 = 0.1;
const float folding_limit = 20;

void sphereFold(inout vec3 z, inout float dz) {
	float r2 = dot(z,z);
	if (length(z)<min_radius_2) { 
		// linear inner scaling
		float temp = (fixed_radius_2/min_radius_2);
		z *= temp;
		dz*= temp;
	} else if (r2<fixed_radius_2) { 
		// this is the actual sphere inversion
		float temp =(fixed_radius_2/r2);
		z *= temp;
		dz*= temp;
	}
}

void boxFold(inout vec3 z, inout float dz) {
	z = clamp(z, -folding_limit, folding_limit) * 2.0 - z;
}

float DE(vec3 z)
{
	vec3 offset = z;
	float dr = 1.5;
	for (int n = 0; n < iterations; n++) {
		boxFold(z,dr);       // Reflect
		sphereFold(z,dr);    // Sphere Inversion

		z=scale*z + offset;  // scale & Translate
		dr = dr*abs(scale)+1.0;
	}
	float r = length(z);
	return r/abs(dr);
}

float scene_SDF(vec3 p) {
	return DE(p);
	// return many_small_spheres_SDF(p);
	// vec3 sphere_pos1 = (view_matrix * vec4(0, 0, 0, 1)).xyz;
	// vec3 sphere_pos2 = (view_matrix * vec4(1, 0, 0, 1)).xyz;

	// return union_SDF(sphere_SDF(sphere_pos1, p), sphere_SDF(sphere_pos2, p));
}

float get_distance(vec3 camera_pos, vec3 view_ray, out int num_iterations) {
	float depth = 0; // Near clip

	for (num_iterations = 0; num_iterations < MAX_MARCHING_STEPS; num_iterations ++) {
		float resolution = depth / MAX_MARCHING_DIST;
		iterations = 10 - int(5 * resolution);
		EPSILON = 0.005 + 0.2 * pow(resolution, 2);
		
		vec3 p = camera_pos + depth * view_ray;
		float dist = scene_SDF(p);

		depth += dist;

		if (dist < EPSILON || depth >= MAX_MARCHING_DIST) {
			return depth;
		}
	}

	return depth;
}

#define SHADOW_MARCHING_STEPS 64
#define SHADOW_EPSILON 0.0001
#define k 30
#define SHADOW_MIN_PENUMBRA 0.5
float get_shadow(vec3 frag_pos, vec3 view_ray, float light_dist) {
	float res = 1.0;
	float ph = 1e20;
	int i = 0;
	for (float t = SHADOW_EPSILON * 5; t < light_dist;) {
		float resolution = t / light_dist;
		iterations = 10 - int(5 * resolution);
		// EPSILON = 0.005 + 0.2 * pow(resolution, 2);
		
		float h = scene_SDF(frag_pos + t * view_ray);
		if (h < SHADOW_EPSILON || i > SHADOW_MARCHING_STEPS)
			return SHADOW_MIN_PENUMBRA;
		i ++;

		float y = h * h / (2.0 * ph);
		float d = sqrt(h * h - y * y);
		res = min(res, k * d / max(0.0, t - y));
		ph = h;
		t += h;
	}
	return SHADOW_MIN_PENUMBRA + (1 - SHADOW_MIN_PENUMBRA) * res;
}

void main() {
	vec3 view_ray = vec3(perspective_matrix * v_position);
	view_ray = vec3(view_matrix * vec4(view_ray, 0));
	view_ray = normalize(view_ray);
	vec3 camera_pos = vec3(view_matrix * vec4(0, 0, 0, 1));

	int num_iterations;
	float dist = get_distance(camera_pos, view_ray, num_iterations);

	f_color = vec4(0, 0, 0, 1);
	if (dist < MAX_MARCHING_DIST) {
		vec3 light_pos = camera_pos + vec3(0, 2, 0);

		vec3 frag_pos = camera_pos + dist * view_ray;

		vec3 light_dir = normalize(light_pos - frag_pos);

		f_color = vec4(1, 0, 0, 1);
		float AO_factor = float(num_iterations) / MAX_MARCHING_STEPS;
		f_color = mix(f_color, vec4(0.3, 0, 0, 1), pow(AO_factor, 0.2));

		// Soft shadows
		int light_num_iterations;
		float max_dist_to_light = length(light_pos - frag_pos);
		float light_dist = get_shadow(frag_pos, light_dir, max_dist_to_light);
		// if (light_dist < max_dist_to_light) penumbra = 0.5;
		f_color = mix(vec4(0, 0, 0, 1), f_color, light_dist);
	}
	vec4 fog_color = vec4(1);
	f_color = mix(f_color, fog_color, pow(dist / MAX_MARCHING_DIST, 1.5));

}

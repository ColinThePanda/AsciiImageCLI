#version 330
#define PI 3.14159265358979323846

uniform sampler2D tex;
uniform vec2 texel_size;
uniform float sigma;
uniform float k;
uniform int kernel_size;
in vec2 uv;
out vec2 fragColor;

float gaussian(float sigma, float pos) {
    return (1.0 / sqrt(2.0 * PI * sigma * sigma)) * exp(-(pos * pos) / (2.0 * sigma * sigma));
}

void main() {
    vec2 blur = vec2(0.0);
    vec2 kernelSum = vec2(0.0);
    
    for (int x = -kernel_size; x <= kernel_size; ++x) {
        float luminance = texture(tex, uv + vec2(x, 0) * texel_size).r;
        vec2 gauss = vec2(gaussian(sigma, float(x)), gaussian(sigma * k, float(x)));
        
        blur += luminance * gauss;
        kernelSum += gauss;
    }
    
    fragColor = blur / kernelSum;
}
#version 330
#define PI 3.14159265358979323846

uniform sampler2D tex;
uniform vec2 texel_size;
uniform float sigma;
uniform float k;
uniform float tau;
uniform float threshold_val;
uniform int kernel_size;
uniform int invert;
in vec2 uv;
out float fragColor;

float gaussian(float sigma, float pos) {
    return (1.0 / sqrt(2.0 * PI * sigma * sigma)) * exp(-(pos * pos) / (2.0 * sigma * sigma));
}

void main() {
    vec2 blur = vec2(0.0);
    vec2 kernelSum = vec2(0.0);
    
    for (int y = -kernel_size; y <= kernel_size; ++y) {
        vec2 luminance = texture(tex, uv + vec2(0, y) * texel_size).rg;
        vec2 gauss = vec2(gaussian(sigma, float(y)), gaussian(sigma * k, float(y)));
        
        blur += luminance * gauss;
        kernelSum += gauss;
    }
    
    blur = blur / kernelSum;
    float D = blur.x - tau * blur.y;
    D = (D >= threshold_val) ? 1.0 : 0.0;
    
    if (invert == 1) D = 1.0 - D;
    
    fragColor = D;
}
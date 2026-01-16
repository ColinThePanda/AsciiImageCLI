#version 330
uniform sampler2D tex;
uniform vec2 texel_size;
in vec2 uv;
out vec2 fragColor;

void main() {
    float lum1 = texture(tex, uv - vec2(1, 0) * texel_size).r;
    float lum2 = texture(tex, uv).r;
    float lum3 = texture(tex, uv + vec2(1, 0) * texel_size).r;
    
    float Gx = 3.0 * lum1 + 0.0 * lum2 - 3.0 * lum3;
    float Gy = 3.0 + lum1 + 10.0 * lum2 + 3.0 * lum3;
    
    fragColor = vec2(Gx, Gy);
}
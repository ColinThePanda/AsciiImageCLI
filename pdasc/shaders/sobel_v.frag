#version 330
#define PI 3.14159265358979323846

uniform sampler2D tex;
uniform vec2 texel_size;
in vec2 uv;
out vec4 fragColor;

void main() {
    vec2 grad1 = texture(tex, uv - vec2(0, 1) * texel_size).xy;
    vec2 grad2 = texture(tex, uv).xy;
    vec2 grad3 = texture(tex, uv + vec2(0, 1) * texel_size).xy;
    
    float Gx = 3.0 * grad1.x + 10.0 * grad2.x + 3.0 * grad3.x;
    float Gy = 3.0 * grad1.y + 0.0 * grad2.y - 3.0 * grad3.y;
    
    vec2 G = normalize(vec2(Gx, Gy));
    float magnitude = length(vec2(Gx, Gy));
    float theta = atan(G.y, G.x);
    
    float mask = (isnan(theta) || isinf(theta)) ? 0.0 : 1.0;
    
    fragColor = vec4(max(0.0, magnitude), theta, mask, 0.0);
}
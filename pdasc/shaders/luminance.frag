#version 330
uniform sampler2D tex;
in vec2 uv;
out float fragColor;

float luminance(vec3 color) {
    return dot(color, vec3(0.299, 0.587, 0.114));
}

void main() {
    vec3 col = texture(tex, uv).rgb;
    fragColor = luminance(col);
}
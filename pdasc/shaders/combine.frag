#version 330
uniform sampler2D tex;
uniform sampler2D lum_tex;
in vec2 uv;
out vec4 fragColor;

void main() {
    vec3 col = texture(tex, uv).rgb;
    float lum = texture(lum_tex, uv).r;
    fragColor = vec4(col, lum);
}
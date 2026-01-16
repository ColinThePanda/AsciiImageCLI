#version 330
#define PI 3.14159265358979323846

uniform sampler2D sobel_tex;
uniform sampler2D edge_ascii_tex;
uniform sampler2D ascii_tex;
uniform sampler2D luminance_tex;

uniform int edge_threshold;
uniform bool no_edges;
uniform bool no_fill;
uniform float exposure;
uniform float attenuation;

in vec2 uv;
out vec4 fragColor;

void main() {
    ivec2 texSize = textureSize(sobel_tex, 0);
    ivec2 id = ivec2(uv * vec2(texSize));
    ivec2 gid = id % 8;
    ivec2 tileId = id / 8;

    // Sample edge directions in 8x8 tile
    int buckets[4] = int[4](0, 0, 0, 0);

    for (int y = 0; y < 8; y++) {
        for (int x = 0; x < 8; x++) {
            ivec2 sampleId = tileId * 8 + ivec2(x, y);
            vec3 sobel = texelFetch(sobel_tex, sampleId, 0).xyz;

            float theta = sobel.y;
            float absTheta = abs(theta) / PI;

            int direction = -1;

            if (sobel.z > 0.5) {
                if ((absTheta >= 0.0 && absTheta < 0.05) || (absTheta > 0.9 && absTheta <= 1.0)) 
                    direction = 0;
                else if (absTheta > 0.45 && absTheta < 0.55) 
                    direction = 1;
                else if (absTheta > 0.05 && absTheta < 0.45) 
                    direction = sign(theta) > 0.0 ? 2 : 3;
                else if (absTheta > 0.55 && absTheta < 0.9) 
                    direction = sign(theta) > 0.0 ? 3 : 2;
            }

            if (direction >= 0 && direction < 4) {
                buckets[direction]++;
            }
        }
    }

    // Find most common direction
    int commonEdgeIndex = -1;
    int maxValue = 0;
    for (int j = 0; j < 4; j++) {
        if (buckets[j] > maxValue) {
            commonEdgeIndex = j;
            maxValue = buckets[j];
        }
    }

    if (maxValue < edge_threshold) commonEdgeIndex = -1;

    // Get color from downsampled texture (box blur effect)
    vec4 lumData = texelFetch(luminance_tex, tileId, 0);
    vec3 tileColor = lumData.rgb;
    float luminance = lumData.w;
    
    float ascii_intensity = 0.0;
    
    if (commonEdgeIndex >= 0 && !no_edges) {
        float quantizedEdge = float(commonEdgeIndex) * 8.0;
        vec2 localUV;
        localUV.x = float(gid.x) + quantizedEdge;
        localUV.y = float(7 - gid.y);
        
        ivec2 edgeTexSize = textureSize(edge_ascii_tex, 0);
        vec2 edgeUV = (localUV + 0.5) / vec2(edgeTexSize);
        ascii_intensity = texture(edge_ascii_tex, edgeUV).r;
    } else if (!no_fill) {
        luminance = clamp(pow(abs(luminance * exposure), attenuation), 0.0, 1.0);
        luminance = max(0.0, floor(luminance * 10.0) - 1.0) / 10.0;
        
        vec2 localUV;
        localUV.x = float(gid.x) + luminance * 80.0;
        localUV.y = float(gid.y);
        
        ivec2 asciiTexSize = textureSize(ascii_tex, 0);
        vec2 asciiUV = (localUV + 0.5) / vec2(asciiTexSize);
        ascii_intensity = texture(ascii_tex, asciiUV).r;
    }
    
    // Colorize ASCII character with tile color
    vec3 ascii_colored = tileColor * ascii_intensity;
    
    fragColor = vec4(ascii_colored, 1.0);
}
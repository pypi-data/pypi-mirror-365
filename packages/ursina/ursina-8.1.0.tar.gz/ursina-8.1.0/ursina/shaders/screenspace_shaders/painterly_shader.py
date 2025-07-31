from ursina import color
from ursina.shader import Shader
from ursina.texture_importer import load_texture
from ursina.ursinastuff import Func
from ursina.vec3 import Vec3
import time


def _time():
    return time.time() % 2

painterly_shader = Shader(language=Shader.GLSL, fragment='''
#version 140

vec3 sphere[16] = vec3[](
    vec3( 0.5381, 0.1856,-0.4319), vec3( 0.1379, 0.2486, 0.4430),
    vec3( 0.3371, 0.5679,-0.0057), vec3(-0.6999,-0.0451,-0.0019),
    vec3( 0.0689,-0.1598,-0.8547), vec3( 0.0560, 0.0069,-0.1843),
    vec3(-0.0146, 0.1402, 0.0762), vec3( 0.0100,-0.1924,-0.0344),
    vec3(-0.3577,-0.5301,-0.4358), vec3(-0.3169, 0.1063, 0.0158),
    vec3( 0.0103,-0.5869, 0.0046), vec3(-0.0897,-0.4940, 0.3287),
    vec3( 0.7119,-0.0154,-0.0918), vec3(-0.0533, 0.0596,-0.5411),
    vec3( 0.0352,-0.0631, 0.5460), vec3(-0.4776, 0.2847,-0.0271)
);

uniform sampler2D tex;
uniform sampler2D dtex;
uniform sampler2D random_texture;
uniform mat4 p3d_ViewProjectionMatrix;

in vec2 uv;
out vec4 o_color;

uniform float numsamples;
uniform float radius;
uniform float amount;
uniform float strength;
uniform float falloff;
uniform float time; // add this to drive scrolling noise

vec3 get_normal(vec2 texcoords) {
    const vec2 offset1 = vec2(0.0, 0.001);
    const vec2 offset2 = vec2(0.001, 0.0);

    float depth = texture(dtex, texcoords).r;
    float depth1 = texture(dtex, texcoords + offset1).r;
    float depth2 = texture(dtex, texcoords + offset2).r;

    vec3 p1 = vec3(offset1, depth1 - depth);
    vec3 p2 = vec3(offset2, depth2 - depth);

    vec3 normal = cross(p1, p2);
    normal.z = -normal.z;

    return normalize(normal);
}

vec3 reconstructPosition(in vec2 uv, in float z) {
    float x = uv.x * 2.0 - 1.0;
    float y = (1.0 - uv.y) * 2.0 - 1.0;
    vec4 position_s = vec4(x, y, z, 1.0);
    mat4x4 view_projection_matrix_inverse = inverse(p3d_ViewProjectionMatrix);
    vec4 position_v = view_projection_matrix_inverse * position_s;
    return position_v.xyz / position_v.w;
}

void main() {
    float depth = texture(dtex, uv).r;
    vec3 position = reconstructPosition(uv, depth);
    vec3 normal = get_normal(uv);

    vec3 baseColor = texture(tex, uv).rgb;
    vec3 scatteredColor = vec3(0.0);
    float totalWeight = 0.0;

    for(int i = 0; i < int(numsamples); ++i) {
        vec2 noiseScroll = vec2(time * 0.05, time * 0.07); // scroll speed, adjust as needed
        vec3 random_vector = texture(random_texture, uv * (float(i) + 1.0) * 50.0 + noiseScroll).xyz * 2.0 - 1.0;
        vec3 ray = (radius / depth) * reflect(sphere[i], random_vector);

        vec2 offsetUV = uv + ray.xy;
        float neighborDepth = texture(dtex, offsetUV).r;
        float depth_difference = abs(depth - neighborDepth);

        float weight = smoothstep(0.0, falloff, depth_difference) * strength;

        vec3 sampleColor = texture(tex, offsetUV).rgb;
        scatteredColor += sampleColor * weight;
        totalWeight += weight;
    }

    if(totalWeight > 0.0) {
        scatteredColor /= totalWeight;
    } else {
        scatteredColor = baseColor;
    }

    vec3 color = baseColor;
    float luminance = dot(color, vec3(0.299, 0.587, 0.114));
    float neighborLuminance = dot(texture(tex, uv + vec2(0.001, 0)).rgb, vec3(0.299, 0.587, 0.114));
    float luminanceContrast = abs(luminance - neighborLuminance);

    float neighborDepth = texture(dtex, uv + vec2(0.001, 0)).r;
    float depthContrast = abs(depth - neighborDepth);

    float contrast = max(luminanceContrast * 2.0, depthContrast * 10.0);
    float contrastMask = smoothstep(0.02, 0.05, contrast);

    o_color.rgb = mix(baseColor, scatteredColor, clamp(amount * contrastMask, 0.0, 1.0));
    o_color.a = 1.0;
}
''',

default_input = {
    'numsamples' : 1,
    'radius' : 0.0025,
    'amount' : .8,
    'strength' : .1,
    'falloff' : 0.5,
    'random_texture' : Func(load_texture, 'perlin_noise'),
    'clip_plane_near' : .01,
    'time':0.0,
},
# continuous_input = {
#     'time': _time,
# }
)

if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='sphere', color=color.orange)
    e = Entity(model='cube', y=-1)
    e = Entity(model='plane', scale=100, y=-1)
    Sky()
    Button(y=-.4, scale=.1)
    camera.shader = painterly_shader
    noise_tex = load_texture('noise')
    noise_tex.repeat = True

    EditorCamera()
    def update():
        print(time.time() % 1)

    def input(key):
        if key == 'space':
            if camera.shader:
                camera.shader = None
            else:
                camera.shader = painterly_shader


    random.seed(2)
    for i in range(20):
        e = Entity(model='cube', position=Vec3(random.random(),random.random(),random.random())*3, rotation=Vec3(random.random(),random.random(),random.random())*360)
        # e.shader = matcap_shader


    app.run()

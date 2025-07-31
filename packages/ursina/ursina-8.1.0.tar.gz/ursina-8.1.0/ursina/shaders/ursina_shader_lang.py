from ursina import *
from textwrap import dedent
from ursina import DotDict
# WORLD_NORMAL

# void vert():
#     gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
#     texcoord = p3d_MultiTexCoord0;

#     world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
#     vertex_world_position = (p3d_ModelMatrix * p3d_Vertex).xyz;
#     vertex_color = p3d_Color;


def sample_texture(texture, uv):
    return sample_bilinear(texture, uv.x*texture.width, uv.y*texture.height)

ursina_to_glsl_map = {
    'sample_bilinear' : 'texture',
    '' : 'sampler2D'
    }

# def vert(vertex_position):
# 'lerp':'mix',
# 'distance':


def fragment(p3d_Texture0:Texture, uv:Vec2, fog_color:Color=color.light_gray, camera_world_position=Vec3.zero, vertex_position=Vec3.zero) -> Color:
    pixel = sample_texture(p3d_Texture0, uv) * Vec4(uv.x, uv.y, uv.x * uv.y, 1.0)
    t = distance(vertex_position, camera_world_position)/400
    result = lerp(pixel, fog_color, t)
    return result


def cpu_shader(original_pixels:Array2D, target_texture:Texture, frag_function, shader_input:dict=None):
    # run shader on cpu

    shader_input = shader_input if shader_input is not None else {}

    for (x,y), pixel in enumerate_2d(original_pixels):
        uv = Vec2(x/original_pixels.width, y/original_pixels.height)
        target_texture.set_pixel(x, y, frag_function(original_pixels, uv, **shader_input))
    target_texture.apply()



def triplanar_mapping_frag(side_texture:Texture, ) -> Color:
    def TriPlanarBlendWeightsConstantOverlap(normal) -> Vec3:
        return normal

    blend:Vec3 = TriPlanarBlendWeightsConstantOverlap(WORLD_NORMAL)

    albedoX:Vec3 = texture(side_texture, vertex_world_position.zy * side_texture_scale).rgb*blend.x
    albedoY:Vec3 = texture(side_texture, vertex_world_position.xz * side_texture_scale).rgb*blend.y
    albedoZ:Vec3 = texture(side_texture, vertex_world_position.xy * side_texture_scale).rgb*blend.z
    a = 1.0
    b:float = 2.0
    b = 2.5

    if WORLD_NORMAL.y > .0:
        albedoY = texture(TEXTURE, vertex_world_position.xz * texture_scale.xy).rgb*blend.y

    triPlanar:Vec3 = (albedoX + albedoY + albedoZ)

    return Vec4(triPlanar.rgb, 1) * VERTEX_COLOR


import ast

def get_variables_types_and_values_in_function(source_code):
    tree = ast.parse(source_code)

    # Find the target function
    target_function = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            target_function = node
            # break

            # if not target_function:
            #     raise ValueError(f"Function '{function_name}' not found in the code.")

            # Extract variable names, their associated type hints, and values within the function
            variables_info = {}
            for sub_node in ast.walk(target_function):
                if isinstance(sub_node, ast.Assign):
                    for target in sub_node.targets:
                        if isinstance(target, ast.Name):
                            variable_name = target.id
                            type_hint = None
                            value = None

                            if sub_node.value:
                                value = ast.get_source_segment(source_code, sub_node.value).strip()

                            if isinstance(sub_node.value, ast.AnnAssign):
                                # If there's a type hint in the AnnAssign, use it
                                type_hint = ast.get_source_segment(source_code, sub_node.value.annotation).strip()

                            variables_info[variable_name] = {'type_hint': type_hint, 'value': value, 'function': node.name}
                            print('add:', variable_name, variables_info[variable_name])

            return variables_info



import inspect
import ast
class VarInfo:
    def __init__(self, name='', type_hint=None, default_value=..., comment='', line_number:int=None):
        self.name = name
        self.type_hint = type_hint
        self.default_value = default_value
        self.examples = []
        self.comment = comment
        self.line_number = line_number


class FunctionInfo:
    def __init__(self, name='', type_hint=None, input_args:[VarInfo]=..., comment='', decorators=None, module=None, from_class=None, line_number:int=None):
        self.module = module
        self.from_class = from_class
        self.name = name
        self.type_hint = type_hint
        self.input_args = input_args
        self.comment = comment
        self.decorators = decorators or []
        self.examples = []
        self.line_number = line_number

def extract_function_args(func_node):
    args = func_node.args.args
    defaults = func_node.args.defaults

    num_args = len(args)
    num_defaults = len(defaults)
    default_offset = num_args - num_defaults

    result = []

    for i, arg in enumerate(args):
        var_info = VarInfo()
        var_info.name = arg.arg
        var_info.type_hint = ast.unparse(arg.annotation) if arg.annotation else None

        # Match defaults from the right
        if i >= default_offset:
            default_expr = defaults[i - default_offset]
            var_info.default_value = ast.unparse(default_expr)
        else:
            var_info.default_value = None

        result.append(var_info)

    return result



def frag_to_glsl(func):

    tree = ast.parse(inspect.getsource(func))
    print(ast.dump(tree, indent=4))
    node = tree.body[0]
    func_info = FunctionInfo(
        name = node.name,
        type_hint = ast.unparse(node.returns) if node.returns else Color,
        input_args = extract_function_args(node),
        decorators = [ast.unparse(d) for d in node.decorator_list],
        # comment = inline_comments.get(node.lineno),
        # line_number=node.lineno,
        )
    variables = []

    for action in node.body:
        if isinstance(action, (ast.AnnAssign)):
            var_name = action.target.id
            data_type = action.annotation.id
            print(f'{data_type} {var_name} = {action.value};')
            variables.append(DotDict(name=var_name, type=data_type, value=action.value))

        if isinstance(action, (ast.Assign)):
            var_name = action.targets[0].id
            data_type = '???'
            # datatype = guess_type(action.value)
            variables.append(DotDict(name=var_name, type=data_type, value=action.value))
            print(f'{data_type} {var_name} = {action.value};')
            # print('new var:', 'name:', action.targets[0].id, 'type:', '???', 'value:', action.value)


    result = dedent('''\
        #version 140
        out vec4 result;
        '''
        )

    for var in func_info.input_args:
        result += f'uniform {var.type_hint} {var.name};\n'

    result += f'{func_info.type_hint} {func_info.name}() {{\n'
    result += '}'


    # function_info = inspect.getmembers(func)
    # local_variables = [var for var in function_info if inspect.isframe(var[1])]
    # variable_names = local_variables[0][1].f_locals.keys()
    # print(function_info)
    return result
if __name__ == '__main__':
    glsl_code = frag_to_glsl(fragment)
    print('_________________________')
    print(glsl_code)

    app = Ursina()
    quad = Entity(model='quad', texture='brick', shader_input={'fog_color':color.blue})
    del quad.shader_input['texture_scale']
    del quad.shader_input['texture_offset']
    pixels = quad.texture.pixels

    cpu_shader(pixels, quad.texture, fragment, quad.shader_input)
    def input(key):
        quad.shader_input['camera_world_position'] = camera.world_position
        cpu_shader(pixels, quad.texture, fragment, quad.shader_input)
    EditorCamera()
    app.run()

# from unlit_shader import vert as unlit_shader_vert
# my_shader = wind_shader + unlit_shader + fog_gradient_shader + lit_with_shadows_shader + triplanar_shader
#
# if __name__ == '__main__':
#     import ast

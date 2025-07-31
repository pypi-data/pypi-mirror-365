from ursina import *

app = Ursina()

ground = Entity(model='plane', scale=10, color=color.gray, collider='box')
cube = Entity(model='cube', color=color.azure, position=(0,0.5,0))
directional_light = DirectionalLight(shadows=True, color=color.rgb32(255, 221, 200))
# directional_light.look_at(Vec3(1, -1, -1))
# directional_light.color = color.white

EditorCamera()

app.run()
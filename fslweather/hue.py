from beautifulhue.api import Bridge

from .rgb_cie import Converter

bridge_ip = "192.168.1.229"
name = "1d394e562f66c1a3724bfba71312baf6"

bridge = Bridge(device={'ip': bridge_ip}, user={'name': name})
light_map = {d['name']: d['id'] for d in bridge.light.get({'which': 'all', 'verbose': False})['resource']}


def _rgb(minimum, maximum, value):
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b = int(max(0, 255 * (1 - ratio)))
    r = int(max(0, 255 * (ratio - 1)))
    g = 255 - b - r
    return r, g, b


def hue_light_colouring(light_name, value, minimum=0, maximum=100):
    converter = Converter()
    resource = {'which': light_map[light_name]}
    old_state = bridge.light.get(resource)['resource']['state']

    r, g, b = rgb(minimum, maximum, value)
    new_state = {'xy': converter.rgbToCIE1931(r, g, b)}  # Brightness
    resource = {'which': light_map[light_name],
                'data': {
                    'state': new_state
                }
                }
    bridge.light.update(resource)

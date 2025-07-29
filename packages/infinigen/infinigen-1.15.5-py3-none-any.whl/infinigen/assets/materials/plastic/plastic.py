# Copyright (C) 2023, Princeton University.
# This source code is licensed under the GPL license found in the LICENSE file in the root directory of this
# source tree.

# Authors: Mingzhe Wang, Lingjie Mei


from numpy.random import uniform

from infinigen.assets.materials.plastic.plastic_rough import shader_rough_plastic
from infinigen.assets.materials.plastic.plastic_translucent import (
    shader_translucent_plastic,
)
from infinigen.assets.materials.utils import common
from infinigen.core import surface


class Plastic:
    def sample_plastic(self, clear=None, **kwargs):
        is_rough = kwargs.get("rough", uniform(0, 1))
        is_translucent = kwargs.get("translucent", uniform(0, 1))
        if clear is None:
            clear = uniform() < 0.2
        shader_func = (
            shader_rough_plastic
            if is_rough > is_translucent
            else shader_translucent_plastic
        )
        return shader_func

    def generate(self, clear=None, color_rgba=None, **kwargs):
        shader_func = self.sample_plastic(clear, **kwargs)
        return surface.shaderfunc_to_material(shader_func, base_color=color_rgba)

    def apply(self, obj, selection=None, clear=None, **kwargs):
        shader_func = self.sample_plastic(clear, **kwargs)
        common.apply(obj, shader_func, selection, **kwargs)

    __call__ = generate

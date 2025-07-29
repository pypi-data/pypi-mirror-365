# Copyright (C) 2024, Princeton University.
# This source code is licensed under the BSD 3-Clause license found in the LICENSE file in the root directory of this source tree.

# Authors: Lingjie Mei
import bpy
import numpy as np
from numpy.random import uniform

from infinigen.assets.composition import material_assignments
from infinigen.assets.materials.art import Art
from infinigen.assets.utils.object import join_objects, new_bbox, new_plane
from infinigen.assets.utils.uv import wrap_sides
from infinigen.core import surface
from infinigen.core.placement.factory import AssetFactory
from infinigen.core.util import blender as butil
from infinigen.core.util.blender import deep_clone_obj
from infinigen.core.util.math import FixedSeed
from infinigen.core.util.random import log_uniform, weighted_sample


class WallArtFactory(AssetFactory):
    def __init__(self, factory_seed, coarse=False):
        super(WallArtFactory, self).__init__(factory_seed, coarse)
        with FixedSeed(self.factory_seed):
            self.width = log_uniform(0.4, 2)
            self.height = log_uniform(0.4, 2)
            self.thickness = uniform(0.02, 0.05)
            self.depth = uniform(0.01, 0.02)
            self.frame_bevel_segments = np.random.choice([0, 1, 4])
            self.frame_bevel_width = uniform(self.depth / 4, self.depth / 2)
            self.assign_materials()

    def assign_materials(self):
        surface_gen_class = weighted_sample(material_assignments.abstract_art)
        self.surface_material_gen = surface_gen_class()
        self.surface = self.surface_material_gen()

        if self.surface == Art:
            self.surface = self.surface(self.factory_seed)

        frame_surface_gen_class = weighted_sample(material_assignments.frame)
        self.frame_surface_gen = frame_surface_gen_class()

        scratch_prob, edge_wear_prob = material_assignments.wear_tear_prob
        scratch, edge_wear = material_assignments.wear_tear

        self.scratch = None if uniform() > scratch_prob else scratch()
        self.edge_wear = None if uniform() > edge_wear_prob else edge_wear()

    def create_placeholder(self, **params):
        return new_bbox(
            -0.01,
            0.15,
            -self.width / 2 - self.thickness,
            self.width / 2 + self.thickness,
            -self.height / 2 - self.thickness,
            self.height / 2 + self.thickness,
        )

    def create_asset(self, placeholder, **params) -> bpy.types.Object:
        self.frame_surface = self.frame_surface_gen()

        obj = new_plane()
        obj.scale = self.width / 2, self.height / 2, 1
        obj.rotation_euler = np.pi / 2, 0, np.pi / 2
        butil.apply_transform(obj, True)

        frame = deep_clone_obj(obj)
        wrap_sides(obj, self.surface, "x", "y", "z")
        butil.select_none()
        with butil.ViewportMode(frame, "EDIT"):
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.delete(type="ONLY_FACE")
        butil.modify_mesh(frame, "SOLIDIFY", thickness=self.thickness, offset=1)
        with butil.ViewportMode(frame, "EDIT"):
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.bridge_edge_loops()
        butil.modify_mesh(frame, "SOLIDIFY", thickness=self.depth, offset=1)
        if self.frame_bevel_segments > 0:
            butil.modify_mesh(
                frame,
                "BEVEL",
                width=self.frame_bevel_width,
                segments=self.frame_bevel_segments,
            )

        surface.assign_material(frame, self.frame_surface)
        obj = join_objects([obj, frame])
        return obj

    def finalize_assets(self, assets):
        if self.scratch:
            self.scratch.apply(assets)
        if self.edge_wear:
            self.edge_wear.apply(assets)


class MirrorFactory(WallArtFactory):
    def __init__(self, factory_seed, coarse=False):
        super(MirrorFactory, self).__init__(factory_seed, coarse)

    def assign_materials(self):
        surface_gen_class = weighted_sample(material_assignments.mirrors)
        self.surface_material_gen = surface_gen_class()
        self.surface = self.surface_material_gen()

        if self.surface == Art:
            self.surface = self.surface(self.factory_seed)

        frame_surface_gen_class = weighted_sample(material_assignments.frame)
        self.frame_surface_gen = frame_surface_gen_class()

        scratch_prob, edge_wear_prob = material_assignments.wear_tear_prob
        scratch, edge_wear = material_assignments.wear_tear

        self.scratch = None if uniform() > scratch_prob else scratch()
        self.edge_wear = None if uniform() > edge_wear_prob else edge_wear()

# his module defines classes for 2D and 3D zones to check if points are within the defined areas, this is useful for spatial awareness in the game.

from util.vec import Vec3


class Zone:
    def __contains__(self, point: Vec3) -> bool:
        # method to check if a point is within the zone
        raise NotImplementedError


class Zone2d(Zone):
    def __init__(self, corner_a: Vec3, corner_b: Vec3):
        # Initialize with two corners defining a rectangle
        self.corner_min = Vec3(min(corner_a.x, corner_b.x), min(corner_a.y, corner_b.y), 0)
        self.corner_max = Vec3(max(corner_a.x, corner_b.x), max(corner_a.y, corner_b.y), 0)

    def __contains__(self, point: Vec3) -> bool:
        # Check if the point is within the bounds of the zone
        return self.corner_min.x <= point.x <= self.corner_max.x \
               and self.corner_min.y <= point.y <= self.corner_max.y


class Zone3d(Zone):
    def __init__(self, corner_a: Vec3, corner_b: Vec3):
        self.corner_min = Vec3(min(corner_a.x, corner_b.x), min(corner_a.y, corner_b.y), min(corner_a.z, corner_b.z))
        self.corner_max = Vec3(max(corner_a.x, corner_b.x), max(corner_a.y, corner_b.y), max(corner_a.z, corner_b.z))

    def __contains__(self, point: Vec3) -> bool:
        # Check if the point is within the 3D bounds of the zone
        return self.corner_min.x <= point.x <= self.corner_max.x \
               and self.corner_min.y <= point.y <= self.corner_max.y \
               and self.corner_min.z <= point.z <= self.corner_max.z

import numpy as np
import scipy.spatial
from ... import Numputils as nput
from ...Data import AtomData, UnitsData

__all__ = [
    "SphereUnionSurface"
]

class SphereUnionSurface:

    default_samples = 50
    default_scaling = 1
    default_expansion = .01
    def __init__(self, centers, radii, scaling=None, expansion=None, samples=None):
        self.centers = np.asanyarray(centers)
        self.radii = np.asanyarray(radii)
        if samples is None:
            samples = self.default_samples
        self.samples = samples
        if scaling is None:
            scaling = self.default_scaling
        self.scaling = scaling
        if expansion is None:
            expansion = self.default_expansion
        self.expansion = expansion
        self._sample_points = None

    @classmethod
    def from_xyz(cls,
                 atoms, positions,
                 scaling=None, expansion=None, samples=None,
                 radius_property='IconRadius',
                 distance_units='BohrRadius'):
        radii = np.array([
            AtomData[a, radius_property] * UnitsData.convert("Angstroms", distance_units)
            for a in atoms
        ])

        return cls(positions, radii, samples=samples, scaling=scaling, expansion=expansion)

    @property
    def sampling_points(self):
        if self._sample_points is None:
            self._sample_points = self.generate_points()
        return self._sample_points
    @sampling_points.setter
    def sampling_points(self, pts):
        if pts is not None: pts = np.asanyarray(pts)
        self._sample_points = pts

    @classmethod
    def sphere_project(cls, pts, centers, radii):
        center_vecs = pts[:, np.newaxis, :] - centers[np.newaxis, :, :]
        center_dm = np.linalg.norm(center_vecs, axis=-1)
        np.fill_diagonal(center_dm, 1e6)
        nearest_centers = np.argmin(center_dm, axis=1)
        sel = (np.arange(len(pts)), nearest_centers)
        scaling = radii[nearest_centers] / center_dm[sel]
        pts = centers[nearest_centers, :] + center_vecs[sel] * scaling[:, np.newaxis]

        return pts

    @classmethod
    def sphere_boundary_pruning(
            cls,
            pts,
            centers,
            # radii,
            min_component=None,
            # max_iterations=15
    ):
        center_vecs = pts[:, np.newaxis, :] - centers[np.newaxis, :, :]
        center_dm = np.linalg.norm(center_vecs, axis=-1)
        np.fill_diagonal(center_dm, 1e6)
        nearest_centers = np.argmin(center_dm, axis=1)

        center_inds, subgroups = nput.group_by(pts, nearest_centers)[0]
        subgroups = list(subgroups)
        if min_component is None:
            primary_comps = []
            for group in subgroups:
                dm = nput.distance_matrix(group)
                np.fill_diagonal(dm, 1e6)
                min_vals = np.min(dm, axis=1)
                vals, bins = np.histogram(min_vals, bins=len(group)//5)
                i = np.argmax(vals)
                primary_comps.append(
                    (bins[i] + bins[i + 1]) / 2
                )
            min_component = np.min(primary_comps) #* .5
        for n,(c, group) in enumerate(zip(center_inds, subgroups)):
            dm = nput.distance_matrix(group)
            np.fill_diagonal(dm, 1e6)
            min_vals = np.min(dm, axis=1)
            print("!", np.sort(min_vals))
            for m,(k, group2) in enumerate(zip(center_inds[n+1:], subgroups[n+1:])):
                dists = np.linalg.norm(group2[:, np.newaxis, :] - group[np.newaxis, :, :], axis=-1)
                dist_cutoff = np.where(np.min(dists, axis=1) < min_component)
                if len(dist_cutoff) > 0 or len(dist_cutoff[0]) > 0:
                    subgroups[n+1+m] = np.delete(group2, dist_cutoff[0], axis=0)

        return np.concatenate(subgroups, axis=0)

    @classmethod
    def point_cloud_repulsion(
            cls,
            pts,
            centers,
            radii,
            min_displacement_cutoff=1e-3,
            stochastic_factor=.0001,
            force_constant=.001,
            power=-3,
            max_iterations=15
    ):
        rows, cols = np.triu_indices(len(pts), k=1)
        n = len(pts)
        for i in range(max_iterations):
            d_vecs = pts[rows, :] - pts[cols, :]
            norms = np.linalg.norm(d_vecs, axis=-1)
            forces = force_constant * np.power(norms, power)
            if np.all(forces < min_displacement_cutoff): break
            force_vecs = d_vecs * forces[:, np.newaxis]
            d_mat = np.zeros((n, n, 3))
            d_mat[rows, cols] = force_vecs
            d_mat[cols, rows] = force_vecs
            disps = np.sum(d_mat, axis=1)

            disps = disps + stochastic_factor * nput.vec_normalize(np.random.normal(size=disps.shape))

            center_vecs = pts[:, np.newaxis, :] - centers[np.newaxis, :, :]
            center_dm = np.linalg.norm(center_vecs, axis=-1)
            np.fill_diagonal(center_dm, 1e6)
            nearest_centers = np.argmin(center_dm, axis=1)
            sel = (np.arange(len(pts)), nearest_centers)
            proj_vecs = (center_vecs[sel] / center_dm[sel][:, np.newaxis])
            eye = nput.identity_tensors((len(pts),), 3)
            proj = eye - proj_vecs[:, :, np.newaxis] * proj_vecs[:, np.newaxis, :]
            pts = pts + (proj @ disps[:, :, np.newaxis]).reshape(disps.shape)

            pts = cls.sphere_project(pts, centers, radii)

        return pts

    @classmethod
    def adjust_point_cloud_density(self,
                                   pts,
                                   centers=None,
                                   radii=None,
                                   min_component=None,
                                   min_component_bins=30,
                                   min_component_scaling=.7,
                                   # max_component=None,
                                   same_point_cutoff=1e-6,
                                   max_iterations=15):
        if len(pts) == 1: return pts

        if centers is not None and radii is None or radii is not None and centers is None:
            raise ValueError("to constrain points, need both centers and radii")
        elif centers is not None:
            centers = np.asanyarray(centers)
            radii = np.asanyarray(radii)

        if max_iterations > 0:
            dm = nput.distance_matrix(pts)
            # rows, cols = np.triu_indices_from(dm, k=1)
            max_dist = np.max(dm) * 100
            np.fill_diagonal(dm, max_dist)
            min_pos = np.argmin(dm, axis=1)
            min_vals = dm[np.arange(len(dm)), min_pos]
            if min_component is None:
                vals, bins = np.histogram(min_vals, bins=min_component_bins)
                i = np.argmax(vals)
                min_component = min_component_scaling * (bins[i] + bins[i+1]) / 2

            for i in range(max_iterations):
                small_mask = min_vals < min_component
                bad_pos = np.where(small_mask)

                # if max_component is not None:
                #     big_mask = min_vals > max_component
                #     big_pos = np.where(big_mask)
                # else:
                #     big_mask = None
                #     big_pos = None

                small_done = len(bad_pos) == 0 or len(bad_pos[0]) == 0
                big_done = True
                # big_done = big_mask is None or (len(big_pos) == 0 or len(big_pos[0]) == 0 or len(pts) == 1)
                if (
                        len(pts) == 1
                        or (small_done and big_done)
                ):
                    break

                bad_vals = min_vals[bad_pos]
                dropped_points = np.where(bad_vals < same_point_cutoff)

                bad_rows = bad_pos[0]
                bad_cols = min_pos[bad_pos]
                _, r_pos = np.unique(bad_rows, return_index=True)
                _, c_pos = np.unique(bad_cols[r_pos], return_index=True)
                # only treat each point once per iteration by first dropping dupes
                # and then ensuring terms that appear in the rows don't appear in the cols
                bad_pos = bad_rows[r_pos[c_pos]]

                if len(dropped_points) > 0 and len(dropped_points[0]) > 0:
                    drop_rows = dropped_points[0]
                    drop_cols = min_pos[dropped_points]
                    drop_mask = drop_cols > drop_rows
                    # drop_rows = drop_rows[drop_mask]
                    drop_cols = drop_cols[drop_mask]
                    bad_pos = np.concatenate([drop_cols, bad_pos])

                bad_rows = bad_pos
                bad_cols = min_pos[bad_pos]

                merge_pos = np.unique(np.concatenate([bad_rows, bad_cols]))
                rem_pos = np.setdiff1d(np.arange(len(pts)), merge_pos)
                # dm = dm[np.ix_(rem_pos, rem_pos)]
                min_vals = min_vals[rem_pos,]
                inv_map = np.argsort(np.concatenate([rem_pos, merge_pos]))
                min_pos = inv_map[min_pos][rem_pos,]
                bad_mask = min_pos >= len(rem_pos)
                min_vals[bad_mask] = max_dist
                min_pos[bad_mask] = -1
                rem_pts = pts[rem_pos,]
                new_pts = (pts[bad_rows] + pts[bad_cols]) / 2 # average point positions

                if centers is not None and radii is not None:
                    d_vecs = new_pts[:, np.newaxis, :] - centers[np.newaxis, :, :]
                    center_dm = np.linalg.norm(d_vecs, axis=-1)
                    np.fill_diagonal(center_dm, max_dist)
                    nearest_centers = np.argmin(center_dm, axis=1)
                    sel = (np.arange(len(new_pts)), nearest_centers)
                    scaling = radii[nearest_centers] / center_dm[sel]
                    new_pts = centers[nearest_centers, :] + d_vecs[sel] * scaling[:, np.newaxis]
                # renormalize to distance to nearest center is unchanged


                if len(new_pts) > 1:
                    new_new_dists = nput.distance_matrix(new_pts)
                    np.fill_diagonal(new_new_dists, max_dist)
                    new_min_pos = np.argmin(new_new_dists, axis=1)
                    new_min_vals = new_new_dists[np.arange(len(new_new_dists)), new_min_pos]
                    dropped_points = np.where(new_min_vals < same_point_cutoff)
                    if len(dropped_points) > 0 and len(dropped_points[0]) > 0:
                        drop_rows = dropped_points[0]
                        drop_cols = new_min_pos[dropped_points]
                        drop_mask = drop_cols > drop_rows
                        # drop_rows = drop_rows[drop_mask]
                        drop_cols = drop_cols[drop_mask]
                        rem_new_pts = np.setdiff1d(np.arange(len(new_pts)), drop_cols)
                        new_pts = new_pts[rem_new_pts,]
                        new_min_vals = new_min_vals[rem_new_pts,]
                        new_min_pos = new_min_pos[rem_new_pts,]
                else:
                    new_min_vals = None
                    new_min_pos = None

                new_rem_dists = np.linalg.norm(rem_pts[:, np.newaxis, :] - new_pts[np.newaxis, :, :], axis=-1)
                new_rem_pos = np.argmin(new_rem_dists, axis=1)
                new_rem_mins = new_rem_dists[np.arange(len(new_rem_dists)), new_rem_pos]
                dropped_points = np.where(new_rem_mins < same_point_cutoff)
                if len(dropped_points) > 0 and len(dropped_points[0]) > 0:
                    drop_rows = dropped_points[0]
                    drop_cols = new_rem_pos[dropped_points]
                    drop_mask = drop_cols > drop_rows
                    # drop_rows = drop_rows[drop_mask]
                    drop_cols = drop_cols[drop_mask]
                    rem_new_pts = np.setdiff1d(np.arange(len(new_pts)), drop_cols)
                    new_pts = new_pts[rem_new_pts,]
                    new_min_vals = new_min_vals[rem_new_pts,]
                    new_rem_dists = np.linalg.norm(rem_pts[:, np.newaxis, :] - new_pts[np.newaxis, :, :], axis=-1)
                    new_rem_pos = np.argmin(new_rem_dists, axis=1)
                    new_rem_mins = new_rem_dists[np.arange(len(new_rem_dists)), new_rem_pos]

                min_mask = min_vals > new_rem_mins
                min_vals[min_mask] = new_rem_mins[min_mask]
                min_pos[min_mask] = new_rem_pos[min_mask]

                new_new_pos = np.argmin(new_rem_dists, axis=0)
                new_new_mins = new_rem_dists[new_new_pos, np.arange(new_rem_dists.shape[1])]
                if new_min_vals is None:
                    new_min_vals = new_new_mins
                    new_min_pos = new_new_pos
                else:
                    min_mask = new_min_vals > new_new_mins
                    new_min_vals[min_mask] = new_new_mins[min_mask]
                    new_min_pos[min_mask] = new_new_pos[min_mask]

                pts = np.concatenate([rem_pts, new_pts], axis=0)
                min_vals = np.concatenate([min_vals, new_min_vals])
                min_pos = np.concatenate([min_pos, new_min_pos])

        return pts

    def generate_points(self, scaling=None, expansion=None, samples=None):
        if samples is None: samples = self.samples
        if scaling is None: scaling = self.scaling
        if expansion is None: expansion = self.expansion
        base_points = self.sphere_points(
            self.centers,
            self.radii*scaling + expansion,
            samples
        ).reshape(-1, 3)
        dvs = np.linalg.norm(
            base_points[:, np.newaxis, :] - self.centers[np.newaxis, :, :],
            axis=-1
        )
        mask = np.all(dvs >= self.radii[np.newaxis], axis=1)

        return base_points[mask,]

    @classmethod
    def sphere_points(cls, centers, radii, samples, generator=None):
        centers = np.asanyarray(centers)
        radii = np.asanyarray(radii)

        base_shape = centers.shape[:-2]
        centers = centers.reshape((-1,) + centers.shape[-2:])
        radii = radii.reshape(-1, radii.shape[-1])

        if generator is None:
            generator = cls.fibonacci_sphere
        if nput.is_int(samples):
            base_points = generator(samples)[np.newaxis, np.newaxis]
        else:
            samples = np.asanyarray(samples)
            if samples.ndim == 1:
                base_points = np.array([
                    generator(n)
                    for n in samples
                ])
                if len(samples) == centers.shape[-2]:
                    base_points = base_points[np.newaxis, :, :, :]
                else:
                    base_points = base_points[:, np.newaxis, :, :]
            else:
                samples = samples.reshape(-1, centers.shape[-2])
                base_points = np.array([
                    [
                        generator(n)
                        for n in subsamp
                    ]
                    for subsamp in samples
                ])

        sphere_points = centers[:, :, np.newaxis, :] + base_points * radii[:, :, np.newaxis, np.newaxis]

        return sphere_points.reshape(base_shape + sphere_points.shape[-3:])

    @classmethod
    def fibonacci_sphere(cls, samples):
        phi = np.pi * (np.sqrt(5.) - 1.)  # golden angle in radians
        samps = np.arange(samples)
        y = 1 - (samps / float(samples - 1)) * 2  # y goes from 1 to -1
        radius = np.sqrt(1 - y * y)  # radius at y
        theta = phi * samps  # golden angle increment
        x = np.cos(theta) * radius
        z = np.sin(theta) * radius

        return np.array([x, y, z]).T

    def get_triangulation(self, *delaunay_kwargs, **delaunay_opts):
        return scipy.spatial.Delaunay(
            self.sampling_points,
            *delaunay_kwargs,
            *delaunay_opts
        )
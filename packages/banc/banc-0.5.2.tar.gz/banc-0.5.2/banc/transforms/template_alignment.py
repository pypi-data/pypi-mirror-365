#!/usr/bin/env python3
"""
Transform points and neurons between the BANC and the 2018 Janelia templates
"""

import os
from typing import Literal

import numpy as np

from .. import auth, template_spaces


vnc_template_voxel_size = 0.40  # µm per voxel
vnc_template_plane_of_symmetry_x_voxel = 329
vnc_template_plane_of_symmetry_x_microns = 329 * vnc_template_voxel_size
brain_template_voxel_size = 0.38  # µm per voxel
brain_template_plane_of_symmetry_x_voxel = 825
brain_template_plane_of_symmetry_x_microns = 825 * brain_template_voxel_size


def align_mesh(mesh,
               target_space='JRC2018_VNC_FEMALE',
               input_units='nanometers',
               output_units='microns',
               inplace=True):
    """
    Given a mesh of a neuron in FANC-space, warp its vertices' coordinates to
    be aligned to a 2018 Janelia VNC template space.

    Parameters
    ----------
    mesh : mesh or int
      The mesh or segment ID to align to the template space.
      If an int, must be a segment ID, in which case the mesh for that
      segment will be downloaded.
      If a mesh, can be any type of mesh object that has .faces and
      .vertices attributes.

    input_units : str (default 'nanometers')
      The units of the input mesh's vertices. Set to 'nanometers' or 'microns'.
      This argument is irrelevant and ignored if the input is a segment ID.

    output_units : str (default 'microns')
      The units you want the mesh to be returned in. Set to 'nanometers'
      or 'microns'.

    target_space : str (default 'JRC2018_VNC_FEMALE')
      The template space to warp the mesh into alignment with. This string will
      be passed to `template_spaces.to_navis_name()`, so check that function's
      docstring for the complete list of valid values for this argument.
      See `fanc.template_spaces` for more information about each template space.

    inplace : bool (default True)
      If true, replace the vertices of the given mesh object. If false, return
      a copy, leaving the given mesh object unchanged.
    """
    import navis
    import flybrains
    if isinstance(mesh, (int, np.integer)):
        inplace = False
        mm = auth.get_meshmanager()
        mesh = mm.mesh(seg_id=mesh)
    elif not inplace:
        mesh = mesh.copy()

    if not hasattr(mesh, 'vertices') or not hasattr(mesh, 'faces'):
        raise ValueError("The input mesh must have .vertices and .faces attributes"
                         f" but was type {type(mesh)}: {mesh}.")

    if input_units in ['um', 'µm', 'micron', 'microns']:
        mesh.vertices *= 1000
    elif input_units not in ['nm', 'nanometer', 'nanometers']:
        raise ValueError("Unrecognized value provided for input_units. Set it"
                         " to 'nanometers' or 'microns'.")

    brain_or_vnc = 'vnc' if 'vnc' in target_space.lower() else 'brain'
    if brain_or_vnc == 'vnc':
        # First remove any mesh faces in the neck connective or brain,
        # since those can't be warped to the VNC template
        # This cutoff is 131000voxels * 4nm/voxel, plus a small epsilon
        y_cutoff = 131000 * 4 + 1e-4
        # Find row numbers of vertices that are out of bounds
        out_of_bounds_vertices = (mesh.vertices[:, 1] < y_cutoff).nonzero()[0]
    elif brain_or_vnc == 'brain':
        # First remove any mesh faces in the neck connective or VNC, since those
        # can't be warped to the brain template
        # This cutoff is 80000voxels * 4nm/voxel, minus a small epsilon
        y_cutoff = 80000 * 4 - 1e-4
        # Find row numbers of vertices that are out of bounds
        out_of_bounds_vertices = (mesh.vertices[:, 1] > y_cutoff).nonzero()[0]

    in_bounds_faces = np.isin(mesh.faces,
                              out_of_bounds_vertices,
                              invert=True).all(axis=1)
    if not in_bounds_faces.any():
        raise ValueError("The mesh is entirely out of bounds of the target space.")
    mesh.update_faces(in_bounds_faces)
    mesh.remove_unreferenced_vertices()

    target = template_spaces.to_navis_name(target_space)
    print(f'Warping into alignment with {target}')

    mesh.vertices = warp_points_BANC_to_template(mesh.vertices,
                                                 brain_or_vnc=brain_or_vnc,
                                                 input_units=input_units,
                                                 output_units='microns')
    if brain_or_vnc == 'vnc' and target != 'JRCVNC2018F':
        mesh.vertices = navis.xform_brain(mesh.vertices,
                                          source='JRCVNC2018F',
                                          target=target)
    if brain_or_vnc == 'brain' and target != 'JRC2018F':
        mesh.vertices = navis.xform_brain(mesh.vertices,
                                          source='JRC2018F',
                                          target=target)
    if output_units in ['nm', 'nanometer', 'nanometers']:
        mesh.vertices *= 1000

    if not inplace:
        return mesh


def warp_points_BANC_to_template(points,
                                 brain_or_vnc: Literal['brain', 'vnc'],
                                 input_units='nanometers',
                                 output_units='microns',
                                 reflect=False):
    """
    Transform point coordinates from the BANC to the corresponding point
    location in the 2018 Janelia Female Brain or VNC Template

    Parameters
    ---------
    points (numpy.ndarray) :
        An Nx3 numpy array representing x,y,z point coordinates in the BANC

    brain_or_vnc (str) :
        Must be set to 'brain' or 'vnc'. Whether to warp points to the brain
        template (JRC2018_FEMALE) or the VNC template (JRC2018_VNC_FEMALE).

    input_units (str) :
        The units of the points you provided as an input. Set to 'nm',
        'nanometer', or 'nanometers' to indicate nanometers;
        'um', 'µm', 'micron', or 'microns' to indicate microns; or
        'pixels' or 'voxels' to indicate pixel indices within the
        full-resolution BANC image volume, which has a pixel size of
        (4, 4, 45) nm.
        Default is nanometers.

    output_units (str) :
        The units you want points returned to you in. Same set of
        options as for `input_units`, the only difference being that the
        pixel size of the output space is either 0.38 µm for the brain
        template or 0.40 µm for the VNC template.
        Default is microns.

    reflect (bool) :
        Whether to reflect the point coordinates across the midplane of
        the template before returning them. This reflection moves points'
        x coordinates from the left to the right side of the template or
        vice versa, but does not affect their y or z coordinates.
        Default is False.

    Returns
    -------
    An Nx3 numpy array representing x,y,z point coordinates in the
    brain or VNC template space, in units specified by `output_units`.
    """
    import transformix  # https://github.com/jasper-tms/pytransformix

    points = np.array(points, dtype=np.float64)
    if len(points.shape) == 1:
        result = warp_points_BANC_to_template(
            np.expand_dims(points, 0),
            brain_or_vnc,
            input_units=input_units,
            output_units=output_units,
            reflect=reflect
        )
        if result is None:
            return result
        else:
            return result[0]

    if brain_or_vnc == 'brain':
        transform_params = os.path.join(
            os.path.dirname(__file__),
            'transform_parameters',
            'brain',
            'BANC_to_template.txt',
        )
        template_plane_of_symmetry_x_microns = brain_template_plane_of_symmetry_x_microns
        template_voxel_size = brain_template_voxel_size
    elif brain_or_vnc == 'vnc':
        transform_params = os.path.join(
            os.path.dirname(__file__),
            'transform_parameters',
            'vnc',
            'BANC_to_template.txt',
        )
        template_plane_of_symmetry_x_microns = vnc_template_plane_of_symmetry_x_microns
        template_voxel_size = vnc_template_voxel_size
    else:
        raise ValueError("The second argument must be set to 'brain' or 'vnc'.")

    if input_units in ['nm', 'nanometer', 'nanometers']:
        input_units = 'nanometers'
    elif input_units in ['um', 'µm', 'micron', 'microns']:
        input_units = 'microns'
    elif input_units in ['pixel', 'pixels', 'voxel', 'voxels']:
        input_units = 'voxels'
    else:
        raise ValueError("Unrecognized value provided for input_units. Set it"
                         " to 'nanometers', 'microns', or 'pixels'.")
    if output_units in ['nm', 'nanometer', 'nanometers']:
        output_units = 'nanometers'
    elif output_units in ['um', 'µm', 'micron', 'microns']:
        output_units = 'microns'
    elif output_units in ['pixel', 'pixels', 'voxel', 'voxels']:
        output_units = 'voxels'
    else:
        raise ValueError("Unrecognized value provided for output_units. Set it"
                         " to 'nanometers', 'microns', or 'pixels'.")

    if input_units == 'nanometers' and (points < 1000).all():
        resp = input("input_units is set to 'nanometers' but you provided "
                     'points with small values. You likely forgot to set '
                     'input_units correctly. Continue [y] or exit [enter]? ')
        if resp.lower() != 'y':
            return None
    if input_units == 'microns' and (points > 1000).any():
        resp = input("input_units is set to 'microns' but you provided "
                     'points with large values. You likely forgot to set '
                     'input_units correctly. Continue [y] or exit [enter]? ')
        if resp.lower() != 'y':
            return None

    # Convert points to nm so that the math below works
    if input_units == 'microns':
        points *= 1000
    elif input_units == 'voxels':
        points *= (4, 4, 45)

    points /= 1000  # Convert nm to microns as required for this transform

    # Do the transform. This requires input in microns and gives output in microns
    points = transformix.transform_points(points, transform_params)

    if reflect:
        points[:, 0] = template_plane_of_symmetry_x_microns * 2 - points[:, 0]

    if output_units == 'nanometers':
        points *= 1000  # Convert microns to nm
    elif output_units == 'voxels':
        points /= template_voxel_size  # Convert microns to template voxels

    return points


def warp_points_BANC_to_brain_template(points,
                                       input_units='nanometers',
                                       output_units='microns',
                                       reflect=False):
    return warp_points_BANC_to_template(points,
                                        'brain',
                                        input_units=input_units,
                                        output_units=output_units,
                                        reflect=reflect)


def warp_points_BANC_to_vnc_template(points,
                                     input_units='nanometers',
                                     output_units='microns',
                                     reflect=False):
    return warp_points_BANC_to_template(points,
                                        'vnc',
                                        input_units=input_units,
                                        output_units=output_units,
                                        reflect=reflect)


def warp_points_template_to_BANC(points,
                                 brain_or_vnc: Literal['brain', 'vnc'],
                                 input_units='microns',
                                 output_units='nanometers',
                                 reflect=False):
    """
    Transform point coordinates from the 2018 Janelia Female Brain or
    VNC Template to the corresponding point location in the BANC.

    Parameters
    ---------
    points (numpy.ndarray) :
        An Nx3 numpy array representing x,y,z point coordinates in the
        2018 Janelia Female Brain or VNC Template. The following
        arguments `brain_or_vnc` and `input_units` specifies what space
        these points are in and what units they are in.

    brain_or_vnc (str) :
        Must be set to 'brain' or 'vnc'. Whether to warp points to the brain
        template (JRC2018_FEMALE) or the VNC template (JRC2018_VNC_FEMALE).

    input_units (str) :
        The units of the points you provided as an input. Set to 'nm',
        'nanometer', or 'nanometers' to indicate nanometers; 'um', 'µm',
        'micron', or 'microns' to indicate microns; or 'pixels' or
        'voxels' to indicate pixel indices within the template
        image volume, which has a pixel size of 0.38 µm for the brain
        template or 0.40 µm for the VNC template.
        Default is microns.

    output_units (str) :
        The units you want points returned to you in. Same set of
        options as for `input_units`, the only difference being that the
        pixel size of the output space, the BANC, is (4, 4, 45) nm.
        Default is nanometers.

    reflect (bool) :
        Whether to reflect the point coordinates across the midplane of
        the template before returning them. This reflection moves points'
        x coordinates from the left to the right side of the template or
        vice versa, but does not affect their y or z coordinates.
        Default is False.

    Returns
    -------
    An Nx3 numpy array representing x,y,z point coordinates in the BANC,
    in units specified by `output_units`.
    """
    import transformix  # https://github.com/jasper-tms/pytransformix

    points = np.array(points, dtype=np.float64)
    if len(points.shape) == 1:
        result = warp_points_template_to_BANC(
            np.expand_dims(points, 0),
            brain_or_vnc,
            input_units=input_units,
            output_units=output_units,
            reflect=reflect
        )
        if result is None:
            return result
        else:
            return result[0]

    if brain_or_vnc == 'brain':
        transform_params = os.path.join(
            os.path.dirname(__file__),
            'transform_parameters',
            'brain',
            'template_to_BANC.txt',
        )
        template_plane_of_symmetry_x_microns = brain_template_plane_of_symmetry_x_microns
        template_voxel_size = brain_template_voxel_size
    elif brain_or_vnc == 'vnc':
        transform_params = os.path.join(
            os.path.dirname(__file__),
            'transform_parameters',
            'vnc',
            'template_to_BANC.txt',
        )
        template_plane_of_symmetry_x_microns = vnc_template_plane_of_symmetry_x_microns
        template_voxel_size = vnc_template_voxel_size
    else:
        raise ValueError("The second argument must be set to 'brain' or 'vnc'.")

    if input_units in ['nm', 'nanometer', 'nanometers']:
        input_units = 'nanometers'
    elif input_units in ['um', 'µm', 'micron', 'microns']:
        input_units = 'microns'
    elif input_units in ['pixel', 'pixels', 'voxel', 'voxels']:
        input_units = 'voxels'
    else:
        raise ValueError("Unrecognized value provided for input_units. Set it"
                         " to 'nanometers', 'microns', or 'pixels'.")
    if output_units in ['nm', 'nanometer', 'nanometers']:
        output_units = 'nanometers'
    elif output_units in ['um', 'µm', 'micron', 'microns']:
        output_units = 'microns'
    elif output_units in ['pixel', 'pixels', 'voxel', 'voxels']:
        output_units = 'voxels'
    else:
        raise ValueError("Unrecognized value provided for output_units. Set it"
                         " to 'nanometers', 'microns', or 'pixels'.")

    if input_units == 'nanometers' and (points < 1000).all():
        resp = input("input_units is set to 'nanometers' but you provided "
                     'points with small values. You likely forgot to set '
                     'input_units correctly. Continue [y] or exit [enter]? ')
        if resp.lower() != 'y':
            return None
    if input_units == 'microns' and (points > 1000).any():
        resp = input("input_units is set to 'microns' but you provided "
                     'points with large values. You likely forgot to set '
                     'input_units correctly. Continue [y] or exit [enter]? ')
        if resp.lower() != 'y':
            return None

    # Convert to microns as required for this transform
    if input_units == 'nanometers':
        points /= 1000  # Convert nm to microns
    elif input_units == 'voxels':
        points = points * template_voxel_size  # Convert voxels to microns

    if reflect:
        points[:, 0] = template_plane_of_symmetry_x_microns * 2 - points[:, 0]

    # Do the transform. This requires input in microns and gives output in microns
    points = transformix.transform_points(points, transform_params)

    points *= 1000  # Convert microns to nm

    if output_units == 'microns':
        points /= 1000  # Convert nm to microns
    elif output_units == 'voxels':
        points /= (4, 4, 45)  # Convert nm to BANC voxels
    return points


def warp_points_brain_template_to_BANC(points,
                                       input_units='microns',
                                       output_units='nanometers',
                                       reflect=False):
    return warp_points_template_to_BANC(points,
                                        'brain',
                                        input_units=input_units,
                                        output_units=output_units,
                                        reflect=reflect)


def warp_points_vnc_template_to_BANC(points,
                                     input_units='microns',
                                     output_units='nanometers',
                                     reflect=False):
    return warp_points_template_to_BANC(points,
                                        'vnc',
                                        input_units=input_units,
                                        output_units=output_units,
                                        reflect=reflect)

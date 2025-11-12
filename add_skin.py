#!/usr/bin/env python3
"""
Add skin label to segmentation file.

This script identifies the most external (peripheral) voxels of the body
and labels them as skin (label 73).
"""

import nibabel as nib
import numpy as np
from scipy import ndimage


def add_skin_label(input_file, output_file, skin_label=73, thickness=1):
    """
    Add skin label to the most peripheral voxels in the axial plane.

    This processes each axial slice independently to find the external boundary
    in the x-y plane only, without marking top/bottom slices entirely as skin.

    Args:
        input_file: Path to input NIfTI file
        output_file: Path to output NIfTI file
        skin_label: Label value for skin (default: 73)
        thickness: Thickness of skin layer in voxels (default: 1)
    """
    print(f"Loading {input_file}...")
    nii = nib.load(input_file)
    data = nii.get_fdata().astype(np.int16)

    print("Original unique labels:", np.unique(data))
    print("Creating binary mask...")
    body_mask = (data > 0).astype(np.uint8)

    print("Finding external surface in axial plane...")
    struct_2d = ndimage.generate_binary_structure(2, 1)  # 4-connectivity in 2D
    skin_mask = np.zeros_like(body_mask, dtype=bool)

    num_slices = body_mask.shape[2]
    for z in range(num_slices):
        slice_mask = body_mask[:, :, z]

        if np.any(slice_mask):
            eroded_slice = ndimage.binary_erosion(slice_mask, structure=struct_2d, iterations=thickness)

            skin_mask[:, :, z] = slice_mask & ~eroded_slice

    num_skin_voxels = np.sum(skin_mask)
    print(f"Found {num_skin_voxels} skin voxels (external boundary in axial plane)")

    output_data = data.copy()

    output_data[skin_mask] = skin_label

    print("New unique labels:", np.unique(output_data))

    print(f"Saving to {output_file}...")
    output_nii = nib.Nifti1Image(output_data.astype(np.int16), nii.affine, nii.header)
    nib.save(output_nii, output_file)

    print("Done!")
    print(f"Added {num_skin_voxels} voxels labeled as skin (label {skin_label})")


if __name__ == "__main__":
    input_file = "combined_manual_filled_nearest_neighbour_cut220_collapsed.nii.gz"
    output_file = "combined_manual_filled_nearest_neighbour_cut220_collapsed_skin.nii.gz"

    from pathlib import Path
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found!")
        exit(1)

    add_skin_label(input_file, output_file, thickness=2)

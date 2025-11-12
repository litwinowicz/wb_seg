#!/usr/bin/env python3
"""
Fill holes in segmentation using fat fraction map.

Holes with fat fraction > threshold are filled with subcutaneous fat label (65).
"""

import nibabel as nib
import numpy as np
from scipy import ndimage
import argparse


def fill_holes_with_fat_fraction(combined_file, ff_file, output_file, ff_threshold=0.7, fat_label=65):
    """
    Fill holes in segmentation based on fat fraction.

    Args:
        combined_file: Combined segmentation file
        ff_file: Fat fraction map
        output_file: Output filled segmentation
        ff_threshold: Fat fraction threshold for filling (default: 0.7)
        fat_label: Label to use for fat-filled holes (default: 65)
    """
    # Load the combined segmentation
    print(f"Loading {combined_file}...")
    combined_nii = nib.load(combined_file)
    combined_data = np.asarray(combined_nii.dataobj, dtype=np.int32)

    # Load the fat fraction image
    print(f"Loading {ff_file}...")
    ff_nii = nib.load(ff_file)
    ff_data = np.asarray(ff_nii.dataobj, dtype=np.float32)

    print(f"Combined segmentation shape: {combined_data.shape}")
    print(f"FF shape: {ff_data.shape}")

    # Create output (start with original combined data)
    output_data = combined_data.copy()

    # Detect actual holes (same logic as detect_holes.py)
    print("Detecting holes slice by slice...")
    binary_mask = (combined_data > 0).astype(np.uint8)
    holes_mask = np.zeros_like(combined_data, dtype=np.uint8)

    # Process slice by slice (assuming axial slices - last dimension)
    for z in range(combined_data.shape[2]):
        slice_binary = binary_mask[:, :, z]

        # Find background regions (zeros)
        background = (slice_binary == 0).astype(np.uint8)

        # Label connected components of background
        labeled_bg, num_features = ndimage.label(background)

        # Check each background component
        for label_id in range(1, num_features + 1):
            component = (labeled_bg == label_id)

            # Check if this component touches the border
            touches_border = (
                np.any(component[0, :]) or      # top edge
                np.any(component[-1, :]) or     # bottom edge
                np.any(component[:, 0]) or      # left edge
                np.any(component[:, -1])        # right edge
            )

            # If it doesn't touch the border, it's a hole
            if not touches_border:
                holes_mask[:, :, z][component] = 1

    total_holes = np.sum(holes_mask)
    print(f"Total hole voxels detected: {total_holes}")

    # Now fill holes with high fat fraction (FF > threshold)
    high_fat_mask = ff_data > ff_threshold
    fill_mask = (holes_mask == 1) & high_fat_mask
    output_data[fill_mask] = fat_label

    num_filled = np.sum(fill_mask)
    print(f"Filled {num_filled} voxels with label {fat_label} (holes with FF > {ff_threshold})")

    # Statistics
    original_nonzero = np.sum(combined_data > 0)
    new_nonzero = np.sum(output_data > 0)
    print(f"Original non-zero voxels: {original_nonzero}")
    print(f"New non-zero voxels: {new_nonzero}")
    print(f"Unique values in output: {np.unique(output_data)}")

    # Create new NIfTI image with the same affine and header
    output_nii = nib.Nifti1Image(output_data, combined_nii.affine, combined_nii.header)

    # Save the result
    print(f"Saving to {output_file}...")
    nib.save(output_nii, output_file)

    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill holes using fat fraction map")
    parser.add_argument("--input", required=True, help="Input combined segmentation file (.nii.gz)")
    parser.add_argument("--ff", required=True, help="Fat fraction map (.nii.gz)")
    parser.add_argument("--output", required=True, help="Output filled segmentation (.nii.gz)")
    parser.add_argument("--ff-threshold", type=float, default=0.7, help="Fat fraction threshold (default: 0.7)")
    parser.add_argument("--fat-label", type=int, default=65, help="Label for fat (default: 65)")

    args = parser.parse_args()

    fill_holes_with_fat_fraction(args.input, args.ff, args.output, args.ff_threshold, args.fat_label)

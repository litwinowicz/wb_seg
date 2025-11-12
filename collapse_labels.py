#!/usr/bin/env python3
"""
Collapse segmentation labels into broader categories.

This script takes a segmentation NIfTI file and merges specific labels
according to anatomical groupings (e.g., combining left and right organs,
grouping bone structures, etc.).
"""

import nibabel as nib
import numpy as np
from pathlib import Path


def collapse_labels(input_file, output_file):
    """
    Collapse segmentation labels according to specified mapping.

    Args:
        input_file: Path to input NIfTI file
        output_file: Path to output NIfTI file
    """
    # Define label collapsing rules: source_labels -> target_label
    label_mapping = {
        # Kidneys
        2: 2, 3: 2,

        # Adrenal glands
        8: 9, 9: 9,

        # Lungs
        10: 10, 11: 10, 12: 10, 13: 10, 14: 10,

        # Vessels
        25: 26, 26: 26, 27: 26, 28: 26, 29: 26, 30: 26, 31: 26, 32: 26, 33: 26,
        35: 26, 36: 26, 37: 26, 38: 26, 39: 26, 40: 26, 41: 26,
        104: 26, 110: 26, 111: 26,

        # Bones
        23: 42, 42: 42, 43: 42, 44: 42, 45: 42, 46: 42, 47: 42, 48: 42, 49: 42,
        50: 42, 51: 42, 63: 42, 69: 42, 70: 42, 72: 42,
        101: 42, 102: 42, 116: 42,

        # Muscle
        53: 66, 54: 66, 55: 66, 56: 66, 57: 66, 58: 66, 59: 66, 60: 66,
        61: 66, 62: 66, 66: 66, 103: 66, 105: 66,

        # Visceral fat
        67: 67, 200: 67,

        # Subcutaneous fat
        65: 65, 106: 65, 114: 65,

        # Prostate
        22: 22, 107: 22,

        # Intestine
        18: 18, 108: 18,

        # Penis
        109: 109,

        # Pancreas
        7: 7, 112: 7,

        # Trachea
        16: 16, 113: 16,

        # Stomach
        6: 6, 115: 6,
    }

    print(f"Loading {input_file}...")
    nii = nib.load(input_file)
    data = nii.get_fdata().astype(np.int16)

    print("Original unique labels:", np.unique(data))
    collapsed_data = data.copy()
    print("Collapsing labels...")
    for source_label, target_label in label_mapping.items():
        if source_label != target_label:
            mask = data == source_label
            collapsed_data[mask] = target_label
            count = np.sum(mask)
            if count > 0:
                print(f"  {source_label} -> {target_label}: {count} voxels")

    print("Collapsed unique labels:", np.unique(collapsed_data))
    print(f"Saving to {output_file}...")

    output_nii = nib.Nifti1Image(collapsed_data.astype(np.int16), nii.affine, nii.header)
    nib.save(output_nii, output_file)

    print("Done!")


if __name__ == "__main__":
    input_file = "combined_manual_filled_nearest_neighbour_cut220.nii.gz"
    output_file = "combined_manual_filled_nearest_neighbour_cut220_collapsed.nii.gz"

    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found!")
        exit(1)

    collapse_labels(input_file, output_file)

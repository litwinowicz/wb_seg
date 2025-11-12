#!/usr/bin/env python3
"""
Combine VIBESegmentator and TotalSegmentator outputs.

Replaces voxels where TotalSegmentator tissue_types == 2 (VAT) with label 200,
which later gets collapsed to label 67 (VAT).
"""

import nibabel as nib
import numpy as np
import argparse


def combine_segmentations(vibe_file, ts_types_file, output_file, vat_label=200):
    """
    Combine VIBESegmentator and TotalSegmentator tissue types.

    Args:
        vibe_file: VIBESegmentator water segmentation file
        ts_types_file: TotalSegmentator tissue_types output file
        output_file: Combined output file
        vat_label: Label to use for VAT voxels (default: 200)
    """
    print(f"Loading {ts_types_file}...")
    types_nii = nib.load(ts_types_file)
    types_data = np.asarray(types_nii.dataobj, dtype=np.int32)

    print(f"Loading {vibe_file}...")
    vibe_nii = nib.load(vibe_file)
    vibe_data = np.asarray(vibe_nii.dataobj, dtype=np.int32)

    print(f"TotalSegmentator shape: {types_data.shape}")
    print(f"VIBESegmentator shape: {vibe_data.shape}")
    combined_data = np.where(types_data == 2, vat_label, vibe_data)

    print(f"Combined data shape: {combined_data.shape}")
    print(f"Unique values in combined: {np.unique(combined_data)}")
    print(f"Voxels labeled as VAT ({vat_label}): {np.sum(combined_data == vat_label)}")
    combined_nii = nib.Nifti1Image(combined_data.astype(np.int32),
                                    vibe_nii.affine,
                                    vibe_nii.header)
    print(f"Saving to {output_file}...")
    nib.save(combined_nii, output_file)

    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine VIBESegmentator and TotalSegmentator outputs")
    parser.add_argument("--vibe", required=True, help="VIBESegmentator water segmentation file (.nii.gz)")
    parser.add_argument("--ts-types", required=True, help="TotalSegmentator tissue_types file (.nii.gz)")
    parser.add_argument("--output", required=True, help="Output combined file (.nii.gz)")
    parser.add_argument("--vat-label", type=int, default=200, help="Label for VAT voxels (default: 200)")

    args = parser.parse_args()

    combine_segmentations(args.vibe, args.ts_types, args.output, args.vat_label)

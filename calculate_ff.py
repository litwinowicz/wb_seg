#!/usr/bin/env python3
"""
Calculate fat fraction from fat and water DIXON images.
FF = fat / (fat + water)
"""

import nibabel as nib
import numpy as np
import argparse


def calculate_fat_fraction(fat_file, water_file, output_file):
    """
    Calculate fat fraction: FF = fat / (fat + water)

    Args:
        fat_file: Path to fat DIXON image
        water_file: Path to water DIXON image
        output_file: Path to save fat fraction map
    """
    print(f"Loading {fat_file}...")
    fat_nii = nib.load(fat_file)
    fat_data = np.asarray(fat_nii.dataobj, dtype=np.float32)

    print(f"Loading {water_file}...")
    water_nii = nib.load(water_file)
    water_data = np.asarray(water_nii.dataobj, dtype=np.float32)

    print(f"Fat shape: {fat_data.shape}")
    print(f"Water shape: {water_data.shape}")
    total_signal = fat_data + water_data
    ff_data = np.zeros_like(fat_data, dtype=np.float32)
    mask = total_signal > 0
    ff_data[mask] = fat_data[mask] / total_signal[mask]

    print(f"Fat fraction range: [{np.min(ff_data):.4f}, {np.max(ff_data):.4f}]")
    print(f"Mean fat fraction (non-zero voxels): {np.mean(ff_data[mask]):.4f}")
    ff_nii = nib.Nifti1Image(ff_data, fat_nii.affine, fat_nii.header)
    print(f"Saving to {output_file}...")
    nib.save(ff_nii, output_file)

    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate fat fraction from DIXON images")
    parser.add_argument("--fat", required=True, help="Input fat DIXON image (.nii.gz)")
    parser.add_argument("--water", required=True, help="Input water DIXON image (.nii.gz)")
    parser.add_argument("--output", required=True, help="Output fat fraction map (.nii.gz)")

    args = parser.parse_args()

    calculate_fat_fraction(args.fat, args.water, args.output)

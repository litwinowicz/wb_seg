import nibabel as nib
import numpy as np
from scipy import ndimage
import argparse


def detect_holes(input_file, output_file):
    print(f"Loading {input_file}...")
    seg_nii = nib.load(input_file)
    seg_data = np.asarray(seg_nii.dataobj, dtype=np.int32)

    print(f"Segmentation shape: {seg_data.shape}")

    binary_mask = (seg_data > 0).astype(np.uint8)

    holes_mask = np.zeros_like(seg_data, dtype=np.uint8)

    print("Detecting holes slice by slice...")
    for z in range(seg_data.shape[2]):
        slice_binary = binary_mask[:, :, z]

        background = (slice_binary == 0).astype(np.uint8)

        labeled_bg, num_features = ndimage.label(background)

        for label_id in range(1, num_features + 1):
            component = (labeled_bg == label_id)

            touches_border = (
                np.any(component[0, :]) or
                np.any(component[-1, :]) or
                np.any(component[:, 0]) or
                np.any(component[:, -1])
            )

            if not touches_border:
                holes_mask[:, :, z][component] = 1

    total_holes = np.sum(holes_mask)
    num_slices_with_holes = np.sum(np.any(holes_mask.reshape(seg_data.shape[0], seg_data.shape[1], -1), axis=(0, 1)))

    print(f"Total hole voxels detected: {total_holes}")
    print(f"Number of slices with holes: {num_slices_with_holes}")

    output_nii = nib.Nifti1Image(holes_mask.astype(np.int32),
                                  seg_nii.affine,
                                  seg_nii.header)

    print(f"Saving to {output_file}...")
    nib.save(output_nii, output_file)

    print("Done! Holes are marked with value 1.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect holes in a segmentation file")
    parser.add_argument("--input", required=True, help="Input segmentation file (.nii.gz)")
    parser.add_argument("--output", required=True, help="Output holes visualization file (.nii.gz)")

    args = parser.parse_args()

    detect_holes(args.input, args.output)

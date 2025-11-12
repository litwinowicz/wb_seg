"""
To run:
    snakemake -p results/{sample id}_filled_ff.nii.gz --cores 1 --use-conda
e.g.:
    snakemake -p results/AA21-02-2019_filled_ff.nii.gz --cores 1 --use-conda
"""

configfile: "config.yaml"

SAMPLES = config.get("samples", ["AA21-02-2019", "AA05-07-2017", "AA03-02-2014"])
VIBESEG_ENV = config["conda_envs"]["vibesegmentator"]
TOTALSEG_ENV = config["conda_envs"]["totalsegmentator"]
INPUT_DIR = config["directories"]["input"]
RESULTS_DIR = config["directories"]["results"]
FF_THRESHOLD = config["parameters"]["ff_threshold"]
FAT_LABEL = config["parameters"]["fat_label"]
VAT_LABEL = config["parameters"]["vat_label"]
DEVICE = config["parameters"]["device"]

rule all:
    input:
        expand(f"{RESULTS_DIR}/{{sample}}_filled_ff.nii.gz", sample=SAMPLES),
        expand(f"{RESULTS_DIR}/{{sample}}_holes_remaining.nii.gz", sample=SAMPLES)


rule run_vibesegmentator:
    input:
        inphase = f"{INPUT_DIR}/{{sample}}/ip.nii.gz",
        outphase = f"{INPUT_DIR}/{{sample}}/oop.nii.gz",
        water = f"{INPUT_DIR}/{{sample}}/water.nii.gz"
    output:
        water_seg = f"{RESULTS_DIR}/{{sample}}_part-water_.nii.gz"
    params:
        device = DEVICE
    conda:
        VIBESEG_ENV
    shell:
        """
        python run_VIBEVibeSegmentator_multi.py \
            --img_inphase {input.inphase} \
            --img_outphase {input.outphase} \
            --img_water {input.water} \
            --out_path {RESULTS_DIR}/{wildcards.sample}.nii.gz \
            --ddevice {params.device}
        """


rule run_totalsegmentator:
    input:
        fat = f"{INPUT_DIR}/{{sample}}/fat.nii.gz"
    output:
        ts_types = f"{RESULTS_DIR}/{{sample}}_ts_types/tissue_types.nii.gz"
    params:
        output_dir = f"{RESULTS_DIR}/{{sample}}_ts_types"
    conda:
        TOTALSEG_ENV
    shell:
        """
        TotalSegmentator -i {input.fat} \
            --task tissue_types_mr \
            --ml \
            -o {output.ts_types}
        """

rule calculate_fat_fraction:
    input:
        fat = f"{INPUT_DIR}/{{sample}}/fat.nii.gz",
        water = f"{INPUT_DIR}/{{sample}}/water.nii.gz"
    output:
        ff = f"{RESULTS_DIR}/{{sample}}_ff.nii.gz"
    conda:
        TOTALSEG_ENV
    shell:
        """
        python calculate_ff.py \
            --fat {input.fat} \
            --water {input.water} \
            --output {output.ff}
        """

rule combine_vibe_ts:
    input:
        vibe = f"{RESULTS_DIR}/{{sample}}_part-water_.nii.gz",
        ts_types = f"{RESULTS_DIR}/{{sample}}_ts_types/tissue_types.nii.gz"
    output:
        combined = f"{RESULTS_DIR}/{{sample}}_combined.nii.gz"
    params:
        vat_label = VAT_LABEL
    conda:
        TOTALSEG_ENV
    shell:
        """
        python combine_vibe_ts.py \
            --vibe {input.vibe} \
            --ts-types {input.ts_types} \
            --output {output.combined} \
            --vat-label {params.vat_label}
        """

rule detect_holes_initial:
    input:
        segmentation = f"{RESULTS_DIR}/{{sample}}_combined.nii.gz"
    output:
        holes = f"{RESULTS_DIR}/{{sample}}_holes_initial.nii.gz"
    shell:
        """
        python detect_holes_cli.py \
            --input {input.segmentation} \
            --output {output.holes}
        """

rule fill_holes_with_ff:
    input:
        combined = f"{RESULTS_DIR}/{{sample}}_combined.nii.gz",
        ff = f"{RESULTS_DIR}/{{sample}}_ff.nii.gz"
    output:
        filled = f"{RESULTS_DIR}/{{sample}}_filled_ff.nii.gz"
    params:
        ff_threshold = FF_THRESHOLD,
        fat_label = FAT_LABEL
    conda:
        TOTALSEG_ENV
    shell:
        """
        python fill_holes_ff.py \
            --input {input.combined} \
            --ff {input.ff} \
            --output {output.filled} \
            --ff-threshold {params.ff_threshold} \
            --fat-label {params.fat_label}
        """

rule detect_holes_remaining:
    input:
        segmentation = f"{RESULTS_DIR}/{{sample}}_filled_ff.nii.gz"
    output:
        holes = f"{RESULTS_DIR}/{{sample}}_holes_remaining.nii.gz"
    shell:
        """
        python detect_holes_cli.py \
            --input {input.segmentation} \
            --output {output.holes}
        """
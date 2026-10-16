# Josell 2002 experimental data extraction

The usable pinned-contact subset is Figure 5 on journal page 230, PDF page 4. This extraction contains all six experimental height symbols and all six experimental offset symbols. Small filled circles on the dashed line are solver output and are excluded.

The primary source is [Josell et al., DOI 10.1115/1.1463732](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827). The source PDF SHA256 is `4917aa35b4b804292826f8ce92b1f7c51eaed83e6f0777aeefb26195e7204990`. Full PDF pages 2 through 5 were read and rendered. The experimental apparatus, joint cross sections, plots, and fitting table were inspected as images.

## Extracted observations

All entries are approximate. The bound from reading the scanned chart is ±0.4 µN horizontally and ±0.3 µm vertically. This bound does not include experimental uncertainty. The values below round the independently transformed marker coordinates to 0.1 units for reproducibility, not measurement precision.

| Shear, µN | Height, µm | Height plotted bar, µm | Offset, µm | Offset plotted bar, µm | Pairing |
| --- | --- | --- | --- | --- | --- |
| 15.8 | 35.1 | 34.1 to 36.2 | 1.2 | lower clipped to 7.1 | Unique shear group |
| 48.0 | 35.1 | 34.1 to 36.2 | 7.1 | 2.1 to 12.2 | Unique shear group |
| 80.1 | 34.7 | 33.7 to 35.7 | 10.2 | 4.2 to 16.3 | Unique shear group |
| 112.0 | 37.2 or 34.2 | 35.2 to 39.2 or 33.2 to 35.2 | 15.1 or 9.3 | 5.2 to 25.2 or 6.2 to 12.3 | Two samples, pairing unknown |
| 144.3 | 35.1 | 34.1 to 36.1 | 31.0 | 26.1 to 36.1 | Unique shear group |

At approximately 112 µN, identical symbols do not identify which height belongs to which offset. Both possible pairings remain in the JSON. There are four unambiguous height/offset pairs and two ambiguous pairs, not six known pairs. The large final offset is retained. The first offset's lower errorbar is clipped by the chart boundary, so a symmetric lower bound is not invented. The paper does not state a confidence level for the Figure 5 bars.

## Inputs and mapping

The material is Sn63-Pb37 eutectic solder with Actiec 2 flux. The stage temperature is 210 ±10 °C. Figure 5 uses nominal solder volume 0.0086 mm³, circular copper pads of diameter 0.64 mm, and pad thickness 5 µm. A 30 nm titanium layer sits below the copper. The nominal 10 mil ball diameter is approximately 255 µm. For the three larger ball sizes, measured mean diameters were within 5 µm of nominal and individual diameter RMS deviations were at most 5 µm. Individual ball volumes and a distribution for the Figure 5 specimens are unavailable.

Each specimen has eight joints. Three sectioned joints supply the reported averages. Each offset averages both pad-edge displacements from those three joints. Height is the distance between upper and lower Si/Cu interfaces. The paper used post-solidification geometry as a proxy for molten geometry. It estimates 4.5% volume shrinkage and 1.5% linear shrinkage on solidification.

The published flat-plane approximation includes both copper-pad volumes. Thus its effective enclosed volume is `0.0086 + 2*pi*0.32**2*0.005 = 0.011816991 mm³`. This is the paper's approximation, not the physical solder volume. Keeping the solder-only volume while using its interface-to-interface height would mix conventions.

The text and Figure 5 caption explicitly place the entire contact line on the pad perimeter. Figure 4 spreads onto the substrate at about 65 µN. Figure 6 spreads throughout. Figure 7 spreads above about 20 µN. Those spreading cases do not validate a pinned-contact model.

## Limits on independent validation

The normal force 1.95 ±0.03 mN appears only in the Figure 3 description for the smallest-ball geometry. The paper does not provide Figure 5's per-specimen total mass or normal load. Normal force is `m*g*cos(tilt)/8`; shear is `m*g*sin(tilt)/8`. The 1.29 g tantalum weight alone does not give total mass because the upper silicon piece also contributes.

The [NIST implementation page](https://www.ctcms.nist.gov/solder/underfill/index.html) explicitly says the experiments used varying weights. Its [original code archive](https://www.ctcms.nist.gov/solder/underfill/underfill.zip) has SHA256 `fa1ceb86bd9f37214194370b809ee92e73614ed3c1c7b1e43a80460d759bfcc5`. Its default is the 0.029 mm³ geometry, mass 1.57 g, pad thickness 4 µm, and gamma 0.45 N/m. It is an example, not Figure 5 input provenance.

The publication's gamma 0.4 N/m and silicon angle 150° were fitted jointly to every experimental point. A comparison using gamma 0.4 is calibration-dependent. Independently measured silicon contact angle is 149 ±3° with stated 2-sigma uncertainty. The measured copper angle is 2 to 5°. Pinned-contact results are independent of silicon angle until spreading occurs. Surface tension units printed as N/m² in parts of the paper are dimensionally inconsistent; the code uses kg/s², equivalent to N/m.

## Extraction recipe

The script `.research/physical/nist-extraction/extract.py` extracts the original embedded `Im5.tiff` raster at 989 by 698 pixels, without resampling. Pixel coordinates start at the upper left. An affine calibration uses the zero corner at `(113,594)`, the 150 µN corner at `(958,589)`, and the 60 µm corner at `(109,10)`. This corrects the small chart skew. Marker centers and bar endpoints were read manually from the original raster and inspected enlarged. The script retains those pixel coordinates in `nist-extraction.csv` and `nist-extraction.json`.

`python3 .research/physical/nist-extraction/extract.py` regenerates both data files. It verifies the source hash and image dimensions before writing. Explain the Number determined the retained raster bounds and parameter provenance. Prove It Works required direct inspection of the symbols and the table, including the duplicate and outlier.

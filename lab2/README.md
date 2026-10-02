# Lab 2: Padframe for the R-2R DAC

**ENCE 3501 VLSI | University of Denver | Fall Quarter 2026 | Charlie Shields**

Die that connects the 5-bit R-2R DAC from Lab 1 to the outside world through a square padframe. Designed in Electric VLSI (`mocmos`, MOSIS).

**Jump to:** [Schematic](#schematic) | [Layout](#layout) | [Notes](#notes) | [Files](#files)

---

## Schematic

### Pad cell

`pad{sch}`: TODO, what is in the pad and why.

- TODO

![Pad schematic](images/pad_sch.png)

*Electric `pad{sch}`*

### DAC

`dac{sch}` is the 5-bit R-2R ladder from Lab 1. See the [Lab 1 README](../lab1/README.md) for the design and simulation.

- Pins: `b0` to `b4`, `vout`, `gnd` (TODO confirm)

![DAC schematic](images/dac_sch.png)

*Electric `dac{sch}`*

### Padframe with the DAC

`padframe{sch}`: TODO

Pad count:

1. DAC pinouts: TODO (count them)
2. Square frame means the same number of pads on every side
3. Minimum pads = TODO, so TODO per side
4. Spare pads: TODO, what they connect to

| Side | Pad | DAC pin |
|---|---|---|
| Top | 1 | TODO |
| Top | 2 | TODO |
| Right | 3 | TODO |
| Right | 4 | TODO |
| Bottom | 5 | TODO |
| Bottom | 6 | TODO |
| Left | 7 | TODO |
| Left | 8 | TODO |

![Padframe schematic](images/padframe_sch.png)

*Electric `padframe{sch}`*

---

## Layout

### Pad cell

`pad{lay}`: TODO, size, metal layers, overglass opening.

![Pad layout](images/pad_layout.png)

*Electric `pad{lay}`*

### Padframe with the DAC inside

`padframe{lay}`: TODO

- Pad placement: TODO
- DAC placement: TODO (centered?)
- Routing: TODO (which metal, wire widths)
- DRC: TODO (clean?)
- NCC / LVS: TODO (schematic vs layout match?)

![Padframe layout](images/padframe_layout.png)

*Electric layout of `padframe{lay}`*

![Padframe 3D view](images/padframe_layout_3d.png)

*Electric 3D view of `padframe{lay}`*

---

## Notes

- TODO

---

## Files

| Path | Purpose |
|---|---|
| `lab2.jelib` | Electric library, Lab 2 cells (TODO list) |
| `lab2_padframe.jelib` | Electric library, padframe cells (TODO list) |
| `lab1.jelib` | Lab 1 library, DAC cells |
| `images/` | Screenshots used above |
| `ENCE_3501_Lab_2.pdf` | Lab handout |

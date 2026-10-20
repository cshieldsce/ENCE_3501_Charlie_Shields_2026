# Lab 4: CMOS Inverter Sizing and Load

**ENCE 3501 VLSI | University of Denver | Fall Quarter 2026 | Charlie Shields**

Two CMOS inverters with the same 2:1 PMOS/NMOS ratio but different absolute size (1x and 4x), compared in LTspice against the C5 models: a DC sweep for the voltage transfer curve, then a transient with a pulse input and a stepped capacitive load. Designed in Electric VLSI (`mocmos`, MOSIS).

**Jump to:** [Inverters](#inverters) | [DC transfer](#dc-transfer) | [Transient with load](#transient-with-load) | [Layout](#layout) | [Files](#files)

---

## Inverters

Both cells are the same schematic (PMOS on top, NMOS on the bottom, gates tied to `in`, drains tied to `out`) at different sizes. Electric shows W/L in lambda; the SPICE deck uses microns (1 lambda = 0.3 um).

| Cell | NMOS W/L | PMOS W/L | NMOS (um) | PMOS (um) |
|---|---|---|---|---|
| `inverter_1` | 6 / 6 | 12 / 6 | 1.8 / 1.8 | 3.6 / 1.8 |
| `inverter_2` | 24 / 6 | 48 / 6 | 7.2 / 1.8 | 14.4 / 1.8 |

`inverter_2` is 4x the width of `inverter_1` at the same length, so it has 4x the drive strength and 4x the gate capacitance.

![inverter_1 schematic](images/inverter_1_sch.png)

*Electric `inverter_1{sch}`. 6/6 NMOS, 12/6 PMOS.*

![inverter_2 schematic](images/inverter_2_sch.png)

*Electric `inverter_2{sch}`. 24/6 NMOS, 48/6 PMOS.*

---

## DC transfer

`test_inverters{sch}` drives both inverters from one `vin` and probes `vout1` / `vout2`. The SPICE card on the schematic is:

```
vdd vdd 0 DC 5
vin vin 0 DC 0
.dc vin 0 5 1m
.include C5_models.txt
```

![test_inverters schematic](images/test_inverters_sch.png)

*Electric `test_inverters{sch}`. Shared `vin`, `Inverter1` to `vout1`, `Inverter2` to `vout2`.*

![DC transfer curves](images/dc_transfer.png)

*LTspice DC sweep, `vin` 0 to 5 V. Green is `vout1` (1x), cyan is `vout2` (4x), blue is the `vin` line for reference.*

Both curves swing rail to rail with a sharp transition. Reading off where each crosses the `vin` line, the switching threshold of `inverter_1` is about 2.4 V and `inverter_2` is about 2.25 V. Same P/N ratio, so the thresholds are close; the small offset is the model's width dependence rather than anything in the topology.

---

## Transient with load

`test_inverters_load{sch}` adds a capacitor to ground on each output and switches `vin` with a pulse. The cap value is a parameter, `{x}`, stepped over the four loads the handout asks for: 100 fF, 1 pF, 10 pF, and 100 pF.

```
vdd vdd 0 DC 5
vin vin 0 pulse(0v 5v 5n 1n 1n 12n 25n)
.step param x list 100f 1p 10p 100p
.tran 0 25n 0 100p
.include C5_models.txt
```

![test_inverters_load schematic](images/test_inverters_load_sch.png)

*Electric `test_inverters_load{sch}`. Each inverter output drives its own `{x}` load cap.*

Both inverters, all four loads:

![Transient, both inverters](images/tran_load_both.png)

*LTspice `.tran`, 0 to 25 ns. Blue is `vout1`, red is `vout2`, cyan is `vin`.*

Per inverter, to make the 1x and 4x comparison readable:

![Transient, inverter_1](images/tran_load_inv1.png)

*`inverter_1` (1x), `vout1` against `vin` for each of the four loads.*

![Transient, inverter_2](images/tran_load_inv2.png)

*`inverter_2` (4x), `vout2` against `vin` for each of the four loads.*

Earlier run with small caps (1 fF, 10 fF, 100 fF), kept for comparison:

![Transient, small caps](images/tran_load_small_caps.png)

*`vin`, `vout1`, `vout2` for the 1 fF / 10 fF / 100 fF run; this is the deck saved in `sim/test_inverters_load*.spi`. All six edges are fast, with visible overshoot past the rails.*

Observations:

- The output edge slows as `x` grows, as expected for an RC-limited transition. At 100 fF the output swings in a few ns or less.
- At 10 pF the output has only fallen to about 1.2 V (`vout1`) / 2.8 V (`vout2`) by the time `vin` falls at 18 ns, and at 100 pF it has barely moved, drooping to about 4.6 V / 4.8 V. At those loads the pulse period is far shorter than the output time constant, so the output never reaches a full logic level.
- Small overshoot above `vdd` and below `gnd` at the input edge in the light-load cases: gate-drain coupling pushes the output past the rail until the drive takes over.

---

## Layout

<!-- TODO: inverter_1{lay} screenshot + DRC result -->
<!-- TODO: inverter_2{lay} screenshot + DRC result -->
<!-- TODO: layout-vs-schematic / extracted simulation if required by the handout -->

`inverter_1{lay}` and `inverter_2{lay}` exist in `Lab4.jelib` as empty cells and are not drawn yet.

---

## Files

| Path | Purpose |
|---|---|
| `Lab4.jelib` | Electric library: `inverter_1`, `inverter_2`, `test_inverters`, `test_inverters_load` |
| `C5_models.txt` | C5 SPICE models, `.include`d by the decks |
| `sim/test_inverters.*` | DC sweep deck, log, and raw data |
| `sim/test_inverters_load1.*`, `load2.*` | Transient decks, logs, raw data, and LTspice plot settings (`.plt`) |
| `images/` | Screenshots used above |

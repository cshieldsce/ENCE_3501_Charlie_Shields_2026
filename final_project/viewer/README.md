# ALU4 design explorer

`index.html` is a self-contained page (open it in any browser, works offline) for walking through the design:

- Click a block once to expand its inner schematic in place; the layout boxes the same block. Click it again to go inside: `ALU4` → bit slice blocks (`XOR`, `FA`, `TRI`) → `FA`'s `XOR` / `NAND` gates → transistors.
- The Components palette on the left opens any cell (`ALU4`, `FA`, `XOR`, `NAND`, `NOT`, `TRI`) on its own, schematic and layout.
- The schematic and layout of the current cell are shown together. Click a wire, transistor or block in either view and its match lights up in the other.
- The matching comes from LVS: Electric NCC's net and part equivalence for each cell. Series transistors that NCC merges into one part are matched by type, gate net and diffusion nets through the same net equivalence.

Keys: Enter opens the selected block, Esc closes an expansion / goes up, Z zooms to the selection, F fits both views.

## Rebuilding

```
java -jar electricBinaryFull-9.08.jar -batch -s src/dump.bsh      # writes src/design.json from ../ALU_cs.jelib
python3 src/build.py src/design.json src/template.html /tmp/artifact.html index.html
```

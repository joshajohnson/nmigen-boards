import os
import subprocess

from nmigen.build import *
from nmigen.vendor.lattice_ecp5 import *
from .resources import *


__all__ = ["ECP5MiniPlatform"]


class ECP5MiniPlatform(LatticeECP5Platform):
    device      = "LFE5U-12F"
    package     = "BG256"
    speed       = "8"
    default_clk = "clk16"

    resources   = [
        Resource("clk16", 0, Pins("A7"), Clock(16e6), Attrs(IO_TYPE="LVCMOS33")),

        # Used to trigger FPGA reconfiguration.
        Resource("program", 0, PinsN("R9"), Attrs(IO_TYPE="LVCMOS33")),

        # RGB LEDs are multiplexed, one anode per LED, RGB cathodes common.
        LEDResources(pins="P14 R13 T14 R14 T4 R4 T3 R5",
            attrs=Attrs(IO_TYPE="LVCMOS33")),
        Resource("led_cathodes", 0, Pins("R12 P13 T13"), Attrs(IO_TYPE="LVCMOS33")),

        # Standalone LEDs
        *LEDResources(pins="R8 A5", invert=True, attrs=Attrs(IO_STANDARD="LVCMOS33")),
        # Semantic aliases
        Resource("led_usr", 0, PinsN("R8", dir="o"), Attrs(IO_STANDARD="LVCMOS33")),
        Resource("led_act", 0, PinsN("A5", dir="o"), Attrs(IO_STANDARD="LVCMOS33")),

        DirectUSBResource(0, d_p="E9", d_n="D9", pullup="B6", vbus_valid="F4",
            attrs=Attrs(IO_TYPE="LVCMOS33")),

        *ButtonResources(
            pins={0: "R8" }, invert=True,
            attrs=Attrs(IO_TYPE="LVCMOS33")),

        *SPIFlashResources(0,
            cs="N8", clk="N9", cipo="T7", copi="T8", wp="M7", hold="N7",
            attrs=Attrs(IO_TYPE="LVCMOS33"),

        *SDCardResources(0,
            dat0="D10", dat1="E10", dat2="E13", dat3="C13", clk="D12", cmd="D13", cd="E12",
            attrs=Attrs(IO_TYPE="LVCMOS33", SLEWRATE="FAST"))

    ]
    connectors = [per
        Connector("io", 0, {
            "A0":   "T15",
            "A1":   "R16",
            "A2":   "P15",
            "A3":   "M15",
            "A4":   "R15",
            "A5":   "P16",
            "A6":   "N16",
            "A7":   "M16",
            "B0":   "L15",
            "B1":   "K15",
            "B2":   "J15",
            "B3":   "K14",
            "B4":   "L16",
            "B5":   "K16",
            "B6":   "J16",
            "B7":   "J14",
            "C0":   "H15",
            "C1":   "G15",
            "C2":   "H14",
            "C3":   "E16",
            "C4":   "G16",
            "C5":   "F16",
            "C6":   "G14",
            "C7":   "F15",
            "D0":   "E15",
            "D1":   "C15",
            "D2":   "D14",
            "D3":   "B15",
            "D4":   "D16",
            "D5":   "C16",
            "D6":   "C14",
            "D7":   "B16",
            "E0":   "C1",
            "E1":   "B1",
            "E2":   "A2",
            "E3":   "A3",
            "E4":   "C2",
            "E5":   "B2",
            "E6":   "B3",
            "E7":   "A4",
            "F0":   "K1",
            "F1":   "J1",
            "F2":   "G1",
            "F3":   "F1",
            "F4":   "K2",
            "F5":   "J2",
            "F6":   "H2",
            "F7":   "G2",
            "G0":   "N1",
            "G1":   "M1",
            "G2":   "L1",
            "G3":   "L3",
            "G4":   "P2",
            "G5":   "M2",
            "G6":   "L2",
            "G7":   "M3",
            "H0":   "R2",
            "H1":   "P4",
            "H2":   "N4",
            "H3":   "P1",
            "H4":   "T2",
            "H5":   "R3",
            "H6":   "P3",
            "H7":   "R1"
        })
    ]

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = dict(ecppack_opts="--compress --freq 38.8")
        overrides.update(kwargs)
        return super().toolchain_prepare(fragment, name, **overrides, **kwargs)

    def toolchain_program(self, products, name):
        dfu_util = os.environ.get("DFU_UTIL", "dfu-util")
        with products.extract("{}.bit".format(name)) as bitstream_filename:
            subprocess.check_call([dfu_util, "-d", "1d50:614b", "-a", "0", "-D", bitstream_filename])

if __name__ == "__main__":
    from .test.blinky import *
    ECP5MiniPlatform().build(Blinky(), do_program=True)

from bluer_ugv.parts.part import Part
from bluer_ugv.parts.part_db import PartDB

db_of_parts: PartDB = PartDB()

db_of_parts["330-ohm"] = Part(
    info=[
        "Resistor, 330-470 Ω, 1/4 watt, 5% tolerance",
    ],
    images=["resistor.png"],
)

db_of_parts["4-ch-transceiver"] = Part(
    info=[
        "4-channel transmitter and receiver",
        "source: [digikala](https://www.digikala.com/product/dkp-11037586/%DA%AF%DB%8C%D8%B1%D9%86%D8%AF%D9%87-%D9%88-%D9%81%D8%B1%D8%B3%D8%AA%D9%86%D8%AF%D9%87-%D9%85%D8%A7%D8%B4%DB%8C%D9%86-%DA%A9%D9%86%D8%AA%D8%B1%D9%84%DB%8C-%D9%85%D8%AF%D9%84-4ch-led/)",
        "voltages: receiver 6 VDC,  transmitter 3 VDC",
    ],
    images="4-channel-remote-control.png",
)

db_of_parts["470-mF"] = Part(
    info=[
        "capacitor, 470 μF to 1000 μF, 16 V or 25 V, Electrolytic, 105 °C rated if possible."
    ],
    images=["capacitor.png"],
)

db_of_parts["BTS7960"] = Part(
    info=[
        "43 A, H-Bridge Motor Driver",
        "specs: [BTS7960](https://www.handsontec.com/dataspecs/module/BTS7960%20Motor%20Driver.pdf)",
    ],
    images="bts7960.jpg",
)

db_of_parts["dc-motor-12-VDC-45W"] = Part(
    info=[
        "12 VDC motor, 20-45 W, 9000 RPM",
    ],
    images=["dcmotor.png"],
)

db_of_parts["LED"] = Part(
    info=[
        "LED, ~2 V forward voltage, 10-20 mA",
    ],
    images=["led.png"],
)

db_of_parts["Polyfuse"] = Part(
    info=[
        "Polyfuse, 1.1 A hold, 2.2 A trip, 16 V, resettable, through-hole, e.g., MF-R110",
    ],
    images=["polyfuse.png"],
)

db_of_parts["rpi3bp"] = Part(
    info=[
        "Raspberry Pi 3B+",
    ],
    images=[
        "rpi3bplus.png",
        "gpio-pinout.png",
    ],
)

db_of_parts["SLA-Battery"] = Part(
    info=[
        "Rechargeable sealed lead acid battery, 12 V, 7 Ah",
    ],
    images=[
        "battery.png",
    ],
)

db_of_parts["TVS-diode"] = Part(
    info=[
        "TVS diode, unidirectional, 600 W, 6.8 V clamp, e.g. P6KE6.8A, DO-15 package",
    ],
    images=[
        "TVSdiode.png",
    ],
)

db_of_parts["XL4015"] = Part(
    info=[
        "12 VDC -> 5 VDC, 4A",
        "specs: [XL4015](https://www.handsontec.com/dataspecs/module/XL4015-5A-PS.pdf)",
    ],
    images=[
        "XL4015.png",
    ],
)

db_of_parts["rpi-camera"] = Part(
    info=[
        "Raspberry Pi Camera, V1.3"
        "https://www.raspberrypi.com/documentation/accessories/camera.html",
    ],
    images=[
        "rpi-camera.jpg",
    ],
)

db_of_parts["DC-gearboxed-motor-12V-120RPM"] = Part(
    info=[
        "Gearboxed DC Motor, 12 V (3-24 V), 3A, 120 RPM, 1:91, 15 Kg cm",
        "[GM6558](https://www.landaelectronic.com/product/%d9%85%d9%88%d8%aa%d9%88%d8%b1-dc-%da%af%db%8c%d8%b1%d8%a8%da%a9%d8%b3-%d8%ad%d9%84%d8%b2%d9%88%d9%86%db%8c-gm6558/)",
    ],
    images=[
        "GM6558/01.jpg",
        "GM6558/02.jpg",
        "GM6558/03.jpg",
        "GM6558/04.jpg",
        "GM6558/measurements.jpg",
        "GM6558/specs.png",
    ],
)

db_of_parts["2xAA-battery-holder"] = Part(
    info=[
        "2 x AA battery holder",
    ],
    images=[
        "2xAA-battery-holder.jpg",
    ],
)

db_of_parts["4xAA-battery-holder"] = Part(
    info=[
        "4 x AA battery holder",
    ],
    images=[
        "4xAA-battery-holder.jpg",
    ],
)

db_of_parts["PCB-double-9x7"] = Part(
    info=[
        "double-sided PCB, 9 cm x 7 cm",
    ],
    images=[
        "PCB-double-9x7.jpeg",
    ],
)

db_of_parts["PCB-single-14x9_5"] = Part(
    info=[
        "single-sided PCB, 14 cm x 9.5 cm",
    ],
    images=[
        "pcb-14x9_5cm.jpg",
    ],
)

db_of_parts["pushbutton"] = Part(
    info=[
        "push button",
    ],
    images=[
        "pushbutton.png",
    ],
)

db_of_parts["yellow-gearbox-dc-motor"] = Part(
    info=[
        "gearboxed DC motor, 6V DC",
    ],
    images=[
        "yellow-gearbox-dc-motor.png",
    ],
)

db_of_parts["yellow-wheels"] = Part(
    info=[
        "wheels for gearboxed DC motor",
    ],
    images=[
        "yellow-wheels.jpg",
    ],
)

db_of_parts["front-wheel-accessories"] = Part(
    info=[
        "front wheel accessories",
    ],
    images=[
        "front-wheel.jpg",
    ],
)

db_of_parts["template"] = Part(
    info=[
        "template",
    ],
    images=[
        "template.jpg",
    ],
)

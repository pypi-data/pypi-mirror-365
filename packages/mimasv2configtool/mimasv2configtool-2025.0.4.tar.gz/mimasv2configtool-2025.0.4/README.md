# Mimas V2 Configuration Tool

Python tool to configure Numato Lab Mimas V2 FPGA board via SPI Flash over USB CDC serial.

## Installing

```
pip install mimasv2configtool
```

or

```
pip install 'git+https://github.com/Khaalidi/mimasv2configtool' 
```

or 
```
git clone https://github.com/Khaalidi/mimasv2configtool
cd mimasv2configtool
pip install .
```
## Usage
```
mimasv2configtool -p <PORT> -b <Binary File>

PORT - The serial port corresponds to Mimas V2 (Eg: COM1 on Windows )
Binary File - Binary file to be downloaded genereated from bitstream on Xilinx ISE.
```
# Mimas V2 Configuration Tool

Python tool to configure Numato Lab Mimas V2 FPGA board via SPI Flash over USB CDC serial.

## Installing

```
pip install .
```
or

```
pip install 'git+https://github.com/Khaalidi/mimasv2configtool' 
```
## Usage
```
mimasv2configtool <PORT> <Binary File>

PORT - The serial port corresponds to Mimas V2 (Eg: COM1 on Windows )
Binary File - Binary file to be downloaded genereated from bitstream on Xilinx ISE.
```
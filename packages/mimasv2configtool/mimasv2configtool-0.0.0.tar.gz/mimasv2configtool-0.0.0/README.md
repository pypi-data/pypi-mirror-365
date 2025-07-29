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
mimasv2configtool [-h] -p PORT -b BINARY_FILE

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  The serial port corresponding to Mimas V2 (Eg: COM1, /dev/ttyUSB0)
  -b BINARY_FILE, --binary-file BINARY_FILE
                        Binary file to be downloaded. See documentation for generating binary file from your design on Xilinx ISE.
```
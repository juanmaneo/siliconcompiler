import siliconcompiler

def main():
    chip = siliconcompiler.Chip('blinky')
    chip.set('input', 'rtl', 'verilog', 'blinky.v')
    chip.set('input', 'fpga', 'pcf', 'icebreaker.pcf')
    chip.set('fpga', 'partname', 'ice40up5k-sg48')
    chip.load_target('fpgaflow_demo')

    chip.run()
    chip.summary()

if __name__ == '__main__':
    main()

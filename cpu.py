"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.branchtable = {}
        self.branchtable[0b10000010] = self.handle_ldi
        self.branchtable[0b01000111] = self.handle_prn
        self.branchtable[0b10100010] = self.handle_alu
        self.branchtable[0b00000001] = self.handle_hlt
        self.branchtable[0b01000101] = self.handle_push
        self.branchtable[0b01000110] = self.handle_pop
        self.branchtable[0b01010000] = self.handle_call
        self.branchtable[0b00010001] = self.handle_ret
        self.branchtable[0b10100000] = self.handle_alu
        self.branchtable[0b10100111] = self.handle_alu
        self.branchtable[0b01010100] = self.handle_jmp
        self.branchtable[0b01010101] = self.handle_jeq
        self.branchtable[0b01010110] = self.handle_jne
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 7
        self.fl = 4
        self.reg[self.fl] = 0b00000000
        self.reg[self.sp] = 0xf4

    def ram_read(self, pc):
        return self.ram[pc]

    def ram_write(self, pc, value):
        self.ram[pc] = value


    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print(f"usage: {sys.argv[0]} filename")
            sys.exit(2)
        
        filename = sys.argv[1]

        with open(filename) as file:
            for line in file:
                comment_split = line.split("#")
                number_string = comment_split[0].strip()

                if number_string == '':
                    continue

                num = int(number_string, 2)
                # print("{:08b} is {:d}".format(num, num))
                # print(f"{num:>08b} is {num:>0d}")
                self.ram[address] = num
                address += 1


    def handle_alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == 0b10100000:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 0b10100010:
            self.reg[reg_a] = self.reg[reg_a]*self.reg[reg_b]
        elif op == 0b10100111:
            if self.reg[reg_a] < self.reg[reg_b]:
                self.reg[self.fl] = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.reg[self.fl] = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.reg[self.fl] = 0b00000001
            else:
                self.reg[self.fl] = 0b00000000
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_ldi(self, command, opA, opB):
        self.reg[opA] = opB
    
    def handle_prn(self, command, opA, _):
        print(self.reg[opA])
    
    def handle_hlt(self, command, _, __):
        sys.exit(1)

    def handle_push(self, command, opA, _):
        self.reg[self.sp] -= 1
        val = self.reg[opA]
        self.ram[self.reg[self.sp]] = val

    def handle_pop(self, command, opA, _):
        val = self.ram[self.reg[self.sp]]
        self.reg[opA] = val
        self.reg[self.sp] += 1

    def handle_call(self, command, opA, _):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + 2
        self.pc = self.reg[opA]

    def handle_ret(self, command, _, __):
        self.pc = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

    def handle_jmp(self, command, opA, _):
        self.pc = self.reg[opA]

    def handle_jeq(self, command, opA, _):
        if (self.reg[self.fl] & 0b00000001) == 1: 
            self.pc = self.reg[opA]
        else:
            self.pc += ( command >> 6 ) + 1

    def handle_jne(self, command, opA, _):
        if (self.reg[self.fl] & 0b00000001) == 0:
            self.pc = self.reg[opA]
        else:
            self.pc += ( command >> 6 ) + 1

    def run(self):
        """Run the CPU."""

        while True:
            command = self.ram_read(self.pc)
            opA = self.ram_read(self.pc + 1)
            opB = self.ram_read(self.pc + 2)
            sets_pc = ((command >> 4) & 0b0001) == 1
            is_alu_operation = ((command >> 5) & 0b001) == 1
            if not sets_pc:
                self.pc += ( command >> 6 ) + 1
            if is_alu_operation:
                self.handle_alu(command, opA, opB)
            else:
                self.branchtable[command](command, opA, opB)
            


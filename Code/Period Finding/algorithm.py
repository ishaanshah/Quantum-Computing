import math
import sys

from qiskit import (Aer, ClassicalRegister,
                    QuantumCircuit, QuantumRegister,
                    execute)
from qiskit.circuit.library import QFT
from qiskit.visualization import plot_histogram

from oracle import oracle


# Get backend
backend = Aer.get_backend('qasm_simulator')

# Length of input (optional)
n = None
try:
    n = int(sys.argv[1])
except IndexError:
    n = 4
except ValueError:
    print("Invalid size")
    sys.exit(1)

# Secret input (optional)
period = None
try:
    period = int(sys.argv[2])
    if int(math.log2(period)) > n:
        print("Period should be smaller than 2^(size)")
        sys.exit(1)
except IndexError:
    pass
except TypeError:
    print("Period should be an integer")
    sys.exit(1)

# Initialise input, output and result registers
input_reg = QuantumRegister(n, "input")
output_reg = QuantumRegister(n, "output")
result = ClassicalRegister(n)

# Initialize circuit
circuit = QuantumCircuit(input_reg, output_reg, result)

# Generate oracle
(oracle_gate, period) = oracle(n, period)
print(f"Secret period - {period}")

# Generete circuit for Quantum Fourier Transform
qft_gate = QFT(num_qubits=n, do_swaps=False, inverse=True).to_gate(label=f"QFT_{n}")

# Apply n Hadamard gates to input bits
circuit.h(input_reg)

# Apply Oracle on input bits
circuit.append(oracle_gate, [*input_reg, *output_reg])

# Perform QFT
circuit.append(qft_gate, input_reg)

# Perform measurement
circuit.measure(input_reg, result)

print(circuit.draw())

res = len(list(execute(circuit, backend).result().get_counts()))
print(f"Calculated period - {res}")

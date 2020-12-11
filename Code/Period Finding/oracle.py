import itertools
import random
import time
import math
from typing import Tuple

from qiskit import (Aer, ClassicalRegister, QuantumCircuit, QuantumRegister,
                    execute)
from qiskit.circuit import Gate

random.seed(time.monotonic())


def oracle(size: int, period: int = None) -> Tuple[Gate, int]:
    """ Returns a quantum gate which acts as an Oracle for the Period Finding Algorithm """
    # Input and Output registers
    input_reg = QuantumRegister(size, "input")
    output_reg = QuantumRegister(size, "output")

    # Initialize circuit
    oracle = QuantumCircuit(input_reg, output_reg)

    # Generate random secret string
    if not period:
        period = random.choice([2**i for i in range(size)])

    # Copy some input qubits to output qubits
    for i in range(int(math.log2(period))):
        oracle.cx(input_reg[i], output_reg[i])

    # Randomly flip qubits for further obfuscation
    for i in range(size):
        if random.choice([0, 1]):
            oracle.x(output_reg[i])

    return oracle.to_gate(label="Oracle"), period


def test_oracle():
    """ Tests the oracle against all possible inputs of length 4
        to verify its working as expected """
    # Get backend
    backend = Aer.get_backend('qasm_simulator')

    # Length of input
    n = 4

    # Initialise input, output and secret registers
    input_reg = QuantumRegister(n, "input")
    output_reg = QuantumRegister(n, "output")
    result = ClassicalRegister(n)

    (oracle_gate, period) = oracle(n)
    print(f"Secret period - {period}")

    # Test Oracle
    for seq in itertools.product(["0", "1"], repeat=n):
        # Initialize circuit
        circuit = QuantumCircuit(input_reg, output_reg, result)

        # Inititialise input qubits
        desired_vector = [0 for i in range(2**n)]
        desired_vector[int("".join(seq), 2)] = 1
        circuit.initialize(desired_vector, input_reg)

        circuit.append(oracle_gate, [*input_reg, *output_reg])

        # Perform measurement
        circuit.measure(output_reg, result)

        inp = list(seq)
        print(
            f"{''.join(inp)} - "
            f"{list(execute(circuit, backend).result().get_counts(circuit))[0]}"
        )


if __name__ == "__main__":
    test_oracle()

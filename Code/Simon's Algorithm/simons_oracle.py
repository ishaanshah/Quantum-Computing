import itertools
import random
import time
from typing import List, Tuple

from qiskit import (Aer, ClassicalRegister, QuantumCircuit, QuantumRegister,
                    execute)
from qiskit.circuit import Gate

random.seed(time.monotonic())


def simons_oracle(size: int, secret_input: List[int] = None) -> Tuple[Gate, List[int]]:
    """ Returns a quantum gate which acts as an Oracle for Simon's Algorithm """
    # Register holding the secret string
    secret = QuantumRegister(size, "secret")

    # Input and Output registers
    input = QuantumRegister(size, "input")
    output = QuantumRegister(size, "output")

    # Initialize circuit
    oracle = QuantumCircuit(input, output, secret)

    # Generate random secret string
    if not secret_input:
        secret_input = [0 for i in range(size)]
        while secret_input.count(0) == size:
            secret_input = [random.choice([0, 1]) for i in range(size)]

    # Encode it in the quantum register
    for i in range(size):
        if secret_input[i]:
            oracle.x(secret[i])

    # Copy input register to output register
    for i in range(size):
        oracle.cx(input[i], output[i])

    # Find msb of secret string
    msb = secret_input.index(1)

    # Create 2-1 mapping
    for i in range(size):
        oracle.ccx(input[msb], secret[i], output[i])

    # Randomly flip qubits for further obfuscation
    for i in range(size):
        if i % 3 == 0:
            oracle.x(output[i])

    return oracle.to_gate(label="oracle"), secret_input


def test_oracle():
    """ Tests the oracle against all possible inputs of length 4
        to verify its working as expected """
    # Get backend
    backend = Aer.get_backend('qasm_simulator')

    # Length of input
    n = 4

    # Initialise input, output and secret registers
    input = QuantumRegister(n, "input")
    output = QuantumRegister(n, "output")
    secret = QuantumRegister(n, "secret")
    result = ClassicalRegister(n)

    (oracle, secret_input) = simons_oracle(n)
    print(f"Secret string - {''.join([str(bit) for bit in secret_input])}")

    # Test Oracle
    for seq in itertools.product(["0", "1"], repeat=n):
        # Initialize circuit
        circuit = QuantumCircuit(input, output, secret, result)

        # Inititialise input qubits
        desired_vector = [0 for i in range(2**n)]
        desired_vector[int("".join(seq), 2)] = 1
        circuit.initialize(desired_vector, input)

        circuit.append(oracle, [*input, *output, *secret])

        # Perform measurement
        circuit.measure(output, result)

        inp = list(seq)
        inp.reverse()
        print(
            f"{''.join(inp)} - "
            f"{list(execute(circuit, backend).result().get_counts(circuit))[0]}"
        )


if __name__ == "__main__":
    test_oracle()

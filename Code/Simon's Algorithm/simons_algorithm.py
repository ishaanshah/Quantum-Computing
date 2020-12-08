import sys

from qiskit import (Aer, ClassicalRegister,
                    QuantumCircuit, QuantumRegister,
                    execute)
from qiskit.visualization import plot_histogram

from simons_oracle import simons_oracle


# Get backend
backend = Aer.get_backend('qasm_simulator')

# Length of input
n = None
try:
    n = int(sys.argv[1])
except IndexError:
    n = 4
except ValueError:
    print("Invalid size")
    sys.exit(1)

# Secret input (optional)
secret_input = None
try:
    secret_input = sys.argv[2]
    secret_input = [int(bit) for bit in secret_input]
    if len(secret_input) != n:
        print("Length of secret string and size of input should be the same")
        exit(1)
except IndexError:
    pass


# Initialise input, output and secret registers
input = QuantumRegister(n, "input")
output = QuantumRegister(n, "output")
secret = QuantumRegister(n, "secret")
result = ClassicalRegister(n)

(oracle, secret_input) = simons_oracle(n, secret_input)
print(f"Secret string - {''.join([str(bit) for bit in secret_input])}")

# Initialize circuit
circuit = QuantumCircuit(input, output, secret, result)

# Actual circuit
circuit.h(input)
circuit.append(oracle, [*input, *output, *secret])
circuit.h(input)

# Perform measurement
circuit.measure(input, result)

print(circuit.draw())

# Take the top results and create a matrix out of it to solve the equations
res = execute(circuit, backend).result().get_counts()
res = sorted(res, key=lambda k: res[k])[:2**(n-1)]

# Convert to proper integer matrix
mat = [[int(bit) for bit in bit_string] for bit_string in res]
for row in mat:
    row.reverse()

# Perform Gaussian Elimination
x, y = len(mat), n
cur_row, cur_col = 0, 0
while cur_row < x and cur_col < y:
    if mat[cur_row][cur_col] == 0:
        non_zero_row = -1
        for j in range(cur_row+1, x):
            if mat[j][cur_col] == 1:
                non_zero_row = j
                break
        if non_zero_row == -1:
            cur_col += 1
            continue
        else:
            mat[cur_col], mat[non_zero_row] = mat[non_zero_row], mat[cur_row]
    for j in range(cur_row+1, x):
        if mat[j][cur_col] == 1:
            for k in range(y):
                mat[j][k] = mat[j][k] ^ mat[cur_row][k]

    cur_row += 1

mat = list(filter(lambda row: row.count(0) < y, mat))

# Solve the reduced matrix
sol = [-1 for i in range(n)]
for i in range(n-1):
    if not mat[i][i]:
        sol[i] = 1
        for j in range(i+1, n):
            sol[j] = 0
        break

if sol.count(-1) == n:
    sol[-1] = 1

start = sol.index(1)-1
for i in range(start, -1, -1):
    cnt = 0
    for j in range(n):
        if sol[j] == 1 and mat[i][j] == 1:
            cnt += 1
    sol[i] = cnt % 2

print(f'Calculated Secret String: {"".join([str(bit) for bit in sol])}')

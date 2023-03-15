# S-DES en Python
# Cruz Rangel Leonardo Said

# Leemos de stdin y colocamos cada linea en un arreglo
import fileinput

lines = []
for line in fileinput.input():
    lines.append(line.strip()) #elimina los saltos de linea

# Permutation
def permute(p, key):
    """
    Permuta la clave dada usando la tabla de permutación proporcionada.
    """
    return bytes([key[i-1] for i in p])

# LFS
def left_shift(key, shifts):
    """
    Realiza un desplazamiento a la izquierda dado un número específico de desplazamientos.
    """
    return key[shifts:] + key[:shifts]

# Key Generation
def key_generation(key):
    """
    Genera las subclaves para S-DES usando la clave original de 10-bits.
    """
    p10_table = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
    p8_table = [6, 3, 7, 4, 8, 5, 10, 9]

    # P10 permutation
    key = permute(p10_table, key)

    # Split in two halves
    left = key[:5]
    right = key[5:]

    # LFS-1 and LFS-2, combine and permute to generate subkeys
    subkeys = []
    for i in range(1, 3):
        left = left_shift(left, i)
        right = left_shift(right, i)

        # Combine the halves and permutation
        combined = left + right
        subkey = permute(p8_table, combined)

        subkeys.append(subkey)

    return subkeys

def xor(a, b):
    """
    Regresa el resultado de operar dos secuencias de bytes bit a bit con XOR
    """
    return bytes(x ^ y for x, y in zip(a,b))

def s_box(input_byte, s_box):
    """Sustitución por S-Boxes S0 y S1"""
    # S-Boxes
    s_box_0 = [
        [1, 0, 3, 2],
        [3, 2, 1, 0],
        [0, 2, 1, 3],
        [3, 1, 3, 2]
    ]

    s_box_1 = [
        [0, 1, 2, 3],
        [2, 0, 1, 3],
        [3, 0, 1, 0],
        [2, 1, 0, 3]
    ]

    # Row: first and fourth bit
    row = int((str(input_byte[0])+str(input_byte[3])).encode(),2)
    # Column: second and third
    col = int((str(input_byte[1])+str(input_byte[2])).encode(),2)

    # S-Box selection
    if s_box == 0:
        new_value = s_box_0[row][col]
    elif s_box == 1:
        new_value = s_box_1[row][col]

    # S-box result to binary, padding 0's if its necessary
    output_bits = bin(new_value)[2:].zfill(2)

    return output_bits

# Round function
def function_k(after_initperm, key):
    """
    Realiza la función de ronda f_k
    """
    # Permutation tables
    ep_table = [4, 1, 2, 3, 2, 3, 4, 1]
    p4_table = [2, 4, 3, 1]

    left = after_initperm[:4]
    right = after_initperm[4:]

    # EP on the right half
    temp = permute(ep_table, right)

    # XOR with K1
    temp = xor(temp, key)

    # Divide the output of XOR into 2 halves of 4-bit each
    xor_left = temp[:4]
    xor_right = temp[4:]

    # S-box output and combine
    combine = s_box(xor_left, 0) + s_box(xor_right, 1)
    combine = combine.encode()

    # P4 permutation
    combine = permute(p4_table, combine)

    # XOR with the left half of the initial permutation
    left = xor(left, combine)
    left = (str(left[0])+str(left[1])+str(left[2])+str(left[3])).encode()

    # Combine both halves, right and left of initial permutation
    output = left + right
    return output

def swap(fk_output):
    """
    Intercambia el lado izquierda y el derecho de una entrada de 8 bits
    """
    left = fk_output[4:]
    right = fk_output[:4]
    return left + right

def encryption(plain_text, keys):
    "Cifra un texto plano utilizando el algoritmo por bloques S-DES"
    ip_table = [2, 6, 3, 1, 4, 8, 5, 7]
    ip_inv = [4, 1, 3, 5, 7, 2, 8, 6]
    # Initial Permutation (IP)
    ip = permute(ip_table, plain_text)
    # f_k1
    round1 = function_k(ip, keys[0])
    # SW
    sw = swap(round1);
    # f_k2
    round2 = function_k(sw, keys[1])
    # IP-1
    ciphertext =  permute(ip_inv, round2)
    return ciphertext

def decryption(cipher_text, keys):
    "Descifra un texto cifrado utilizando el algoritmo por bloques S-DES"
    ip_table = [2, 6, 3, 1, 4, 8, 5, 7]
    ip_inv = [4, 1, 3, 5, 7, 2, 8, 6]
    # Initial Permutation (IP)
    ip = permute(ip_table, cipher_text)
    # f_k2
    round1 = function_k(ip, keys[1])
    # SW
    sw = swap(round1);
    # f_k1
    round2 = function_k(sw, keys[0])
    # IP
    plaintext =  permute(ip_inv, round2)
    return plaintext

# E-encryption, D-decryption
process = lines[0]
clave = lines[1].encode()
textoplano = lines[2].encode()

subkeys = key_generation(clave)

output = encryption(textoplano, subkeys) if process == 'E' else decryption(textoplano, subkeys)

print(output.decode())



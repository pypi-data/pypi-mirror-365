import torch as tc
import numpy as np
import re
import math
from QuantumIntelligence.QuantumSimulator import Simulator, Circuit, Gate
import itertools
from collections import defaultdict
from QuantumIntelligence.BasicFunSZZ.BasicClass import DefaultValuedDict as DVD

def factor_control_iter_list(n_q, degree):
    n_q_iter = itertools.product(*(degree*[range(n_q)]))
    factor_control_dict = defaultdict(int)
    for nn in n_q_iter:
        control = tuple(set(nn))
        factor_control_dict[control] = factor_control_dict[control] + 2**((n_q-1) * int(degree) - sum(nn))
    factor_control_list = [(factor, list(control)) for control, factor in factor_control_dict.items()]
    if degree == 0:
        factor_control_list = [(1, [])]
    return factor_control_list

class Polynomial:
    def __init__(self, terms):
        """
        Initialize the polynomial with a tensor where each row represents a term.
        The first column is the coefficient, and the subsequent columns are the degrees of variables.

        Args:
        terms (tc.Tensor): A tensor of shape (n_terms, n_vars + 1) where n_terms is the number of terms
                           and (n_vars + 1) is the coefficient and degrees of each variable.
        """
        assert isinstance(terms, tc.Tensor), "Input terms must be a tc.Tensor"
        self.device = terms.device
        self.terms = terms

    @property
    def num_vars(self):
        return self.terms.size(1) - 1

    @property
    def num_terms(self):
        return self.terms.size(0)

    @property
    def coes(self):
        return self.terms[:, :1]

    @property
    def degrees(self):
        return self.terms[:, 1:]

    @num_vars.setter
    def num_vars(self, new_num_vars):
        current_num_vars = self.num_vars

        if new_num_vars > current_num_vars:
            # Pad with zeros
            padding = new_num_vars - current_num_vars
            self.terms = tc.cat([self.terms, tc.zeros((self.terms.size(0), padding), dtype=self.terms.dtype)], dim=1)
        elif new_num_vars < current_num_vars:
            # Check if truncating will remove any non-zero degrees
            if tc.any(self.terms[:, new_num_vars + 1:] != 0):
                raise ValueError("Cannot truncate variables as it will remove non-zero degrees.")
            self.terms = self.terms[:, :new_num_vars + 1]

    @classmethod
    def from_string(cls, poly_str, max_vars=None, device=None):
        # Improved term splitting pattern to correctly handle coefficients
        term_split_pattern = r'([+-]?[^+-]+)'
        split_terms = re.findall(term_split_pattern, poly_str.replace(" ", ""))
        terms = []

        if max_vars is None:
            # Auto-detect max_vars by finding the highest variable index in the string
            all_vars = re.findall(r"x(\d+)", poly_str)
            max_vars = max([int(var) for var in all_vars], default=0)

        for term in split_terms:
            if not term:
                continue

            # Find coefficient and the rest of the term separately
            match = re.match(r'([+-]?\d*)(.*)', term)
            coe_str = match.group(1)
            monomial_part = match.group(2)

            # Extract the coefficient or assume it's 1
            if coe_str in ['+', '-', '']:
                coe = int(coe_str + '1') if coe_str else 1
            elif coe_str == '':
                coe = 1
            else:
                coe = int(coe_str)

            # Split the monomial part into individual `xi^yi` segments
            single_vars = re.findall(r"(x\d+\^?\d*)", monomial_part)
            degrees = tc.zeros(max_vars, dtype=tc.int32)

            for var in single_vars:
                # Extract the variable and its degree
                var_match = re.match(r"x(\d+)(\^(\d+))?", var)
                if var_match:
                    var_index = int(var_match.group(1)) - 1
                    if var_match.group(3):
                        deg = int(var_match.group(3))
                    else:
                        deg = 1  # If no degree is specified, assume it is 1
                    if var_index < max_vars:
                        degrees[var_index] = deg
                    else:
                        raise ValueError(f"Variable index x{var} exceeds the maximum number of variables {max_vars}")

            terms.append(tc.tensor([coe] + degrees.tolist(), dtype=tc.int32))

        terms_tensor = tc.stack(terms) if terms else tc.zeros((0, max_vars + 1), dtype=tc.int32)
        if device is not None:
            terms_tensor = terms_tensor.to(device)
        return cls(terms_tensor)

    def __repr__(self):
        if self.terms.numel() == 0:
            return "0"

        term_strs = []
        for term in self.terms:
            coe = term[0]
            degrees = term[1:]
            monomial = []
            for var_index, degree in enumerate(degrees):
                if degree > 0:
                    monomial.append(f"x{var_index + 1}^{int(degree)}")
            term_str = f"{coe.item()}*{'*'.join(monomial)}" if monomial else str(coe.item())
            term_strs.append(term_str)
        return " + ".join(term_strs)

    def __str__(self):
        return self.__repr__()

    def add_term(self, coe, var_indices, degrees):
        """
        Add a new term to the polynomial.

        Args:
        coe (float): The coefficient of the new term.
        var_indices (list or tuple): The list of variable indices (1-based).
        degrees (list or tuple): The list of degrees corresponding to the variable indices.
        """
        if len(var_indices) != len(degrees):
            raise ValueError("var_indices and degrees must have the same length")

        max_var_index = max(var_indices)
        if max_var_index > self.num_vars:
            self.num_vars = max_var_index

        new_term = tc.zeros(self.num_vars + 1, dtype=tc.int32, device=self.device)
        new_term[0] = coe
        for var_index, degree in zip(var_indices, degrees):
            new_term[var_index + 1] = degree

        self.terms = tc.cat([self.terms, new_term.unsqueeze(0)], dim=0)
    def to_tensor(self):
        return self.terms

    def max_degree(self, var_index):
        """
        Get the maximum degree of a specific variable in the polynomial.

        Args:
        var_index (int): The index of the variable (0-based) to get the maximum degree of.

        Returns:
        int: The maximum degree of the specified variable.
        """
        if self.terms.numel() == 0:
            return 0

        return int(tc.max(self.terms[:, var_index + 1]).item())

    def leading_coe(self, var_index):
        """
        Extract the polynomial representing the coefficients of the highest power of the specified variable.

        Args:
        var_index (int): The index of the variable (0-based) for which to find the leading coefficient polynomial.

        Returns:
        Polynomial: A new Polynomial instance representing the leading coefficient polynomial.
        """
        # Find the highest power of the specified variable
        highest_power = tc.max(self.terms[:, var_index + 1]).item()

        # Extract terms with the highest power of the specified variable
        leading_coe_terms = self.terms[self.terms[:, var_index + 1] == highest_power]

        # Remove the variable's power for the extracted terms
        leading_coe_terms[:, var_index + 1] = 0

        return Polynomial(leading_coe_terms)

    def align_terms(self, other):
        """
        Align the terms of two polynomials to have the same number of variables by adding zero-degree variables.

        Args:
        other (Polynomial): The other polynomial to align with this one.

        Returns:
        Polynomial, Polynomial: Two new polynomials with aligned terms.
        """
        max_vars = max(self.terms.size(1), other.terms.size(1))
        if self.terms.size(1) < max_vars:
            padding = max_vars - self.terms.size(1)
            self_terms_padded = tc.cat([self.terms, tc.zeros((self.terms.size(0), padding),
                                                             dtype=self.terms.dtype, device=self.device)], dim=1)
        else:
            self_terms_padded = self.terms

        if other.terms.size(1) < max_vars:
            padding = max_vars - other.terms.size(1)
            other_terms_padded = tc.cat([other.terms, tc.zeros((other.terms.size(0), padding), dtype=other.terms.dtype)], dim=1)
        else:
            other_terms_padded = other.terms

        return Polynomial(self_terms_padded), Polynomial(other_terms_padded.to(self.device))

    def combine_like_terms(self):
        """
        Combine like terms in the polynomial.
        """
        if self.terms.numel() == 0:
            return self

        # Extract degrees and coefficients
        degrees = self.terms[:, 1:]
        coes = self.terms[:, 0]

        # Find unique degree vectors and their corresponding indices
        unique_degrees, inverse_indices = tc.unique(degrees, return_inverse=True, dim=0)

        # Sum coefficients for terms with the same degrees
        summed_coes = tc.zeros(unique_degrees.size(0), dtype=coes.dtype, device=self.device)
        summed_coes = summed_coes.index_add(0, inverse_indices, coes)

        # Filter out terms with zero coefficients
        non_zero_mask = (summed_coes != 0)
        non_zero_coes = summed_coes[non_zero_mask].unsqueeze(1)
        non_zero_degrees = unique_degrees[non_zero_mask]

        # Combine back the non-zero terms
        self.terms = tc.cat((non_zero_coes, non_zero_degrees), dim=1)
        return self

    def reduce_variable(self):
        for ii in range(self.num_vars):
            while True:
                self.terms[:, ii + 1] = self.terms[:, ii + 1] - 1
                if tc.any(self.terms[:, ii + 1] < 0):
                    self.terms[:, ii + 1] = self.terms[:, ii + 1] + 1
                    break
                if tc.all(self.terms[:, 1:] == 0).item():
                    self.terms[:, ii + 1] = self.terms[:, ii + 1] + 1
                    break

    def simplify_coe(self):
        # Extract the first column
        col = self.terms[:, 0]

        # Initialize GCD with the first element
        if self.terms.shape[0] > 0:
            gcd = col[0]
        else:
            gcd = 1
        # Compute GCD for the entire column
        for elem in col[1:]:
            gcd = tc.gcd(gcd, elem)
            if gcd == 1:
                break
        if gcd != 1:  # Only divide if gcd is greater than 1
            self.terms[:, 0] = self.terms[:, 0]//gcd
        return self

    def __add__(self, other):
        """
        Add another Polynomial to this Polynomial.

        Args:
        other (Polynomial): The polynomial to add to this one.

        Returns:
        Polynomial: The resulting polynomial after addition.
        """
        if not isinstance(other, Polynomial):
            raise ValueError("Addition is only supported between Polynomial instances.")

        # Align terms to handle polynomials with different numbers of variables
        self_aligned, other_aligned = self.align_terms(other)

        # Step 1: Concatenate the terms of both polynomials
        combined_terms = tc.cat((self_aligned.terms, other_aligned.terms), dim=0)

        # Step 2: Combine like terms
        # Step 3: Return the resulting polynomial
        return Polynomial(combined_terms).combine_like_terms()

    def __sub__(self, other):
        """
        Subtract another Polynomial from this Polynomial.

        Args:
        other (Polynomial): The polynomial to subtract from this one.

        Returns:
        Polynomial: The resulting polynomial after subtraction.
        """
        if not isinstance(other, Polynomial):
            raise ValueError("Subtraction is only supported between Polynomial instances.")

        # Align terms to handle polynomials with different numbers of variables
        self_aligned, other_aligned = self.align_terms(other)

        # Negate the terms of the other polynomial
        negated_other_terms = other_aligned.terms.clone()
        negated_other_terms[:, 0] = -1 * negated_other_terms[:, 0]

        # Use the addition method to complete the subtraction
        return self.__add__(Polynomial(negated_other_terms))

    def __mul__(self, other):
        """
        Multiply this Polynomial with another Polynomial.

        Args:
        other (Polynomial): The polynomial to multiply with this one.

        Returns:
        Polynomial: The resulting polynomial after multiplication.
        """
        if not isinstance(other, Polynomial):
            raise ValueError("Multiplication is only supported between Polynomial instances.")

        # Align terms to handle polynomials with different numbers of variables
        self_aligned, other_aligned = self.align_terms(other)

        # Step 1: Find the number of terms in both polynomials
        num_terms_self = self_aligned.terms.size(0)
        num_terms_other = other_aligned.terms.size(0)

        # Step 2: Expand both tensors to prepare for element-wise multiplication
        expanded_self = self_aligned.terms.unsqueeze(1).expand(-1, num_terms_other, -1)
        expanded_other = other_aligned.terms.unsqueeze(0).expand(num_terms_self, -1, -1)

        # Step 3: Multiply coefficients and add degrees element-wise
        product_coes = expanded_self[:, :, 0] * expanded_other[:, :, 0]
        product_degrees = expanded_self[:, :, 1:] + expanded_other[:, :, 1:]

        # Step 4: Reshape the result tensors
        product_coes = product_coes.reshape(-1, 1)
        product_degrees = product_degrees.reshape(-1, product_degrees.size(-1))

        # Step 5: Concatenate coefficients and degrees
        result_terms = tc.cat((product_coes, product_degrees), dim=1)

        # Step 6: Combine like terms (similar to the addition method)
        degrees = result_terms[:, 1:]
        coes = result_terms[:, 0]

        # Find unique degree vectors and their corresponding indices
        unique_degrees, inverse_indices = tc.unique(degrees, return_inverse=True, dim=0)

        # Sum coefficients for terms with the same degrees
        summed_coes = tc.zeros(unique_degrees.size(0), dtype=coes.dtype, device=self.device)
        summed_coes = summed_coes.index_add(0, inverse_indices, coes)

        # Filter out terms with zero coefficients
        non_zero_mask = (summed_coes != 0)
        non_zero_coes = summed_coes[non_zero_mask].unsqueeze(1)
        non_zero_degrees = unique_degrees[non_zero_mask]

        # Combine back the non-zero terms
        simplified_terms = tc.cat((non_zero_coes, non_zero_degrees), dim=1)

        return Polynomial(simplified_terms)

    def evaluate(self, input_values):
        """
        Evaluate the polynomial at given input values.

        Args:
        input_values (tc.Tensor): A tensor of shape (n_vars,) containing the values of the variables.

        Returns:
        tc.Tensor: The value of the polynomial at the given input values.
        """

        assert input_values.dtype is tc.int or input_values.dtype is tc.int64
        result = 0
        for term in self.terms:
            degrees = term[1:]
            term_value = term[0] * tc.prod(input_values ** degrees)
            result += term_value
        return result

    def nonzero_var_indices(self):
        """
        Return the indices of variables that have a nonzero degree in any term.

        Returns:
        List[int]: A list of variable indices (0-based) with nonzero degrees.
        """
        degrees = self.terms[:, 1:]
        non_zero_indices = tc.where(tc.any(degrees != 0, dim=0))[0]
        return non_zero_indices

    def coe_var_degree(self, var_index, degree):
        new_term = self.terms[self.terms[:, var_index+1]==degree, :]
        new_term[:, var_index+1] = 0
        return Polynomial(new_term)

    def max_degree2qubit_dict(self, max_degree):
        n_qubit_dict = DVD(default_value=0)
        for ii in range(self.num_vars):
            n_qubit_dict[ii] = math.ceil(tc.log2(max_degree[ii] + 1))
        max_result = 0
        for ii in range(self.num_terms):
            max_result = max_result + tc.abs(self.coes[ii]) * tc.prod(max_degree.pow(self.degrees[ii, :]))
        n_qubit_dict['result'] = math.ceil(np.log2(max_result + 1)) + 1
        return n_qubit_dict

    def to_circuit(self, max_degree=None, n_qubit_dict=None):
        if max_degree is None:
            max_degree = self.degrees.max(dim=0).values
        num_terms = self.num_terms
        if n_qubit_dict is None:
            n_qubit_dict = self.max_degree2qubit_dict(max_degree)
        key_list = n_qubit_dict.keys()
        n_qubit = sum(n_qubit_dict.values())
        p_dict = {}
        position = list(range(n_qubit))
        p_start = 0
        for kk in key_list:
            p_dict[kk] = position[p_start:p_start + n_qubit_dict[kk]]
            p_start = p_start + n_qubit_dict[kk]
        c = Circuit.Circuit(n_qubit=n_qubit, device=self.device)
        c.hadamard(position=p_dict['result'])
        theta0 = 2 * np.pi / 2 ** n_qubit_dict['result']
        for tt in range(num_terms):
            factor_control_iter = []
            for nn in range(self.num_vars):
                factor_control_iter.append(factor_control_iter_list(n_qubit_dict[nn], self.degrees[tt, nn]))
            for ff in itertools.product(*factor_control_iter):
                factor_tmp = 1
                control_tmp = []
                var_index = 0
                for ft, cc in ff:
                    factor_tmp = factor_tmp * ft
                    control_tmp = control_tmp + [p_dict[var_index][ct] for ct in cc]
                    var_index += 1
                for rr in range(n_qubit_dict['result']):
                    factor = factor_tmp * (2 ** rr)
                    if factor % 2 ** n_qubit_dict['result'] != 0:
                        c.phase_shift(position=[p_dict['result'][rr]], theta=theta0 * factor * int(self.coes[tt]),
                                      control=control_tmp)
        c.qft(position=p_dict['result'], inverse=True, ordering=False)
        return c, n_qubit_dict, p_dict

    def to_circuit_without_qft(self, max_degree=None, n_qubit_dict=None):
        if max_degree is None:
            max_degree = self.degrees.max(dim=0).values
        num_terms = self.num_terms
        if n_qubit_dict is None:
            n_qubit_dict = self.max_degree2qubit_dict(max_degree)
        key_list = n_qubit_dict.keys()
        n_qubit = sum(n_qubit_dict.values())
        p_dict = {}
        position = list(range(n_qubit))
        p_start = 0
        for kk in key_list:
            p_dict[kk] = position[p_start:p_start + n_qubit_dict[kk]]
            p_start = p_start + n_qubit_dict[kk]
        c = Circuit.Circuit(n_qubit=n_qubit, device=self.device)
        theta0 = 2 * np.pi / 2 ** n_qubit_dict['result']
        for tt in range(num_terms):
            factor_control_iter = []
            for nn in range(self.num_vars):
                factor_control_iter.append(factor_control_iter_list(n_qubit_dict[nn], self.degrees[tt, nn]))
            for ff in itertools.product(*factor_control_iter):
                factor_tmp = 1
                control_tmp = []
                var_index = 0
                for ft, cc in ff:
                    factor_tmp = factor_tmp * ft
                    control_tmp = control_tmp + [p_dict[var_index][ct] for ct in cc]
                    var_index += 1
                for rr in range(n_qubit_dict['result']):
                    factor = factor_tmp * (2 ** rr)
                    if factor % 2 ** n_qubit_dict['result'] != 0:
                        c.phase_shift(position=[p_dict['result'][rr]], theta=theta0 * factor * int(self.coes[tt]),
                                      control=control_tmp)
        return c, n_qubit_dict, p_dict

    def to_circuit_coe_var(self, var_index, max_degree=None, n_qubit_dict=None):
        if max_degree is None:
            max_degree = degrees.max(dim=0).values
        degrees = self.terms[:, 1:]
        coes = self.terms[:, :1]
        n_qubit_dict = defaultdict(int)
        for dd in range(max_degree[var_index]+1):
            new_n_qubit_dict = self.coe_var_degree(var_index=var_index, degree=dd).max_degree2qubit_dict(max_degree)
            if new_n_qubit_dict['result'] > n_qubit_dict['results']:
                n_qubit_dict = new_n_qubit_dict
        n_qubit = sum(n_qubit_dict.values())
        circuit_list = []
        for dd in range(max_degree[var_index]+1):
            tmp_circuit, _, p_dict = (self.coe_var_degree(var_index=var_index, degree=dd).
                                      to_circuit_without_qft(n_qubit_dict=n_qubit_dict))
            circuit_list.append(tmp_circuit)
        c = Circuit.Circuit(n_qubit=n_qubit, device=self.device)
        c.qft(position=p_dict['result'], inverse=False, ordering=False)
        control_indice = p_dict[var_index]
        for dd in range(max_degree[var_index]+1):
        # for dd in [2]:
            binary_rep = format(dd, 'b').zfill(len(control_indice))
            x_gate_indice = [control_indice[idx] for idx, bit in enumerate(binary_rep) if bit == '0']
            # print('!!!!', binary_rep, x_gate_indice)
            c.x_gate(position=x_gate_indice)
            c.compose(circuit_list[dd], control=control_indice)
            c.x_gate(position=x_gate_indice)
        c.qft(position=p_dict['result'], inverse=True, ordering=False)
        return c, n_qubit_dict, p_dict



# Example usage
if __name__ == "__main__":
    # Define the polynomials
    # terms1 = tc.tensor([[3.0, 2, 0],  # 3*x1^2
    #                     [-6.0, 1, 0], # -6*x1
    #                     [2.0, 0, 0]], dtype=tc.int32) # +2
    # poly1 = Polynomial(terms1)
    #
    # terms2 = tc.tensor([[6.0, 1, 0],  # 6*x1
    #                     [-1.0, 0, 1], # -x2
    #                     [1.0, 0, 0]], dtype=tc.int32) # +1
    # poly2 = Polynomial(terms2)
    #
    # # Print the polynomials
    # print(f"Polynomial 1: {poly1}")    # Expected: 3.0*x1^2 + -6.0*x1 + 2.0
    # print(f"Polynomial 2: {poly2}")    # Expected: 6.0*x1 + -1.0*x2 + 1.0
    #
    # # Add the polynomials
    # sum_poly = poly1 + poly2
    # print(f"Sum: {sum_poly}")          # Expected: 3.0*x1^2 + 0.0*x1 + 1.0*x2 + 3.0
    #
    # # Subtract the polynomials
    # diff_poly = poly1 - poly2
    # print(f"Difference: {diff_poly}")  # Expected: 3.0*x1^2 - 12.0*x1 + 1.0*x2 + 1.0
    #
    # # Multiply the polynomials
    # prod_poly = poly1 * poly2
    # print(f"Product: {prod_poly}")  # Expected: 18.0*x1^3 - 3.0*x1^2*x2 + 3.0*x1^2 - 36.0*x1^2 + 6.0*x1*x2 - 6.0*x1 + 12.0*x1 - 2.0*x2 + 2.0

    poly_str1 = "x1^2*x2 + -1*x3 - 1*x4 - +x5"
    poly_str2 = "3*x1^3*x2 - 4*x2^2*x3 + 5*x4 - 7*x5^2"
    poly_str3 = "x6^2 - 2*x1*x7 + 3*x5*x6 - 4*x8"
    poly_str4 = "10*x1^2 - 7*x2^3 + x3*x4^2 - 5"

    # Convert these polynomial strings to Polynomial objects
    poly1 = Polynomial.from_string(poly_str1)
    poly2 = Polynomial.from_string(poly_str2)
    poly3 = Polynomial.from_string(poly_str3)
    poly4 = Polynomial.from_string(poly_str4)

    # Print the parsed polynomials and their tensor representations
    print("Polynomial 1:")
    print(poly1)
    print(poly1.to_tensor())
    print(f"Number of variables: {poly1.num_vars}\n")

    print("Polynomial 2:")
    print(poly2)
    print(poly2.to_tensor())
    print(f"Number of variables: {poly2.num_vars}\n")

    print("Polynomial 3:")
    print(poly3)
    print(poly3.to_tensor())
    print(f"Number of variables: {poly3.num_vars}\n")

    print("Polynomial 4:")
    print(poly4)
    print(poly4.to_tensor())
    print(f"Number of variables: {poly4.num_vars}\n")

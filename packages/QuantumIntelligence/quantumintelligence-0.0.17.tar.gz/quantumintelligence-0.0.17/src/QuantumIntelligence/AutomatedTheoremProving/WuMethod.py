import torch as tc
from QuantumIntelligence.BasicFunSZZ.Polynomial import Polynomial


class WuMethod:
    def __init__(self, hypotheses=None, conclusion=None):
        """
        Initialize WuMethod with optional hypotheses and conclusion.

        Args:
        hypotheses (list of poly, optional): A list of Polynomial objects representing the hypotheses. Default is None.
        conclusion (poly, optional): A Polynomial object representing the conclusion. Default is None.
        """
        if hypotheses is None:
            hypotheses = []
        else:
            assert all(isinstance(h, poly) for h in hypotheses), "All hypotheses must be Polynomial instances."

        if conclusion is not None:
            assert isinstance(conclusion, poly), "Conclusion must be a Polynomial instance."

        self.hypotheses = hypotheses
        self.conclusion = conclusion

    def __repr__(self):
        return f"WuMethod(Hypotheses: {self.hypotheses}, Conclusion: {self.conclusion})"

    def __str__(self):
        hypotheses_str = "\n".join([str(h) for h in self.hypotheses])
        return f"Hypotheses:\n{hypotheses_str}\nConclusion:\n{self.conclusion}"

    def pseudo_divide(self, dividend, divisor, var_index):
        """
        Perform pseudo-division of two polynomials with respect to a specific variable.

        Args:
        dividend (poly): The polynomial to be divided.
        divisor (poly): The polynomial to divide by.
        var_index (int): The index of the variable (0-based) with respect to which the division is performed.

        Returns:
        remainder (poly): The remainder polynomial after pseudo-division.
        """
        device = dividend.device

        # Compute the leading term of the divisor
        leading_term_divisor = divisor.leading_coe(var_index)
        leading_term_dividend = dividend.leading_coe(var_index)
        highest_degree_divisor = int(tc.max(divisor.terms[:, var_index + 1]).item())
        highest_degree_dividend = int(tc.max(dividend.terms[:, var_index + 1]).item())

        degree_diff = highest_degree_dividend - highest_degree_divisor

        # Create the variable raised to the power of the degree difference
        variable_power_term = Polynomial(tc.tensor([[1] + [degree_diff if i == var_index else 0 for i in range(dividend.terms.size(1) - 1)]], dtype=tc.int32, device=device))

        # Compute the next term in the division sequence
        remainder = dividend * leading_term_divisor - divisor * leading_term_dividend * variable_power_term
        # remainder.reduce_variable()
        # remainder.combine_like_terms()
        # remainder.simplify_coe()
        # print(remainder)
        return remainder

    def pseudo_divide_iteratively(self, dividend, divisor_list, var_index_list):
        pp = dividend
        for dd, vv in zip(divisor_list, var_index_list):
            pp = self.pseudo_divide(pp, dd, vv)
        return pp

    def eliminate_variable(self, dividend, divisor, var_index):
        """
        Eliminate a specific variable from two polynomials using pseudo-division method.

        Args:
        poly1 (poly): The first polynomial.
        poly2 (poly): The second polynomial.
        var_index (int): The index of the variable (0-based) to eliminate.

        Returns:
        poly: The final remainder after eliminating the variable.
        """
        count = 0
        while True:
            highest_degree_poly1 = dividend.max_degree(var_index)
            highest_degree_poly2 = divisor.max_degree(var_index)

            if highest_degree_poly1 == 0 or highest_degree_poly2 == 0:
                break

            if highest_degree_poly1 >= highest_degree_poly2:
                dividend = self.pseudo_divide(dividend, divisor, var_index)
                count = count + 1
                # print('!')
            else:
                divisor = self.pseudo_divide(divisor, dividend, var_index)
                count = count + 1
                # print('?')
            assert count > 0
            # print(count)
            # print(poly1)
            # print(poly2)
        return dividend if highest_degree_poly1 == 0 else divisor

    def eliminate_variable_iteratively(self, dividend, divisor_list, var_index_list):
        pp = dividend
        for dd, vv in zip(divisor_list, var_index_list):
            pp = self.eliminate_variable(pp, dd, vv)

        return pp


# Example usage
if __name__ == "__main__":
    terms_hypothesis1 = tc.tensor([[3, 2, 0], [-6, 1, 0], [2, 0, 0]], dtype=tc.int32)  # 3*x1^2 - 6*x1 + 2
    hypothesis1 = Polynomial(terms_hypothesis1)

    terms_hypothesis2 = tc.tensor([[1, 1, 0], [-1, 0, 1], [1, 0, 0]], dtype=tc.int32)  # x1 - x2 + 1
    hypothesis2 = Polynomial(terms_hypothesis2)

    terms_conclusion = tc.tensor([[2, 1, 1], [1, 0, 0]], dtype=tc.int32)  # 2*x1*x2 + 1
    conclusion = Polynomial(terms_conclusion)

    # Initialize Wu's Method
    wu_method = WuMethod([hypothesis1, hypothesis2], conclusion)
    print(wu_method)

    # Perform pseudo-division
    dividend = Polynomial(tc.tensor([[6, 3, 0, 2], [-8, 2, 1, 1], [7, 1, 0, 1], [-5, 0, 0, 0]], dtype=tc.int32))  # 6*x1^3*x4^2 - 8*x1^2*x2*x3 + 7*x1*x3 - 5
    divisor = hypothesis1  # Divide by 3*x1^2*x2 - 6*x2*x3 + 4*x1*x3 - 2*x3
    var_index = 0  # Perform pseudo-division with respect to x1
    remainder = wu_method.pseudo_divide(dividend, divisor, var_index)
    print(f"Remainder: {remainder}")  # Display the remainder after pseudo-division

    # Define some complicated polynomials
    terms_poly1 = tc.tensor([[1, 0, 0, 2, 0],  # x1^2
                             [-1, 1, 1, 0, 0],  # -u1u2
                             [1, 0, 1, 0, 1]], dtype=tc.int32)  # +u2x2
    poly1 = Polynomial(terms_poly1)

    terms_poly2 = tc.tensor([[-1, 0, 0, 0, 1],  # -x1^2
                             [-1, 0, 0, 0, 2],  # -x2^2
                             [1, 2, 0, 0, 0]], dtype=tc.int32)  # u1^2
    poly2 = Polynomial(terms_poly2)

    # Initialize Wu's Method (use the already defined hypotheses and conclusion)
    wu_method = WuMethod([hypothesis1, hypothesis2], conclusion)
    print(wu_method)
    print(poly1)
    print(poly2)
    # Eliminate variable x1 (var_index = 0)
    final_remainder = wu_method.eliminate_variable(poly1, poly2, 2)
    print(f"Final Remainder after eliminating variable x1: {final_remainder}")
import torch as tc
from QuantumIntelligence.BasicFunSZZ.Polynomial import Polynomial

class Geometry:
    def __init__(self, num_vars=0, device='cpu'):
        self.points = {}
        self.relations = {}
        self.device = device
        self.num_vars = num_vars

    def add_point(self, name, *coordinates):
        if not coordinates:
            raise ValueError("Coordinates must be provided.")
        if not all(isinstance(x, int) for x in coordinates):
            raise ValueError("Coordinates must be integers.")
        self.points[name] = coordinates

        # Update num_vars to be the highest index + 1
        max_index = max(coordinates)
        if max_index >= self.num_vars:
            self.num_vars = max_index + 1

    def collinear2D(self, point1_name, point2_name, point3_name):
        if point1_name not in self.points or point2_name not in self.points or point3_name not in self.points:
            raise ValueError("All three points must be added to the geometry before checking collinearity.")

        pt1 = self.points[point1_name]
        pt2 = self.points[point2_name]
        pt3 = self.points[point3_name]

        if len(pt1) != 2 or len(pt2) != 2 or len(pt3) != 2:
            raise ValueError("All points must be in 2D.")

        x1, y1 = pt1
        x2, y2 = pt2
        x3, y3 = pt3

        poly = Polynomial(tc.zeros(0, self.num_vars + 1, dtype=tc.int32, device=self.device))
        # Polynomial representing x1 y2 - x1 y3 - y1 x2 + y1 x3 + x2 y3 - x3 y2 = 0
        poly.add_term(1, [x1, y2], [1, 1])
        poly.add_term(1, [x2, y3], [1, 1])
        poly.add_term(1, [x3, y1], [1, 1])
        poly.add_term(-1, [x1, y3], [1, 1])
        poly.add_term(-1, [x2, y1], [1, 1])
        poly.add_term(-1, [x3, y2], [1, 1])

        # Creating a tensor from the polynomial terms
        relation_poly = [poly]
        # Record the relation
        if 'collinear2D' not in self.relations:
            self.relations['collinear2D'] = []
        self.relations['collinear2D'].append(((point1_name, point2_name, point3_name), relation_poly))

        # Return the relation polynomial
        return relation_poly

    def midpoint(self, midpoint_name, point1_name, point2_name):
        if midpoint_name not in self.points or point1_name not in self.points or point2_name not in self.points:
            raise ValueError("All three points must be added to the geometry before checking the midpoint relation.")

        mid_pt = self.points[midpoint_name]
        pt1 = self.points[point1_name]
        pt2 = self.points[point2_name]

        if len(mid_pt) != len(pt1) or len(pt1) != len(pt2):
            raise ValueError("All points must have the same dimensionality.")

        # Construct the system of polynomial equations for the 'midpoint' relation
        relation_poly = []
        n_vars = len(mid_pt)
        for i in range(n_vars):
            poly = Polynomial(tc.zeros((0, self.num_vars + 1), dtype=tc.int32, device=self.device))

            # Equation: 2 * mid_pt[i] - pt1[i] - pt2[i] = 0
            # Term 1: 2 * mid_pt[i]
            poly.add_term(2, [mid_pt[i]], [1])

            # Term 2: - pt1[i]
            poly.add_term(-1, [pt1[i]], [1])

            # Term 3: - pt2[i]
            poly.add_term(-1, [pt2[i]], [1])

            relation_poly.append(poly)

        # Record the relation
        if 'midpoint' not in self.relations:
            self.relations['midpoint'] = []
        self.relations['midpoint'].append(((midpoint_name, point1_name, point2_name), relation_poly))

        # Return the relation polynomial
        return relation_poly

    def orthocenter(self, ortho_name, point1_name, point2_name, point3_name):
        if any(name not in self.points for name in [ortho_name, point1_name, point2_name, point3_name]):
            raise ValueError("All four points must be added to the geometry before checking the orthocenter relation.")

        ortho_pt = self.points[ortho_name]
        pt1 = self.points[point1_name]
        pt2 = self.points[point2_name]
        pt3 = self.points[point3_name]

        if len(ortho_pt) != 2 or len(pt1) != 2 or len(pt2) != 2 or len(pt3) != 2:
            raise ValueError("All points must be in 2D.")

        x_h, y_h = ortho_pt
        x_a, y_a = pt1
        x_b, y_b = pt2
        x_c, y_c = pt3

        relation_polys = []

        # Condition for AH ⊥ BC: x_h x_c - x_h x_b - x_a x_c + x_a x_b + y_h y_c - y_h y_b - y_a y_c + y_a y_b = 0
        poly_A = Polynomial(tc.zeros((0, self.num_vars + 1), dtype=tc.int32, device=self.device))
        poly_A.add_term(1, [x_h, x_c], [1, 1])
        poly_A.add_term(-1, [x_h, x_b], [1, 1])
        poly_A.add_term(-1, [x_a, x_c], [1, 1])
        poly_A.add_term(1, [x_a, x_b], [1, 1])
        poly_A.add_term(1, [y_h, y_c], [1, 1])
        poly_A.add_term(-1, [y_h, y_b], [1, 1])
        poly_A.add_term(-1, [y_a, y_c], [1, 1])
        poly_A.add_term(1, [y_a, y_b], [1, 1])

        relation_polys.append(poly_A)

        # Condition for BH ⊥ AC: x_h x_c - x_h x_a - x_b x_c + x_b x_a + y_h y_c - y_h y_a - y_b y_c + y_b y_a = 0
        poly_B = Polynomial(tc.zeros((0, self.num_vars + 1), dtype=tc.int32, device=self.device))
        poly_B.add_term(1, [x_h, x_c], [1, 1])
        poly_B.add_term(-1, [x_h, x_a], [1, 1])
        poly_B.add_term(-1, [x_b, x_c], [1, 1])
        poly_B.add_term(1, [x_b, x_a], [1, 1])
        poly_B.add_term(1, [y_h, y_c], [1, 1])
        poly_B.add_term(-1, [y_h, y_a], [1, 1])
        poly_B.add_term(-1, [y_b, y_c], [1, 1])
        poly_B.add_term(1, [y_b, y_a], [1, 1])

        relation_polys.append(poly_B)

        # Condition for CH ⊥ AB: x_h x_b - x_h x_a - x_c x_b + x_c x_a + y_h y_b - y_h y_a - y_c y_b + y_c y_a = 0
        poly_C = Polynomial(tc.zeros((0, self.num_vars + 1), dtype=tc.int32, device=self.device))
        poly_C.add_term(1, [x_h, x_b], [1, 1])
        poly_C.add_term(-1, [x_h, x_a], [1, 1])
        poly_C.add_term(-1, [x_c, x_b], [1, 1])
        poly_C.add_term(1, [x_c, x_a], [1, 1])
        poly_C.add_term(1, [y_h, y_b], [1, 1])
        poly_C.add_term(-1, [y_h, y_a], [1, 1])
        poly_C.add_term(-1, [y_c, y_b], [1, 1])
        poly_C.add_term(1, [y_c, y_a], [1, 1])

        relation_polys.append(poly_C)

        # Record the relation
        if 'orthocenter' not in self.relations:
            self.relations['orthocenter'] = []
        self.relations['orthocenter'].append(((ortho_name, point1_name, point2_name, point3_name), relation_polys))

        # Return the relation polynomials
        return relation_polys

    def point_on_circle(self, point_name, center_name, circle_point_name):
        if any(name not in self.points for name in [point_name, center_name, circle_point_name]):
            raise ValueError("All points must be added to the geometry before checking the point-on-circle relation.")

        point = self.points[point_name]
        center = self.points[center_name]
        circle_point = self.points[circle_point_name]

        if len(point) != 2 or len(center) != 2 or len(circle_point) != 2:
            raise ValueError("All points must be in 2D.")

        x_a, y_a = point
        x_d, y_d = center
        x_e, y_e = circle_point

        relation_polys = []

        # Polynomial representing the equation of the circle
        poly = Polynomial(tc.zeros((0, self.num_vars + 1), dtype=tc.int32, device=self.device))

        # x_a^2 term
        poly.add_term(1, [x_a], [2])

        # y_a^2 term
        poly.add_term(1, [y_a], [2])

        # -2 * x_a * x_d term
        poly.add_term(-2, [x_a, x_d], [1, 1])

        # -2 * y_a * y_d term
        poly.add_term(-2, [y_a, y_d], [1, 1])

        # - x_e^2 term
        poly.add_term(-1, [x_e], [2])

        # - y_e^2 term
        poly.add_term(-1, [y_e], [2])

        # 2 * x_e * x_d term
        poly.add_term(2, [x_e, x_d], [1, 1])

        # 2 * y_e * y_d term
        poly.add_term(2, [y_e, y_d], [1, 1])

        relation_polys.append(poly)

        # Record the relation
        if 'point_on_circle' not in self.relations:
            self.relations['point_on_circle'] = []
        self.relations['point_on_circle'].append(((point_name, center_name, circle_point_name), relation_polys))

        # Return the relation polynomials
        return relation_polys

    def concyclic(self, point1_name, point2_name, point3_name, point4_name):
        """
        Add a relation indicating that four points are concyclic.

        Args:
            point1_name (str): The name of the first point.
            point2_name (str): The name of the second point.
            point3_name (str): The name of the third point.
            point4_name (str): The name of the fourth point.
        """
        if any(name not in self.points for name in [point1_name, point2_name, point3_name, point4_name]):
            raise ValueError(
                "All four points must be added to the geometry before checking the concyclic relation.")

        pt1 = self.points[point1_name]
        pt2 = self.points[point2_name]
        pt3 = self.points[point3_name]
        pt4 = self.points[point4_name]

        if not all(len(pt) == 2 for pt in [pt1, pt2, pt3, pt4]):
            raise ValueError("All points must be in 2D.")

        x_a, y_a = pt1
        x_b, y_b = pt2
        x_c, y_c = pt3
        x_d, y_d = pt4


        poly_concyclic = Polynomial(tc.zeros((0, self.num_vars + 1), dtype=tc.int32, device=self.device))

        # Full polynomial:
        # x_cy_ax_b^2 - x_by_ax_c^2 - x_dy_ax_b^2 + x_dy_ax_c^2 +
        # x_by_ax_d^2 - x_cy_ax_d^2 - x_cy_bx_a^2 + x_ay_bx_c^2 +
        # x_dy_bx_a^2 - x_dy_bx_c^2 - x_ay_bx_d^2 + x_cy_bx_d^2 -
        # x_cy_by_a^2 + x_dy_by_a^2 + x_cy_ay_b^2 - x_dy_ay_b^2 +
        # x_by_cx_a^2 - x_ay_cx_b^2 - x_dy_cx_a^2 + x_dy_cx_b^2 +
        # x_ay_cx_d^2 - x_by_cx_d^2 + x_by_cy_a^2 - x_dy_cy_a^2 -
        # x_ay_cy_b^2 + x_dy_cy_b^2 - x_by_ay_c^2 + x_dy_ay_c^2 +
        # x_ay_by_c^2 - x_dy_by_c^2 - x_by_dx_a^2 + x_ay_dx_b^2 +
        # x_cy_dx_a^2 - x_cy_dx_b^2 - x_ay_dx_c^2 + x_by_dx_c^2 -
        # x_by_dy_a^2 + x_cy_dy_a^2 + x_ay_dy_b^2 - x_cy_dy_b^2 -
        # x_ay_dy_c^2 + x_by_dy_c^2 + x_by_ay_d^2 - x_cy_ay_d^2 -
        # x_ay_by_d^2 + x_cy_by_d^2 + x_ay_cy_d^2 - x_by_cy_d^2

        # Adding all terms of the polynomial
        # x_cy_ax_b^2 - x_by_ax_c^2 - x_dy_ax_b^2 + x_dy_ax_c^2
        poly_concyclic.add_term(1, [x_c, y_a, x_b], [1, 1, 2])  # x_cy_ax_b^2
        poly_concyclic.add_term(-1, [x_b, y_a, x_c], [1, 1, 2])  # -x_by_ax_c^2
        poly_concyclic.add_term(-1, [x_d, y_a, x_b], [1, 1, 2])  # -x_dy_ax_b^2
        poly_concyclic.add_term(1, [x_d, y_a, x_c], [1, 1, 2])  # x_dy_ax_c^2

        # x_by_ax_d^2 - x_cy_ax_d^2 - x_cy_bx_a^2 + x_ay_bx_c^2
        poly_concyclic.add_term(1, [x_b, y_a, x_d], [1, 1, 2])  # x_by_ax_d^2
        poly_concyclic.add_term(-1, [x_c, y_a, x_d], [1, 1, 2])  # -x_cy_ax_d^2
        poly_concyclic.add_term(-1, [x_c, y_b, x_a], [1, 1, 2])  # -x_cy_bx_a^2
        poly_concyclic.add_term(1, [x_a, y_b, x_c], [1, 1, 2])  # x_ay_bx_c^2

        # x_dy_bx_a^2 - x_dy_bx_c^2 - x_ay_bx_d^2 + x_cy_bx_d^2
        poly_concyclic.add_term(1, [x_d, y_b, x_a], [1, 1, 2])  # x_dy_bx_a^2
        poly_concyclic.add_term(-1, [x_d, y_b, x_c], [1, 1, 2])  # -x_dy_bx_c^2
        poly_concyclic.add_term(-1, [x_a, y_b, x_d], [1, 1, 2])  # -x_ay_bx_d^2
        poly_concyclic.add_term(1, [x_c, y_b, x_d], [1, 1, 2])  # x_cy_bx_d^2

        # -x_cy_by_a^2 + x_dy_by_a^2 + x_cy_ay_b^2 - x_dy_ay_b^2
        poly_concyclic.add_term(-1, [x_c, y_b, y_a], [1, 1, 2])  # -x_cy_by_a^2
        poly_concyclic.add_term(1, [x_d, y_b, y_a], [1, 1, 2])  # x_dy_by_a^2
        poly_concyclic.add_term(1, [x_c, y_a, y_b], [1, 1, 2])  # x_cy_ay_b^2
        poly_concyclic.add_term(-1, [x_d, y_a, y_b], [1, 1, 2])  # -x_dy_ay_b^2

        # x_by_cx_a^2 - x_ay_cx_b^2 - x_dy_cx_a^2 + x_dy_cx_b^2
        poly_concyclic.add_term(1, [x_b, y_c, x_a], [1, 1, 2])  # x_by_cx_a^2
        poly_concyclic.add_term(-1, [x_a, y_c, x_b], [1, 1, 2])  # -x_ay_cx_b^2
        poly_concyclic.add_term(-1, [x_d, y_c, x_a], [1, 1, 2])  # -x_dy_cx_a^2
        poly_concyclic.add_term(1, [x_d, y_c, x_b], [1, 1, 2])  # x_dy_cx_b^2

        # x_ay_cx_d^2 - x_by_cx_d^2 + x_by_cy_a^2 - x_dy_cy_a^2
        poly_concyclic.add_term(1, [x_a, y_c, x_d], [1, 1, 2])  # x_ay_cx_d^2
        poly_concyclic.add_term(-1, [x_b, y_c, x_d], [1, 1, 2])  # -x_by_cx_d^2
        poly_concyclic.add_term(1, [x_b, y_c, y_a], [1, 1, 2])  # x_by_cy_a^2
        poly_concyclic.add_term(-1, [x_d, y_c, y_a], [1, 1, 2])  # -x_dy_cy_a^2

        # -x_ay_cy_b^2 + x_dy_cy_b^2 - x_by_ay_c^2 + x_dy_ay_c^2
        poly_concyclic.add_term(-1, [x_a, y_c, y_b], [1, 1, 2])  # -x_ay_cy_b^2
        poly_concyclic.add_term(1, [x_d, y_c, y_b], [1, 1, 2])  # x_dy_cy_b^2
        poly_concyclic.add_term(-1, [x_b, y_a, y_c], [1, 1, 2])  # -x_by_ay_c^2
        poly_concyclic.add_term(1, [x_d, y_a, y_c], [1, 1, 2])  # x_dy_ay_c^2

        # x_ay_by_c^2 - x_dy_by_c^2 - x_by_dx_a^2 + x_ay_dx_b^2
        poly_concyclic.add_term(1, [x_a, y_b, y_c], [1, 1, 2])  # x_ay_by_c^2
        poly_concyclic.add_term(-1, [x_d, y_b, y_c], [1, 1, 2])  # -x_dy_by_c^2
        poly_concyclic.add_term(-1, [x_b, y_d, x_a], [1, 1, 2])  # -x_by_dx_a^2
        poly_concyclic.add_term(1, [x_a, y_d, x_b], [1, 1, 2])  # x_ay_dx_b^2

        # x_cy_dx_a^2 - x_cy_dx_b^2 - x_ay_dx_c^2 + x_by_dx_c^2
        poly_concyclic.add_term(1, [x_c, y_d, x_a], [1, 1, 2])  # x_cy_dx_a^2
        poly_concyclic.add_term(-1, [x_c, y_d, x_b], [1, 1, 2])  # -x_cy_dx_b^2
        poly_concyclic.add_term(-1, [x_a, y_d, x_c], [1, 1, 2])  # -x_ay_dx_c^2
        poly_concyclic.add_term(1, [x_b, y_d, x_c], [1, 1, 2])  # x_by_dx_c^2

        # -x_by_dy_a^2 + x_cy_dy_a^2 + x_ay_dy_b^2 - x_cy_dy_b^2
        poly_concyclic.add_term(-1, [x_b, y_d, y_a], [1, 1, 2])  # -x_by_dy_a^2
        poly_concyclic.add_term(1, [x_c, y_d, y_a], [1, 1, 2])  # x_cy_dy_a^2
        poly_concyclic.add_term(1, [x_a, y_d, y_b], [1, 1, 2])  # x_ay_dy_b^2
        poly_concyclic.add_term(-1, [x_c, y_d, y_b], [1, 1, 2])  # -x_cy_dy_b^2

        # -x_ay_dy_c^2 + x_by_dy_c^2 + x_by_ay_d^2 - x_cy_ay_d^2
        poly_concyclic.add_term(-1, [x_a, y_d, y_c], [1, 1, 2])  # -x_ay_dy_c^2
        poly_concyclic.add_term(1, [x_b, y_d, y_c], [1, 1, 2])  # x_by_dy_c^2
        poly_concyclic.add_term(1, [x_b, y_a, y_d], [1, 1, 2])  # x_by_ay_d^2
        poly_concyclic.add_term(-1, [x_c, y_a, y_d], [1, 1, 2])  # -x_cy_ay_d^2

        # -x_ay_by_d^2 + x_cy_by_d^2 + x_ay_cy_d^2 - x_by_cy_d^2
        poly_concyclic.add_term(-1, [x_a, y_b, y_d], [1, 1, 2])  # -x_ay_by_d^2
        poly_concyclic.add_term(1, [x_c, y_b, y_d], [1, 1, 2])  # x_cy_by_d^2
        poly_concyclic.add_term(1, [x_a, y_c, y_d], [1, 1, 2])  # x_ay_cy_d^2
        poly_concyclic.add_term(-1, [x_b, y_c, y_d], [1, 1, 2])  # -x_by_cy_d^2


        relation_poly = [poly_concyclic]

        # Record the relation
        if 'concyclic' not in self.relations:
            self.relations['concyclic'] = []
        self.relations['concyclic'].append(((point1_name, point2_name, point3_name, point4_name), relation_poly))
        return relation_poly

    def equal_zero(self, point_name, coordinate_index):
        """
        Add a = 0 relation, which means a coordinate of a point is zero.

        Args:
            point_name (str): The name of the point.
            coordinate_index (int): The index of the coordinate (0-based).
        """
        if point_name not in self.points:
            raise ValueError(f"Point {point_name} is not added to the geometry.")

        point = self.points[point_name]
        if coordinate_index >= len(point):
            raise ValueError(f"Coordinate index {coordinate_index} out of range for point {point_name}.")

        relation_poly = []

        # Construct the poly tensor representing that point[coordinate_index] = 0
        poly_tensor_zero = tc.zeros((1, self.num_vars + 1), dtype=tc.int32, device=self.device)
        poly_tensor_zero[0, 0] = 1
        poly_tensor_zero[0, point[coordinate_index]+ 1] = 1

        relation_poly.append(Polynomial(poly_tensor_zero))

        # Record the relation
        if 'zero' not in self.relations:
            self.relations['zero'] = []
        self.relations['zero'].append((point_name, relation_poly))

        return relation_poly


    def get_all_relations(self):
        """
        Return a list of all polynomials representing the relations in the geometry.
        """
        all_polys = []
        for relation, relations in self.relations.items():
            for _, polys in relations:
                if isinstance(polys, list):
                    all_polys.extend(polys)
                else:
                    all_polys.append(polys)
        return all_polys

    def __repr__(self):
        points_str = ", ".join(
            f"{name}: ({', '.join(f'{coord}' for coord in coordinates)})"
            for name, coordinates in self.points.items()
        )
        relations_str = "\n".join(
            f"{relation}:\n" + "\n".join(
                f"  {pts}: {str(poly)}" for pts, polys in relations for poly in (polys if isinstance(polys, list) else [polys])
            )
            for relation, relations in self.relations.items()
        )
        return f"Points:\n{points_str}\n\nRelations:\n{relations_str}"

    def __str__(self):
        return self.__repr__()

# Example usage
if __name__ == "__main__":
    geom = Geometry()
    geom.add_point("A", 0, 3)  # Point A at coordinates (0, 3)
    geom.add_point("B", 4, 6)  # Point B at coordinates (4, 6)
    geom.add_point("C", 5, 9)  # Point C at coordinates (5, 9)
    geom.add_point("D", 2, 7)  # Point C at coordinates (5, 9)

    poly = geom.collinear2D("A", "B", "C")
    poly = geom.midpoint("A", "B", "C")
    poly = geom.orthocenter('D', "A", "B", "C")
    print(geom)
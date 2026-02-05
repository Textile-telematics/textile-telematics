import cellpylib as cpl
import numpy as np

class CATextile:
    def evolveMatrix(self, matrix, rule_number, debug=False):
        # treat each row as one initial state
        rows, cols = matrix.shape
        ca_matrix = np.zeros((rows, cols))
        print(f"running rule {rule_number}\n")
        if debug:
            print(matrix)
            print("\n")
        for y in range(rows):
            init_state = np.expand_dims(matrix[y], axis=0)
            # print(init_state)
            ca = cpl.evolve(
                init_state,
                timesteps=2,  # we only want the first next line
                apply_rule=lambda n, c, t: cpl.nks_rule(n, rule_number)
            )
            # print(ca)
            ca_matrix[y] = ca[1]
        return ca_matrix

    def evolveMatrixVertical(self, matrix, rule_number, debug=False):
        v_matrix = np.rot90(matrix, k=-1)
        ca_v_matrix = self.evolveMatrix(v_matrix, rule_number, debug)
        ca_matrix = np.rot90(ca_v_matrix, k=1)
        return ca_matrix


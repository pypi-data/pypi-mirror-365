""""""""
import numpy

'''
Functions for n degree of freedon
'''
import numpy as np
from scipy.linalg import eigvals, eig


def get_natural_frequencies(k, m):
    m_inv_k = np.linalg.inv(m) @ k
    lambda_ = eigvals(m_inv_k)
    lambda_ = lambda_
    natural_frequencies = lambda_ ** (1 / 2)
    natural_frequencies_real = np.real_if_close(natural_frequencies, tol=1)
    natural_frequencies_real.sort()
    return natural_frequencies_real


def get_modes_shapes(k, m):
    # Cálculo da matriz M⁻¹K
    m_inv_k = np.linalg.inv(m) @ k
    eigenvals, mode_shapes = np.linalg.eig(m_inv_k)

    # Ordena pelo menor autovalor (freq²)
    idx = np.argsort(eigenvals)
    mode_shapes_sorted = mode_shapes[:, idx]
    for j in range(mode_shapes_sorted.shape[1]):
        aux = mode_shapes_sorted[0, j]
        for i in range(mode_shapes.shape[0]):
            mode_shapes_sorted[i, j] = mode_shapes_sorted[i, j] / aux
    return mode_shapes_sorted


def get_normal_modal_vectors(modeShapes, m):
    normal_modal_vector = np.zeros(modeShapes.shape)
    for i in range(modeShapes.shape[0]):  # itera sobre o numero de linhas que tem na matriz
        vector_aux1 = modeShapes[:, i].T
        vector_aux2 = vector_aux1 @ m @ modeShapes[:, i]
        normal_modal_vector[:, i] = modeShapes[:, i] / np.sqrt(vector_aux2)

    return normal_modal_vector


def get_coef_resp_natural(normal_modal_vectors, natural_frequencies, m, desloc_init, vel_init):
    coef1 = np.zeros(normal_modal_vectors.shape[0])
    coef2 = np.zeros(normal_modal_vectors.shape[0])
    a = np.zeros(normal_modal_vectors.shape[0])
    for i in range(normal_modal_vectors.shape[0]):
        aux1 = normal_modal_vectors[:, i].T
        coef1[i] = aux1 @ m @ desloc_init
        coef2[i] = aux1 @ m @ vel_init
        a[i] = np.sqrt(coef1[i] ** 2 + (coef2[i] / natural_frequencies[i]) ** 2)

    return a


def get_modal_phases(normal_modal_vectors, natural_frequencies, m, desloc_init, vel_init):
    coef1 = np.zeros(normal_modal_vectors.shape[0])
    coef2 = np.zeros(normal_modal_vectors.shape[0])
    phase = np.zeros(normal_modal_vectors.shape[0])
    for i in range(normal_modal_vectors.shape[0]):
        aux1 = normal_modal_vectors[:, i].T
        coef1[i] = aux1 @ m @ desloc_init
        coef2[i] = aux1 @ m @ vel_init
        phase[i] = np.arctan(-(coef2[i] / (natural_frequencies[i] * coef1[i])))

    return phase


def get_natural_modes_of_vibration(normal_modal_vectors, natural_frequencies, coef, phase):
    def x_of_t(time):
        n_dof = normal_modal_vectors.shape[0]
        n_modes = normal_modal_vectors.shape[1]
        if type(time) == numpy.ndarray:
            n_times = len(time)
            result = np.zeros((n_dof, n_modes, n_times))
            for i in range(n_modes):
                result[:, i, :] = (
                        coef[i] * normal_modal_vectors[:, i][:, np.newaxis]
                        * np.cos(natural_frequencies[i] * time + phase[i])
                )
            return result

        elif type(time) == float:
            result = np.zeros((n_dof, n_modes))
            for i in range(n_modes):
                result[:, i] = coef[i] * normal_modal_vectors[:, i] * np.cos(natural_frequencies[i] * time +
                                                                  phase[i])
            return result

    return x_of_t


def get_total_natural_response(natural_modes_in_time):


    if natural_modes_in_time.ndim == 3:
        n_dof, n_modes, n_times = natural_modes_in_time.shape
        total_response = np.zeros((n_dof, n_times))

        for i in range(n_modes):
            total_response += natural_modes_in_time[:, i, :]

        return total_response

    elif natural_modes_in_time.ndim == 2:
        n_dof, n_modes = natural_modes_in_time.shape
        total_response = np.zeros((n_dof))

        for i in range(n_modes):
            total_response += natural_modes_in_time[:, i]

        return total_response

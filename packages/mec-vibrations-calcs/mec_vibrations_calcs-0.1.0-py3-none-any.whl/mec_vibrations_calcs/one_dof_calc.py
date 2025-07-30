import math
import numpy as np


def get_natural_frequency(keq, meq):
    w_natural = math.sqrt(keq / meq)
    return w_natural


def get_dumping_ratio(ceq, meq, w_n):
    epsilon = ceq / (2 * meq * w_n)
    return epsilon


def get_resonance_frequency(w_natural, epslon):  # Frequencia natural e
    w_resonance = w_natural * math.sqrt(1 - 2 * epslon ** 2)
    return w_resonance


def get_recept(meq, ceq, keq, omega):
    alpha = 1 / ((keq - meq * omega ** 2) + 1j * omega * ceq)
    return alpha


def get_real_recept(meq, ceq, keq, omega):
    real_part = (keq - meq * (omega ** 2)) / ((keq - meq * (omega ** 2)) ** 2 + (omega * ceq) ** 2)
    return real_part


def get_imaginary_recept(meq, ceq, keq, omega):
    imaginaria_part = -(omega * ceq) / ((keq - meq * omega ** 2) ** 2 + (omega * ceq) ** 2)
    return imaginaria_part


def get_mobility(meq, ceq, keq, omega):
    mob = (1j * omega) / ((keq - (omega ** 2) * meq) + 1j * omega * ceq)
    return mob


def get_real_mobility(meq, ceq, keq, omega):
    real_part = ((omega ** 2) * ceq) / (((keq - (omega ** 2) * meq) ** 2) + (omega * ceq) ** 2)
    return real_part


def get_imaginary_mobility(meq, ceq, keq, omega):
    imaginary = (omega * (keq - meq * (omega ** 2))) / (((keq - meq * (omega ** 2)) ** 2) + (omega * ceq) ** 2)
    return imaginary


def get_acelerance(meq, ceq, keq, omega):
    acel = - (omega ** 2) / ((keq - meq * (omega ** 2)) + 1j * omega * ceq)
    return acel


def get_real_acelerance(meq, ceq, keq, omega):
    real = - ((omega ** 2) * (keq - meq * (omega ** 2))) / (((keq - meq * (omega ** 2)) ** 2) + (omega * ceq) ** 2)
    return real


def get_imaginary_acelerance(meq, ceq, keq, omega):
    imag = omega ** 3 * ceq / (((keq - meq * (omega ** 2)) ** 2) + (omega * ceq) ** 2)
    return imag


def get_period(natual_frequency):
    periodo = (2 * math.pi / natual_frequency)
    return periodo


def get_natural_response(natural_frequency, dumping_ratio, init_deloc, init_vel, time):
    if dumping_ratio == 0:
        a1 = init_deloc
        a2 = (init_vel / natural_frequency)
        a = math.sqrt((a1 ** 2) + (a2 ** 2))
        phi = math.atan(a2 / a1)
        response = a * np.cos(natural_frequency * time - phi)
        return response
    if 0 < dumping_ratio < 1:
        a1 = init_deloc
        a2 = (init_vel + dumping_ratio * natural_frequency * init_deloc) / (
                natural_frequency * math.sqrt(1 - dumping_ratio ** 2))
        a = np.sqrt((a1 ** 2) + (a2 ** 2))
        natural_dumped_frequency = natural_frequency * math.sqrt(1 - dumping_ratio ** 2)
        phi = np.atan(a2 / a1)
        response = a * np.exp(-dumping_ratio * natural_frequency * time) * np.cos(
            natural_dumped_frequency * time - phi)
        return response
    if dumping_ratio == 1:
        response = (init_deloc + (init_vel + natural_frequency * init_deloc) * time) * np.exp(
            -natural_frequency * time)
        return response
    if dumping_ratio > 1:
        a1 = init_deloc
        a2 = (init_vel + dumping_ratio * natural_frequency * init_deloc) / (
                natural_frequency * np.sqrt(dumping_ratio ** 2 - 1))
        part1 = np.cosh(natural_frequency * (np.sqrt((dumping_ratio ** 2)) - 1) * time)
        part2 = np.sinh(natural_frequency * (np.sqrt((dumping_ratio ** 2)) - 1) * time)
        response = np.exp(-dumping_ratio * natural_frequency * time) * (a1 * part1 + a2 * part2)
        return response


def get_log_decrement(dumping_ratio):
    decrement = (2 * math.pi * dumping_ratio) / (math.sqrt(1 - dumping_ratio ** 2))
    return decrement


def get_transitory_response_HE(natural_frequency, dumping_ratio, init_deloc, init_vel, time):
    return get_natural_response(natural_frequency, dumping_ratio, init_deloc, init_vel, time)


def get_permanent_response_HE(natural_frequency, k, f_ext, dumping_ratio, omega, time):
    x_s = f_ext / k
    beta = omega / natural_frequency
    part1 = np.sqrt((1 - beta ** 2) ** 2 + (2 * dumping_ratio * beta) ** 2)
    part2 = x_s / part1
    phase = np.atan((2 * dumping_ratio * beta) / (1 - beta ** 2))
    response = part2 * np.cos(omega * time - phase)
    return response


def get_total_response_HE(natural_frequency, k, f_ext, dumping_ratio, omega, time, init_deloc, init_vel):
    return get_transitory_response_HE(natural_frequency, dumping_ratio, init_deloc, init_vel,
                                      time) + get_permanent_response_HE(
        natural_frequency, k, f_ext, dumping_ratio, omega, time)


def get_amplitute_factor_HE(natural_frequency, dumping_ratio, omega):
    beta = omega / natural_frequency
    part1 = (1 - beta ** 2) ** 2
    part2 = (2 * beta * dumping_ratio) ** 2
    result = 1 / (np.sqrt(part1 + part2))
    return result


def get_force_transmissibility_HE(natural_frequency, dumping_ratio, omega):
    beta = omega / natural_frequency
    part1 = np.sqrt(1 + (2 * beta * dumping_ratio) ** 2)
    part2 = np.sqrt((1 - beta ** 2) ** 2 + (2 * beta * dumping_ratio) ** 2)
    tr = part1 / part2
    return tr

import random
from copy import deepcopy

from data import figure_list, greek


class Figure:
    def __init__(self, parameters):
        self.parameters = parameters

    def change(self, figure, color, matrix, all=1):
        if figure != -1 and color != -1:
            elem_to_change = [0, 1]

            if not figure:
                elem_to_change = [1]
            elif not color:
                elem_to_change = [0]

            elem_to_change = random.choice(elem_to_change)

            if all:
                if elem_to_change == 0:
                    possible_parameters = [x for x in figure_list if
                                           x[0] != self.parameters[0] and
                                           x[1] == self.parameters[1] and
                                           x not in matrix]
                    new_parameters = random.choice(possible_parameters)
                    self.parameters = new_parameters
                elif elem_to_change == 1:
                    possible_parameters = [x for x in figure_list if
                                           x[0] == self.parameters[0] and
                                           x[1] != self.parameters[1] and
                                           x not in matrix]
                    new_parameters = random.choice(possible_parameters)
                    self.parameters = new_parameters
            else:
                if elem_to_change == 0:
                    possible_parameters = [x for x in figure_list if
                                           x[0] != self.parameters[0] and
                                           x[1] == self.parameters[1] and
                                           x not in matrix and
                                           0 <= x[1] <= 5]
                    new_parameters = random.choice(possible_parameters)
                    self.parameters = new_parameters
                elif elem_to_change == 1:
                    possible_parameters = [x for x in figure_list if
                                           x[0] == self.parameters[0] and
                                           x[1] != self.parameters[1] and
                                           x not in matrix and
                                           0 <= x[1] <= 5]
                    new_parameters = random.choice(possible_parameters)
                    self.parameters = new_parameters
        else:
            if all:
                new_greek = deepcopy(greek)
                new_greek.remove(self.parameters)
                self.parameters = random.choice(new_greek)
            else:
                new_greek = deepcopy(greek[0:5])
                new_greek.remove(self.parameters)
                self.parameters = random.choice(new_greek)

    def info(self):
        try:
            return str(self.parameters[0]) + '_' + str(self.parameters[1]) + 'a.png'
        except:
            return 'g' + str(self.parameters) + '.png'

    def __str__(self):
        return str(self.parameters)

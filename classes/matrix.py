import random
from copy import deepcopy

from data import figure_list, greek
from figure import Figure


class Matrix:
    def __init__(self, elements, ftime, mtime, stime, feedb, wait, exp, unique=False, figure=1, colors=1, all=1):
        self.size = 9
        self.matrix = []
        self.matrix_changed = []
        self.unique = unique
        self.figure = figure
        self.colors = colors
        self.elements = elements
        self.all = all

        self.exp = exp
        self.WAIT = wait
        self.FEEDB = feedb
        self.STIME = stime
        self.MTIME = mtime
        self.FTIME = ftime

        if self.figure == -1 and self.colors == -1:
            self.greek_letters = True
        else:
            self.greek_letters = False

        if self.greek_letters:
            if all:
                fig_list = deepcopy(greek)
            else:
                fig_list = deepcopy(greek[0:5])
        else:
            if all:
                fig_list = [(x, y) for x, y in figure_list]
            else:
                fig_list = [(x, y) for x, y in figure_list if 0 <= x < 5 and 0 <= y < 5]

            if not self.colors:
                fig_list = [x for x in fig_list if x[1] == 15]
            elif not self.figure:
                fig_list = [x for x in fig_list if x[0] == 3]

        self.all_possible_figures = fig_list
        self.possible_figures = fig_list

        for _ in range(self.size):
            self.matrix.append(None)
        for _ in range(elements):
            # if elements <= 9:
            #    self.add_figure("small")
            # else:
            #    self.add_figure("big")
            self.add_figure("big")

    def add_figure(self, size):
        if self.unique:
            if not self.possible_figures:
                self.possible_figures = self.all_possible_figures
            fig = random.choice(self.possible_figures)
            self.possible_figures.remove(fig)
        else:
            fig = random.choice(self.all_possible_figures)

        free = []
        for i in range(self.size):
            if self.matrix[i] is None:
                if size == 'big':
                    free.append(i)
                elif i in [6, 7, 8, 11, 12, 13, 16, 17, 18]:
                    free.append(i)

        self.matrix[random.choice(free)] = Figure(fig)

    def info(self):
        list_of_figures_info = []
        for fig in self.matrix:
            if fig is None:
                list_of_figures_info.append(None)
            else:
                list_of_figures_info.append(fig.info())

        list_of_figures_info_2 = []
        for fig in self.matrix_changed:
            if fig is None:
                list_of_figures_info_2.append(None)
            else:
                list_of_figures_info_2.append(fig.info())

        informations = {
            "size": self.size,
            "matrix": list_of_figures_info,
            "matrix_changed": list_of_figures_info_2,
            "unique": self.unique,
            "figure": self.figure,
            "colors": self.colors,
            "elements": self.elements,
            "all": self.all,
            "EXP": self.exp,
            "WAIT": self.WAIT,
            "FEEDB": self.FEEDB,
            "STIME": self.STIME,
            "MTIME": self.MTIME,
            "FTIME": self.FTIME,
        }
        return informations

    def __repr__(self):
        return str(self.info())

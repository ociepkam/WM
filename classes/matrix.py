import random
from copy import deepcopy

from data import figure_list, greek
from figure import Figure


class Matrix:
    def __init__(self, elements, ftime, mtime, stime, maxtime, var, shint, ehint,
                 feedb, wait, exp, change=2, unique=False, figure=1, colors=1, all=1):
        self.size = 16
        self.matrix = []
        self.matrix_changed = []
        self.change = change
        self.unique = unique
        self.figure = figure
        self.colors = colors
        self.elements = elements
        self.all = all

        self.exp = exp
        self.WAIT = wait
        self.FEEDB = feedb
        self.EHINT = ehint
        self.SHINT = shint
        self.VAR = var
        self.MAXTIME = maxtime
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

    def convert_matrix(self):
        self.matrix_changed = deepcopy(self.matrix)
        if self.change == 1:
            fig_idx = []
            for i in range(self.size):
                if self.matrix_changed[i] is not None:
                    fig_idx.append(i)

            change_idx_1 = random.choice(fig_idx)
            fig_idx.remove(change_idx_1)
            change_idx_2 = random.choice(fig_idx)
            self.matrix_changed[change_idx_1], self.matrix_changed[change_idx_2] = \
                self.matrix_changed[change_idx_2], self.matrix_changed[change_idx_1]
        elif self.change == 2:
            fig_idx = []
            for i in range(self.size):
                if self.matrix[i] is not None:
                    fig_idx.append(i)
            while True:
                self.matrix_changed = deepcopy(self.matrix)
                self.matrix_changed[random.choice(fig_idx)].change(self.figure, self.colors, self.matrix_changed,
                                                                   self.all)
                if len([figure.parameters for figure in self.matrix_changed if figure is not None]) == \
                   len(set([figure.parameters for figure in self.matrix_changed if figure is not None])):
                    break

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
            "change": self.change,
            "unique": self.unique,
            "figure": self.figure,
            "colors": self.colors,
            "elements": self.elements,
            "all": self.all,
            "EXP": self.exp,
            "WAIT": self.WAIT,
            "FEEDB": self.FEEDB,
            "EHINT": self.EHINT,
            "SHINT": self.SHINT,
            "VAR": self.VAR,
            "MAXTIME": self.MAXTIME,
            "STIME": self.STIME,
            "MTIME": self.MTIME,
            "FTIME": self.FTIME,
        }
        return informations

    def __repr__(self):
        return str(self.info())

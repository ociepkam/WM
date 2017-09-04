#!/usr/bin/env python
# -*- coding: latin-1 -*-
import atexit
import collections
import csv
import random
import copy
from os.path import join
from math import sqrt
import time

import yaml
from psychopy import visual, core, event, logging, gui

from concrete_experiment import concrete_experiment
from classes.data import greek, figure_list as figure
from classes.load_data import read_text_from_file
from classes.ophthalmic_procedure import ophthalmic_procedure
from classes.check_exit import check_exit
from classes.triggers import send_trigger_eeg
from misc.screen_misc import get_screen_res, get_frame_rate

# GLOBALS
TEXT_SIZE = 30
VISUAL_OFFSET = 90
FIGURES_SCALE = 0.5
HEIGHT_OFFSET = 1.0 * VISUAL_OFFSET
RESULTS = list()
RESULTS.append(
    ['NR', 'FTIME', 'MTIME', 'STIME', 'ELEMENTS', 'ALL', 'UNIQUE', 'FIGURE', 'COLORS', 'FEATURES',
     'FEEDB', 'WAIT', 'EXP', 'LAT', 'TRUE_ANS', 'ANS', 'ACC'])
TRIGGER_LIST = []
OPHTHALMIC_PROCEDURE = True
USE_EEG = True


class CaseInsensitiveDict(collections.Mapping):
    def __init__(self, d):
        self._d = d
        self._s = dict((k.lower(), k) for k in d)

    def __contains__(self, k):
        return k.lower() in self._s

    def __len__(self):
        return len(self._s)

    def __iter__(self):
        return iter(self._s)

    def __getitem__(self, k):
        return self._d[self._s[k.lower()]]

    def __setitem__(self, key, value):
        self._d[key] = value
        self._s[key.lower()] = key


@atexit.register
def save_beh_results():
    with open(join('results', PART_ID + '_beh.csv'), 'w') as beh_file:
        beh_writer = csv.writer(beh_file)
        beh_writer.writerows(RESULTS)
    logging.flush()
    with open(join('results', PART_ID + '_triggermap.txt'), 'w') as trigger_file:
        trigger_writer = csv.writer(trigger_file)
        trigger_writer.writerows(TRIGGER_LIST)


def show_info(win, file_name, insert=''):
    """
    Clear way to show info message into screen.
    :param insert:
    :param file_name:
    :param win:
    :return:
    """
    msg = read_text_from_file(file_name, insert=insert)
    msg = visual.TextStim(win, color='black', text=msg, height=TEXT_SIZE - 10, wrapWidth=SCREEN_RES['width'])
    msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'return', 'space'])
    if key == ['f7']:
        abort_with_error('Experiment finished by user on info screen! F7 pressed.')
    win.flip()


def abort_with_error(err):
    logging.critical(err)
    raise Exception(err)


class StimAggregator(object):
    def __init__(self, win, matrix, fig_scale=1.0):
        self._stims_matrix = list()
        self._grid_matrix = list()
        self._items_names = list()
        self._pos = list()
        sqrt_len = sqrt(len(matrix))
        if not sqrt_len.is_integer():
            abort_with_error('Illegal matrix shape n = {}'.format(len(matrix)))
        sqrt_len = int(sqrt_len)
        matrix = [matrix[i:i + sqrt_len] for i in range(0, len(matrix), sqrt_len)]  # group into N x N subsets
        self.width_offset = -sqrt_len / 2.0  # determine start (left) shift for squares in matrix
        self.height_offset = -sqrt_len / 2.0
        # Figure matrix must be centered.
        center_shift = (0.5 * VISUAL_OFFSET * fig_scale)  # shift to center of square
        width = self.width_offset * VISUAL_OFFSET * fig_scale + center_shift
        height = self.height_offset * VISUAL_OFFSET * fig_scale + center_shift
        for row in matrix:
            for item in row:
                if isinstance(item, str):
                    self._items_names.append(item)
                    item = visual.ImageStim(win=win, image=join('images', 'all_png', item), interpolate=True,
                                            size=90 * fig_scale, pos=(width, height))
                    self._stims_matrix.append(item)
                elif isinstance(item, visual.rect.Rect):
                    item.setPos((width, height))
                    self._stims_matrix.append(copy.copy(item))

                square = visual.Rect(win=win, lineColor='green', size=180 * fig_scale, pos=(width, height), lineWidth=5)
                self._grid_matrix.append(square)
                width += VISUAL_OFFSET * fig_scale
            height += VISUAL_OFFSET * fig_scale
            width = self.width_offset * VISUAL_OFFSET * fig_scale + center_shift
            self._pos.append((width, height))

    @staticmethod
    def get_elem_status(elem):
        try:
            if elem.status == 1:
                return elem.status
            else:
                return 0
        except:
            return elem.__dict__['autoDraw']

    def get_offsets(self):
        return self.width_offset, self.height_offset

    def get_positions(self):
        return self._pos

    def get_grid(self):
        return self._grid_matrix

    def get_marked_items_names(self):
        names = list()
        for idx, elem in enumerate(self._grid_matrix):
            if self.get_elem_status(elem):
                names.append(self._items_names[idx])
        return names

    def drawStims(self):
        for item in self._stims_matrix:
            item.draw()

    def drawGrid(self):
        for item in self._grid_matrix:
            item.draw()

    def setAutoDrawStims(self, draw):
        if not isinstance(draw, bool):
            abort_with_error('Aggregator.setAutoDrawStims can handle only boolean, got {} instead.'.format(type(draw)))
        for item in self._stims_matrix:
            item.setAutoDraw(draw)

    def setAutoDrawGrid(self, draw):
        if not isinstance(draw, bool):
            abort_with_error(
                'Aggregator.setAutoDrawGrid can handle only boolean, got {} instead.'.format(type(draw)))
        for item in self._grid_matrix:
            item.setAutoDraw(draw)

    def changeDrawGridElem(self, elem):
        if self.get_elem_status(elem):
            elem.setAutoDraw(False)
            return False
        else:
            elem.setAutoDraw(True)
            return True


class IntervalTimer(object):
    def __init__(self, start, stop):
        self._start_timer = core.CountdownTimer(float(start))
        self._stop_timer = core.CountdownTimer(float(stop))

    def in_interval(self):
        if self._start_timer.getTime() < 0.0 < self._stop_timer.getTime():
            return True
        return False


def main():
    global PART_ID, TRIGGER_LIST, USE_EEG
    info = {'Part_id': '', 'Part_age': '20', 'Part_sex': ['MALE', "FEMALE"], 'ExpDate': '06.2016'}
    dict_dlg = gui.DlgFromDict(dictionary=info, title='PWPR', fixed=['ExpDate'])
    if not dict_dlg.OK:
        abort_with_error('Info dialog terminated.')
    PART_ID = info['Part_id'] + info['Part_sex'] + info['Part_age']
    logging.LogFile('results/' + PART_ID + '.log', level=logging.INFO)
    win = visual.Window(SCREEN_RES.values(), fullscr=True, monitor='testMonitor', units='pix', screen=0,
                        color='Gainsboro')
    mouse = event.Mouse()
    event.Mouse(visible=False, newPos=None, win=win)
    frame_rate = get_frame_rate(win)
    concrete_experiment(participant_age=info['Part_age'], participant_id=info['Part_id'],
                        participant_sex=info['Part_sex'],
                        file_name="experiment_figury")
    data = yaml.load(open(join('data', PART_ID + '.yaml')))
    response_clock = core.Clock()

    next_trial = visual.TextStim(win, text=u'Naci\u015Bnij spacj\u0119 aby kontynuowa\u0107', color='black',
                                 height=TEXT_SIZE, wrapWidth=TEXT_SIZE * 50)

    fixation_cross = visual.TextStim(win, text='+', color='black', height=2 * TEXT_SIZE)

    # EEG
    trigger_no = 1
    # prepare eeg
    if USE_EEG:
        try:
            import parallel
            EEG = parallel.Parallel()
            EEG.setData(0x00)
        except:
            raise Exception("Can't connect to EEG")
    else:
        EEG = None

    # ophthalmic procedure
    if OPHTHALMIC_PROCEDURE:
        trigger_no, TRIGGER_LIST = ophthalmic_procedure(win, SCREEN_RES, frame_rate, trigger_no, TRIGGER_LIST,
                                                        port_eeg=EEG, text_color='black')

    # answers
    answers_list_figure = ["{}_{}.png".format(x, y) for x, y in figure]

    problem_number = 0
    for block in data['list_of_blocks']:
        if block['instruction_type'] != 'text':
            abort_with_error('Illegal instruction type, only text supported')
        show_info(win, join('messages', block['instruction']))
        for trial in block['list_of_matrix']:
            trial = CaseInsensitiveDict(trial)
            trial['TRUE_ANS'] = [elem for elem in trial['matrix'] if elem is not None]

            trial['FEEDBTIME'] = 2
            trial['NR'] = problem_number
            trial['features'] = trial['figure'] + trial['colors']
            trial['LAT'] = None

            # prepare visualisation
            matrix = StimAggregator(win, trial['matrix'], fig_scale=FIGURES_SCALE)
            random.shuffle(answers_list_figure)
            answers_figure = StimAggregator(win, answers_list_figure, fig_scale=FIGURES_SCALE)

            sqrt_len = int(sqrt(len(trial['matrix'])))
            mask = visual.Rect(win, fillColor='black', lineColor='black', size=FIGURES_SCALE * 180 * sqrt_len)

            for _ in range(int(0.5 * frame_rate)):  # fixation cross
                fixation_cross.draw()
                check_exit()
                win.flip()

            # First matrix
            if trial['EXP'] == 'experiment':
                trigger_no = send_trigger_eeg(trigger_no, EEG)
            for _ in range(int(float(trial['FTIME']) * frame_rate)):  # show original matrix
                matrix.drawStims()
                check_exit()
                win.flip()
            if trial['EXP'] == 'experiment':
                TRIGGER_LIST.append((str(trigger_no), "FM_" + str(trial['elements'])))

            # Mask
            if trial['EXP'] == 'experiment':
                trigger_no = send_trigger_eeg(trigger_no, EEG)
            for _ in range(int(float(trial['MTIME']) * frame_rate)):  # show mask
                mask.draw()
                check_exit()
                win.flip()
            event.clearEvents()
            win.callOnFlip(response_clock.reset)
            if trial['EXP'] == 'experiment':
                TRIGGER_LIST.append((str(trigger_no), "MASK_" + str(trial['elements'])))

            # Second matrix
            event.Mouse(visible=True, newPos=None, win=win)
            answers_figure.setAutoDrawStims(True)
            pressed = False
            if trial['EXP'] == 'experiment':
                trigger_no = send_trigger_eeg(trigger_no, EEG)
            for _ in range(int(float(trial['STIME']) * frame_rate)):  # show original matrix
                if mouse.getPressed()[0] == 0:
                    pressed = False
                if not pressed:
                    for idx, pos in enumerate(answers_figure.get_grid()):
                        if mouse.isPressedIn(pos):
                            if not answers_figure.get_elem_status(pos):
                                if len(answers_figure.get_marked_items_names()) < len(trial['TRUE_ANS']):
                                    answers_figure.changeDrawGridElem(pos)
                            else:
                                answers_figure.changeDrawGridElem(pos)
                            pressed = True

                check_exit()
                win.flip()
            if trial['EXP'] == 'experiment':
                TRIGGER_LIST.append((str(trigger_no), "SM_" + str(trial['elements'])))

            trial['ANS'] = answers_figure.get_marked_items_names()

            event.Mouse(visible=False, newPos=None, win=win)
            answers_figure.setAutoDrawStims(False)
            answers_figure.setAutoDrawGrid(False)
            win.flip()

            good_answers = [elem for elem in trial['ANS'] if elem in trial['TRUE_ANS']]
            trial['ACC'] = len(good_answers) / float(len(trial['TRUE_ANS']))

            check_exit()
            if trial['FEEDB']:
                acc = round(trial['ACC']*100, 2)
                feedb = visual.TextStim(win, text=u'Poprawno\u015B\u0107: {}%'.format(acc), color='black',
                                        height=TEXT_SIZE, wrapWidth=TEXT_SIZE * 50)
                feedb.setAutoDraw(True)
                win.flip()
                time.sleep(1)
                feedb.setAutoDraw(False)
                win.flip()

            if trial['WAIT'] == 0:
                next_trial.draw()
                win.flip()
                event.waitKeys(keyList=['space'])
            else:
                jitter = int(frame_rate)
                jitter = random.choice(range(-jitter, jitter))
                for _ in range(int((float(trial['WAIT']) * frame_rate) + jitter)):  # show break
                    check_exit()
                    win.flip()
            RESULTS.append(map(trial.__getitem__, RESULTS[0]))  # collect results

    # clear all mess
    save_beh_results()
    logging.flush()
    show_info(win, join('.', 'messages', 'end.txt'))
    win.close()


if __name__ == '__main__':
    PART_ID = ''
    SCREEN_RES = get_screen_res()
    main()

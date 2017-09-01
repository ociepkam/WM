#!/usr/bin/env python
# -*- coding: latin-1 -*-
import atexit
import codecs
import collections
import csv
import random
from os.path import join
from math import sqrt

import yaml
from psychopy import visual, core, event, logging, gui

from concrete_experiment import concrete_experiment
from misc.screen_misc import get_screen_res, get_frame_rate

# GLOBALS
TEXT_SIZE = 30
VISUAL_OFFSET = 90
FIGURES_SCALE = 0.5
HEIGHT_OFFSET = 1.0 * VISUAL_OFFSET
KEYS = ['left', 'right']
LABELS = ['Brak zmiany', 'Byla zmiana']
RESULTS = list()
RESULTS.append(
    ['NR', 'FTIME', 'MTIME', 'STIME', 'MAXTIME', 'CHANGE', 'ELEMENTS', 'ALL', 'UNIQUE', 'FIGURE', 'COLORS', 'FEATURES',
     'VAR', 'SHINT', 'EHINT', 'FEEDB', 'WAIT', 'EXP', 'LAT', 'ANS', 'ACC'])
TRIGGER_LIST = []


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


def read_text_from_file(file_name, insert=''):
    """
    Method that read message from text file, and optionally add some
    dynamically generated info.
    :param file_name: Name of file to read
    :param insert:
    :return: message
    """
    if not isinstance(file_name, str):
        logging.error('Problem with file reading, filename must be a string')
        raise TypeError('file_name must be a string')
    msg = list()
    with codecs.open(file_name, encoding='utf-8', mode='r') as data_file:
        for line in data_file:
            if not line.startswith('#'):  # if not commented line
                if line.startswith('<--insert-->'):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return ''.join(msg)


def check_exit(key='f7'):
    stop = event.getKeys(keyList=[key])
    if stop:
        abort_with_error('Experiment finished by user! {} pressed.'.format(key))


def show_info(win, file_name, insert=''):
    """
    Clear way to show info message into screen.
    :param win:
    :return:
    """
    msg = read_text_from_file(file_name, insert=insert)
    msg = visual.TextStim(win, color='black', text=msg, height=TEXT_SIZE - 10, wrapWidth=SCREEN_RES['width'])
    msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'return', 'space', 'left', 'right'] + KEYS)
    if key == ['f7']:
        abort_with_error('Experiment finished by user on info screen! F7 pressed.')
    win.flip()


def abort_with_error(err):
    logging.critical(err)
    raise Exception(err)


class StimAggregator(object):
    def __init__(self, win, matrix, fig_scale=1.0, show_grid=False):
        self._stims_matrix = list()
        self._grid_matrix = list()
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
        height = self.height_offset * VISUAL_OFFSET * fig_scale + center_shift + HEIGHT_OFFSET
        for row in matrix:
            for item in row:
                if item is not None:
                    item = visual.ImageStim(win=win, image=join('images', 'all_png', item), interpolate=True,
                                            size=90 * fig_scale, pos=(width, height))
                    self._stims_matrix.append(item)
                if show_grid:
                    square = visual.Rect(win=win, lineColor='black', size=180 * fig_scale, pos=(width, height))
                    self._grid_matrix.append(square)
                width += VISUAL_OFFSET * fig_scale
            height += VISUAL_OFFSET * fig_scale
            width = self.width_offset * VISUAL_OFFSET * fig_scale + center_shift

    def get_offsets(self):
        return self.width_offset, self.height_offset

    def draw(self):
        for item in self._stims_matrix:
            item.draw()
        for item in self._grid_matrix:
            item.draw()

    def setAutoDraw(self, draw):
        if not isinstance(draw, bool):
            abort_with_error('Aggregator.setAutoDraw can handle only boolean, got {} instead.'.format(type(draw)))
        for item in self._stims_matrix:
            item.setAutoDraw(draw)
        for item in self._grid_matrix:
            item.setAutoDraw(draw)


def determine_hint_pos(first_matrix, sec_matrix, change, fig_scale, offsets):
    sqrt_len = int(sqrt(len(first_matrix)))
    if change == 0:  # hint on random stimulus
        stim_idx = first_matrix.index(random.choice([x for x in first_matrix if x is not None]))
    elif change == 1:  # two stims place swapping
        stim_idx = random.choice([idx for idx, (x, y) in enumerate(zip(first_matrix, sec_matrix)) if x != y])
    else:  # change == 2 One stimuli has changed
        stim_idx = [idx for idx, (x, y) in enumerate(zip(first_matrix, sec_matrix)) if x != y][0]
    width_offset, height_offset = offsets
    center_shift = (0.5 * VISUAL_OFFSET * fig_scale)  # shift to center of square
    hint_x = (width_offset + (stim_idx % sqrt_len)) * (VISUAL_OFFSET * fig_scale) + center_shift
    hint_y = (height_offset + (int(stim_idx) / sqrt_len)) * (VISUAL_OFFSET * fig_scale) + center_shift + HEIGHT_OFFSET
    return hint_x, hint_y


class IntervalTimer(object):
    def __init__(self, start, stop):
        self._start_timer = core.CountdownTimer(float(start))
        self._stop_timer = core.CountdownTimer(float(stop))

    def in_interval(self):
        if self._start_timer.getTime() < 0.0 < self._stop_timer.getTime():
            return True
        return False


def main():
    global PART_ID
    info = {'Part_id': '', 'Part_age': '20', 'Part_sex': ['MALE', "FEMALE"], 'ExpDate': '06.2016'}
    dictDlg = gui.DlgFromDict(dictionary=info, title='PWPR', fixed=['ExpDate'])
    if not dictDlg.OK:
        abort_with_error('Info dialog terminated.')
    PART_ID = info['Part_id'] + info['Part_sex'] + info['Part_age']
    logging.LogFile('results/' + PART_ID + '.log', level=logging.INFO)
    win = visual.Window(SCREEN_RES.values(), fullscr=True, monitor='testMonitor', units='pix', screen=0,
                        color='Gainsboro')
    event.Mouse(visible=False, newPos=None, win=win)
    FRAME_RATE = get_frame_rate(win)
    concrete_experiment(participant_age=info['Part_age'], participant_id=info['Part_id'],
                        participant_sex=info['Part_sex'],
                        file_name="experiment")
    data = yaml.load(open(join('data', PART_ID + '.yaml')))
    response_clock = core.Clock()
    pos_feedb = visual.TextStim(win, text=u'Poprawna odpowied\u017A', color='black', height=TEXT_SIZE)
    neg_feedb = visual.TextStim(win, text=u'Odpowied\u017A niepoprawna', color='black', height=TEXT_SIZE)
    no_feedb = visual.TextStim(win, text=u'Nie udzieli\u0142e\u015B odpowiedzi', color='black', height=TEXT_SIZE)
    next_trial = visual.TextStim(win, text=u'Naci\u015Bnij dowolny klawisz reakcyjny', color='black', height=TEXT_SIZE,
                                 wrapWidth=TEXT_SIZE * 50)
    fixation_cross = visual.TextStim(win, text='+', color='black', height=2 * TEXT_SIZE, pos=(0, HEIGHT_OFFSET))
    problem_number = 0
    for block in data['list_of_blocks']:
        if block['instruction_type'] != 'text':
            abort_with_error('Illegal instruction type, only text supported')
        show_info(win, join('messages', block['instruction']))
        for trial in block['list_of_matrix']:
            trial = CaseInsensitiveDict(trial)
            # should already be in config!
            response_time = trial['MAXTIME'] - trial['STIME']
            trial['RESPTIME'] = response_time if response_time > 0.0 else 0
            trial['FEEDBTIME'] = 2
            trial['NR'] = problem_number
            trial['features'] = trial['figure'] + trial['colors']
            trial['LAT'] = None

            # prepare visualisation
            matrix = StimAggregator(win, trial['matrix'], fig_scale=FIGURES_SCALE)
            matrix_changed = StimAggregator(win, trial['matrix_changed'], fig_scale=FIGURES_SCALE)
            hint_pos = determine_hint_pos(trial['matrix'], trial['matrix_changed'], trial['change'], FIGURES_SCALE,
                                          matrix.get_offsets())
            hint = visual.Circle(win, fillColor='crimson', size=10, pos=hint_pos, lineColor='white')
            sqrt_len = int(sqrt(len(trial['matrix'])))
            mask = visual.Rect(win, fillColor='black', lineColor='black', size=FIGURES_SCALE * 180 * sqrt_len,
                               pos=(0, HEIGHT_OFFSET))
            left_label = visual.TextStim(win, text=LABELS[0], color='black', height=TEXT_SIZE,
                                         pos=(-2.5 * VISUAL_OFFSET, -2 * VISUAL_OFFSET))
            right_label = visual.TextStim(win, text=LABELS[1], color='black', height=TEXT_SIZE,
                                          pos=(2.5 * VISUAL_OFFSET, -2 * VISUAL_OFFSET))

            for _ in range(int(0.5 * FRAME_RATE)):  # fixation cross
                fixation_cross.draw()
                check_exit()
                win.flip()
            for _ in range(int(float(trial['FTIME']) * FRAME_RATE)):  # show original matrix
                matrix.draw()
                check_exit()
                win.flip()
            hint_timer = IntervalTimer(trial['SHINT'], trial['EHINT'])  # start hint display timer
            for _ in range(int(float(trial['MTIME']) * FRAME_RATE)):  # show mask
                mask.draw()
                if hint_timer.in_interval():
                    hint.draw()
                check_exit()
                win.flip()
            event.clearEvents()
            win.callOnFlip(response_clock.reset)
            left_label.setAutoDraw(True)
            right_label.setAutoDraw(True)
            for _ in range(int(float(trial['STIME']) * FRAME_RATE)):  # show changed matrix
                matrix_changed.draw()
                check_exit()
                if hint_timer.in_interval():
                    hint.draw()
                win.flip()
                keys = event.getKeys(keyList=KEYS)
                if keys:
                    trial['LAT'] = response_clock.getTime()
                    break
            if trial['LAT'] is None:  # wait a little more for ans
                for _ in range(int(float(trial['RESPTIME']) * FRAME_RATE)):
                    check_exit()
                    if hint_timer.in_interval():
                        hint.draw()
                    win.flip()
                    keys = event.getKeys(keyList=KEYS)
                    if keys:
                        trial['LAT'] = response_clock.getTime()
                        break

            left_label.setAutoDraw(False)
            right_label.setAutoDraw(False)
            trial['ANS'] = keys[0] if keys else -1

            if keys:  # determine correctness
                change = bool(trial['change'])
                change_detected = trial['ANS'] == KEYS[1]
                if change == change_detected:
                    trial['ACC'] = 1
                else:
                    trial['ACC'] = 0
            else:
                trial['ACC'] = -1
            problem_number += 1
            if trial['FEEDB'] == 1:  # show feedback
                if trial['ACC'] == 1:
                    feedb_msg = pos_feedb
                elif trial['ACC'] == 0:
                    feedb_msg = neg_feedb
                else:
                    feedb_msg = no_feedb
                for _ in range(int(float(trial['FEEDBTIME']) * FRAME_RATE)):
                    feedb_msg.draw()
                    check_exit()
                    win.flip()
            if trial['WAIT'] == 0:
                next_trial.draw()
                win.flip()
                event.waitKeys(keyList=KEYS)
            else:
                jitter = int(FRAME_RATE)
                jitter = random.choice(range(-jitter, jitter))
                for _ in range(int((float(trial['WAIT']) * FRAME_RATE) + jitter)):  # show break
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

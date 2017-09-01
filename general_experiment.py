from gooey import Gooey, GooeyParser
from openpyxl import Workbook

__author__ = 'Michal Ociepka'


def save_to_xlsx(tab, filename):
    wb = Workbook()

    # grab the active worksheet
    ws = wb.active

    # Data can be assigned directly to cells
    ws.append(
        ['block_number', 'trial_type', 'elements', 'feedb', 'figure', 'colors', 'change', 'unique', 'all', 'var',
         'wait', 'ftime', 'mtime', 'stime', 'maxtime', 'shint', 'ehint', 'tip', 'tip_time'])

    # TODO: napisac excele
    for idx, trial in enumerate(tab):
        if trial[1] == "instruction":
            trial_with_verification = trial[0:2] + [''] * 15 + trial[-2:]
        else:
            trial_with_verification = trial
        ws.append(trial_with_verification)

    # Save the file
    wb.save(filename + ".xlsx")


@Gooey(language='english',  # Translations configurable via json
       default_size=(850, 700),  # starting size of the GUI
       required_cols=1,  # number of columns in the "Required" section
       optional_cols=4,  # number of columns in the "Optional" section
       )
def generate_trials_gui():
    # General information
    parser = GooeyParser(description='Create_general_experiment')
    parser.add_argument('Number_of_blocks', default=1, action='store', type=int, help='Number')
    parser.add_argument('Number_of_training_trials_in_blocks', default=4, action='store', type=int, help='Number')
    parser.add_argument('Number_of_experiment_trials_in_blocks', default=4, action='store', type=int, help='Number')
    parser.add_argument('File_name', default='experiment', type=str, help='Name of file with not personalized data')
    parser.add_argument('EEG_connected', default='1', choices=['1', '0'], help='Choice')
    parser.add_argument('fNIRS_connected', default='1', choices=['1', '0'], help='Choice')

    parser.add_argument('--Instruction', widget='FileChooser', help='Choose instruction file')
    parser.add_argument('--Instruction_show_time', default=5, action='store', type=int, help='Number')

    # Information about training
    parser.add_argument('--Training_elements', default=2, action='store', type=int, help='Number of elements in matrix')
    parser.add_argument('--Training_feedback', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Training_figure', default='0', choices=['1', '0'], help='Choice')
    parser.add_argument('--Training_colors', default='0', choices=['1', '0'], help='Choice')
    parser.add_argument('--Training_change', default='2', choices=['2', '1', '0'], help='Choice')
    parser.add_argument('--Training_unique', default='0', choices=['1', '0'], help='Choice')
    parser.add_argument('--Training_all', default='1', choices=['1', '0'], help='Choice')
    parser.add_argument('--Training_var', default='ICO', choices=['ICO', 'FRA', 'ROB'], help='Choice')

    parser.add_argument('--Training_wait', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Training_ftime', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Training_mtime', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Training_stime', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Training_maxtime', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Training_shint', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Training_ehint', default=1, action='store', type=int, help='Number')

    parser.add_argument('--Training_tip', widget='FileChooser', help='Choose tip file')
    parser.add_argument('--Training_tip_time', default=4, action='store', type=int, help='Number')

    # Information about experiment
    parser.add_argument('--Experiment_elements', default=2, action='store', type=int,
                        help='Number of elements in matrix')
    parser.add_argument('--Experiment_feedback', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Experiment_figure', default='0', choices=['1', '0'], help='Choice')
    parser.add_argument('--Experiment_colors', default='0', choices=['1', '0'], help='Choice')
    parser.add_argument('--Experiment_change', default='2', choices=['2', '1', '0'], help='Choice')
    parser.add_argument('--Experiment_unique', default='0', choices=['1', '0'], help='Choice')
    parser.add_argument('--Experiment_all', default='1', choices=['1', '0'], help='Choice')
    parser.add_argument('--Experiment_var', default='ICO', choices=['ICO', 'FRA', 'ROB'], help='Choice')

    parser.add_argument('--Experiment_wait', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Experiment_ftime', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Experiment_mtime', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Experiment_stime', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Experiment_maxtime', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Experiment_shint', default=1, action='store', type=int, help='Number')
    parser.add_argument('--Experiment_ehint', default=1, action='store', type=int, help='Number')

    parser.add_argument('--Experiment_tip', widget='FileChooser', help='Choose tip file')
    parser.add_argument('--Experiment_tip_time', default=4, action='store', type=int, help='Number')

    args = parser.parse_args()
    experiment = []

    name = args.Instruction.split('/')[-1]

    for idx in range(args.Number_of_blocks):
        instruction = [idx + 1, 'instruction', name, args.Instruction_show_time]
        experiment.append(instruction)

        for _ in range(args.Number_of_training_trials_in_blocks):
            trial = [idx + 1, 'training',
                     int(args.Training_elements), int(args.Training_feedback), int(args.Training_figure),
                     int(args.Training_colors), int(args.Training_change), int(args.Training_unique),
                     int(args.Training_all), args.Training_var, int(args.Training_wait), int(args.Training_ftime),
                     int(args.Training_mtime), int(args.Training_stime), int(args.Training_maxtime),
                     int(args.Training_shint), int(args.Training_ehint), args.Training_tip, args.Training_tip_time]
            experiment.append(trial)

        for _ in range(args.Number_of_experiment_trials_in_blocks):
            trial = [idx + 1, 'experiment',
                     int(args.Experiment_elements), int(args.Experiment_feedback), int(args.Experiment_figure),
                     int(args.Experiment_colors), int(args.Experiment_change), int(args.Experiment_unique),
                     int(args.Experiment_all), args.Experiment_var, int(args.Experiment_wait),
                     int(args.Experiment_ftime), int(args.Experiment_mtime), int(args.Experiment_stime),
                     int(args.Experiment_maxtime), int(args.Experiment_shint), int(args.Experiment_ehint),
                     args.Experiment_tip, args.Experiment_tip_time]
            experiment.append(trial)

    save_to_xlsx(experiment, args.File_name)


def main():
    generate_trials_gui()


if __name__ == '__main__':
    main()

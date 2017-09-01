import random


class Block:
    def __init__(self, list_of_matrix=None, instruction=None, instruction_time=-1):
        if list_of_matrix is None:
            list_of_matrix = []
        self.list_of_matrix = list_of_matrix
        self.instruction = instruction
        self.instruction_time = instruction_time
        if instruction is not None:
            self.instruction_type = self.instruction.split('.')[-1]
        else:
            self.instruction_type = None

    def info(self):
        list_of_matrix_info = [x.info() for x in self.list_of_matrix]

        informations = {

            "list_of_matrix": list_of_matrix_info,
            "instruction": self.instruction,
            "instruction_time": self.instruction_time,
            "instruction_type": self.instruction_type
        }
        return informations

    def randomize_block(self):
        experiment_elements = [x for x in self.list_of_matrix if x.exp]
        random.shuffle(experiment_elements)
        test_elements = [x for x in self.list_of_matrix if not x.exp]
        random.shuffle(test_elements)
        self.list_of_matrix = test_elements + experiment_elements

    def __repr__(self):
        return str(self.info())

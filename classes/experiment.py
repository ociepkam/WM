import yaml


class Experiment:
    def __init__(self, age, sex, id, list_of_blocks=None, eeg=0, fnirs=0):
        if list_of_blocks is None:
            list_of_blocks = []
        self.list_of_blocks = list_of_blocks
        self.age = int(age)
        self.sex = sex
        self.id = str(id)
        self.eeg = int(eeg)
        self.name = str(id) + sex + str(age)
        self.fnirs = int(fnirs)

    def info(self):
        list_of_blocks_info = [x.info() for x in self.list_of_blocks]

        informations = {
            "list_of_blocks": list_of_blocks_info,
            "age": self.age,
            "sex": self.sex,
            "id": self.id,
            "eeg": self.eeg,
            "name": self.name,
            "fnirs": self.fnirs
        }
        return informations

    def randomize(self):
        for block in self.list_of_blocks:
            block.randomize_block()

    def save(self):
        informations = self.info()
        with open("data/" + self.name + ".yaml", 'w') as save_file:
            save_file.write(yaml.dump(informations))

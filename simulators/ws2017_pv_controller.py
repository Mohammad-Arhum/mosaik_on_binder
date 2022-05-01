import math

import mosaik_api

meta = {
    'models': {
        'Ctrl': {
            'public': True,
            'params': ['target_attr'],
            'attrs': ['P'],
        },
    },
}

class Controller(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(meta)
        self.units = {}

    def init(self, sid, step_size=60):
        self.sid = sid
        self.step_size = step_size

        return self.meta

    def create(self, num, model, **model_params):
        n_units = len(self.units)
        entities = []
        for i in range(n_units, n_units + num):
            eid = 'Ctrl_%d' % i
            self.units[eid] = model_params
            entities.append({'eid': eid, 'type': model, 'rel': []})

        return entities

    def step(self, time, inputs):
        commands = {}
        for eid, attrs in inputs.items():
            measure = 0
            for attr, vals in attrs.items():
                if attr == 'P':
                    for src_id, val in vals.items():
                        target_id = src_id
                        measure += sum(list(vals.values()))

            if measure < 0:
                modifier = ctrl_function(measure)
            else:
                continue

            if eid not in commands:
                commands[eid] = {}
            target_attr = self.units[eid]['target_attr']
            if target_id not in commands[eid]:
                commands[eid][target_id] = {}
            commands[eid][target_id][target_attr] = modifier

        yield self.mosaik.set_data(commands)

        return time + self.step_size


def ctrl_function(measurement):
    modifier = 1 - (1.0 / (1 + math.exp((measurement/7000)+2)))
    return modifier


def main():
    return mosaik_api.start_simulation(Controller(), 'example controller')

if __name__ == '__main__':
    main()

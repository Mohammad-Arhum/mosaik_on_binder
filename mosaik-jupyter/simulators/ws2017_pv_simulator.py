import itertools
import mosaik_api
import arrow

import simulators.ws2017_pv_model as pvpanel

meta = {
    'models': {
        'PV': {
            'public': True,
            'params': [
                'lat',          # latitude of data measurement location [°]
                'area',         # area of panel [m2]
                'efficiency',   # panel efficiency
                'el_tilt',      # panel elevation tilt [°]
                'az_tilt',      # panel azimuth tilt [°]
            ],
            'attrs': ['P',      # output active power [W]
                      'DNI',    # input direct normal insolation [W/m2]
                      'mod']    # input of modifier from ctrl
        },
    },
}

DATE_FORMAT = 'YYYY-MM-DD HH:mm:ss'

class PvAdapter(mosaik_api.Simulator):
    def __init__(self):
        super(PvAdapter, self).__init__(meta)
        self.sid = None

        self.gen_neg = True     # true if generation is negative
        self.cache = None

        self._entities = {}
        self.eid_counters = {}

    def init(self, sid, start_date, step_time=3600, gen_neg=True):
        self.sid = sid
        self.gen_neg = gen_neg

        self.start_date = start_date
        self.step_size = step_time

        return self.meta

    def create(self, num, model, **model_params):
        counter = self.eid_counters.setdefault(model, itertools.count())

        entities = []

        # creation of the entities:
        for i in range(num):
            eid = '%s_%s' % (model, next(counter))

            self._entities[eid] = pvpanel.PVpanel(start_date=self.start_date,
                                                  **model_params)

            entities.append({'eid': eid, 'type': model, 'rel': []})

        return entities

    def step(self, t, inputs):
        self.cache = {}
        for eid, attrs in inputs.items():
            mod = 1
            for attr, vals in attrs.items():
                if attr == 'DNI':
                    dni = list(vals.values())[0] # only one source expected
                    self.cache[eid] = self._entities[eid].power(dni)
                    self._entities[eid].step_time(self.step_size)
                    if self.gen_neg:
                        self.cache[eid] *= (-1)
                elif attr == 'mod':
                    mod = list(vals.values())[0]

            self.cache[eid] *= mod

        return t + self.step_size

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            if eid not in self._entities.keys():
                raise ValueError('Unknown entity ID "%s"' % eid)

            data[eid] = {}
            for attr in attrs:
                if attr != 'P':
                    raise ValueError('Unknown output attribute "%s"' % attr)
                data[eid][attr] = self.cache[eid]

        return data


def main():
    mosaik_api.start_simulation(PvAdapter(), 'PV-Simulator')

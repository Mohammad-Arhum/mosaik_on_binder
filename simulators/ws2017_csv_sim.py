import arrow

import mosaik_api

DATE_FORMAT = 'YYYY-MM-DD HH:mm:ss'

class CSV(mosaik_api.Simulator):
    def __init__(self):
        super().__init__({'models': {}})
        self.start_date = None
        self.datafile = None
        self.next_row = None
        self.modelnames = None
        self.attrs = None
        self.eids = []
        self.cache = None
        
    def init(self, sid, sim_start, datafile):
        self.start_date = arrow.get(sim_start, DATE_FORMAT)
        self.next_date = self.start_date
        
        self. datafile = open(datafile)
        self.modelname = next(self.datafile).strip()
        
        attrs = next(self.datafile).strip().split(',')[1:]
        for i, attr in enumerate(attrs):
            try:
                attr = attr[:attr.index('#')]
            except ValueError:
                pass
            attrs[i] = attr.strip()
        self.attrs = attrs

        self.meta['models'][self.modelname] = {
            'public': True,
            'params': [],
            'attrs': attrs,
        }

        # Check start date
        self._read_next_row()
        if self.start_date < self.next_row[0]:
            raise ValueError('Start date "%s" not in CSV file.' %
                             self.start_date.format(DATE_FORMAT))
        while self.start_date > self.next_row[0]:
            self._read_next_row()
            if self.next_row is None:
                raise ValueError('Start date "%s" not in CSV file.' %
                                 self.start_date.format(DATE_FORMAT))

        return self.meta

    def create(self, num, model):
        if model != self.modelname:
            raise ValueError('Invalid model "%s" % model')

        start_idx = len(self.eids)
        entities = []
        for i in range(num):
            eid = '%s_%s' % (model, i + start_idx)
            entities.append({
                'eid': eid,
                'type': model,
                'rel': [],
            })
            self.eids.append(eid)
        return entities

    def step(self, time, inputs=None):
        data = self.next_row
        if data is None:
            raise IndexError('End of CSV file reached.')

        # Chacke date
        date = data[0]
        expected_date = self.start_date.replace(seconds=time)
        if date != expected_date:
            raise IndexError('Wrong date "%s", expected "%s"' % (
                date.format(DATE_FORMAT),
                expected_date.format(DATE_FORMAT)))

        # Put data into the cache for get_data() calls
        self.cache = {}
        for eid in self.eids:
            self.cache[eid] = {}
            for attr, val in zip(self.attrs, data[1:]):
                self.cache[eid][attr] = float(val)

        # Modify data if modifier is given
        if inputs is not None:
            for eid, attrs in inputs.items():
                for attr, vals in attrs.items():
                    modifier = list(vals.values())[0]
                    if modifier >= 0:
                        self.cache[eid][attr] *= modifier

        self._read_next_row()
        if self.next_row is not None:
            return time + (self.next_row[0].timestamp - date.timestamp)
        else:
            return float('inf')

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            if eid not in self.eids:
                raise ValueError('Unknown entity ID "%s"' % eid)

            data[eid] = {}
            for attr in attrs:
                data[eid][attr] = self.cache[eid][attr]

        return data

    def _read_next_row(self):
        try:
            self.next_row = next(self.datafile).strip().split(',')
            self.next_row[0] = arrow.get(self.next_row[0], DATE_FORMAT)
        except StopIteration:
            self.next_row = None


def main():
    return mosaik_api.start_simulation(CSV(), 'mosaik-csv simulator')

if __name__ == '__main__':
    main()
    

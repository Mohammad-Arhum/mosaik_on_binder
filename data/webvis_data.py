etypes = {
    'RefBus': {
        'cls': 'refbus',
        'attr': 'P',
        'unit': 'P [W]',
        'default': 0,
        'min': 0,
        'max': 30000,
    },
    'PQBus': {
        'cls': 'pqbus',
        'attr': 'Vm',
        'unit': 'U [V]',
        'default': 230,
        'min': 0.99 * 230,
        'max': 1.01 * 230,
    },
    'House': {
        'cls': 'load',
        'attr': 'P',
        'unit': 'P [W]',
        'default': 0,
        'min': 0,
        'max': 3000,
    },
    'PV': {
        'cls': 'gen',
        'attr': 'P',
        'unit': 'P [W]',
        'default': 0,
        'min': -10000,
        'max': 0,
    },
}

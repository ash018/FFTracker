
DOMAIN_CONF = {
    'Sales': 0,
    'Delivery Service': 1,
    'Installation/Maintenance/Repair': 2,
    'Rent-a-car/Ride sharing': 3,
    'Insurance': 4,
    'Others': 5,
    'Sales(Pharma)': 6,
}

DOMAIN_CHOICES = tuple((value, key) for key, value in DOMAIN_CONF.items())

SURVEY_CONTAINER = 'Survey'
SURVEY_KEYS = 'survey_keys'

DEMAND_CONTAINER = 'Demands'
DEMAND_TAG_LIST = ['Item', 'Quantity']
DEMAND_KEYS = 'demand_keys'

PAYMENT_CONTAINER = 'Payment'
COST_CONTAINER = 'Cost'
DESCRIPTION_CONTAINER = 'Description'
SHOP_PERSON_CONTAINER = 'Shop/Person'
BARCODE_CONTAINER = 'Barcode'


TASK_TYPE = {
    0: {
        'Demand Collection': {
            SHOP_PERSON_CONTAINER: '',
            DEMAND_KEYS: DEMAND_TAG_LIST,
            DEMAND_CONTAINER: []
        },
        'Payment Collection': {
            SHOP_PERSON_CONTAINER: '',
            PAYMENT_CONTAINER: 0,
        },
        'Goods Delivery': {
            SHOP_PERSON_CONTAINER: '',
            PAYMENT_CONTAINER: 0,
        },
        'Feedback/Survey': {
            SURVEY_KEYS: [],
            SURVEY_CONTAINER: {}
        },
        'Lead Generation': {
            'Contact': '',
            'Details': '',
            'Conversion %': 0

        }
    },
    1: {
        'Refueling': {
            'Fuel (L)': 0,
            COST_CONTAINER: 0,
        },
        'Rent Collection': {
            'Rent': 0,
            'Contact': '',
        },
        'Journey': {
            'Distance (Km)': 0,
            PAYMENT_CONTAINER: 0,
        },
        'Maintenance/Repair': {
            DESCRIPTION_CONTAINER: '',
            'Workshop': 0,
            COST_CONTAINER: 0
        }

    },
    2: {
        'Installation': {
            PAYMENT_CONTAINER: 0,
            DESCRIPTION_CONTAINER: '',
        },
        'Commissioning': {
            PAYMENT_CONTAINER: 0,
            DESCRIPTION_CONTAINER: '',
        },
        'Repair': {
            PAYMENT_CONTAINER: 0,
            DESCRIPTION_CONTAINER: '',
        },
        'Maintenance': {
            PAYMENT_CONTAINER: 0,
        },
        'Feasibility visit': {
            DESCRIPTION_CONTAINER: '',
        }

    },

    3: {
        'Pickup': {
            SHOP_PERSON_CONTAINER: '',
            BARCODE_CONTAINER: [],
        },
        'Drop off': {
            SHOP_PERSON_CONTAINER: '',
            BARCODE_CONTAINER: [],
        },
        'Payment Collection': {
            SHOP_PERSON_CONTAINER: '',
            PAYMENT_CONTAINER: 0,
        },
        'Refueling': {
            'Fuel (L)': 0,
            COST_CONTAINER: 0,
        },
        'Maintenance': {
            DESCRIPTION_CONTAINER: '',
            'Workshop': 0,
            COST_CONTAINER: 0
        }

    },
    4: {
        'Client Visit': {
            'Client Name': '',
            DESCRIPTION_CONTAINER: '',
        },

        'Feedback/Survey': {
            SURVEY_KEYS: [],
            SURVEY_CONTAINER: {}
        },
        'Lead Generation': {
            'Contact': '',
            'Detail': '',
            'Conversion %': 0

        }
    },
    5: {
        'Customized Task': {
            DESCRIPTION_CONTAINER: '',
            SHOP_PERSON_CONTAINER: '',
            PAYMENT_CONTAINER: 0,
            BARCODE_CONTAINER: [],
            SURVEY_KEYS: [],
            SURVEY_CONTAINER: {},
            DEMAND_KEYS: DEMAND_TAG_LIST,
            DEMAND_CONTAINER: []
        }

    },

    6: {
        'Payment Collection': {
            SHOP_PERSON_CONTAINER: '',
            PAYMENT_CONTAINER: 0,
        },
        'Goods Delivery': {
            SHOP_PERSON_CONTAINER: '',
            PAYMENT_CONTAINER: 0,
        },
        'Doctor Visit': {
            'Doctor': '',
            DESCRIPTION_CONTAINER: '',

        },
        'Pharmacy Visit': {
            'Pharmacy': '',
            DEMAND_KEYS: DEMAND_TAG_LIST,
            DEMAND_CONTAINER: []
        },

        'Feedback/Survey': {
            SURVEY_KEYS: [],
            SURVEY_CONTAINER: {}
        },
    },
}


def get_other_templates(manager):
    templates = {}
    for key, val in TASK_TYPE.items():
        if key != manager.domain:
            templates.update(val)
    return templates

from apps.common.config import get_choices

BILL_CYCLE = 30

PREMIUM_STORAGE = 30

MONTHLY_AVG_TASK = 150
MONTHLY_AVG_TASK_PREMIUM = 200

FREE_AGENT = 10
FREE_TASK = FREE_AGENT * MONTHLY_AVG_TASK

EXTRA_TASK_PRICE = 0.5

BILL_TYPES = {
    'New subscription': 1,
    'New agents': 2,
    'Extra tasks': 3,
    # 'Package Change': 4,
}

BILL_CHOICES = get_choices(BILL_TYPES)

PACKAGE_IDS = {
    'None': 0,
    'Attendance': 1,
    'Tracking': 2,
    'Full Suite': 3,
    'Task Management': 4,
}

PACKAGE_CHOICES = get_choices(PACKAGE_IDS)

PACKAGE_INFO = {
    1: {
        'title': 'Attendance Management',
        'price': 40.0,
        'package_id': 1,
        'has_attendance': True,
        'has_agent_tracking': False,
        'has_messaging': False,
        'has_task_management': False,
    },
    2: {
        'title': 'Employee Tracking & Attendance',
        'price': 100.0,
        'package_id': 2,
        'has_attendance': True,
        'has_agent_tracking': True,
        'has_messaging': True,
        'has_task_management': False,
    },
    3: {
        'title': 'Full Suite',
        'price': 150.0,
        'package_id': 3,
        'has_attendance': True,
        'has_agent_tracking': True,
        'has_messaging': True,
        'has_task_management': True,
    },

    4: {
        'title': 'Attendance & Task Management',
        'price': 120.0,
        'package_id': 4,
        'has_attendance': True,
        'has_agent_tracking': False,
        'has_messaging': True,
        'has_task_management': True,
    },
}


PAYMENT_STATUS_DICT = {
    'Initiated': 0,
    'Created': 1,
    'Successful': 2
}


PAYMENT_STATUS_CHOICES = get_choices(PAYMENT_STATUS_DICT)

CURRENCY_DICT = {
    'BDT': 1,
    'USD': 2,
    'EUR': 3
}

GATEWAYS = {
    'BKASH': 1,
    'SSL': 2,
    'IPAY': 3
}

GATEWAY_CHOICES = get_choices(GATEWAYS)

CURRENCY_CHOICE = get_choices(CURRENCY_DICT)


USAGE_DICT = {
    'active': 1,
    'expired': 2,
    'suspended': 3
}

USAGE_CHOICE = get_choices(USAGE_DICT)

BILL_URLS = {
    'get_usage': 'usage/',
    'send_mail':'mail/send',
    'payment_create_internal': 'payment/internal/',
    'bkash_template': 'bkash/template/',
    'bkash_success_template': 'bkash/success/template/',
    'bkash_fail_template': 'bkash/fail/template/',
    'create_payment': 'payment/create/',
    'execute_payment': 'payment/execute/',

    'apply_coupon': 'coupon/',
    'new_subscription_bill': 'bill/subscription/',
    'extra_tasks_bill': 'bill/tasks/',
    'new_agents_bill': 'bill/agents/',
    'set_package': 'manager/premium/',

    'execute_payment_ssl': 'ssl/payment/execute/',
    'ssl_redirect': 'ssl/redirect/',
    'ssl_create': 'ssl/payment/create/',
}

BKASH_CONF = {
    "body": {
        "app_key": "ld8j9cbehq5850nsg9me5po14",
        "app_secret": "7glp8uerfh8cjde0i2rtuarhov9ok0affgf1uf34c66e8nnohif"
    },
    "headers": {
        "username": "DINGITECHNOLOGIESLIMITED",
        "password": "D@7iLt3c16k"
    },
    # "sandbox_checkout_url": "https://checkout.sandbox.bka.sh/v1.0.0-beta/checkout",
    "live_checkout_url": "https://checkout.pay.bka.sh/v1.0.0-beta/checkout"

}

SSL_REDIRECT_URL = 'https://tw.api.dingi.work/v0/billing/ssl/redirect/'

SSL_CONF = {
    "secure_validator_url_ssl": "https://securepay.sslcommerz.com/validator/api/validationserverAPI.php",
    "secure_create_url_ssl": "https://securepay.sslcommerz.com/gwprocess/v3/api.php",
    'store_id': 'dingitechnologieslimitedlive',
    'store_passwd': '5B962941A53B996973',

    "sandbox_validator_url_ssl": "https://sanbox.sslcommerz.com/validator/api/validationserverAPI.php",
    "sandbox_create_url_ssl": "https://sandbox.sslcommerz.com/gwprocess/v3/api.php",
    'sandbox_store_id': 'dingi5b4b0604bd021',
    'sandbox_store_passwd': 'dingi5b4b0604bd021@ssl',
}


BKASH_ERRORS = {
    '2001': 'Invalid App Key',

    '2002': 'Invalid Payment ID',

    '2003': 'Process failed',

    '2004': 'Invalid firstPaymentDate',

    '2005': 'Invalid frequency',

    '2006': 'Invalid amount',

    '2007': 'Invalid currency',

    '2008': 'Invalid intent',

    '2009': 'Invalid Wallet',

    '2010': 'Invalid OTP',

    '2011': 'Invalid PIN',

    '2012': 'Invalid Receiver MSISDN',

    '2013': 'Resend Limit Exceeded',

    '2014': 'Wrong PIN',

    '2015': 'Wrong PIN count exceeded',

    '2016': 'Wrong verification code',

    '2017': 'Wrong verification limit exceeded',

    '2018': 'OTP verification time expired',

    '2019': 'PIN verification time expired',

    '2020': 'Exception Occurred',

    '2021': 'Invalid Mandate ID',

    '2022': 'The mandate does not exist',

    '2023': 'Insufficient Balance',

    '2024': 'Exception occurred',

    '2025': 'Invalid request body',

    '2026': 'The reversal amount cannot be greater than the original transaction amount',

    '2027': 'The mandate corresponding to the payer reference number already exists and cannot be created again',

    '2028': 'Reverse failed because the transaction serial number does not exist',

    '2029': 'Duplicate for all transactions',

    '2030': 'Invalid mandate request type',

    '2031': 'Invalid merchant invoice number',

    '2032': 'Invalid transfer type',

    '2033': 'Transaction not found',

    '2034': 'The transaction cannot be reversed because the original transaction has been reversed',

    '2035': 'Reverse failed because the initiator has no permission to reverse the transaction',

    '2036': 'The direct debit mandate is not in Active state',

    '2037': 'The account of the debit party is in a state which prohibits execution of this transaction',

    '2038': 'Debit party identity tag prohibits execution of this transaction',

    '2039': 'The account of the credit party is in a state which prohibits execution of this transaction',

    '2040': 'Credit party identity tag prohibits execution of this transaction',

    '2041': 'Credit party identity is in a state which does not support the current service',

    '503': 'System is undergoing maintenance. Please try again later'
}


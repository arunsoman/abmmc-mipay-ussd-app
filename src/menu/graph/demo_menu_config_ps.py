config = {
    "root_validation_gate": {
        "type": "validation_gate",
        "prompt": "خپل د مای پیسې پټ نوم ولیکئ:\n",
        "valid_pin": "123456",
        "max_attempts": 3,
        "validation_url": "http://localhost:8080/ussd/customer/USSDlogin",
        "on_success": {"target_menu": "main_menu"},
        "on_failure": {"target_menu": "exit_node"}
    },
    "main_menu": {
        "type": "menu_navigation",
        "prompt": "اصلي مینو: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "زما پیسې", "target_menu": "my_money_menu"},
            {"key": "2", "label": "بانکونه", "target_menu": "banks_menu"},
            {"key": "3", "label": "تادیه", "target_menu": "payment_menu"},
            {"key": "4", "label": "بلونه", "target_menu": "bills_menu"},
            {"key": "5", "label": "ټاپ-اپ", "target_menu": "topup_menu"},
            {"key": "6", "label": "منظورۍ", "target_menu": "approvals_menu"}
        ],
        "transitions": {
            "9": "root_validation_gate",
            "0": "exit_node"
        }
    },
    "my_money_menu": {
        "type": "menu_navigation",
        "prompt": "زما پیسې: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "بیلانس", "target_menu": "balance_check"},
            {"key": "2", "label": "پټ نوم بدل کړئ", "target_menu": "change_pin"},
            {"key": "3", "label": "معامله", "target_menu": "transaction_menu"},
            {"key": "4", "label": "لیږد", "target_menu": "transfer_menu"},
            {"key": "5", "label": "ژبه", "target_menu": "language_menu"}
        ],
        "transitions": {
            "9": "main_menu",
            "0": "exit_node"
        }
    },
    "balance_check": {
        "type": "cache_post",
        "prompt": "ستاسو بیلانس {balance} افغانۍ دی\nوضعیت: {status}\nد بیرته تګ لپاره 9 او د وتلو لپاره 0 فشار ورکړئ",
        "cache_params": {
            "auth_token": "token",
            "msisdn": "phone_number"
        },
        "action_url": "http://localhost:8080/ts/api/transaction-services/CurrentBalance",
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        }
    },
    "change_pin": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل زوړ د مای پیسې پټ نوم ولیکئ (6 عددونه):\n",
                "input_key": "old_pin",
                "validation": {"regex": "^\\d{6}$"}
            },
            {
                "prompt": "خپل نوی د مای پیسې پټ نوم ولیکئ (6 عددونه):\n",
                "input_key": "new_pin",
                "validation": {"regex": "^\\d{6}$"}
            },
            {
                "prompt": "خپل نوی پټ نوم تایید کړئ:\n",
                "input_key": "confirm_pin",
                "validation": {"regex": "^\\d{6}$"}
            }
        ],
        "confirmation_prompt": "پټ نوم {new_pin} ته بدل کړی؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/pwd/update",
        "params": {},
        "success_prompt": "پټ نوم په بریالیتوب سره بدل شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        }
    },
    "transaction_menu": {
        "type": "single_input_action",
        "prompt": "د معاملاتو تاریخ لیدو لپاره خپل پټ نوم ولیکئ:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{6}$"},
        "confirmation_prompt": "د معاملاتو تاریخ وګورئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/ts/api/transaction-services/getFilteredHistory",
        "params": {},
        "success_prompt": "د معاملاتو تاریخ: {transactions}\nوضعیت: {status}",
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        }
    },
    "transfer_menu": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ترلاسه کونکي د تلیفون شمیره ولیکئ:\n",
                "input_key": "phone_number",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "{phone_number} ته {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        }
    },
    "language_menu": {
        "type": "menu_navigation",
        "prompt": "ژبه وټاکئ:",
        "options": [
            {"key": "1", "label": "دري", "target_menu": "my_money_menu"},
            {"key": "2", "label": "پښتو", "target_menu": "my_money_menu"},
            {"key": "3", "label": "انګلیسي", "target_menu": "my_money_menu"}
        ],
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        }
    },
    "banks_menu": {
        "type": "menu_navigation",
        "prompt": "بانکونه: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "میوند بانک", "target_menu": "maiwand_bank"},
            {"key": "2", "label": "نوی کابل بانک", "target_menu": "nkb_bank"},
            {"key": "3", "label": "عزیزي بانک", "target_menu": "azizi_bank"},
            {"key": "4", "label": "نور", "target_menu": "other_bank"},
            {"key": "5", "label": "AUB", "target_menu": "aub_bank"},
            {"key": "6", "label": "BMA", "target_menu": "bma_bank"},
            {"key": "7", "label": "غضنفر بانک", "target_menu": "ghazanfar_bank"}
        ],
        "transitions": {
            "9": "main_menu",
            "0": "exit_node"
        }
    },
    "maiwand_bank": {
        "type": "menu_navigation",
        "prompt": "میوند بانک: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "د بانک بیلانس", "target_menu": "maiwand_balance"},
            {"key": "2", "label": "بانک سره نښلول", "target_menu": "maiwand_link"},
            {"key": "3", "label": "بانک ته لیږد", "target_menu": "maiwand_transfer_to"},
            {"key": "4", "label": "د بانک څخه لیږد", "target_menu": "maiwand_transfer_from"}
        ],
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "maiwand_balance": {
        "type": "single_input_action",
        "prompt": "د میوند بانک بیلانس چک کولو لپاره خپل پټ نوم ولیکئ:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{4}$"},
        "confirmation_prompt": "د میوند بانک بیلانس چک کړی؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/bank_balance",
        "params": {"bank": "Maiwand"},
        "success_prompt": "د میوند بانک بیلانس: {balance} افغانۍ\nوضعیت: {status}",
        "transitions": {
            "9": "maiwand_bank",
            "0": "exit_node"
        }
    },
    "maiwand_link": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل د میوند بانک حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "خپل د بانک پټ نوم ولیکئ:\n",
                "input_key": "bank_pin",
                "validation": {"regex": "^\\d{4}$"}
            }
        ],
        "confirmation_prompt": "د میوند بانک حساب {account_id} سره ونښلول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/link_bank",
        "params": {"bank": "Maiwand"},
        "success_prompt": "حساب ونښلول شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "maiwand_bank",
            "0": "exit_node"
        }
    },
    "maiwand_transfer_to": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ترلاسه کونکي حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "د میوند بانک حساب {account_id} ته {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/transfer_bank",
        "params": {"bank": "Maiwand"},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "maiwand_bank",
            "0": "exit_node"
        }
    },
    "maiwand_transfer_from": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل د میوند بانک حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "د میوند بانک حساب {account_id} څخه {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/transfer_from_bank",
        "params": {"bank": "Maiwand"},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "maiwand_bank",
            "0": "exit_node"
        }
    },
    "nkb_bank": {
        "type": "menu_navigation",
        "prompt": "نوی کابل بانک: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "د بانک بیلانس", "target_menu": "nkb_balance"},
            {"key": "2", "label": "بانک سره نښلول", "target_menu": "nkb_link"},
            {"key": "3", "label": "بانک ته لیږد", "target_menu": "nkb_transfer_to"},
            {"key": "4", "label": "د بانک څخه لیږد", "target_menu": "nkb_transfer_from"}
        ],
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "nkb_balance": {
        "type": "single_input_action",
        "prompt": "د نوي کابل بانک بیلانس چک کولو لپاره خپل پټ نوم ولیکئ:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{4}$"},
        "confirmation_prompt": "د نوي کابل بانک بیلانس چک کړی؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/bank_balance",
        "params": {"bank": "NKB"},
        "success_prompt": "د نوي کابل بانک بیلانس: {balance} افغانۍ\nوضعیت: {status}",
        "transitions": {
            "9": "nkb_bank",
            "0": "exit_node"
        }
    },
    "nkb_link": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل د نوي کابل بانک حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "خپل د بانک پټ نوم ولیکئ:\n",
                "input_key": "bank_pin",
                "validation": {"regex": "^\\d{4}$"}
            }
        ],
        "confirmation_prompt": "د نوي کابل بانک حساب {account_id} سره ونښلول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/link_bank",
        "params": {"bank": "NKB"},
        "success_prompt": "حساب ونښلول شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "nkb_bank",
            "0": "exit_node"
        }
    },
    "nkb_transfer_to": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ترلاسه کونکي حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "د نوي کابل بانک حساب {account_id} ته {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/transfer_bank",
        "params": {"bank": "NKB"},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "nkb_bank",
            "0": "exit_node"
        }
    },
    "nkb_transfer_from": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل د نوي کابل بانک حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "د نوي کابل بانک حساب {account_id} څخه {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/transfer_from_bank",
        "params": {"bank": "NKB"},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "nkb_bank",
            "0": "exit_node"
        }
    },
    "azizi_bank": {
        "type": "menu_navigation",
        "prompt": "عزیزي بانک: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "د بانک بیلانس", "target_menu": "azizi_balance"},
            {"key": "2", "label": "بانک سره نښلول", "target_menu": "azizi_link"},
            {"key": "3", "label": "بانک ته لیږد", "target_menu": "azizi_transfer_to"},
            {"key": "4", "label": "د بانک څخه لیږد", "target_menu": "azizi_transfer_from"}
        ],
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "azizi_balance": {
        "type": "single_input_action",
        "prompt": "د عزیزي بانک بیلانس چک کولو لپاره خپل پټ نوم ولیکئ:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{4}$"},
        "confirmation_prompt": "د عزیزي بانک بیلانس چک کړی؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/bank_balance",
        "params": {"bank": "Azizi"},
        "success_prompt": "د عزیزي بانک بیلانس: {balance} افغانۍ\nوضعیت: {status}",
        "transitions": {
            "9": "azizi_bank",
            "0": "exit_node"
        }
    },
    "azizi_link": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل د عزیزي بانک حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "خپل د بانک پټ نوم ولیکئ:\n",
                "input_key": "bank_pin",
                "validation": {"regex": "^\\d{4}$"}
            }
        ],
        "confirmation_prompt": "د عزیزي بانک حساب {account_id} سره ونښلول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/link_bank",
        "params": {"bank": "Azizi"},
        "success_prompt": "حساب ونښلول شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "azizi_bank",
            "0": "exit_node"
        }
    },
    "azizi_transfer_to": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ترلاسه کونکي حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "د عزیزي بانک حساب {account_id} ته {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/transfer_bank",
        "params": {"bank": "Azizi"},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "azizi_bank",
            "0": "exit_node"
        }
    },
    "azizi_transfer_from": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل د عزیزي بانک حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "د عزیزي بانک حساب {account_id} څخه {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/transfer_from_bank",
        "params": {"bank": "Azizi"},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "azizi_bank",
            "0": "exit_node"
        }
    },
    "other_bank": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د بانک نوم ولیکئ:\n",
                "input_key": "bank_name",
                "validation": {"regex": "^[A-Za-z ]+$"}
            },
            {
                "prompt": "د حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            }
        ],
        "confirmation_prompt": "د {bank_name} حساب {account_id} سره ونښلول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/link_other_bank",
        "params": {},
        "success_prompt": "حساب ونښلول شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "aub_bank": {
        "type": "menu_navigation",
        "prompt": "AUB بانک: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "د بانک بیلانس", "target_menu": "aub_balance"},
            {"key": "2", "label": "بانک سره نښلول", "target_menu": "aub_link"},
            {"key": "3", "label": "بانک ته لیږد", "target_menu": "aub_transfer_to"},
            {"key": "4", "label": "د بانک څخه لیږد", "target_menu": "aub_transfer_from"}
        ],
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "aub_balance": {
        "type": "single_input_action",
        "prompt": "د AUB بانک بیلانس چک کولو لپاره خپل پټ نوم ولیکئ:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{4}$"},
        "confirmation_prompt": "د AUB بانک بیلانس چک کړی؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/bank_balance",
        "params": {"bank": "AUB"},
        "success_prompt": "د AUB بانک بیلانس: {balance} افغانۍ\nوضعیت: {status}",
        "transitions": {
            "9": "aub_bank",
            "0": "exit_node"
        }
    },
    "aub_link": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل د AUB بانک حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "خپل د بانک پټ نوم ولیکئ:\n",
                "input_key": "bank_pin",
                "validation": {"regex": "^\\d{4}$"}
            }
        ],
        "confirmation_prompt": "د AUB بانک حساب {account_id} سره ونښلول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/link_bank",
        "params": {"bank": "AUB"},
        "success_prompt": "حساب ونښلول شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "aub_bank",
            "0": "exit_node"
        }
    },
    "aub_transfer_to": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ترلاسه کونکي حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "د AUB بانک حساب {account_id} ته {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"bank": "AUB"},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "aub_bank",
            "0": "exit_node"
        }
    },
    "aub_transfer_from": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل د AUB بانک حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "د AUB بانک حساب {account_id} څخه {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"bank": "AUB"},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "aub_bank",
            "0": "exit_node"
        }
    },
    "bma_bank": {
        "type": "menu_navigation",
        "prompt": "BMA بانک: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "د بانک بیلانس", "target_menu": "bma_balance"},
            {"key": "2", "label": "بانک سره نښلول", "target_menu": "bma_link"},
            {"key": "3", "label": "بانک ته لیږد", "target_menu": "bma_transfer_to"},
            {"key": "4", "label": "د بانک څخه لیږد", "target_menu": "bma_transfer_from"}
        ],
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "bma_balance": {
        "type": "single_input_action",
        "prompt": "د BMA بانک بیلانس چک کولو لپاره خپل پټ نوم ولیکئ:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{4}$"},
        "confirmation_prompt": "د BMA بانک بیلانس چک کړی؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/bank_balance",
        "params": {"bank": "BMA"},
        "success_prompt": "د BMA بانک بیلانس: {balance} افغانۍ\nوضعیت: {status}",
        "transitions": {
            "9": "bma_bank",
            "0": "exit_node"
        }
    },
    "bma_link": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل د BMA بانک حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "خپل د بانک پټ نوم ولیکئ:\n",
                "input_key": "bank_pin",
                "validation": {"regex": "^\\d{4}$"}
            }
        ],
        "confirmation_prompt": "د BMA بانک حساب {account_id} سره ونښلول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/link_bank",
        "params": {"bank": "BMA"},
        "success_prompt": "حساب ونښلول شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "bma_bank",
            "0": "exit_node"
        }
    },
    "bma_transfer_to": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ترلاسه کونکي حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "د BMA بانک حساب {account_id} ته {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/transfer_bank",
        "params": {"bank": "BMA"},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "bma_bank",
            "0": "exit_node"
        }
    },
    "bma_transfer_from": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل د BMA بانک حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "د BMA بانک حساب {account_id} څخه {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/transfer_from_bank",
        "params": {"bank": "BMA"},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "bma_bank",
            "0": "exit_node"
        }
    },
    "ghazanfar_bank": {
        "type": "menu_navigation",
        "prompt": "غضنفر بانک: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "د بانک بیلانس", "target_menu": "ghazanfar_balance"},
            {"key": "2", "label": "بانک سره نښلول", "target_menu": "ghazanfar_link"},
            {"key": "3", "label": "بانک ته لیږد", "target_menu": "ghazanfar_transfer_to"},
            {"key": "4", "label": "د بانک څخه لیږد", "target_menu": "ghazanfar_transfer_from"}
        ],
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "ghazanfar_balance": {
        "type": "single_input_action",
        "prompt": "د غضنفر بانک بیلانس چک کولو لپاره خپل پټ نوم ولیکئ:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{4}$"},
        "confirmation_prompt": "د غضنفر بانک بیلانس چک کړی؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/bank_balance",
        "params": {"bank": "Ghazanfar"},
        "success_prompt": "د غضنفر بانک بیلانس: {balance} افغانۍ\nوضعیت: {status}",
        "transitions": {
            "9": "ghazanfar_bank",
            "0": "exit_node"
        }
    },
    "ghazanfar_link": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل د غضنفر بانک حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "خپل د بانک پټ نوم ولیکئ:\n",
                "input_key": "bank_pin",
                "validation": {"regex": "^\\d{4}$"}
            }
        ],
        "confirmation_prompt": "د غضنفر بانک حساب {account_id} سره ونښلول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/link_bank",
        "params": {"bank": "Ghazanfar"},
        "success_prompt": "حساب ونښلول شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "ghazanfar_bank",
            "0": "exit_node"
        }
    },
    "ghazanfar_transfer_to": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ترلاسه کونکي حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "د غضنفر بانک حساب {account_id} ته {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"bank": "Ghazanfar"},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "ghazanfar_bank",
            "0": "exit_node"
        }
    },
    "ghazanfar_transfer_from": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "خپل د غضنفر بانک حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د لیږد اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "د غضنفر بانک حساب {account_id} څخه {amount} افغانۍ ولیږدول شي؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"bank": "Ghazanfar"},
        "success_prompt": "لیږد بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "ghazanfar_bank",
            "0": "exit_node"
        }
    },
    "payment_menu": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د تادیه کونکي حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د تادیې وړ اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "{account_id} حساب ته {amount} افغانۍ تادیه کړی؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/payment",
        "params": {},
        "success_prompt": "تادیه بشپړه شوه\nرسید: {receipt_number}",
        "transitions": {
            "9": "main_menu",
            "0": "exit_node"
        }
    },
    "bills_menu": {
        "type": "menu_navigation",
        "prompt": "بلونه: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "برشنا شرکت", "target_menu": "dabs_bill"},
            {"key": "2", "label": "ډیلایټ", "target_menu": "delight_bill"}
        ],
        "transitions": {
            "9": "main_menu",
            "0": "exit_node"
        }
    },
    "dabs_bill": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د برشنا شرکت حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د بل اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 10}
            }
        ],
        "confirmation_prompt": "د {account_id} حساب لپاره {amount} افغانۍ تادیه کړی؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"provider": "DABS"},
        "success_prompt": "تادیه پروسس شوه\nرسید: {receipt_number}",
        "transitions": {
            "9": "bills_menu",
            "0": "exit_node"
        }
    },
    "delight_bill": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ډیلایټ حساب آی ډي ولیکئ:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د بل اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 10}
            }
        ],
        "confirmation_prompt": "د {account_id} حساب لپاره {amount} افغانۍ تادیه کړی؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/pay_bill",
        "params": {"provider": "Delight"},
        "success_prompt": "تادیه پروسس شوه\nرسید: {receipt_number}",
        "transitions": {
            "9": "bills_menu",
            "0": "exit_node"
        }
    },
    "topup_menu": {
        "type": "menu_navigation",
        "prompt": "ټاپ-اپ: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "ځان ته ټاپ-اپ", "target_menu": "topup_self"},
            {"key": "2", "label": "نورو ته ټاپ-اپ", "target_menu": "topup_others"},
            {"key": "3", "label": "د ټاپ-اپ بنډلونه واخلئ", "target_menu": "bundles_menu"}
        ],
        "transitions": {
            "9": "main_menu",
            "0": "exit_node"
        }
    },
    "topup_self": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ټاپ-اپ اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "خپل حساب ته {amount} افغانۍ ټاپ-اپ کړی؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"type": "self"},
        "success_prompt": "ټاپ-اپ بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "topup_menu",
            "0": "exit_node"
        }
    },
    "topup_others": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د منزل شمیره ولیکئ:\n",
                "input_key": "phone_number",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "د ټاپ-اپ اندازه ولیکئ (افغانۍ):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "{phone_number} ته {amount} افغانۍ ټاپ-اپ کړی؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"type": "others"},
        "success_prompt": "ټاپ-اپ بشپړ شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "topup_menu",
            "0": "exit_node"
        }
    },
    "bundles_menu": {
        "type": "menu_navigation",
        "prompt": "بنډلونه: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "د ځان لپاره بنډل", "target_menu": "self_bundle"},
            {"key": "2", "label": "د نورو لپاره بنډل", "target_menu": "others_bundle"}
        ],
        "transitions": {
            "9": "topup_menu",
            "0": "exit_node"
        }
    },
    "self_bundle": {
        "type": "menu_navigation",
        "prompt": "د ځان لپاره بنډل: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "د ډیټا بنډل", "target_menu": "data_bundle"},
            {"key": "2", "label": "د غږ بنډل", "target_menu": "voice_bundle"}
        ],
        "transitions": {
            "9": "bundles_menu",
            "0": "exit_node"
        }
    },
    "data_bundle": {
        "type": "menu_navigation",
        "prompt": "د ډیټا بنډل: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "280 افغانۍ: 2.5 جي بي", "target_menu": "data_280"},
            {"key": "2", "label": "450 افغانۍ: 6 جي بي", "target_menu": "data_450"},
            {"key": "3", "label": "670 افغانۍ: 10 جي بي", "target_menu": "data_670"},
            {"key": "4", "label": "1220 افغانۍ: 22.2 جي بي", "target_menu": "data_1220"}
        ],
        "transitions": {
            "9": "self_bundle",
            "0": "exit_node"
        }
    },
    "data_280": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د 280 افغانیو په بدل کې د 2.5 جي بي بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د 280 افغانیو په بدل کې د 2.5 جي بي بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"bundle_type": "DATA", "option": 0},
        "success_prompt": "د 280 افغانیو 2.5 جي بي بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        }
    },
    "data_450": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د 450 افغانیو په بدل کې د 6 جي بي بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د 450 افغانیو په بدل کې د 6 جي بي بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 1},
        "success_prompt": "د 450 افغانیو 6 جي بي بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        }
    },
    "data_670": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د 670 افغانیو په بدل کې د 10 جي بي بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د 670 افغانیو په بدل کې د 10 جي بي بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 2},
        "success_prompt": "د 670 افغانیو 10 جي بي بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        }
    },
    "data_1220": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د 1220 افغانیو په بدل کې د 22.2 جي بي بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د 1220 افغانیو په بدل کې د 22.2 جي بي بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 3},
        "success_prompt": "د 1220 افغانیو 22.2 جي بي بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        }
    },
    "voice_bundle": {
        "type": "menu_navigation",
        "prompt": "د غږ بنډل: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "50 افغانۍ: 200 دقیقې", "target_menu": "voice_50"},
            {"key": "2", "label": "100 افغانۍ: 550 دقیقې", "target_menu": "voice_100"},
            {"key": "3", "label": "200 افغانۍ: 1000 دقیقې", "target_menu": "voice_200"},
            {"key": "4", "label": "550 افغانۍ: 6600 دقیقې", "target_menu": "voice_550"}
        ],
        "transitions": {
            "9": "self_bundle",
            "0": "exit_node"
        }
    },
    "voice_50": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د 50 افغانیو په بدل کې د 200 دقیقو بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د 50 افغانیو په بدل کې د 200 دقیقو بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 0},
        "success_prompt": "د 50 افغانیو 200 دقیقو بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "voice_bundle",
            "0": "exit_node"
        }
    },
    "voice_100": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د 100 افغانیو په بدل کې د 550 دقیقو بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د 100 افغانیو په بدل کې د 550 دقیقو بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 1},
        "success_prompt": "د 100 افغانیو 550 دقیقو بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "voice_bundle",
            "0": "exit_node"
        }
    },
    "voice_200": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د 200 افغانیو په بدل کې د 1000 دقیقو بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د 200 افغانیو په بدل کې د 1000 دقیقو بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 2},
        "success_prompt": "د 200 افغانیو 1000 دقیقو بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "voice_bundle",
            "0": "exit_node"
        }
    },
    "voice_550": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د 550 افغانیو په بدل کې د 6600 دقیقو بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د 550 افغانیو په بدل کې د 6600 دقیقو بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 3},
        "success_prompt": "د 550 افغانیو 6600 دقیقو بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "voice_bundle",
            "0": "exit_node"
        }
    },
    "others_bundle": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د منزل شمیره ولیکئ:\n",
                "input_key": "phone_number",
                "validation": {"regex": "^\\d{10}$"}
            }
        ],
        "confirmation_prompt": "{phone_number} ته بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_others_bundle",
        "params": {},
        "success_prompt": "په بریالیتوب سره د {phone_number} لپاره بنډل واخیستل شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "bundles_menu",
            "0": "exit_node",
            "*": "others_bundle_type"
        }
    },
    "others_bundle_type": {
        "type": "menu_navigation",
        "prompt": "د بنډل ډول: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "د ډیټا بنډل", "target_menu": "others_data_bundle"},
            {"key": "2", "label": "د غږ بنډل", "target_menu": "others_voice_bundle"}
        ],
        "transitions": {
            "9": "bundles_menu",
            "0": "exit_node"
        }
    },
    "others_data_bundle": {
        "type": "menu_navigation",
        "prompt": "د نورو لپاره د ډیټا بنډل: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "280 افغانۍ: 2.5 جي بي", "target_menu": "others_data_280"},
            {"key": "2", "label": "450 افغانۍ: 6 جي بي", "target_menu": "others_data_450"},
            {"key": "3", "label": "670 افغانۍ: 10 جي بي", "target_menu": "others_data_670"},
            {"key": "4", "label": "1220 افغانۍ: 22.2 جي بي", "target_menu": "others_data_1220"}
        ],
        "transitions": {
            "9": "others_bundle_type",
            "0": "exit_node"
        }
    },
    "others_data_280": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ۲۸۰ افغانیو په بدل کې د ۲.۵ جي بي بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د منزل شمیرې لپاره د 280 افغانیو په بدل کې 2.5 جي بي بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 0, "phone_number": "<phone_number>"},
        "success_prompt": "د منزل شمیرې لپاره د 280 افغانیو 2.5 جي بي بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        }
    },
    "others_data_450": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ۴۵۰ افغانیو په بدل کې د ۶ جي بي بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د منزل شمیرې لپاره د 450 افغانیو په بدل کې 6 جي بي بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 1, "phone_number": "<phone_number>"},
        "success_prompt": "د منزل شمیرې لپاره د 450 افغانیو 6 جي بي بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        }
    },
    "others_data_670": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ۶۷۰ افغانیو په بدل کې د ۱۰ جي بي بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د منزل شمیرې لپاره د 670 افغانیو په بدل کې 10 جي بي بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 2, "phone_number": "<phone_number>"},
        "success_prompt": "د منزل شمیرې لپاره د 670 افغانیو 10 جي بي بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        }
    },
    "others_data_1220": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ۱۲۲۰ افغانیو په بدل کې د ۲۲.۲ جي بي بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د منزل شمیرې لپاره د 1220 افغانیو په بدل کې 22.2 جي بي بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 3, "phone_number": "<phone_number>"},
        "success_prompt": "د منزل شمیرې لپاره د 1220 افغانیو 22.2 جي بي بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        }
    },
    "others_voice_bundle": {
        "type": "menu_navigation",
        "prompt": "د نورو لپاره د غږ بنډل: یو انتخاب وټاکئ:",
        "options": [
            {"key": "1", "label": "50 افغانۍ: 200 دقیقې", "target_menu": "others_voice_50"},
            {"key": "2", "label": "100 افغانۍ: 550 دقیقې", "target_menu": "others_voice_100"},
            {"key": "3", "label": "200 افغانۍ: 1000 دقیقې", "target_menu": "others_voice_200"},
            {"key": "4", "label": "550 افغانۍ: 6600 دقیقې", "target_menu": "others_voice_550"}
        ],
        "transitions": {
            "9": "others_bundle_type",
            "0": "exit_node"
        }
    },
    "others_voice_50": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ۵۰ افغانیو په بدل کې د ۲۰۰ دقیقو بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د منزل شمیرې لپاره د 50 افغانیو په بدل کې 200 دقیقې بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 0, "phone_number": "<phone_number>"},
        "success_prompt": "د منزل شمیرې لپاره د 50 افغانیو 200 دقیقو بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        }
    },
    "others_voice_100": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ۱۰۰ افغانیو په بدل کې د ۵۵۰ دقیقو بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د منزل شمیرې لپاره د 100 افغانیو په بدل کې 550 دقیقې بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 1, "phone_number": "<phone_number>"},
        "success_prompt": "د منزل شمیرې لپاره د 100 افغانیو 550 دقیقو بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        }
    },
    "others_voice_200": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ۲۰۰ افغانیو په بدل کې د ۱۰۰۰ دقیقو بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د منزل شمیرې لپاره د 200 افغانیو په بدل کې 1000 دقیقې بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 2, "phone_number": "<phone_number>"},
        "success_prompt": "د منزل شمیرې لپاره د 200 افغانیو 1000 دقیقو بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        }
    },
    "others_voice_550": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "د ۵۵۰ افغانیو په بدل کې د ۶۶۰۰ دقیقو بنډل پیرود تایید کړئ:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "د منزل شمیرې لپاره د 550 افغانیو په بدل کې 6600 دقیقې بنډل واخلئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 3, "phone_number": "<phone_number>"},
        "success_prompt": "د منزل شمیرې لپاره د 550 افغانیو 6600 دقیقو بنډل فعال شو\nرسید: {receipt_number}",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        }
    },
    "approvals_menu": {
        "type": "single_input_action",
        "prompt": "د منظوریو لیدو لپاره خپل پټ نوم ولیکئ:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{6}$"},
        "confirmation_prompt": "منظورۍ وګورئ؟ 1: سمه ده، 2: لغوه",
        "action_url": "http://localhost:8080/api/approvals",
        "params": {},
        "success_prompt": "منظورۍ: {approvals}\nوضعیت: {status}",
        "transitions": {
            "9": "main_menu",
            "0": "exit_node"
        }
    },
    "exit_node": {
        "type": "exit",
        "prompt": "زموږ د خدمت څخه د کار اخیستو څخه مننه\n"
    }
}
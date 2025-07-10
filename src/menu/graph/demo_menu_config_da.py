config = {
    "root_validation_gate": {
        "type": "validation_gate",
        "prompt": "Enter Your My Money Pin:\n",
        "valid_pin": "123456",
        "max_attempts": 3,
        "validation_url": "http://localhost:8080/ussd/customer/USSDlogin",
        "on_success": {"target_menu": "main_menu"},
        "on_failure": {"target_menu": "exit_node"}
    },
    "main_men   u": {
        "type": "menu_navigation",
        "prompt": "Main Menu: Select an option:",
        "options": [
            {"key": "1", "label": "My Money", "target_menu": "my_money_menu"},
            {"key": "2", "label": "Banks", "target_menu": "banks_menu"},
            {"key": "3", "label": "Payment", "target_menu": "payment_menu"},
            {"key": "4", "label": "Bills", "target_menu": "bills_menu"},
            {"key": "5", "label": "Top-up", "target_menu": "topup_menu"},
            {"key": "6", "label": "Approvals", "target_menu": "approvals_menu"}
        ],
        "transitions": {
            "9": "root_validation_gate",
            "0": "exit_node"
        }
    },
    "my_money_menu": {
        "type": "menu_navigation",
        "prompt": "My Money: Select an option:",
        "options": [
            {"key": "1", "label": "Balance", "target_menu": "balance_check"},
            {"key": "2", "label": "Change PIN", "target_menu": "change_pin"},
            {"key": "3", "label": "Transaction", "target_menu": "transaction_menu"},
            {"key": "4", "label": "Transfer", "target_menu": "transfer_menu"},
            {"key": "5", "label": "Language", "target_menu": "language_menu"}
        ],
        "transitions": {
            "9": "main_menu",
            "0": "exit_node"
        }
    },
    "balance_check": {
        "type": "cache_post",
        "prompt": "Your balance is {balance} AFN\nStatus: {status}\nPress 9 to go back, 0 to exit",
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
                "prompt": "Enter your old My Money PIN (6 digits):\n",
                "input_key": "old_pin",
                "validation": {"regex": "^\\d{6}$"}
            },
            {
                "prompt": "Enter your new My Money PIN (6 digits):\n",
                "input_key": "new_pin",
                "validation": {"regex": "^\\d{6}$"}
            },
            {
                "prompt": "Confirm your new PIN:\n",
                "input_key": "confirm_pin",
                "validation": {"regex": "^\\d{6}$"}
            }
        ],
        "confirmation_prompt": "Change PIN to {new_pin}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/pwd/update",
        "params": {},
        "success_prompt": "PIN changed successfully\nReceipt: {receipt_number}",
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        }
    },
    "transaction_menu": {
        "type": "single_input_action",
        "prompt": "Enter your PIN to view transaction history:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{6}$"},
        "confirmation_prompt": "View transaction history? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/ts/api/transaction-services/getFilteredHistory",
        "params": {},
        "success_prompt": "Transaction History: {transactions}\nStatus: {status}",
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        }
    },
    "transfer_menu": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter the recipient's phone number:\n",
                "input_key": "phone_number",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN to {phone_number}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        }
    },
    "language_menu": {
        "type": "menu_navigation",
        "prompt": "Select Language:",
        "options": [
            {"key": "1", "label": "Dari", "target_menu": "my_money_menu"},
            {"key": "2", "label": "Pashto", "target_menu": "my_money_menu"},
            {"key": "3", "label": "English", "target_menu": "my_money_menu"}
        ],
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        }
    },
    "banks_menu": {
        "type": "menu_navigation",
        "prompt": "Banks: Select an option:",
        "options": [
            {"key": "1", "label": "Maiwand Bank", "target_menu": "maiwand_bank"},
            {"key": "2", "label": "NKB", "target_menu": "nkb_bank"},
            {"key": "3", "label": "Azizi", "target_menu": "azizi_bank"},
            {"key": "4", "label": "Other", "target_menu": "other_bank"},
            {"key": "5", "label": "AUB", "target_menu": "aub_bank"},
            {"key": "6", "label": "BMA", "target_menu": "bma_bank"},
            {"key": "7", "label": "Ghazanfar", "target_menu": "ghazanfar_bank"}
        ],
        "transitions": {
            "9": "main_menu",
            "0": "exit_node"
        }
    },
    "maiwand_bank": {
        "type": "menu_navigation",
        "prompt": "Maiwand Bank: Select an option:",
        "options": [
            {"key": "1", "label": "Bank Balance", "target_menu": "maiwand_balance"},
            {"key": "2", "label": "Link Bank", "target_menu": "maiwand_link"},
            {"key": "3", "label": "Transfer to Bank", "target_menu": "maiwand_transfer_to"},
            {"key": "4", "label": "Transfer from Bank", "target_menu": "maiwand_transfer_from"}
        ],
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "maiwand_balance": {
        "type": "single_input_action",
        "prompt": "Enter your PIN to check Maiwand Bank balance:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{4}$"},
        "confirmation_prompt": "Check Maiwand Bank balance? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/bank_balance",
        "params": {"bank": "Maiwand"},
        "success_prompt": "Maiwand Bank Balance: {balance} AFN\nStatus: {status}",
        "transitions": {
            "9": "maiwand_bank",
            "0": "exit_node"
        }
    },
    "maiwand_link": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter your Maiwand account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter your bank PIN:\n",
                "input_key": "bank_pin",
                "validation": {"regex": "^\\d{4}$"}
            }
        ],
        "confirmation_prompt": "Link Maiwand account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/link_bank",
        "params": {"bank": "Maiwand"},
        "success_prompt": "Account linked\nReceipt: {receipt_number}",
        "transitions": {
            "9": "maiwand_bank",
            "0": "exit_node"
        }
    },
    "maiwand_transfer_to": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter the recipient's account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN to Maiwand account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/transfer_bank",
        "params": {"bank": "Maiwand"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "maiwand_bank",
            "0": "exit_node"
        }
    },
    "maiwand_transfer_from": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter your Maiwand account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN from Maiwand account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/transfer_from_bank",
        "params": {"bank": "Maiwand"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "maiwand_bank",
            "0": "exit_node"
        }
    },
    "nkb_bank": {
        "type": "menu_navigation",
        "prompt": "NKB Bank: Select an option:",
        "options": [
            {"key": "1", "label": "Bank Balance", "target_menu": "nkb_balance"},
            {"key": "2", "label": "Link Bank", "target_menu": "nkb_link"},
            {"key": "3", "label": "Transfer to Bank", "target_menu": "nkb_transfer_to"},
            {"key": "4", "label": "Transfer from Bank", "target_menu": "nkb_transfer_from"}
        ],
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "nkb_balance": {
        "type": "single_input_action",
        "prompt": "Enter your PIN to check NKB Bank balance:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{4}$"},
        "confirmation_prompt": "Check NKB Bank balance? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/bank_balance",
        "params": {"bank": "NKB"},
        "success_prompt": "NKB Bank Balance: {balance} AFN\nStatus: {status}",
        "transitions": {
            "9": "nkb_bank",
            "0": "exit_node"
        }
    },
    "nkb_link": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter your NKB account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter your bank PIN:\n",
                "input_key": "bank_pin",
                "validation": {"regex": "^\\d{4}$"}
            }
        ],
        "confirmation_prompt": "Link NKB account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/link_bank",
        "params": {"bank": "NKB"},
        "success_prompt": "Account linked\nReceipt: {receipt_number}",
        "transitions": {
            "9": "nkb_bank",
            "0": "exit_node"
        }
    },
    "nkb_transfer_to": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter the recipient's account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN to NKB account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/transfer_bank",
        "params": {"bank": "NKB"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "nkb_bank",
            "0": "exit_node"
        }
    },
    "nkb_transfer_from": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter your NKB account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN from NKB account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/transfer_from_bank",
        "params": {"bank": "NKB"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "nkb_bank",
            "0": "exit_node"
        }
    },
    "azizi_bank": {
        "type": "menu_navigation",
        "prompt": "Azizi Bank: Select an option:",
        "options": [
            {"key": "1", "label": "Bank Balance", "target_menu": "azizi_balance"},
            {"key": "2", "label": "Link Bank", "target_menu": "azizi_link"},
            {"key": "3", "label": "Transfer to Bank", "target_menu": "azizi_transfer_to"},
            {"key": "4", "label": "Transfer from Bank", "target_menu": "azizi_transfer_from"}
        ],
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "azizi_balance": {
        "type": "single_input_action",
        "prompt": "Enter your PIN to check Azizi Bank balance:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{4}$"},
        "confirmation_prompt": "Check Azizi Bank balance? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/bank_balance",
        "params": {"bank": "Azizi"},
        "success_prompt": "Azizi Bank Balance: {balance} AFN\nStatus: {status}",
        "transitions": {
            "9": "azizi_bank",
            "0": "exit_node"
        }
    },
    "azizi_link": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter your Azizi account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter your bank PIN:\n",
                "input_key": "bank_pin",
                "validation": {"regex": "^\\d{4}$"}
            }
        ],
        "confirmation_prompt": "Link Azizi account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/link_bank",
        "params": {"bank": "Azizi"},
        "success_prompt": "Account linked\nReceipt: {receipt_number}",
        "transitions": {
            "9": "azizi_bank",
            "0": "exit_node"
        }
    },
    "azizi_transfer_to": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter the recipient's account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN to Azizi account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/transfer_bank",
        "params": {"bank": "Azizi"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "azizi_bank",
            "0": "exit_node"
        }
    },
    "azizi_transfer_from": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter your Azizi account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN from Azizi account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/transfer_from_bank",
        "params": {"bank": "Azizi"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "azizi_bank",
            "0": "exit_node"
        }
    },
    "other_bank": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter the bank name:\n",
                "input_key": "bank_name",
                "validation": {"regex": "^[A-Za-z ]+$"}
            },
            {
                "prompt": "Enter the account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            }
        ],
        "confirmation_prompt": "Link {bank_name} account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/link_other_bank",
        "params": {},
        "success_prompt": "Account linked\nReceipt: {receipt_number}",
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "aub_bank": {
        "type": "menu_navigation",
        "prompt": "AUB Bank: Select an option:",
        "options": [
            {"key": "1", "label": "Bank Balance", "target_menu": "aub_balance"},
            {"key": "2", "label": "Link Bank", "target_menu": "aub_link"},
            {"key": "3", "label": "Transfer to Bank", "target_menu": "aub_transfer_to"},
            {"key": "4", "label": "Transfer from Bank", "target_menu": "aub_transfer_from"}
        ],
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "aub_balance": {
        "type": "single_input_action",
        "prompt": "Enter your PIN to check AUB Bank balance:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{4}$"},
        "confirmation_prompt": "Check AUB Bank balance? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/bank_balance",
        "params": {"bank": "AUB"},
        "success_prompt": "AUB Bank Balance: {balance} AFN\nStatus: {status}",
        "transitions": {
            "9": "aub_bank",
            "0": "exit_node"
        }
    },
    "aub_link": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter your AUB account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter your bank PIN:\n",
                "input_key": "bank_pin",
                "validation": {"regex": "^\\d{4}$"}
            }
        ],
        "confirmation_prompt": "Link AUB account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/link_bank",
        "params": {"bank": "AUB"},
        "success_prompt": "Account linked\nReceipt: {receipt_number}",
        "transitions": {
            "9": "aub_bank",
            "0": "exit_node"
        }
    },
    "aub_transfer_to": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter the recipient's account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN to AUB account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"bank": "AUB"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "aub_bank",
            "0": "exit_node"
        }
    },
    "aub_transfer_from": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter your AUB account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN from AUB account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"bank": "AUB"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "aub_bank",
            "0": "exit_node"
        }
    },
    "bma_bank": {
        "type": "menu_navigation",
        "prompt": "BMA Bank: Select an option:",
        "options": [
            {"key": "1", "label": "Bank Balance", "target_menu": "bma_balance"},
            {"key": "2", "label": "Link Bank", "target_menu": "bma_link"},
            {"key": "3", "label": "Transfer to Bank", "target_menu": "bma_transfer_to"},
            {"key": "4", "label": "Transfer from Bank", "target_menu": "bma_transfer_from"}
        ],
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "bma_balance": {
        "type": "single_input_action",
        "prompt": "Enter your PIN to check BMA Bank balance:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{4}$"},
        "confirmation_prompt": "Check BMA Bank balance? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/bank_balance",
        "params": {"bank": "BMA"},
        "success_prompt": "BMA Bank Balance: {balance} AFN\nStatus: {status}",
        "transitions": {
            "9": "bma_bank",
            "0": "exit_node"
        }
    },
    "bma_link": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter your BMA account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter your bank PIN:\n",
                "input_key": "bank_pin",
                "validation": {"regex": "^\\d{4}$"}
            }
        ],
        "confirmation_prompt": "Link BMA account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/link_bank",
        "params": {"bank": "BMA"},
        "success_prompt": "Account linked\nReceipt: {receipt_number}",
        "transitions": {
            "9": "bma_bank",
            "0": "exit_node"
        }
    },
    "bma_transfer_to": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter the recipient's account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN to BMA account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/transfer_bank",
        "params": {"bank": "BMA"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "bma_bank",
            "0": "exit_node"
        }
    },
    "bma_transfer_from": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter your BMA account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN from BMA account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/transfer_from_bank",
        "params": {"bank": "BMA"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "bma_bank",
            "0": "exit_node"
        }
    },
    "ghazanfar_bank": {
        "type": "menu_navigation",
        "prompt": "Ghazanfar Bank: Select an option:",
        "options": [
            {"key": "1", "label": "Bank Balance", "target_menu": "ghazanfar_balance"},
            {"key": "2", "label": "Link Bank", "target_menu": "ghazanfar_link"},
            {"key": "3", "label": "Transfer to Bank", "target_menu": "ghazanfar_transfer_to"},
            {"key": "4", "label": "Transfer from Bank", "target_menu": "ghazanfar_transfer_from"}
        ],
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "ghazanfar_balance": {
        "type": "single_input_action",
        "prompt": "Enter your PIN to check Ghazanfar Bank balance:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{4}$"},
        "confirmation_prompt": "Check Ghazanfar Bank balance? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/bank_balance",
        "params": {"bank": "Ghazanfar"},
        "success_prompt": "Ghazanfar Bank Balance: {balance} AFN\nStatus: {status}",
        "transitions": {
            "9": "ghazanfar_bank",
            "0": "exit_node"
        }
    },
    "ghazanfar_link": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter your Ghazanfar account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter your bank PIN:\n",
                "input_key": "bank_pin",
                "validation": {"regex": "^\\d{4}$"}
            }
        ],
        "confirmation_prompt": "Link Ghazanfar account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/link_bank",
        "params": {"bank": "Ghazanfar"},
        "success_prompt": "Account linked\nReceipt: {receipt_number}",
        "transitions": {
            "9": "ghazanfar_bank",
            "0": "exit_node"
        }
    },
    "ghazanfar_transfer_to": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter the recipient's account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN to Ghazanfar account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"bank": "Ghazanfar"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "ghazanfar_bank",
            "0": "exit_node"
        }
    },
    "ghazanfar_transfer_from": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter your Ghazanfar account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to transfer (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Transfer {amount} AFN from Ghazanfar account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"bank": "Ghazanfar"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "ghazanfar_bank",
            "0": "exit_node"
        }
    },
    "payment_menu": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter the payee's account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to be paid (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Pay {amount} AFN to account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/payment",
        "params": {},
        "success_prompt": "Payment completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "main_menu",
            "0": "exit_node"
        }
    },
    "bills_menu": {
        "type": "menu_navigation",
        "prompt": "Bills: Select an option:",
        "options": [
            {"key": "1", "label": "DABS", "target_menu": "dabs_bill"},
            {"key": "2", "label": "Delight", "target_menu": "delight_bill"}
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
                "prompt": "Enter DABS account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter bill amount (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 10}
            }
        ],
        "confirmation_prompt": "Pay {amount} AFN for account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"provider": "DABS"},
        "success_prompt": "Payment processed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "bills_menu",
            "0": "exit_node"
        }
    },
    "delight_bill": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter Delight account ID:\n",
                "input_key": "account_id",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter bill amount (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 10}
            }
        ],
        "confirmation_prompt": "Pay {amount} AFN for account {account_id}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/pay_bill",
        "params": {"provider": "Delight"},
        "success_prompt": "Payment processed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "bills_menu",
            "0": "exit_node"
        }
    },
    "topup_menu": {
        "type": "menu_navigation",
        "prompt": "Top-up: Select an option:",
        "options": [
            {"key": "1", "label": "Top-up myself", "target_menu": "topup_self"},
            {"key": "2", "label": "Top-up others", "target_menu": "topup_others"},
            {"key": "3", "label": "Buy top-up bundles", "target_menu": "bundles_menu"}
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
                "prompt": "Enter the amount to top-up (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Top-up {amount} AFN for your account? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"type": "self"},
        "success_prompt": "Top-up completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "topup_menu",
            "0": "exit_node"
        }
    },
    "topup_others": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter the destination number:\n",
                "input_key": "phone_number",
                "validation": {"regex": "^\\d{10}$"}
            },
            {
                "prompt": "Enter the amount to top-up (AFN):\n",
                "input_key": "amount",
                "validation": {"type": "numeric", "min": 1}
            }
        ],
        "confirmation_prompt": "Top-up {amount} AFN for {phone_number}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"type": "others"},
        "success_prompt": "Top-up completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "topup_menu",
            "0": "exit_node"
        }
    },
    "bundles_menu": {
        "type": "menu_navigation",
        "prompt": "Bundles: Select an option:",
        "options": [
            {"key": "1", "label": "Bundle for Self", "target_menu": "self_bundle"},
            {"key": "2", "label": "Bundle for Others", "target_menu": "others_bundle"}
        ],
        "transitions": {
            "9": "topup_menu",
            "0": "exit_node"
        }
    },
    "self_bundle": {
        "type": "menu_navigation",
        "prompt": "Self Bundle: Select an option:",
        "options": [
            {"key": "1", "label": "Data Bundle", "target_menu": "data_bundle"},
            {"key": "2", "label": "Voice Bundle", "target_menu": "voice_bundle"}
        ],
        "transitions": {
            "9": "bundles_menu",
            "0": "exit_node"
        }
    },
    "data_bundle": {
        "type": "menu_navigation",
        "prompt": "Data Bundle: Select an option:",
        "options": [
            {"key": "1", "label": "280 AFN: 2.5GB", "target_menu": "data_280"},
            {"key": "2", "label": "450 AFN: 6GB", "target_menu": "data_450"},
            {"key": "3", "label": "670 AFN: 10GB", "target_menu": "data_670"},
            {"key": "4", "label": "1220 AFN: 22.2GB", "target_menu": "data_1220"}
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
                "prompt": "Confirm purchase of 280 AFN for 2.5GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 280 AFN: 2.5GB bundle? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/tms/router/basic",
        "params": {"bundle_type": "DATA", "option": 0},
        "success_prompt": "280 AFN: 2.5GB bundle activated\nReceipt: {receipt_number}",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        }
    },
    "data_450": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm purchase of 450 AFN for 6GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 450 AFN: 6GB bundle? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 1},
        "success_prompt": "450 AFN: 6GB bundle activated\nReceipt: {receipt_number}",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        }
    },
    "data_670": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm purchase of 670 AFN for 10GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 670 AFN: 10GB bundle? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 2},
        "success_prompt": "670 AFN: 10GB bundle activated\nReceipt: {receipt_number}",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        }
    },
    "data_1220": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm purchase of 1220 AFN for 22.2GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 1220 AFN: 22.2GB bundle? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 3},
        "success_prompt": "1220 AFN: 22.2GB bundle activated\nReceipt: {receipt_number}",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        }
    },
    "voice_bundle": {
        "type": "menu_navigation",
        "prompt": "Voice Bundle: Select an option:",
        "options": [
            {"key": "1", "label": "50 AFN: 200min", "target_menu": "voice_50"},
            {"key": "2", "label": "100 AFN: 550min", "target_menu": "voice_100"},
            {"key": "3", "label": "200 AFN: 1000min", "target_menu": "voice_200"},
            {"key": "4", "label": "550 AFN: 6600min", "target_menu": "voice_550"}
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
                "prompt": "Confirm purchase of 50 AFN for 200min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 50 AFN: 200min bundle? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 0},
        "success_prompt": "50 AFN: 200min bundle activated\nReceipt: {receipt_number}",
        "transitions": {
            "9": "voice_bundle",
            "0": "exit_node"
        }
    },
    "voice_100": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm purchase of 100 AFN for 550min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 100 AFN: 550min bundle? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 1},
        "success_prompt": "100 AFN: 550min bundle activated\nReceipt: {receipt_number}",
        "transitions": {
            "9": "voice_bundle",
            "0": "exit_node"
        }
    },
    "voice_200": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm purchase of 200 AFN for 1000min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 200 AFN: 1000min bundle? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 2},
        "success_prompt": "200 AFN: 1000min bundle activated\nReceipt: {receipt_number}",
        "transitions": {
            "9": "voice_bundle",
            "0": "exit_node"
        }
    },
    "voice_550": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm purchase of 550 AFN for 6600min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 550 AFN: 6600min bundle? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 3},
        "success_prompt": "550 AFN: 6600min bundle activated\nReceipt: {receipt_number}",
        "transitions": {
            "9": "voice_bundle",
            "0": "exit_node"
        }
    },
    "others_bundle": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Enter the destination number:\n",
                "input_key": "phone_number",
                "validation": {"regex": "^\\d{10}$"}
            }
        ],
        "confirmation_prompt": "Buy bundle for {phone_number}? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_others_bundle",
        "params": {},
        "success_prompt": "Successfully purchased bundle for {phone_number}\nReceipt: {receipt_number}",
        "transitions": {
            "9": "bundles_menu",
            "0": "exit_node",
            "*": "others_bundle_type"
        }
    },
    "others_bundle_type": {
        "type": "menu_navigation",
        "prompt": "Bundle Type: Select an option:",
        "options": [
            {"key": "1", "label": "Data Bundle", "target_menu": "others_data_bundle"},
            {"key": "2", "label": "Voice Bundle", "target_menu": "others_voice_bundle"}
        ],
        "transitions": {
            "9": "bundles_menu",
            "0": "exit_node"
        }
    },
    "others_data_bundle": {
        "type": "menu_navigation",
        "prompt": "Data Bundle for Others: Select an option:",
        "options": [
            {"key": "1", "label": "280 AFN: 2.5GB", "target_menu": "others_data_280"},
            {"key": "2", "label": "450 AFN: 6GB", "target_menu": "others_data_450"},
            {"key": "3", "label": "670 AFN: 10GB", "target_menu": "others_data_670"},
            {"key": "4", "label": "1220 AFN: 22.2GB", "target_menu": "others_data_1220"}
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
                "prompt": "Confirm purchase of 280 AFN for 2.5GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 280 AFN: 2.5GB bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 0, "phone_number": "<phone_number>"},
        "success_prompt": "280 AFN: 2.5GB bundle activated for destination number\nReceipt: {receipt_number}",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        }
    },
    "others_data_450": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm purchase of 450 AFN for 6GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 450 AFN: 6GB bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 1, "phone_number": "<phone_number>"},
        "success_prompt": "450 AFN: 6GB bundle activated for destination number\nReceipt: {receipt_number}",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        }
    },
    "others_data_670": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm purchase of 670 AFN for 10GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 670 AFN: 10GB bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 2, "phone_number": "<phone_number>"},
        "success_prompt": "670 AFN: 10GB bundle activated for destination number\nReceipt: {receipt_number}",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        }
    },
    "others_data_1220": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm purchase of 1220 AFN for 22.2GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 1220 AFN: 22.2GB bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 3, "phone_number": "<phone_number>"},
        "success_prompt": "1220 AFN: 22.2GB bundle activated for destination number\nReceipt: {receipt_number}",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        }
    },
    "others_voice_bundle": {
        "type": "menu_navigation",
        "prompt": "Voice Bundle for Others: Select an option:",
        "options": [
            {"key": "1", "label": "50 AFN: 200min", "target_menu": "others_voice_50"},
            {"key": "2", "label": "100 AFN: 550min", "target_menu": "others_voice_100"},
            {"key": "3", "label": "200 AFN: 1000min", "target_menu": "others_voice_200"},
            {"key": "4", "label": "550 AFN: 6600min", "target_menu": "others_voice_550"}
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
                "prompt": "Confirm purchase of 50 AFN for 200min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 50 AFN: 200min bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 0, "phone_number": "<phone_number>"},
        "success_prompt": "50 AFN: 200min bundle activated for destination number\nReceipt: {receipt_number}",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        }
    },
    "others_voice_100": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm purchase of 100 AFN for 550min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 100 AFN: 550min bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 1, "phone_number": "<phone_number>"},
        "success_prompt": "100 AFN: 550min bundle activated for destination number\nReceipt: {receipt_number}",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        }
    },
    "others_voice_200": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm purchase of 200 AFN for 1000min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 200 AFN: 1000min bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 2, "phone_number": "<phone_number>"},
        "success_prompt": "200 AFN: 1000min bundle activated for destination number\nReceipt: {receipt_number}",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        }
    },
    "others_voice_550": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm purchase of 550 AFN for 6600min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 550 AFN: 6600min bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 3, "phone_number": "<phone_number>"},
        "success_prompt": "550 AFN: 6600min bundle activated for destination number\nReceipt: {receipt_number}",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        }
    },
    "approvals_menu": {
        "type": "single_input_action",
        "prompt": "Enter your PIN to view approvals:",
        "input_key": "pin",
        "validation": {"regex": "^\\d{6}$"},
        "confirmation_prompt": "View approvals? 1: OK, 2: Cancel",
        "action_url": "http://localhost:8080/api/approvals",
        "params": {},
        "success_prompt": "Approvals: {approvals}\nStatus: {status}",
        "transitions": {
            "9": "main_menu",
            "0": "exit_node"
        }
    },
    "exit_node": {
        "type": "exit",
        "prompt": "Thank you for using our service\n"
    }
}
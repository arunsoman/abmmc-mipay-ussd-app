config = {
    "root_validation_gate": {
        "type": "validation_gate",
        "prompt": "Enter Your My Money Pin:\n",
        "valid_pin": "123456",
        "max_attempts": 3,
        "validation_url": "https://example.com/validate",
        "on_success": {"target_menu": "main_menu"},
        "on_failure": {"target_menu": "exit_node"}
    },
    "main_menu": {
        "type": "menu_navigation",
        "prompt": "1. My Money\n2. Banks\n3. Payment\n4. Bills\n5. Top-up\n6. Approvals\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "my_money_menu"},
            {"key": "2", "target_menu": "banks_menu"},
            {"key": "3", "target_menu": "payment_menu"},
            {"key": "4", "target_menu": "bills_menu"},
            {"key": "5", "target_menu": "topup_menu"},
            {"key": "6", "target_menu": "approvals_menu"},
            {"key": "9", "target_menu": "root_validation_gate"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "main_menu"}
    },
    "my_money_menu": {
        "type": "menu_navigation",
        "prompt": "1. Balance\n2. Change PIN\n3. Transaction\n4. Transfer\n5. Language\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "balance_check"},
            {"key": "2", "target_menu": "change_pin"},
            {"key": "3", "target_menu": "transaction_menu"},
            {"key": "4", "target_menu": "transfer_menu"},
            {"key": "5", "target_menu": "language_menu"},
            {"key": "9", "target_menu": "main_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "my_money_menu"}
    },
    "balance_check": {
        "type": "single_input_action",
        "prompt": "Your balance is 1,234.56 AFN\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        }
    },
    "change_pin": {
        "type": "multi_input_action",
        "steps": [
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
        "action_url": "/api/change_pin",
        "params": {},
        "success_prompt": "PIN changed successfully\nReceipt: {receipt_number}",
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        }
    },
    "transaction_menu": {
        "type": "single_input_action",
        "prompt": "Transaction History\nPress 9 to go back or 0 to exit\n",
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
        "action_url": "/api/transfer",
        "params": {},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_no   de"
        }
    },
    "language_menu": {
        "type": "menu_navigation",
        "prompt": "1. Dari\n2. Pashto\n3. English\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "my_money_menu", "action": "set_language_dari"},
            {"key": "2", "target_menu": "my_money_menu", "action": "set_language_pashto"},
            {"key": "3", "target_menu": "my_money_menu", "action": "set_language_english"},
            {"key": "9", "target_menu": "my_money_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "language_menu"}
    },
    "banks_menu": {
        "type": "menu_navigation",
        "prompt": "1. Maiwand Bank\n2. NKB\n3. Azizi\n4. Other\n5. AUB\n6. BMA\n7. Ghazanfar\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "maiwand_bank"},
            {"key": "2", "target_menu": "nkb_bank"},
            {"key": "3", "target_menu": "azizi_bank"},
            {"key": "4", "target_menu": "other_bank"},
            {"key": "5", "target_menu": "aub_bank"},
            {"key": "6", "target_menu": "bma_bank"},
            {"key": "7", "target_menu": "ghazanfar_bank"},
            {"key": "9", "target_menu": "main_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "banks_menu"}
    },
    "maiwand_bank": {
        "type": "menu_navigation",
        "prompt": "1. Bank Balance\n2. Link Bank\n3. Transfer to Bank\n4. Transfer from Bank\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "maiwand_balance"},
            {"key": "2", "target_menu": "maiwand_link"},
            {"key": "3", "target_menu": "maiwand_transfer_to"},
            {"key": "4", "target_menu": "maiwand_transfer_from"},
            {"key": "9", "target_menu": "banks_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "maiwand_bank"}
    },
    "maiwand_balance": {
        "type": "single_input_action",
        "prompt": "Maiwand Bank Balance: 5,000 AFN\nPress 9 to go back or 0 to exit\n",
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
        "action_url": "/api/link_bank",
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
        "action_url": "/api/transfer_bank",
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
        "action_url": "/api/transfer_from_bank",
        "params": {"bank": "Maiwand"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "maiwand_bank",
            "0": "exit_node"
        }
    },
    "nkb_bank": {
        "type": "menu_navigation",
        "prompt": "1. Bank Balance\n2. Link Bank\n3. Transfer to Bank\n4. Transfer from Bank\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "nkb_balance"},
            {"key": "2", "target_menu": "nkb_link"},
            {"key": "3", "target_menu": "nkb_transfer_to"},
            {"key": "4", "target_menu": "nkb_transfer_from"},
            {"key": "9", "target_menu": "banks_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "nkb_bank"}
    },
    "nkb_balance": {
        "type": "single_input_action",
        "prompt": "NKB Bank Balance: 3,500 AFN\nPress 9 to go back or 0 to exit\n",
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
        "action_url": "/api/link_bank",
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
        "action_url": "/api/transfer_bank",
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
        "action_url": "/api/transfer_from_bank",
        "params": {"bank": "NKB"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "nkb_bank",
            "0": "exit_node"
        }
    },
    "azizi_bank": {
        "type": "menu_navigation",
        "prompt": "1. Bank Balance\n2. Link Bank\n3. Transfer to Bank\n4. Transfer from Bank\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "azizi_balance"},
            {"key": "2", "target_menu": "azizi_link"},
            {"key": "3", "target_menu": "azizi_transfer_to"},
            {"key": "4", "target_menu": "azizi_transfer_from"},
            {"key": "9", "target_menu": "banks_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "azizi_bank"}
    },
    "azizi_balance": {
        "type": "single_input_action",
        "prompt": "Azizi Bank Balance: 2,800 AFN\nPress 9 to go back or 0 to exit\n",
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
        "action_url": "/api/link_bank",
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
        "action_url": "/api/transfer_bank",
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
        "action_url": "/api/transfer_from_bank",
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
        "action_url": "/api/link_other_bank",
        "params": {},
        "success_prompt": "Account linked\nReceipt: {receipt_number}",
        "transitions": {
            "9": "banks_menu",
            "0": "exit_node"
        }
    },
    "aub_bank": {
        "type": "menu_navigation",
        "prompt": "1. Bank Balance\n2. Link Bank\n3. Transfer to Bank\n4. Transfer from Bank\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "aub_balance"},
            {"key": "2", "target_menu": "aub_link"},
            {"key": "3", "target_menu": "aub_transfer_to"},
            {"key": "4", "target_menu": "aub_transfer_from"},
            {"key": "9", "target_menu": "banks_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "aub_bank"}
    },
    "aub_balance": {
        "type": "single_input_action",
        "prompt": "AUB Bank Balance: 4,200 AFN\nPress 9 to go back or 0 to exit\n",
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
        "action_url": "/api/link_bank",
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
        "action_url": "/api/transfer_bank",
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
        "action_url": "/api/transfer_from_bank",
        "params": {"bank": "AUB"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "aub_bank",
            "0": "exit_node"
        }
    },
    "bma_bank": {
        "type": "menu_navigation",
        "prompt": "1. Bank Balance\n2. Link Bank\n3. Transfer to Bank\n4. Transfer from Bank\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "bma_balance"},
            {"key": "2", "target_menu": "bma_link"},
            {"key": "3", "target_menu": "bma_transfer_to"},
            {"key": "4", "target_menu": "bma_transfer_from"},
            {"key": "9", "target_menu": "banks_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "bma_bank"}
    },
    "bma_balance": {
        "type": "single_input_action",
        "prompt": "BMA Bank Balance: 6,100 AFN\nPress 9 to go back or 0 to exit\n",
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
        "action_url": "/api/link_bank",
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
        "action_url": "/api/transfer_bank",
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
        "action_url": "/api/transfer_from_bank",
        "params": {"bank": "BMA"},
        "success_prompt": "Transfer completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "bma_bank",
            "0": "exit_node"
        }
    },
    "ghazanfar_bank": {
        "type": "menu_navigation",
        "prompt": "1. Bank Balance\n2. Link Bank\n3. Transfer to Bank\n4. Transfer from Bank\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "ghazanfar_balance"},
            {"key": "2", "target_menu": "ghazanfar_link"},
            {"key": "3", "target_menu": "ghazanfar_transfer_to"},
            {"key": "4", "target_menu": "ghazanfar_transfer_from"},
            {"key": "9", "target_menu": "banks_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "ghazanfar_bank"}
    },
    "ghazanfar_balance": {
        "type": "single_input_action",
        "prompt": "Ghazanfar Bank Balance: 3,900 AFN\nPress 9 to go back or 0 to exit\n",
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
        "action_url": "/api/link_bank",
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
        "action_url": "/api/transfer_bank",
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
        "action_url": "/api/transfer_from_bank",
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
        "action_url": "/api/payment",
        "params": {},
        "success_prompt": "Payment completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "main_menu",
            "0": "exit_node"
        }
    },
    "bills_menu": {
        "type": "menu_navigation",
        "prompt": "1. DABS\n2. Delight\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "dabs_bill"},
            {"key": "2", "target_menu": "delight_bill"},
            {"key": "9", "target_menu": "main_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "bills_menu"}
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
        "action_url": "/api/pay_bill",
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
        "action_url": "/api/pay_bill",
        "params": {"provider": "Delight"},
        "success_prompt": "Payment processed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "bills_menu",
            "0": "exit_node"
        }
    },
    "topup_menu": {
        "type": "menu_navigation",
        "prompt": "1. Top-up myself\n2. Top-up others\n3. Buy top-up bundles\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "topup_self"},
            {"key": "2", "target_menu": "topup_others"},
            {"key": "3", "target_menu": "bundles_menu"},
            {"key": "9", "target_menu": "main_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "topup_menu"}
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
        "action_url": "/api/topup",
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
        "action_url": "/api/topup",
        "params": {"type": "others"},
        "success_prompt": "Top-up completed\nReceipt: {receipt_number}",
        "transitions": {
            "9": "topup_menu",
            "0": "exit_node"
        }
    },
    "bundles_menu": {
        "type": "menu_navigation",
        "prompt": "1. Bundle for Self\n2. Bundle for Others\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "self_bundle"},
            {"key": "2", "target_menu": "others_bundle"},
            {"key": "9", "target_menu": "topup_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "bundles_menu"}
    },
    "self_bundle": {
        "type": "menu_navigation",
        "prompt": "1. Data Bundle\n2. Voice Bundle\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "data_bundle"},
            {"key": "2", "target_menu": "voice_bundle"},
            {"key": "9", "target_menu": "bundles_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "self_bundle"}
    },
    "data_bundle": {
        "type": "menu_navigation",
        "prompt": "1. 280 AFN: 2.5GB\n2. 450 AFN: 6GB\n3. 670 AFN: 10GB\n4. 1220 AFN: 22.2GB\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "data_280"},
            {"key": "2", "target_menu": "data_450"},
            {"key": "3", "target_menu": "data_670"},
            {"key": "4", "target_menu": "data_1220"},
            {"key": "9", "target_menu": "self_bundle"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "data_bundle"}
    },
    "data_280": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm 280 AFN for 2.5GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 280 AFN: 2.5GB bundle? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
                "prompt": "Confirm 450 AFN for 6GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 450 AFN: 6GB bundle? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
                "prompt": "Confirm 670 AFN for 10GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 670 AFN: 10GB bundle? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
                "prompt": "Confirm 1220 AFN for 22.2GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 1220 AFN: 22.2GB bundle? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 3},
        "success_prompt": "1220 AFN: 22.2GB bundle activated\nReceipt: {receipt_number}",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        }
    },
    "voice_bundle": {
        "type": "menu_navigation",
        "prompt": "1. 50 AFN: 200min\n2. 100 AFN: 550min\n3. 200 AFN: 1000min\n4. 550 AFN: 6600min\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "voice_50"},
            {"key": "2", "target_menu": "voice_100"},
            {"key": "3", "target_menu": "voice_200"},
            {"key": "4", "target_menu": "voice_550"},
            {"key": "9", "target_menu": "self_bundle"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "voice_bundle"}
    },
    "voice_50": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm 50 AFN for 200min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 50 AFN: 200min bundle? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
                "prompt": "Confirm 100 AFN for 550min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 100 AFN: 550min bundle? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
                "prompt": "Confirm 200 AFN for 1000min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 200 AFN: 1000min bundle? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
                "prompt": "Confirm 550 AFN for 6600min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 550 AFN: 6600min bundle? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
        "action_url": "/api/buy_others_bundle",
        "params": {},
        "success_prompt": "successfully purchased bundle for {phone_number}\nReceipt: {receipt_number}",
        "transitions": {
            "9": "bundles_menu",
            "0": "exit_node",
            "*": "others_bundle_type"
        }
    },
    "others_bundle_type": {
        "type": "menu_navigation",
        "prompt": "1. Data Bundle\n2. Voice Bundle\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "others_data_bundle"},
            {"key": "2", "target_menu": "others_voice_bundle"},
            {"key": "9", "target_menu": "bundles_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "others_bundle_type"}
    },
    "others_data_bundle": {
        "type": "menu_navigation",
        "prompt": "1. 280 AFN: 2.5GB\n2. 450 AFN: 6GB\n3. 670 AFN: 10GB\n4. 1220 AFN: 22.2GB\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "others_data_280"},
            {"key": "2", "target_menu": "others_data_450"},
            {"key": "3", "target_menu": "others_data_670"},
            {"key": "4", "target_menu": "others_data_1220"},
            {"key": "9", "target_menu": "others_bundle_type"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "others_data_bundle"}
    },
    "others_data_280": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm 280 AFN for 2.5GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 280 AFN: 2.5GB bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
                "prompt": "Confirm 450 AFN for 6GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 450 AFN: 6GB bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
                "prompt": "Confirm 670 AFN for 10GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 670 AFN: 10GB bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
                "prompt": "Confirm 1220 AFN for 22.2GB bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 1220 AFN: 22.2GB bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
        "params": {"bundle_type": "DATA", "option": 3, "phone_number": "<phone_number>"},
        "success_prompt": "1220 AFN: 22.2GB bundle activated for destination number\nReceipt: {receipt_number}",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        }
    },
    "others_voice_bundle": {
        "type": "menu_navigation",
        "prompt": "1. 50 AFN: 200min\n2. 100 AFN: 550min\n3. 200 AFN: 1000min\n4. 550 AFN: 6600min\n9. Back\n0. Exit\n",
        "options": [
            {"key": "1", "target_menu": "others_voice_50"},
            {"key": "2", "target_menu": "others_voice_100"},
            {"key": "3", "target_menu": "others_voice_200"},
            {"key": "4", "target_menu": "others_voice_550"},
            {"key": "9", "target_menu": "others_bundle_type"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "others_voice_bundle"}
    },
    "others_voice_50": {
        "type": "multi_input_action",
        "steps": [
            {
                "prompt": "Confirm 50 AFN for 200min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 50 AFN: 200min bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
                "prompt": "Confirm 100 AFN for 550min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 100 AFN: 550min bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
                "prompt": "Confirm 200 AFN for 1000min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 200 AFN: 1000min bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
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
                "prompt": "Confirm 550 AFN for 6600min bundle:\n",
                "input_key": "confirm",
                "validation": {"regex": "^[1-2]$"}
            }
        ],
        "confirmation_prompt": "Purchase 550 AFN: 6600min bundle for destination number? 1: OK, 2: Cancel",
        "action_url": "/api/buy_bundle",
        "params": {"bundle_type": "VOICE", "option": 3, "phone_number": "<phone_number>"},
        "success_prompt": "550 AFN: 6600min bundle activated for destination number\nReceipt: {receipt_number}",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        }
    },
    "approvals_menu": {
        "type": "single_input_action",
        "prompt": "Approvals section\nPress 9 to go back or 0 to exit\n",
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
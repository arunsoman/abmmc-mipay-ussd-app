config ={
    "root_validation_gate": {
        "type": "validation_gate",
        "prompt": "Enter Your My Money Pin:\n",
        "valid_pin": "123456",
        "max_attempts": 3,
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
        "type": "single_input_action",
        "prompt": "Enter your new My Money PIN:\n",
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        },
        "action": "change_pin_service"
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
        "type": "single_input_action",
        "prompt": "Enter the amount to transfer:\n",
        "transitions": {
            "9": "my_money_menu",
            "0": "exit_node"
        },
        "action": "transfer_service"
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
        "type": "single_input_action",
        "prompt": "Enter bank account details to link:\n",
        "transitions": {
            "9": "maiwand_bank",
            "0": "exit_node"
        }
    },
    "maiwand_transfer_to": {
        "type": "single_input_action",
        "prompt": "Enter amount to transfer to Maiwand Bank:\n",
        "transitions": {
            "9": "maiwand_bank",
            "0": "exit_node"
        }
    },
    "maiwand_transfer_from": {
        "type": "single_input_action",
        "prompt": "Enter amount to transfer from Maiwand Bank:\n",
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
        "type": "single_input_action",
        "prompt": "Enter bank account details to link:\n",
        "transitions": {
            "9": "nkb_bank",
            "0": "exit_node"
        }
    },
    "nkb_transfer_to": {
        "type": "single_input_action",
        "prompt": "Enter amount to transfer to NKB Bank:\n",
        "transitions": {
            "9": "nkb_bank",
            "0": "exit_node"
        }
    },
    "nkb_transfer_from": {
        "type": "single_input_action",
        "prompt": "Enter amount to transfer from NKB Bank:\n",
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
        "type": "single_input_action",
        "prompt": "Enter bank account details to link:\n",
        "transitions": {
            "9": "azizi_bank",
            "0": "exit_node"
        }
    },
    "azizi_transfer_to": {
        "type": "single_input_action",
        "prompt": "Enter amount to transfer to Azizi Bank:\n",
        "transitions": {
            "9": "azizi_bank",
            "0": "exit_node"
        }
    },
    "azizi_transfer_from": {
        "type": "single_input_action",
        "prompt": "Enter amount to transfer from Azizi Bank:\n",
        "transitions": {
            "9": "azizi_bank",
            "0": "exit_node"
        }
    },
    "other_bank": {
        "type": "single_input_action",
        "prompt": "Enter bank name for other banks:\n",
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
        "type": "single_input_action",
        "prompt": "Enter bank account details to link:\n",
        "transitions": {
            "9": "aub_bank",
            "0": "exit_node"
        }
    },
    "aub_transfer_to": {
        "type": "single_input_action",
        "prompt": "Enter amount to transfer to AUB Bank:\n",
        "transitions": {
            "9": "aub_bank",
            "0": "exit_node"
        }
    },
    "aub_transfer_from": {
        "type": "single_input_action",
        "prompt": "Enter amount to transfer from AUB Bank:\n",
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
        "type": "single_input_action",
        "prompt": "Enter bank account details to link:\n",
        "transitions": {
            "9": "bma_bank",
            "0": "exit_node"
        }
    },
    "bma_transfer_to": {
        "type": "single_input_action",
        "prompt": "Enter amount to transfer to BMA Bank:\n",
        "transitions": {
            "9": "bma_bank",
            "0": "exit_node"
        }
    },
    "bma_transfer_from": {
        "type": "single_input_action",
        "prompt": "Enter amount to transfer from BMA Bank:\n",
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
        "type": "single_input_action",
        "prompt": "Enter bank account details to link:\n",
        "transitions": {
            "9": "ghazanfar_bank",
            "0": "exit_node"
        }
    },
    "ghazanfar_transfer_to": {
        "type": "single_input_action",
        "prompt": "Enter amount to transfer to Ghazanfar Bank:\n",
        "transitions": {
            "9": "ghazanfar_bank",
            "0": "exit_node"
        }
    },
    "ghazanfar_transfer_from": {
        "type": "single_input_action",
        "prompt": "Enter amount to transfer from Ghazanfar Bank:\n",
        "transitions": {
            "9": "ghazanfar_bank",
            "0": "exit_node"
        }
    },
    "payment_menu": {
        "type": "single_input_action",
        "prompt": "Enter the amount to be paid:\n",
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
        "type": "single_input_action",
        "prompt": "Enter DABS bill amount:\n",
        "transitions": {
            "9": "bills_menu",
            "0": "exit_node"
        }
    },
    "delight_bill": {
        "type": "single_input_action",
        "prompt": "Enter Delight bill amount:\n",
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
            {"key": "nkb_bank9", "target_menu": "main_menu"},
            {"key": "0", "target_menu": "exit_node"}
        ],
        "on_invalid_input": {"target_menu": "topup_menu"}
    },
    "topup_self": {
        "type": "single_input_action",
        "prompt": "Enter the amount to top-up:\n",
        "transitions": {
            "9": "topup_menu",
            "0": "exit_node"
        },
        "action": "TelcoService.TopUpSelf"
    },
    "topup_others": {
        "type": "single_input_action",
        "prompt": "Enter the destination number you will top-up:\n",
        "transitions": {
            "9": "topup_menu",
            "0": "exit_node"
        },
        "action": "TelcoService.TopUpOthers"
    },
    "bundles_menu": {
        "type": "menu_navigation",
        "prompt": "1. Bundle from Self\n2. Bundle from others\n9. Back\n0. Exit\n",
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
        "type": "single_input_action",
        "prompt": "280 AFN: 2.5GB bundle activated\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleSelf",
        "params": {"bundle_type": "DATA", "option": 0}
    },
    "data_450": {
        "type": "single_input_action",
        "prompt": "450 AFN: 6GB bundle activated\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleSelf",
        "params": {"bundle_type": "DATA", "option": 1}
    },
    "data_670": {
        "type": "single_input_action",
        "prompt": "670 AFN: 10GB bundle activated\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleSelf",
        "params": {"bundle_type": "DATA", "option": 2}
    },
    "data_1220": {
        "type": "single_input_action",
        "prompt": "1220 AFN: 22.2GB bundle activated\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "data_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleSelf",
        "params": {"bundle_type": "DATA", "option": 3}
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
        "type": "single_input_action",
        "prompt": "50 AFN: 200min bundle activated\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "voice_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleSelf",
        "params": {"bundle_type": "VOICE", "option": 0}
    },
    "voice_100": {
        "type": "single_input_action",
        "prompt": "100 AFN: 550min bundle activated\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "voice_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleSelf",
        "params": {"bundle_type": "VOICE", "option": 1}
    },
    "voice_200": {
        "type": "single_input_action",
        "prompt": "200 AFN: 1000min bundle activated\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "voice_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleSelf",
        "params": {"bundle_type": "VOICE", "option": 2}
    },
    "voice_550": {
        "type": "single_input_action",
        "prompt": "550 AFN: 6600min bundle activated\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "voice_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleSelf",
        "params": {"bundle_type": "VOICE", "option": 3}
    },
    "others_bundle": {
        "type": "single_input_action",
        "prompt": "Enter the destination number you will buy bundle for:\n",
        "transitions": {
            "9": "bundles_menu",
            "0": "exit_node",
            "*": "others_bundle_type"
        },
        "action": "store_destination_number"
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
        "type": "single_input_action",
        "prompt": "280 AFN: 2.5GB bundle activated for destination number\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleOthers",
        "params": {"bundle_type": "DATA", "option": 0}
    },
    "others_data_450": {
        "type": "single_input_action",
        "prompt": "450 AFN: 6GB bundle activated for destination number\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleOthers",
        "params": {"bundle_type": "DATA", "option": 1}
    },
    "others_data_670": {
        "type": "single_input_action",
        "prompt": "670 AFN: 10GB bundle activated for destination number\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleOthers",
        "params": {"bundle_type": "DATA", "option": 2}
    },
    "others_data_1220": {
        "type": "single_input_action",
        "prompt": "1220 AFN: 22.2GB bundle activated for destination number\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "others_data_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleOthers",
        "params": {"bundle_type": "DATA", "option": 3}
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
        "type": "single_input_action",
        "prompt": "50 AFN: 200min bundle activated for destination number\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleOthers",
        "params": {"bundle_type": "VOICE", "option": 0}
    },
    "others_voice_100": {
        "type": "single_input_action",
        "prompt": "100 AFN: 550min bundle activated for destination number\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleOthers",
        "params": {"bundle_type": "VOICE", "option": 1}
    },
    "others_voice_200": {
        "type": "single_input_action",
        "prompt": "200 AFN: 1000min bundle activated for destination number\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleOthers",
        "params": {"bundle_type": "VOICE", "option": 2}
    },
    "others_voice_550": {
        "type": "single_input_action",
        "prompt": "550 AFN: 6600min bundle activated for destination number\nPress 9 to go back or 0 to exit\n",
        "transitions": {
            "9": "others_voice_bundle",
            "0": "exit_node"
        },
        "action": "TelcoService.BuyBundleOthers",
        "params": {"bundle_type": "VOICE", "option": 3}
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
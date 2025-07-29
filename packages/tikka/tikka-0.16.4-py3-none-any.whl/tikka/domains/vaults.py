# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from tikka.domains.accounts import Accounts
from tikka.domains.currencies import Currencies
from tikka.domains.entities.account import Account, AccountCryptoType
from tikka.domains.entities.constants import DERIVATION_SCAN_MAX_NUMBER
from tikka.interfaces.adapters.network.node.accounts import NodeAccountsInterface
from tikka.libs.keypair import Keypair


class Vaults:
    """
    Vaults domain class
    """

    def __init__(
        self,
        network: NodeAccountsInterface,
        accounts: Accounts,
        currencies: Currencies,
    ):
        """
        Init Vaults domain

        :param network: NetworkAccountsInterface instance
        :param accounts: Accounts domain instance
        :param currencies: Currencies domain instance
        """
        self.network = network
        self.accounts = accounts
        self.currencies = currencies

    def import_from_network(
        self,
        mnemonic: str,
        language_code: str,
        crypto_type: AccountCryptoType,
        name: str,
        password: str,
    ) -> None:
        """
        Import Account and the derivations (vault) from network

        :param mnemonic: Mnemonic phrase
        :param language_code: Mnemonic language code
        :param crypto_type: Key type as AccountCryptoType instance
        :param name: Root account name
        :param password: Vault/Root account password

        :return:
        """
        root_keypair = Keypair.create_from_uri(
            mnemonic,
            language_code=language_code,
            ss58_format=self.currencies.get_current().ss58_format,
            crypto_type=crypto_type,
        )
        root_account = self.accounts.get_by_address(root_keypair.ss58_address)
        if root_account is None:
            root_account = self.accounts.create_new_root_account(
                mnemonic,
                language_code,
                crypto_type,
                name,
                password,
                add_event=False,
            )
            root_account.balance = self.accounts.network_get_balance(
                root_account.address
            )
            self.accounts.update(root_account)

        self.import_derived_account_from_network(
            root_account, mnemonic, language_code, crypto_type, name, password
        )

    def import_derived_account_from_network(
        self,
        root_account: Account,
        mnemonic: str,
        language_code: str,
        crypto_type: AccountCryptoType,
        name: str,
        password: str,
    ):
        """
        Import derived account from network for root_account

        :param crypto_type:
        :param root_account: Root Account instance
        :param mnemonic: Mnemonic phrase
        :param language_code: Mnemonic language code
        :param crypto_type: Key type as AccountCryptoType instance
        :param name: Root account name
        :param password: Vault/Root account password

        :return:
        """
        derived_accounts = []
        addresses = []
        for derivation_number in range(0, DERIVATION_SCAN_MAX_NUMBER + 1):
            derivation = f"//{derivation_number}"
            suri = mnemonic + derivation
            keypair = Keypair.create_from_uri(
                suri,
                language_code=language_code,
                ss58_format=self.currencies.get_current().ss58_format,
                crypto_type=crypto_type,
            )
            derived_account = self.accounts.get_instance(
                keypair.ss58_address, f"{name}{derivation}"
            )
            derived_account.path = derivation
            derived_accounts.append(derived_account)
            addresses.append(keypair.ss58_address)

        balances = self.accounts.network_get_balances(addresses)

        for derived_account in derived_accounts:
            if balances[derived_account.address] is not None:
                existing_account = self.accounts.get_by_address(derived_account.address)
                if existing_account is not None:
                    existing_account.root = root_account.address
                    self.accounts.repository.update(existing_account)
                else:
                    balance = balances[derived_account.address]
                    if balance is not None:
                        account = self.accounts.create_new_account(
                            mnemonic,
                            language_code,
                            derived_account.path or "",
                            crypto_type,
                            derived_account.name or "",
                            password,
                        )
                        account.balance = balance
                        self.accounts.repository.update(account)
            else:
                self.accounts.repository.delete(derived_account.address)

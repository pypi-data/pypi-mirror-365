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
import sys
from typing import Optional

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from scalecodec.utils.ss58 import is_valid_ss58_address

from tikka.domains.application import Application
from tikka.domains.entities.account import Account, AccountCryptoType
from tikka.domains.entities.address import DisplayAddress
from tikka.domains.entities.constants import DATA_PATH
from tikka.libs import crypto_type
from tikka.libs.keypair import Keypair
from tikka.slots.pyqt.entities.constants import ADDRESS_MONOSPACE_FONT_NAME
from tikka.slots.pyqt.resources.gui.windows.address_add_rc import Ui_AddressAddDialog


class AddressAddWindow(QDialog, Ui_AddressAddDialog):
    """
    AddressAddWindow class
    """

    display_crypto_type = {
        AccountCryptoType.ED25519: "ED25519",
        AccountCryptoType.SR25519: "SR25519",
    }

    def __init__(self, application: Application, parent: Optional[QWidget] = None):
        """
        Init add address window

        :param application: Application instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext
        self.crypto_type = AccountCryptoType.ED25519

        # set monospace font to address field
        monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        monospace_font.setStyleHint(QFont.Monospace)
        self.addressLineEdit.setFont(monospace_font)

        # buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        # events
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.addressLineEdit.textChanged.connect(self.on_address_line_edit_changed)
        self.buttonBox.rejected.connect(self.close)

    def _normalize_address_field(self) -> Optional[DisplayAddress]:
        """
        Validate and convert address field to DisplayAddress instance

        :return:
        """
        self.errorLabel.setText("")
        address = self.addressLineEdit.text()
        if not is_valid_ss58_address(address):
            self.errorLabel.setText(self._("Account address is not valid!"))
            self.keyTypeValueLabel.setText("")
            return None
        keypair = Keypair(address)
        try:
            result = crypto_type.is_valid_ed25519(keypair.public_key)
        except AttributeError:
            result = False
        except AssertionError:
            result = False

        if result is True:
            self.crypto_type = AccountCryptoType.ED25519
            self.keyTypeValueLabel.setText(
                self.display_crypto_type[AccountCryptoType.ED25519]
            )
        else:
            try:
                result = crypto_type.is_valid_sr25519(keypair.public_key)
            except AttributeError:
                result = False
            except AssertionError:
                result = False
            if result is True:
                self.crypto_type = AccountCryptoType.SR25519
                self.keyTypeValueLabel.setText(
                    self.display_crypto_type[AccountCryptoType.SR25519]
                )

        # create account instance
        account = Account(address)
        for existing_account in self.application.accounts.get_list():
            if account == existing_account:
                self.errorLabel.setText(self._("Account already exists!"))
                return None

        return DisplayAddress(address)

    def on_address_line_edit_changed(self) -> None:
        """
        Triggered when the address field is changed

        :return:
        """
        display_address = self._normalize_address_field()
        if display_address is not None:
            self.errorLabel.setText("")
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

    def on_accepted_button(self) -> None:
        """
        Triggered when user click on ok button

        :return:
        """
        display_address = self._normalize_address_field()
        if display_address is not None:
            # create account instance
            account = Account(display_address.address, crypto_type=self.crypto_type)

            # add instance in application
            self.application.accounts.add(account)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    AddressAddWindow(application_).exec_()

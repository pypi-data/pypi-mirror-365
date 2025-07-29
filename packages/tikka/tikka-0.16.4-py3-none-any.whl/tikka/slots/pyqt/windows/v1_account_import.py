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
import logging
import sys
from typing import Optional

from PyQt5.QtCore import QMutex, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account, AccountCryptoType
from tikka.domains.entities.constants import DATA_PATH, WALLETS_PASSWORD_LENGTH
from tikka.libs.keypair import Keypair
from tikka.libs.secret import generate_alphabetic
from tikka.libs.signing_key_v1 import SigningKey
from tikka.slots.pyqt.entities.constants import (
    ADDRESS_MONOSPACE_FONT_NAME,
    DEBOUNCE_TIME,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.windows.v1_account_import_rc import (
    Ui_V1AccountImportDialog,
)


class V1AccountImportWindow(QDialog, Ui_V1AccountImportDialog):
    """
    V1AccountImportWindow class
    """

    def __init__(
        self, application: Application, mutex: QMutex, parent: Optional[QWidget] = None
    ):
        """
        Init import V1 account window

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext
        self.mutex = mutex
        self.is_legacy_v1: Optional[bool] = None

        # set monospace font to address fields
        monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        monospace_font.setStyleHint(QFont.Monospace)
        self.addressValueLabel.setFont(monospace_font)
        self.v1AddressValueLabel.setFont(monospace_font)

        # buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        # events
        self.secretIDLineEdit.textChanged.connect(self._on_secret_id_line_edit_changed)
        self.passwordIDLineEdit.textChanged.connect(
            self._on_password_id_line_edit_changed
        )

        self.showButton.clicked.connect(self.on_show_button_clicked)
        self.passwordChangeButton.clicked.connect(self._generate_wallet_password)
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.close)

        # debounce timer on self._generate_address()
        self.debounce_timer = QTimer()
        self.debounce_timer.timeout.connect(self._generate_address)
        # Create a QWorker object
        self.network_check_legacy_v1_async_qworker = AsyncQWorker(
            self.network_check_legacy_v1, self.mutex
        )
        self.network_check_legacy_v1_async_qworker.finished.connect(
            self._on_finished_network_check_legacy_v1
        )

        # fill form
        self._generate_wallet_password()

    def _on_secret_id_line_edit_changed(self):
        """
        Triggered when text is changed in the secret ID field

        :return:
        """
        if self.debounce_timer.isActive():
            self.debounce_timer.stop()
        self.debounce_timer.start(DEBOUNCE_TIME)

    def _on_password_id_line_edit_changed(self):
        """
        Triggered when text is changed in the password ID field

        :return:
        """
        if self.debounce_timer.isActive():
            self.debounce_timer.stop()
        self.debounce_timer.start(DEBOUNCE_TIME)

    def _generate_address(self):
        """
        Generate address from ID

        :return:
        """
        # stop debounce_timer to avoid infinite loop
        if self.debounce_timer.isActive():
            self.debounce_timer.stop()

        self.v1AddressValueLabel.setText("")
        self.addressValueLabel.setText("")
        self.errorLabel.setText("")
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        secret_id = self.secretIDLineEdit.text().strip()
        password_id = self.passwordIDLineEdit.text().strip()
        if secret_id == "" or password_id == "":
            return

        signing_key = SigningKey.from_credentials(secret_id, password_id)
        try:
            address = Keypair.create_from_seed(
                seed_hex=signing_key.seed.hex(),
                ss58_format=self.application.currencies.get_current().ss58_format,
                crypto_type=AccountCryptoType.ED25519,
            ).ss58_address
        except Exception as exception:
            logging.exception(exception)
            self.errorLabel.setText(self._("Error generating account wallet!"))
            return

        self.addressValueLabel.setText(address)
        self.v1AddressValueLabel.setText(
            Account(address).get_v1_address(
                self.application.currencies.get_current().ss58_format
            )
        )

        if self.application.accounts.get_by_address(address) is not None:
            self.errorLabel.setText(self._("Account already exists!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
        else:
            self.errorLabel.setText("")
            self.network_check_legacy_v1_async_qworker.start()

    def on_show_button_clicked(self):
        """
        Triggered when user click on show button

        :return:
        """
        if self.secretIDLineEdit.echoMode() == QLineEdit.Password:
            self.secretIDLineEdit.setEchoMode(QLineEdit.Normal)
            self.passwordIDLineEdit.setEchoMode(QLineEdit.Normal)
            self.showButton.setText(self._("Hide"))
        else:
            self.secretIDLineEdit.setEchoMode(QLineEdit.Password)
            self.passwordIDLineEdit.setEchoMode(QLineEdit.Password)
            self.showButton.setText(self._("Show"))

    def _generate_wallet_password(self):
        """
        Generate new password for wallet encryption in UI

        :return:
        """
        self.passwordLineEdit.setText(generate_alphabetic(WALLETS_PASSWORD_LENGTH))

    def network_check_legacy_v1(self):
        """
        Check if account is really a known legacy v1 account

        :return:
        """
        address = self.addressValueLabel.text().strip()
        try:
            self.is_legacy_v1 = self.application.accounts.network_is_legacy_v1(address)
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)

    def _on_finished_network_check_legacy_v1(self):
        """
        Triggered when async request network_check_legacy_v1 is finished

        :return:
        """
        if self.is_legacy_v1 is not None:
            if not self.is_legacy_v1:
                self.errorLabel.setText(self._("V1 account unknown!"))
                self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            else:
                self.errorLabel.setText("")
                self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)

    def on_accepted_button(self):
        """
        Triggered when user click on ok button

        :return:
        """
        secret_id = self.secretIDLineEdit.text().strip()
        password_id = self.passwordIDLineEdit.text().strip()
        password = self.passwordLineEdit.text()
        name = self.nameLineEdit.text().strip()

        self.application.accounts.create_new_root_account_v1_from_credentials(
            secret_id, password_id, name, password
        )


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    V1AccountImportWindow(application_, QMutex()).exec_()

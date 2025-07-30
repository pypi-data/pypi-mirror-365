from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QLabel, QWidget

from PySideJZ.JZAbvs import JZAbvs


class JZLabel(QLabel):
    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(text=text, parent=parent)
        self.setSizePolicy(JZAbvs.Policy.MAX, JZAbvs.Policy.MINEX)
        self.setWordWrap(True)


class JZStatusLabel(QLabel):
    """A label that is used for status display, such as 'Connected', 'Disconnected', etc.

    Has connected signals that change stylesheet of the label (takes it from QSS file).
    Therefore, QSS file must be loaded when using this class, otherwise the colorings
    will not work.
    """

    class Status:
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"
        CONNECTING = "Connecting"
        NEUTRAL = "Neutral"
        INFO = "Info"

    connected = Signal()
    disconnected = Signal()
    connecting = Signal()
    neutral = Signal()
    info = Signal()

    def __init__(self, parent: QWidget, default_status: str = Status.NEUTRAL) -> None:
        super().__init__(parent=parent)
        self.setObjectName("StatusLabel")
        self.setSizePolicy(JZAbvs.Policy.MAX, JZAbvs.Policy.MINEX)
        self.setWordWrap(True)
        self.status = default_status

        self.connected.connect(self._on_connected)
        self.disconnected.connect(self._on_disconnected)
        self.connecting.connect(self._on_connecting)
        self.neutral.connect(self._on_neutral)
        self.info.connect(self._on_info)

        match default_status:
            case self.Status.CONNECTED: self.connected.emit()  # noqa: E701
            case self.Status.DISCONNECTED: self.disconnected.emit()  # noqa: E701
            case self.Status.CONNECTING: self.connecting.emit()  # noqa: E701
            case self.Status.NEUTRAL: self.neutral.emit()  # noqa: E701
            case self.Status.INFO: self.info.emit()  # noqa: E701
            case _: raise ValueError(f"Unknown status for JZStatusLabel: {default_status}")  # noqa: E701

    @Slot()
    def _on_connected(self) -> None:
        self.setProperty("onLabelStatus", "On")
        self.style().polish(self)
        self.setText("Connected")

    @Slot()
    def _on_disconnected(self) -> None:
        self.setProperty("onLabelStatus", "Off")
        self.style().polish(self)
        self.setText("Disconnected")

    @Slot()
    def _on_connecting(self) -> None:
        self.setProperty("onLabelStatus", "Ongoing")
        self.style().polish(self)
        self.setText("Connecting")

    @Slot()
    def _on_neutral(self) -> None:
        self.setProperty("onLabelStatus", "Neutral")
        self.style().polish(self)
        self.setText("Disconnected")

    @Slot()
    def _on_info(self) -> None:
        self.setProperty("onLabelStatus", "Info")
        self.style().polish(self)
        self.setText("Disconnected")

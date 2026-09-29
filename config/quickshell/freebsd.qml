//@ pragma UseQApplication
pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import qs.core
import qs.state
import qs.launcher
import qs.notifications
import qs.panel

ShellRoot {
    id: desktop
    property var nativeState: ({})
    property string nativeError: ""
    property bool controlsVisible: false
    Component.onCompleted: { Theme.fontFamily = "Noto Sans"; desktop.refresh(); }

    function refresh() {
        if (!provider.running) {
            provider.command = ["dwm-freebsd-provider", "snapshot"];
            provider.running = true;
        }
    }
    function audio(action, value) {
        if (provider.running) return;
        provider.command = value === undefined ? ["dwm-freebsd-provider", action]
            : ["dwm-freebsd-provider", action, value.toString()];
        provider.running = true;
    }
    DwmState { id: dwmState }
    ClockModel { id: clock }
    LauncherModel { id: appsModel }
    NotificationModel { id: notices }
    LauncherWindow { launcherModel: appsModel }
    NotificationPopupWindow { notificationModel: notices; panelWindow: panel }
    NotificationHistoryWindow { notificationModel: notices }

    Process {
        id: provider
        stdout: StdioCollector {
            onStreamFinished: {
                try { desktop.nativeState = JSON.parse(text); desktop.nativeError = ""; }
                catch (error) { desktop.nativeError = "Native status unavailable"; }
            }
        }
        onExited: (code, status) => { if (code !== 0) desktop.nativeError = "Native control failed; check session log"; }
    }
    // FreeBSD mixer has no subscription interface used here. Only sample while
    // controls are open; hidden controls do not spawn periodic processes.
    Timer { interval: 3000; repeat: true; running: desktop.controlsVisible; onTriggered: desktop.refresh() }
    IpcHandler {
        target: "desktop"
        function launcher(): void { appsModel.toggle(); }
        function controls(): void { desktop.controlsVisible = !desktop.controlsVisible; desktop.refresh(); }
        function notifications(): void { notices.toggleHistory(); }
        function activeTitle(): string { return dwmState.activeWindowTitle; }
        function workspace(): int { return dwmState.currentWorkspace; }
        function applicationCount(): int { return appsModel.apps.length; }
        function notificationCount(): int { return notices.history.length; }
    }

    component Action: Rectangle {
        property string label
        signal triggered()
        implicitWidth: caption.implicitWidth + 22
        implicitHeight: 30
        radius: 5
        color: pointer.containsMouse ? "#3b5166" : "#233244"
        Text { id: caption; anchors.centerIn: parent; text: parent.label; color: "#dce6f2"; font.pixelSize: 13 }
        MouseArea { id: pointer; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: parent.triggered() }
    }
    PanelWindow {
        id: panel
        anchors { top: true; left: true; right: true }
        implicitHeight: 42
        exclusiveZone: 42
        color: "#18212f"
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 10; anchors.rightMargin: 10
            spacing: 7
            Action { label: "C9 / Apps"; onTriggered: appsModel.toggle() }
            Repeater {
                model: dwmState.workspaceNames
                delegate: WorkspaceButton {
                    required property int index
                    required property string modelData
                    label: modelData
                    selected: dwmState.currentWorkspace === index
                    occupied: dwmState.workspaceOccupied(index)
                    onClicked: dwmState.switchWorkspace(index)
                }
            }
            Text {
                Layout.fillWidth: true
                Layout.minimumWidth: 20
                text: dwmState.activeWindowTitle
                elide: Text.ElideRight
                color: "#dce6f2"; font.pixelSize: 13
            }
            TrayArea {}
            Action { label: "Notifications"; onTriggered: notices.toggleHistory() }
            Action {
                label: "System"
                onTriggered: { desktop.controlsVisible = !desktop.controlsVisible; desktop.refresh(); }
            }
            Text { text: clock.panelText; color: "#72d6c9"; font.pixelSize: 13 }
        }
    }
    FloatingWindow {
        id: controls
        title: "C9 FreeBSD controls"
        visible: desktop.controlsVisible
        implicitWidth: 560; implicitHeight: 450
        color: "#18212f"
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 24; spacing: 14
            focus: true
            Keys.onEscapePressed: desktop.controlsVisible = false
            Text { text: "FreeBSD / System"; font.pixelSize: 24; color: "#72d6c9" }
            Text {
                Layout.fillWidth: true; wrapMode: Text.Wrap
                text: (desktop.nativeState.hostname || "") + "   Load " + (desktop.nativeState.load ?? "-")
                    + "\nNetwork: " + ((desktop.nativeState.network || []).join(", ") || "No IPv4 address")
                    + "\nBattery: " + (desktop.nativeState.battery === null || desktop.nativeState.battery === undefined
                        ? "Not available" : desktop.nativeState.battery + "%")
                color: "#dce6f2"; font.pixelSize: 14
            }
            Text {
                text: desktop.nativeState.volume === null || desktop.nativeState.volume === undefined
                    ? "Audio device unavailable" : "Volume " + desktop.nativeState.volume + "%" + (desktop.nativeState.muted ? " (muted)" : "")
                color: "#dce6f2"; font.pixelSize: 16
            }
            RowLayout {
                enabled: desktop.nativeState.volume !== null && desktop.nativeState.volume !== undefined
                Action { label: "- 5%"; onTriggered: desktop.audio("volume", Math.max(0, desktop.nativeState.volume - 5)) }
                Action { label: "+ 5%"; onTriggered: desktop.audio("volume", Math.min(100, desktop.nativeState.volume + 5)) }
                Action { label: "Mute / unmute"; onTriggered: desktop.audio("mute") }
            }
            Text {
                Layout.fillWidth: true; wrapMode: Text.Wrap
                text: "Network status is read-only. Wi-Fi configuration, Bluetooth, brightness and suspend are not supported in this native profile."
                color: "#aab8cb"; font.pixelSize: 13
            }
            Text { text: desktop.nativeError; color: "#f0a080"; Layout.fillWidth: true; wrapMode: Text.Wrap }
            Item { Layout.fillHeight: true }
            RowLayout {
                Action { label: "Terminal"; onTriggered: Quickshell.execDetached(["dwm-terminal"]) }
                Action { label: "System monitor"; onTriggered: Quickshell.execDetached(["dwm-terminal", "-e", "top"]) }
                Action { label: "Close"; onTriggered: desktop.controlsVisible = false }
            }
        }
    }
}

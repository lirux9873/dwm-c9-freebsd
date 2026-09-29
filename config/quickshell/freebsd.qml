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
    property string activeTheme: ""
    property bool controlsVisible: false
    readonly property string configHome: Quickshell.env("XDG_CONFIG_HOME")
    readonly property string themePath: configHome + "/dwm-titus/native-theme.json"
    Component.onCompleted: { Theme.fontFamily = "Noto Sans"; desktop.refresh(); themeFile.reload(); }

    function loadTheme() {
        try {
            const record = JSON.parse(themeFile.text());
            const colors = record.colors;
            desktop.activeTheme = record.name || "";
            Theme.applyAppearanceColors(colors, colors.dark !== false);
        } catch (error) {
            desktop.nativeError = "Native theme could not be loaded";
        }
    }

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
    function setTheme(name) {
        if (appearance.running) return;
        appearance.command = ["dwm-freebsd-appearance", "theme", name];
        appearance.running = true;
    }
    DwmState { id: dwmState }
    ClockModel { id: clock }
    LauncherModel { id: appsModel }
    NotificationModel { id: notices }
    LauncherWindow { launcherModel: appsModel }
    NotificationPopupWindow { notificationModel: notices; panelWindow: panel }
    NotificationHistoryWindow { notificationModel: notices }
    FileView {
        id: themeFile
        path: desktop.themePath
        watchChanges: true
        printErrors: false
        onLoaded: desktop.loadTheme()
        onFileChanged: reload()
    }

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
    Process {
        id: appearance
        onExited: (code, status) => {
            if (code !== 0) desktop.nativeError = "Theme change failed; check session log";
            else themeFile.reload();
        }
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
        function theme(name: string): void { desktop.setTheme(name); }
        function themeName(): string { return desktop.activeTheme; }
    }

    component Action: Rectangle {
        property string label
        signal triggered()
        implicitWidth: caption.implicitWidth + 22
        implicitHeight: 30
        radius: 5
        color: pointer.containsMouse ? Theme.controlHoverFill : Theme.controlNormalFill
        border.color: pointer.containsMouse ? Theme.controlHoverBorder : Theme.controlNormalBorder
        border.width: 1
        Text { id: caption; anchors.centerIn: parent; text: parent.label; color: Theme.controlNormalText; font.pixelSize: 13 }
        MouseArea { id: pointer; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: parent.triggered() }
    }
    PanelWindow {
        id: panel
        anchors { top: true; left: true; right: true }
        implicitHeight: 42
        exclusiveZone: 42
        color: Theme.barBackground
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
                color: Theme.text; font.pixelSize: 13
            }
            TrayArea {}
            Action { label: "Notifications"; onTriggered: notices.toggleHistory() }
            Action {
                label: "System"
                onTriggered: { desktop.controlsVisible = !desktop.controlsVisible; desktop.refresh(); }
            }
            Text { text: clock.panelText; color: Theme.accent; font.pixelSize: 13 }
        }
    }
    FloatingWindow {
        id: controls
        title: "C9 FreeBSD controls"
        visible: desktop.controlsVisible
        implicitWidth: 560; implicitHeight: 450
        color: Theme.bg
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 24; spacing: 14
            focus: true
            Keys.onEscapePressed: desktop.controlsVisible = false
            Text { text: "FreeBSD / System"; font.pixelSize: 24; color: Theme.accent }
            Text {
                Layout.fillWidth: true; wrapMode: Text.Wrap
                text: (desktop.nativeState.hostname || "") + "   Load " + (desktop.nativeState.load ?? "-")
                    + "\nNetwork: " + ((desktop.nativeState.network || []).join(", ") || "No IPv4 address")
                    + "\nBattery: " + (desktop.nativeState.battery === null || desktop.nativeState.battery === undefined
                        ? "Not available" : desktop.nativeState.battery + "%")
                color: Theme.text; font.pixelSize: 14
            }
            Text {
                text: desktop.nativeState.volume === null || desktop.nativeState.volume === undefined
                    ? "Audio device unavailable" : "Volume " + desktop.nativeState.volume + "%" + (desktop.nativeState.muted ? " (muted)" : "")
                color: Theme.text; font.pixelSize: 16
            }
            Text { text: "Theme " + (desktop.activeTheme || "default"); color: Theme.text; font.pixelSize: 16 }
            RowLayout {
                Action { label: "Nord"; onTriggered: desktop.setTheme("nord") }
                Action { label: "Dracula"; onTriggered: desktop.setTheme("dracula") }
                Action { label: "Gruvbox"; onTriggered: desktop.setTheme("gruvbox") }
                Action { label: "Tokyo Night"; onTriggered: desktop.setTheme("tokyonight") }
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
                color: Theme.textMuted; font.pixelSize: 13
            }
            Text { text: desktop.nativeError; color: Theme.danger; Layout.fillWidth: true; wrapMode: Text.Wrap }
            Item { Layout.fillHeight: true }
            RowLayout {
                Action { label: "Terminal"; onTriggered: Quickshell.execDetached(["dwm-terminal"]) }
                Action { label: "System monitor"; onTriggered: Quickshell.execDetached(["dwm-terminal", "-e", "top"]) }
                Action { label: "Close"; onTriggered: desktop.controlsVisible = false }
            }
        }
    }
}

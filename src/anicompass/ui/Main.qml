import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: root
    objectName: "appShell"

    width: 1080
    height: 700
    minimumWidth: 820
    minimumHeight: 560
    visible: true
    title: "AniCompass"
    color: root.windowBg

    readonly property string language: settingsService.language
    readonly property int currentPage: settingsService.currentPage
    readonly property int accentRed: settingsService.accentRed
    readonly property int accentGreen: settingsService.accentGreen
    readonly property int accentBlue: settingsService.accentBlue

    readonly property var navItems: [
        { "key": "recommend", "icon": "*" },
        { "key": "search", "icon": ">" },
        { "key": "list", "icon": "+" },
        { "key": "history", "icon": "~" },
        { "key": "settings", "icon": "#" }
    ]
    readonly property color accent: Qt.rgba(root.accentRed / 255, root.accentGreen / 255, root.accentBlue / 255, 1)
    readonly property color accentSoft: Qt.rgba(root.accentRed / 255, root.accentGreen / 255, root.accentBlue / 255, 0.12)
    readonly property color textStrong: "#17202A"
    readonly property color textMuted: "#5C6672"
    readonly property color line: "#D9DEE7"
    readonly property color surface: "#FFFFFF"
    readonly property color windowBg: "#F5F7FA"



    function selectPage(index) {
        if (index >= 0 && index < navItems.length) {
            settingsService.setCurrentPage(index)
        }
    }

    function setLanguage(code) {
        settingsService.setLanguage(code)
    }

    function setAccentColor(red, green, blue) {
        settingsService.setAccentColor(red, green, blue)
    }

    function syncSettings() {
        settingsService.sync()
    }

    function copyFor(key) {
        const zh = {
            appSubtitle: "\u52a8\u6f2b\u63a8\u8350\u4e0e\u8ffd\u756a\u5de5\u4f5c\u53f0",
            recommend: "\u63a8\u8350",
            search: "\u641c\u7d22",
            list: "\u7247\u5355",
            history: "\u5386\u53f2",
            settings: "\u8bbe\u7f6e",
            recommendTitle: "\u63a8\u8350\u5de5\u4f5c\u53f0",
            recommendEmpty: "\u8f93\u5165\u504f\u597d\uff0c\u751f\u6210\u5e76\u6821\u9a8c\u771f\u5b9e\u76ee\u5f55\u63a8\u8350\u3002",
            searchTitle: "\u52a8\u6f2b\u641c\u7d22",
            searchEmpty: "\u8f93\u5165\u52a8\u6f2b\u540d\u79f0\uff0c\u4ece Jikan \u641c\u7d22\u771f\u5b9e\u76ee\u5f55\u3002",
            listTitle: "\u6211\u7684\u7247\u5355",
            listEmpty: "\u8fd9\u91cc\u5c06\u7ba1\u7406\u60f3\u770b\u3001\u5728\u770b\u3001\u5df2\u5b8c\u6210\u7684\u672c\u5730\u8bb0\u5f55\u3002",
            historyTitle: "\u63a8\u8350\u5386\u53f2",
            historyEmpty: "\u8fd9\u91cc\u5c06\u4fdd\u5b58\u6700\u8fd1\u786e\u8ba4\u8fc7\u7684\u63a8\u8350\u4f1a\u8bdd\u3002",
            settingsTitle: "\u504f\u597d\u8bbe\u7f6e",
            settingsEmpty: "\u8bed\u8a00\u4e0e\u4e3b\u9898\u8272\u4f1a\u4fdd\u5b58\u5728\u672c\u673a\u975e\u654f\u611f\u8bbe\u7f6e\u4e2d\u3002",
            language: "\u8bed\u8a00",
            theme: "\u4e3b\u9898\u8272",
            red: "\u7ea2",
            green: "\u7eff",
            blue: "\u84dd",
            stateEmpty: "\u7a7a\u72b6\u6001",
            stateLoading: "\u52a0\u8f7d\u72b6\u6001",
            stateError: "\u9519\u8bef\u72b6\u6001",
            stateMissingConfig: "\u7f3a\u5c11\u914d\u7f6e",
            preferenceInput: "\u60f3\u770b\u4ec0\u4e48\u98ce\u683c\u6216\u60c5\u7eea",
            recommendAction: "\u751f\u6210\u63a8\u8350",
            countLabel: "\u6570\u91cf",
            unresolvedLabel: "\u672a\u5339\u914d",
            searchInput: "\u641c\u7d22\u52a8\u6f2b\u6807\u9898",
            searchAction: "\u641c\u7d22",
            sourceLabel: "\u6765\u6e90",
            scoreLabel: "\u8bc4\u5206",
            episodesLabel: "\u96c6\u6570",
            detailTitle: "\u8be6\u60c5",
            detailEmpty: "\u9009\u62e9\u4e00\u4e2a\u641c\u7d22\u7ed3\u679c\u67e5\u770b\u8be6\u60c5\u3002",
            ratingLabel: "\u5206\u7ea7",
            studiosLabel: "\u5236\u4f5c",
            addToList: "\u52a0\u5165\u7247\u5355",
            allItems: "\u5168\u90e8",
            planToWatch: "\u60f3\u770b",
            watching: "\u5728\u770b",
            completed: "\u5df2\u5b8c\u6210",
            remove: "\u5220\u9664",
            save: "\u4fdd\u5b58",
            notes: "\u5907\u6ce8",
            aiProvider: "AI \u63d0\u4f9b\u5546",
            apiKey: "API Key",
            saveApiKey: "\u4fdd\u5b58 Key",
            deleteApiKey: "\u5220\u9664 Key",
            testConnection: "\u6d4b\u8bd5\u8fde\u63a5",
            backupTitle: "\u672c\u5730\u5907\u4efd",
            exportBackup: "\u5bfc\u51fa\u5907\u4efd",
            importBackup: "\u6062\u590d\u5907\u4efd",
            backupDialogTitle: "\u9009\u62e9\u5907\u4efd\u6587\u4ef6",
            backupSaveTitle: "\u4fdd\u5b58\u5907\u4efd\u6587\u4ef6",
            phase: "Phase 3 \u672c\u5730\u7247\u5355"
        }
        const en = {
            appSubtitle: "Anime recommendation and watch-list workspace",
            recommend: "Recommend",
            search: "Search",
            list: "My List",
            history: "History",
            settings: "Settings",
            recommendTitle: "Recommendation Workspace",
            recommendEmpty: "Enter preferences and generate catalog-verified recommendations.",
            searchTitle: "Anime Search",
            searchEmpty: "Enter an anime title and search the real Jikan catalog.",
            listTitle: "My Watch List",
            listEmpty: "Local plan-to-watch, watching, and completed records will live here.",
            historyTitle: "Recommendation History",
            historyEmpty: "Recent verified recommendation sessions will live here.",
            settingsTitle: "Preferences",
            settingsEmpty: "Language and theme color are stored as local non-secret settings.",
            language: "Language",
            theme: "Theme Color",
            red: "Red",
            green: "Green",
            blue: "Blue",
            stateEmpty: "Empty",
            stateLoading: "Loading",
            stateError: "Error",
            stateMissingConfig: "Missing Config",
            preferenceInput: "Mood, genre, pacing, or favorites",
            recommendAction: "Recommend",
            countLabel: "Count",
            unresolvedLabel: "Unmatched",
            searchInput: "Search anime title",
            searchAction: "Search",
            sourceLabel: "Source",
            scoreLabel: "Score",
            episodesLabel: "Episodes",
            detailTitle: "Details",
            detailEmpty: "Select a search result to view details.",
            ratingLabel: "Rating",
            studiosLabel: "Studios",
            addToList: "Add to List",
            allItems: "All",
            planToWatch: "Plan",
            watching: "Watching",
            completed: "Completed",
            remove: "Delete",
            save: "Save",
            notes: "Notes",
            aiProvider: "AI Provider",
            apiKey: "API Key",
            saveApiKey: "Save Key",
            deleteApiKey: "Delete Key",
            testConnection: "Test",
            backupTitle: "Local Backup",
            exportBackup: "Export",
            importBackup: "Restore",
            backupDialogTitle: "Choose Backup File",
            backupSaveTitle: "Save Backup File",
            phase: "Phase 3 Local List"
        }
        return root.language === "zh" ? zh[key] : en[key]
    }

    component StateBadge: Rectangle {
        required property string label
        required property bool selected

        Layout.preferredWidth: 132
        Layout.preferredHeight: 34
        radius: 8
        color: selected ? root.accentSoft : "#F1F4F8"
        border.color: selected ? root.accent : root.line

        Text {
            anchors.centerIn: parent
            width: parent.width - 16
            text: parent.label
            color: parent.selected ? root.accent : root.textMuted
            font.pixelSize: 12
            font.bold: parent.selected
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }
    }

    component ColorSliderRow: RowLayout {
        required property string label
        required property int channelValue
        signal changed(int newValue)

        Text {
            Layout.preferredWidth: 52
            text: label
            color: root.textMuted
            font.pixelSize: 12
            elide: Text.ElideRight
        }

        Slider {
            Layout.fillWidth: true
            from: 0
            to: 255
            stepSize: 1
            value: parent.channelValue
            onMoved: parent.changed(Math.round(value))
        }

        Text {
            Layout.preferredWidth: 34
            text: parent.channelValue
            color: root.textMuted
            font.pixelSize: 12
            horizontalAlignment: Text.AlignRight
        }
    }

    component PageBody: Item {
        required property string titleKey
        required property string emptyKey
        property bool isSettingsPage: false
        property bool isSearchPage: false
        property bool isListPage: false
        property bool isRecommendPage: false
        property bool isHistoryPage: false

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 28
            spacing: 20

            RowLayout {
                Layout.fillWidth: true
                spacing: 14

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4

                    Text {
                        objectName: "pageTitle_" + titleKey
                        Layout.fillWidth: true
                        text: root.copyFor(titleKey)
                        color: root.textStrong
                        font.pixelSize: 28
                        font.bold: true
                        elide: Text.ElideRight
                    }

                    Text {
                        Layout.fillWidth: true
                        text: root.copyFor(emptyKey)
                        color: root.textMuted
                        font.pixelSize: 14
                        wrapMode: Text.WordWrap
                    }
                }

                ComboBox {
                    Layout.preferredWidth: 120
                    model: ["\u4e2d\u6587", "English"]
                    currentIndex: root.language === "zh" ? 0 : 1
                    onActivated: function(index) {
                        root.setLanguage(index === 0 ? "zh" : "en")
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 8
                color: root.surface
                border.color: root.line

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 22
                    spacing: 18

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        StateBadge { label: root.copyFor("stateEmpty"); selected: true }
                        StateBadge { label: root.copyFor("stateLoading"); selected: false }
                        StateBadge { label: root.copyFor("stateError"); selected: false }
                        StateBadge { label: root.copyFor("stateMissingConfig"); selected: false }
                    }

                    Loader {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        sourceComponent: isSettingsPage ? settingsPanel : (isSearchPage ? searchPanel : (isListPage ? listPanel : (isRecommendPage ? recommendPanel : (isHistoryPage ? historyPanel : emptyPanel))))
                    }
                }
            }
        }
    }
    Rectangle {
        anchors.fill: parent
        color: root.windowBg

        RowLayout {
            anchors.fill: parent
            spacing: 0

            Rectangle {
                Layout.fillHeight: true
                Layout.preferredWidth: 236
                Layout.minimumWidth: 236
                color: root.surface
                border.color: root.line
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 18

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4

                        Text {
                            Layout.fillWidth: true
                            text: "AniCompass"
                            color: root.textStrong
                            font.pixelSize: 26
                            font.bold: true
                            elide: Text.ElideRight
                        }

                        Text {
                            Layout.fillWidth: true
                            text: root.copyFor("appSubtitle")
                            color: root.textMuted
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Repeater {
                            model: root.navItems

                            Button {
                                id: navButton
                                required property int index
                                required property var modelData

                                objectName: "navButton_" + modelData.key
                                Layout.fillWidth: true
                                Layout.preferredHeight: 42
                                text: modelData.icon + "  " + root.copyFor(modelData.key)
                                highlighted: root.currentPage === index
                                onClicked: root.selectPage(index)

                                contentItem: Text {
                                    text: navButton.text
                                    color: navButton.highlighted ? root.accent : root.textStrong
                                    font.pixelSize: 14
                                    font.bold: navButton.highlighted
                                    elide: Text.ElideRight
                                    verticalAlignment: Text.AlignVCenter
                                }

                                background: Rectangle {
                                    radius: 8
                                    color: navButton.highlighted ? root.accentSoft : "transparent"
                                    border.color: navButton.activeFocus ? root.accent : "transparent"
                                    border.width: 2
                                }
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 44
                        radius: 8
                        color: root.accentSoft

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 8

                            Rectangle {
                                Layout.preferredWidth: 24
                                Layout.preferredHeight: 24
                                radius: 12
                                color: root.accent
                            }

                            Text {
                                Layout.fillWidth: true
                                text: root.copyFor("phase")
                                color: root.textStrong
                                font.pixelSize: 12
                                elide: Text.ElideRight
                            }
                        }
                    }
                }
            }

            StackLayout {
                objectName: "pageStack"
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: root.currentPage

                PageBody {
                    titleKey: "recommendTitle"
                    emptyKey: "recommendEmpty"
                    isRecommendPage: true
                }

                PageBody {
                    titleKey: "searchTitle"
                    emptyKey: "searchEmpty"
                    isSearchPage: true
                }

                PageBody {
                    titleKey: "listTitle"
                    emptyKey: "listEmpty"
                    isListPage: true
                }

                PageBody {
                    titleKey: "historyTitle"
                    emptyKey: "historyEmpty"
                    isHistoryPage: true
                }

                PageBody {
                    titleKey: "settingsTitle"
                    emptyKey: "settingsEmpty"
                    isSettingsPage: true
                }
            }
        }
    }

    Component {
        id: emptyPanel

        Item {
            Text {
                anchors.centerIn: parent
                width: Math.min(parent.width - 40, 520)
                text: root.copyFor("stateEmpty")
                color: root.textMuted
                font.pixelSize: 20
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
            }
        }
    }


    Component {
        id: recommendPanel

        ColumnLayout {
            spacing: 14

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                TextArea {
                    id: recommendPreferenceInput
                    objectName: "recommendPreferenceInput"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 76
                    placeholderText: root.copyFor("preferenceInput")
                    wrapMode: TextArea.Wrap
                    enabled: !recommendBridge.isBusy
                }

                ColumnLayout {
                    Layout.preferredWidth: 120
                    spacing: 8

                    Text {
                        Layout.fillWidth: true
                        text: root.copyFor("countLabel")
                        color: root.textMuted
                        font.pixelSize: 12
                    }

                    SpinBox {
                        id: recommendCountInput
                        objectName: "recommendCountInput"
                        Layout.fillWidth: true
                        from: 1
                        to: 10
                        value: 5
                        enabled: !recommendBridge.isBusy
                    }

                    Button {
                        objectName: "recommendButton"
                        Layout.fillWidth: true
                        text: root.copyFor("recommendAction")
                        enabled: !recommendBridge.isBusy && recommendPreferenceInput.text.trim().length >= 3
                        highlighted: true
                        onClicked: recommendBridge.recommend(
                            recommendPreferenceInput.text,
                            recommendCountInput.value,
                            root.language
                        )
                    }
                }
            }

            Text {
                objectName: "recommendStatusText"
                Layout.fillWidth: true
                text: recommendBridge.copyForStatus(root.language)
                color: recommendBridge.status === "error" ? "#B42318" : root.textMuted
                font.pixelSize: 13
                wrapMode: Text.WordWrap
            }

            BusyIndicator {
                objectName: "recommendBusyIndicator"
                running: recommendBridge.isBusy
                visible: recommendBridge.isBusy
            }

            ListView {
                objectName: "recommendResultsList"
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: 10
                model: recommendBridge.items
                visible: recommendBridge.status === "success"

                delegate: Rectangle {
                    required property var modelData

                    width: ListView.view.width
                    height: Math.max(104, recommendResultColumn.implicitHeight + 24)
                    radius: 8
                    color: "#F9FAFB"
                    border.color: root.line

                    ColumnLayout {
                        id: recommendResultColumn
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 6

                        Text {
                            Layout.fillWidth: true
                            text: modelData.title
                            color: root.textStrong
                            font.pixelSize: 16
                            font.bold: true
                            elide: Text.ElideRight
                        }

                        Text {
                            Layout.fillWidth: true
                            text: modelData.year + "  " + root.copyFor("scoreLabel") + ": " + modelData.score
                            color: root.textMuted
                            font.pixelSize: 12
                            elide: Text.ElideRight
                        }

                        Text {
                            Layout.fillWidth: true
                            text: modelData.reason
                            color: root.textStrong
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                            maximumLineCount: 3
                            elide: Text.ElideRight
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Text {
                                Layout.fillWidth: true
                                text: root.copyFor("sourceLabel") + ": " + modelData.attribution
                                color: root.textMuted
                                font.pixelSize: 11
                                elide: Text.ElideRight
                            }

                            Button {
                                Layout.preferredWidth: 96
                                Layout.preferredHeight: 32
                                text: root.copyFor("addToList")
                                onClicked: watchListBridge.addFromCatalogItem(modelData)
                            }
                        }
                    }
                }
            }

            Text {
                Layout.fillWidth: true
                text: root.copyFor("unresolvedLabel") + ": " + recommendBridge.unresolved.length
                color: root.textMuted
                font.pixelSize: 12
                visible: recommendBridge.unresolved.length > 0
            }
        }
    }

    Component {
        id: searchPanel

        ColumnLayout {
            spacing: 16

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                TextField {
                    id: searchInput
                    objectName: "searchInput"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 40
                    placeholderText: root.copyFor("searchInput")
                    enabled: !searchBridge.isBusy
                    onAccepted: searchBridge.search(text)
                }

                Button {
                    objectName: "searchButton"
                    Layout.preferredWidth: 96
                    Layout.preferredHeight: 40
                    text: root.copyFor("searchAction")
                    enabled: !searchBridge.isBusy && searchInput.text.trim().length > 0
                    highlighted: true
                    onClicked: searchBridge.search(searchInput.text)
                }
            }

            Text {
                objectName: "searchStatusText"
                Layout.fillWidth: true
                text: searchBridge.copyForStatus(root.language)
                color: searchBridge.status === "error" ? "#B42318" : root.textMuted
                font.pixelSize: 13
                wrapMode: Text.WordWrap
            }

            BusyIndicator {
                objectName: "searchBusyIndicator"
                running: searchBridge.isBusy
                visible: searchBridge.isBusy
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: searchBridge.status === "success"

                ListView {
                    objectName: "searchResultsList"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    spacing: 10
                    model: searchBridge.items

                    delegate: Rectangle {
                        required property var modelData

                        width: ListView.view.width
                        height: Math.max(116, contentColumn.implicitHeight + 24)
                        radius: 8
                        color: searchBridge.hasSelection
                               && searchBridge.selectedItem.providerId === modelData.providerId
                               ? root.accentSoft : "#F9FAFB"
                        border.color: searchBridge.hasSelection
                                      && searchBridge.selectedItem.providerId === modelData.providerId
                                      ? root.accent : root.line

                        MouseArea {
                            anchors.fill: parent
                            onClicked: searchBridge.selectItem(modelData.providerId)
                        }

                        ColumnLayout {
                            id: contentColumn
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 6

                            Text {
                                Layout.fillWidth: true
                                text: modelData.title
                                color: root.textStrong
                                font.pixelSize: 16
                                font.bold: true
                                elide: Text.ElideRight
                            }

                            Text {
                                Layout.fillWidth: true
                                text: modelData.originalTitle || modelData.englishTitle
                                color: root.textMuted
                                font.pixelSize: 12
                                visible: text.length > 0
                                elide: Text.ElideRight
                            }

                            Text {
                                Layout.fillWidth: true
                                text: modelData.year + "  " + modelData.mediaType + "  "
                                      + root.copyFor("episodesLabel") + ": "
                                      + modelData.episodes + "  "
                                      + root.copyFor("scoreLabel") + ": " + modelData.score
                                color: root.textMuted
                                font.pixelSize: 12
                                elide: Text.ElideRight
                            }

                            Text {
                                Layout.fillWidth: true
                                text: modelData.genres
                                color: root.textMuted
                                font.pixelSize: 12
                                visible: text.length > 0
                                elide: Text.ElideRight
                            }

                            Text {
                                Layout.fillWidth: true
                                text: modelData.synopsis
                                color: root.textStrong
                                font.pixelSize: 12
                                maximumLineCount: 2
                                wrapMode: Text.WordWrap
                                elide: Text.ElideRight
                                visible: text.length > 0
                            }

                            Text {
                                Layout.fillWidth: true
                                text: root.copyFor("sourceLabel") + ": " + modelData.attribution
                                color: root.textMuted
                                font.pixelSize: 11
                                elide: Text.ElideRight
                            }
                        }
                    }
                }

                Rectangle {
                    objectName: "searchDetailPanel"
                    Layout.preferredWidth: 320
                    Layout.fillHeight: true
                    radius: 8
                    color: "#F9FAFB"
                    border.color: root.line

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 10

                        Text {
                            Layout.fillWidth: true
                            text: root.copyFor("detailTitle")
                            color: root.textStrong
                            font.pixelSize: 17
                            font.bold: true
                            elide: Text.ElideRight
                        }

                        Text {
                            objectName: "searchDetailTitle"
                            Layout.fillWidth: true
                            text: searchBridge.hasSelection ? searchBridge.selectedItem.title : root.copyFor("detailEmpty")
                            color: searchBridge.hasSelection ? root.textStrong : root.textMuted
                            font.pixelSize: searchBridge.hasSelection ? 20 : 13
                            font.bold: searchBridge.hasSelection
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            Layout.fillWidth: true
                            text: searchBridge.hasSelection
                                  ? searchBridge.selectedItem.year + "  "
                                    + searchBridge.selectedItem.mediaType + "  "
                                    + root.copyFor("scoreLabel") + ": "
                                    + searchBridge.selectedItem.score
                                  : ""
                            color: root.textMuted
                            font.pixelSize: 12
                            visible: searchBridge.hasSelection
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            Layout.fillWidth: true
                            text: searchBridge.hasSelection
                                  ? root.copyFor("ratingLabel") + ": " + searchBridge.selectedItem.rating
                                  : ""
                            color: root.textMuted
                            font.pixelSize: 12
                            visible: searchBridge.hasSelection && searchBridge.selectedItem.rating.length > 0
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            Layout.fillWidth: true
                            text: searchBridge.hasSelection
                                  ? root.copyFor("studiosLabel") + ": " + searchBridge.selectedItem.studios
                                  : ""
                            color: root.textMuted
                            font.pixelSize: 12
                            visible: searchBridge.hasSelection && searchBridge.selectedItem.studios.length > 0
                            wrapMode: Text.WordWrap
                        }

                        ScrollView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            visible: searchBridge.hasSelection

                            Text {
                                width: parent.availableWidth
                                text: searchBridge.selectedItem.synopsis
                                color: root.textStrong
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                            }
                        }

                        Button {
                            objectName: "addSelectedToListButton"
                            Layout.fillWidth: true
                            Layout.preferredHeight: 38
                            text: root.copyFor("addToList")
                            enabled: searchBridge.hasSelection
                            highlighted: true
                            onClicked: watchListBridge.addFromCatalogItem(searchBridge.selectedItem)
                        }

                        Text {
                            Layout.fillWidth: true
                            text: searchBridge.hasSelection
                                  ? root.copyFor("sourceLabel") + ": " + searchBridge.selectedItem.attribution
                                  : ""
                            color: root.textMuted
                            font.pixelSize: 11
                            visible: searchBridge.hasSelection
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }
    }

    Component {
        id: listPanel

        ColumnLayout {
            spacing: 14

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Button {
                    objectName: "watchFilter_all"
                    Layout.preferredWidth: 78
                    text: root.copyFor("allItems")
                    highlighted: watchListBridge.statusFilter === "all"
                    onClicked: watchListBridge.setStatusFilter("all")
                }

                Button {
                    objectName: "watchFilter_plan"
                    Layout.preferredWidth: 78
                    text: root.copyFor("planToWatch")
                    highlighted: watchListBridge.statusFilter === "plan_to_watch"
                    onClicked: watchListBridge.setStatusFilter("plan_to_watch")
                }

                Button {
                    objectName: "watchFilter_watching"
                    Layout.preferredWidth: 96
                    text: root.copyFor("watching")
                    highlighted: watchListBridge.statusFilter === "watching"
                    onClicked: watchListBridge.setStatusFilter("watching")
                }

                Button {
                    objectName: "watchFilter_completed"
                    Layout.preferredWidth: 104
                    text: root.copyFor("completed")
                    highlighted: watchListBridge.statusFilter === "completed"
                    onClicked: watchListBridge.setStatusFilter("completed")
                }
            }

            Text {
                objectName: "watchListStatusText"
                Layout.fillWidth: true
                text: watchListBridge.copyForStatus(root.language)
                color: watchListBridge.errorCode.length > 0 ? "#B42318" : root.textMuted
                font.pixelSize: 13
                wrapMode: Text.WordWrap
            }

            ListView {
                objectName: "watchListResultsList"
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: 10
                model: watchListBridge.items

                delegate: Rectangle {
                    required property var modelData

                    width: ListView.view.width
                    height: 158
                    radius: 8
                    color: "#F9FAFB"
                    border.color: root.line

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Text {
                            Layout.fillWidth: true
                            text: modelData.title
                            color: root.textStrong
                            font.pixelSize: 16
                            font.bold: true
                            elide: Text.ElideRight
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            ComboBox {
                                id: watchStatusCombo
                                Layout.preferredWidth: 130
                                model: ["plan_to_watch", "watching", "completed"]
                                currentIndex: modelData.status === "watching" ? 1 : (modelData.status === "completed" ? 2 : 0)
                            }

                            SpinBox {
                                id: watchProgressInput
                                Layout.preferredWidth: 86
                                from: 0
                                to: 9999
                                value: modelData.progress
                            }

                            SpinBox {
                                id: watchScoreInput
                                Layout.preferredWidth: 76
                                from: 0
                                to: 10
                                value: modelData.score === "" ? 0 : modelData.score
                            }

                            TextField {
                                id: watchNotesInput
                                Layout.fillWidth: true
                                placeholderText: root.copyFor("notes")
                                text: modelData.notes
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Item { Layout.fillWidth: true }

                            Button {
                                Layout.preferredWidth: 72
                                Layout.preferredHeight: 34
                                text: root.copyFor("save")
                                highlighted: true
                                onClicked: watchListBridge.updateItem(
                                    modelData.itemId,
                                    watchStatusCombo.currentText,
                                    watchProgressInput.value,
                                    watchScoreInput.value,
                                    watchNotesInput.text
                                )
                            }

                            Button {
                                Layout.preferredWidth: 72
                                Layout.preferredHeight: 34
                                text: root.copyFor("remove")
                                onClicked: watchListBridge.removeItem(modelData.itemId)
                            }
                        }
                    }
                }
            }
        }
    }


    Component {
        id: historyPanel

        ColumnLayout {
            spacing: 14

            Text {
                objectName: "historyStatusText"
                Layout.fillWidth: true
                text: historyBridge.copyForStatus(root.language)
                color: historyBridge.errorCode.length > 0 ? "#B42318" : root.textMuted
                font.pixelSize: 13
                wrapMode: Text.WordWrap
            }

            ListView {
                objectName: "historyResultsList"
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: 10
                model: historyBridge.sessions

                delegate: Rectangle {
                    required property var modelData

                    width: ListView.view.width
                    height: 96
                    radius: 8
                    color: "#F9FAFB"
                    border.color: root.line

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 12

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 5

                            Text {
                                Layout.fillWidth: true
                                text: modelData.preferences
                                color: root.textStrong
                                font.pixelSize: 15
                                font.bold: true
                                elide: Text.ElideRight
                            }

                            Text {
                                Layout.fillWidth: true
                                text: root.copyFor("recommend") + ": " + modelData.verifiedCount
                                      + "  " + root.copyFor("unresolvedLabel") + ": " + modelData.unresolvedCount
                                color: root.textMuted
                                font.pixelSize: 12
                                elide: Text.ElideRight
                            }

                            Text {
                                Layout.fillWidth: true
                                text: modelData.createdAt
                                color: root.textMuted
                                font.pixelSize: 11
                                elide: Text.ElideRight
                            }
                        }

                        Button {
                            Layout.preferredWidth: 72
                            Layout.preferredHeight: 34
                            text: root.copyFor("remove")
                            onClicked: historyBridge.deleteSession(modelData.sessionId)
                        }
                    }
                }
            }
        }
    }

    Component {
        id: settingsPanel

        ColumnLayout {
            spacing: 18

            Text {
                Layout.fillWidth: true
                text: root.copyFor("language")
                color: root.textStrong
                font.pixelSize: 16
                font.bold: true
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Button {
                    Layout.preferredWidth: 100
                    text: "\u4e2d\u6587"
                    highlighted: root.language === "zh"
                    onClicked: root.setLanguage("zh")
                }

                Button {
                    Layout.preferredWidth: 100
                    text: "English"
                    highlighted: root.language === "en"
                    onClicked: root.setLanguage("en")
                }
            }

            Text {
                Layout.fillWidth: true
                text: root.copyFor("aiProvider")
                color: root.textStrong
                font.pixelSize: 16
                font.bold: true
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                ComboBox {
                    objectName: "aiProviderCombo"
                    Layout.preferredWidth: 260
                    model: aiConfigBridge.providers
                    textRole: "displayName"
                    onActivated: function(index) {
                        aiConfigBridge.selectProvider(model[index].providerId)
                    }
                }

                TextField {
                    id: aiApiKeyInput
                    objectName: "aiApiKeyInput"
                    Layout.fillWidth: true
                    placeholderText: root.copyFor("apiKey")
                    echoMode: TextInput.Password
                }

                Button {
                    objectName: "saveApiKeyButton"
                    Layout.preferredWidth: 96
                    text: root.copyFor("saveApiKey")
                    highlighted: true
                    onClicked: {
                        aiConfigBridge.saveApiKey(aiApiKeyInput.text)
                        aiApiKeyInput.text = ""
                    }
                }

                Button {
                    objectName: "deleteApiKeyButton"
                    Layout.preferredWidth: 96
                    text: root.copyFor("deleteApiKey")
                    onClicked: aiConfigBridge.deleteApiKey()
                }

                Button {
                    objectName: "testAiConnectionButton"
                    Layout.preferredWidth: 96
                    text: root.copyFor("testConnection")
                    enabled: !aiConfigBridge.isTestingConnection
                    onClicked: aiConfigBridge.testConnection()
                }
            }

            Text {
                objectName: "aiConfigStatusText"
                Layout.fillWidth: true
                text: aiConfigBridge.copyForStatus(root.language)
                color: aiConfigBridge.errorCode.length > 0 ? "#B42318" : root.textMuted
                font.pixelSize: 13
                wrapMode: Text.WordWrap
            }

            Text {
                Layout.fillWidth: true
                text: root.copyFor("backupTitle")
                color: root.textStrong
                font.pixelSize: 16
                font.bold: true
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Button {
                    objectName: "exportBackupButton"
                    Layout.preferredWidth: 120
                    text: root.copyFor("exportBackup")
                    highlighted: true
                    onClicked: exportBackupDialog.open()
                }

                Button {
                    objectName: "importBackupButton"
                    Layout.preferredWidth: 120
                    text: root.copyFor("importBackup")
                    onClicked: importBackupDialog.open()
                }
            }

            Text {
                objectName: "backupStatusText"
                Layout.fillWidth: true
                text: backupBridge.copyForStatus(root.language)
                color: backupBridge.errorCode.length > 0 ? "#B42318" : root.textMuted
                font.pixelSize: 13
                wrapMode: Text.WordWrap
            }

            FileDialog {
                id: exportBackupDialog
                objectName: "exportBackupDialog"
                title: root.copyFor("backupSaveTitle")
                fileMode: FileDialog.SaveFile
                defaultSuffix: "json"
                nameFilters: ["AniCompass Backup (*.json)"]
                onAccepted: backupBridge.exportBackup(selectedFile.toString())
            }

            FileDialog {
                id: importBackupDialog
                objectName: "importBackupDialog"
                title: root.copyFor("backupDialogTitle")
                fileMode: FileDialog.OpenFile
                nameFilters: ["AniCompass Backup (*.json)"]
                onAccepted: backupBridge.importBackup(selectedFile.toString())
            }

            Text {
                Layout.fillWidth: true
                text: root.copyFor("theme")
                color: root.textStrong
                font.pixelSize: 16
                font.bold: true
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 14

                Rectangle {
                    Layout.preferredWidth: 54
                    Layout.preferredHeight: 54
                    radius: 8
                    color: root.accent
                    border.color: root.line
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    ColorSliderRow {
                        label: root.copyFor("red")
                        channelValue: root.accentRed
                        onChanged: function(newValue) { settingsService.setAccentColor(newValue, root.accentGreen, root.accentBlue) }
                    }

                    ColorSliderRow {
                        label: root.copyFor("green")
                        channelValue: root.accentGreen
                        onChanged: function(newValue) { settingsService.setAccentColor(root.accentRed, newValue, root.accentBlue) }
                    }

                    ColorSliderRow {
                        label: root.copyFor("blue")
                        channelValue: root.accentBlue
                        onChanged: function(newValue) { settingsService.setAccentColor(root.accentRed, root.accentGreen, newValue) }
                    }
                }
            }
        }
    }
}



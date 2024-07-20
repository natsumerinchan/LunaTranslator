from qtsymbols import *
import functools, importlib
from traceback import print_exc
import qtawesome
from myutils.config import globalconfig, _TR
from myutils.utils import makehtml
from myutils.wrapper import Singleton_close
from gui.usefulwidget import (
    MySwitch,
    selectcolor,
    getsimpleswitch,
    threebuttons,
    listediterline,
    TableViewW,
    getsimplepatheditor,
    FocusSpin,
    FocusDoubleSpin,
    LFocusCombo,
    getsimplecombobox,
)
from gui.dynalang import (
    LFormLayout,
    LLabel,
    LPushButton,
    LStandardItemModel,
    LDialog,
    LDialog,
    LAction,
)


@Singleton_close
class noundictconfigdialog1(LDialog):
    def newline(self, row, item):
        self.model.insertRow(
            row,
            [
                QStandardItem(),
                QStandardItem(item["key"]),
                QStandardItem(item["value"]),
            ],
        )
        self.table.setIndexWidget(
            self.model.index(row, 0), getsimpleswitch(item, "regex")
        )

    def showmenu(self, table: TableViewW, _):
        r = table.currentIndex().row()
        if r < 0:
            return
        menu = QMenu(table)
        up = LAction(("上移"))
        down = LAction(("下移"))
        menu.addAction(up)
        menu.addAction(down)
        action = menu.exec(table.cursor().pos())

        if action == up:

            self.moverank(table, -1)

        elif action == down:
            self.moverank(table, 1)

    def moverank(self, table: TableViewW, dy):
        curr = table.currentIndex()
        model = table.model()
        target = (curr.row() + dy) % model.rowCount()
        texts = [model.item(curr.row(), i).text() for i in range(model.columnCount())]

        item = self.reflist.pop(curr.row())
        self.reflist.insert(
            target, {"key": texts[1], "value": [2], "regex": item["regex"]}
        )
        model.removeRow(curr.row())
        model.insertRow(target, [QStandardItem(text) for text in texts])
        table.setCurrentIndex(model.index(target, curr.column()))
        table.setIndexWidget(
            model.index(target, 0), getsimpleswitch(self.reflist[target], "regex")
        )

    def __init__(self, parent, reflist, title, label) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.label = label
        self.setWindowTitle(title)
        # self.setWindowModality(Qt.ApplicationModal)
        self.reflist = reflist
        formLayout = QVBoxLayout(self)  # 配置layout

        self.model = LStandardItemModel()
        self.model.setHorizontalHeaderLabels(label)
        table = TableViewW(self)
        table.setModel(self.model)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            functools.partial(self.showmenu, table)
        )

        self.table = table
        for row, item in enumerate(reflist):
            self.newline(row, item)

        search = QHBoxLayout()
        searchcontent = QLineEdit()
        search.addWidget(searchcontent)
        button4 = LPushButton("搜索")

        def clicked4():
            text = searchcontent.text()

            rows = self.model.rowCount()
            cols = self.model.columnCount()
            for row in range(rows):
                ishide = True
                for c in range(cols):
                    if text in self.model.item(row, c).text():
                        ishide = False
                        break
                table.setRowHidden(row, ishide)

        button4.clicked.connect(clicked4)
        search.addWidget(button4)

        button = threebuttons(texts=["添加行", "删除行", "上移", "下移", "立即应用"])

        def clicked1():
            self.reflist.insert(0, {"key": "", "value": "", "regex": False})

            self.newline(0, self.reflist[0])

        button.btn1clicked.connect(clicked1)

        def clicked2():
            skip = []
            for index in self.table.selectedIndexes():
                if index.row() in skip:
                    continue
                skip.append(index.row())
            skip = reversed(sorted(skip))

            for row in skip:
                self.model.removeRow(row)
                self.reflist.pop(row)

        button.btn2clicked.connect(clicked2)
        button.btn5clicked.connect(self.apply)
        button.btn3clicked.connect(functools.partial(self.moverank, table, -1))
        button.btn4clicked.connect(functools.partial(self.moverank, table, 1))
        self.button = button
        formLayout.addWidget(table)
        formLayout.addLayout(search)
        formLayout.addWidget(button)

        self.resize(QSize(600, 400))
        self.show()

    def apply(self):
        rows = self.model.rowCount()
        dedump = set()
        needremoves = []
        for row in range(rows):
            k = self.model.item(row, 1).text()
            v = self.model.item(row, 2).text()
            if k == "" or k in dedump:
                needremoves.append(row)
                continue
            self.reflist[row].update({"key": k, "value": v})
            dedump.add(k)
        for row in reversed(needremoves):
            self.model.removeRow(row)
            self.reflist.pop(row)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.button.setFocus()
        self.apply()


@Singleton_close
class noundictconfigdialog2(LDialog):
    def newline(self, row, item):

        self.model.insertRow(
            row,
            [QStandardItem(), QStandardItem(), QStandardItem(item["key"])],
        )
        self.table.setIndexWidget(
            self.model.index(row, 0), getsimpleswitch(item, "regex")
        )
        com = getsimplecombobox(["首尾", "包含"], item, "condition")
        self.table.setIndexWidget(self.model.index(row, 1), com)

    def showmenu(self, table: TableViewW, _):
        r = table.currentIndex().row()
        if r < 0:
            return
        menu = QMenu(table)
        up = LAction(("上移"))
        down = LAction(("下移"))
        menu.addAction(up)
        menu.addAction(down)
        action = menu.exec(table.cursor().pos())

        if action == up:

            self.moverank(table, -1)

        elif action == down:
            self.moverank(table, 1)

    def moverank(self, table: TableViewW, dy):
        curr = table.currentIndex()
        model = table.model()
        target = (curr.row() + dy) % model.rowCount()
        texts = [model.item(curr.row(), i).text() for i in range(model.columnCount())]

        item = self.reflist.pop(curr.row())
        self.reflist.insert(
            target,
            {"key": texts[1], "condition": item["condition"], "regex": item["regex"]},
        )

        model.removeRow(curr.row())
        model.insertRow(target, [QStandardItem(text) for text in texts])
        table.setCurrentIndex(model.index(target, curr.column()))
        table.setIndexWidget(
            model.index(target, 0), getsimpleswitch(self.reflist[target], "regex")
        )
        com = getsimplecombobox(["首尾", "包含"], item, "condition")
        table.setIndexWidget(self.model.index(target, 1), com)

    def __init__(self, parent, reflist, title, label) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.label = label
        self.setWindowTitle(title)
        # self.setWindowModality(Qt.ApplicationModal)
        self.reflist = reflist
        formLayout = QVBoxLayout(self)  # 配置layout

        self.model = LStandardItemModel()
        self.model.setHorizontalHeaderLabels(label)
        table = TableViewW(self)
        table.setModel(self.model)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            functools.partial(self.showmenu, table)
        )

        self.table = table
        for row, item in enumerate(reflist):
            self.newline(row, item)

        search = QHBoxLayout()
        searchcontent = QLineEdit()
        search.addWidget(searchcontent)
        button4 = LPushButton("搜索")

        def clicked4():
            text = searchcontent.text()

            rows = self.model.rowCount()
            cols = self.model.columnCount()
            for row in range(rows):
                ishide = True
                for c in range(cols):
                    if text in self.model.item(row, c).text():
                        ishide = False
                        break
                table.setRowHidden(row, ishide)

        button4.clicked.connect(clicked4)
        search.addWidget(button4)

        button = threebuttons(texts=["添加行", "删除行", "上移", "下移", "立即应用"])

        def clicked1():
            self.reflist.insert(0, {"key": "", "condition": 0, "regex": False})

            self.newline(0, self.reflist[0])

        button.btn1clicked.connect(clicked1)

        def clicked2():
            skip = []
            for index in self.table.selectedIndexes():
                if index.row() in skip:
                    continue
                skip.append(index.row())
            skip = reversed(sorted(skip))

            for row in skip:
                self.model.removeRow(row)
                self.reflist.pop(row)

        button.btn2clicked.connect(clicked2)
        button.btn5clicked.connect(self.apply)
        button.btn3clicked.connect(functools.partial(self.moverank, table, -1))
        button.btn4clicked.connect(functools.partial(self.moverank, table, 1))
        self.button = button
        formLayout.addWidget(table)
        formLayout.addLayout(search)
        formLayout.addWidget(button)

        self.resize(QSize(600, 400))
        self.show()

    def apply(self):
        rows = self.model.rowCount()
        dedump = set()
        needremoves = []
        for row in range(rows):
            k = self.model.item(row, 2).text()

            if k == "" or k in dedump:
                needremoves.append(row)
                continue
            self.reflist[row].update({"key": k})
            dedump.add(k)
        for row in reversed(needremoves):
            self.model.removeRow(row)
            self.reflist.pop(row)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.button.setFocus()
        self.apply()


@Singleton_close
class regexedit(LDialog):
    def __init__(self, parent, regexlist) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.regexlist = regexlist
        self.setWindowTitle("正则匹配")

        formLayout = QVBoxLayout(self)  # 配置layout

        self.model = LStandardItemModel()
        self.model.setHorizontalHeaderLabels(["正则"])
        table = TableViewW(self)
        table.setModel(self.model)

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table = table
        for row, regex in enumerate(regexlist):
            self.model.insertRow(row, [QStandardItem(regex)])

        button = threebuttons(texts=["添加行", "删除行", "立即应用"])

        def clicked1():
            regexlist.insert(0, "")
            self.model.insertRow(0, [QStandardItem()])

        button.btn1clicked.connect(clicked1)

        def clicked2():
            skip = []
            for index in self.table.selectedIndexes():
                if index.row() in skip:
                    continue
                skip.append(index.row())
            skip = reversed(sorted(skip))

            for row in skip:
                self.model.removeRow(row)
                regexlist.pop(row)

        button.btn2clicked.connect(clicked2)
        button.btn3clicked.connect(self.apply)
        self.button = button
        formLayout.addWidget(table)
        formLayout.addWidget(button)
        self.resize(QSize(600, 400))
        self.show()

    def apply(self):
        rows = self.model.rowCount()
        dedump = set()
        needremoves = []
        for row in range(rows):
            regex = self.model.item(row, 0).text()
            if regex == "" or regex in dedump:
                needremoves.append(row)
                continue

            self.regexlist[row] = regex
            dedump.add(regex)

        for row in reversed(needremoves):
            self.model.removeRow(row)
            self.regexlist.pop(row)

    def closeEvent(self, _) -> None:
        self.button.setFocus()
        self.apply()


def autoinitdialog_items(dic):
    items = []
    for arg in dic["args"]:
        default = dict(name=arg, d=dic["args"], k=arg, type="lineedit")

        if "argstype" in dic and arg in dic["argstype"]:
            default.update(dic["argstype"][arg])
        items.append(default)
    items.append({"type": "okcancel"})
    return items


@Singleton_close
class autoinitdialog(LDialog):
    def __init__(self, parent, title, width, lines, _=None) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(title)
        self.resize(QSize(width, 10))
        for line in lines:
            if line["type"] != "program":
                continue
            try:
                func = getattr(
                    importlib.import_module(line["route"][0]),
                    line["route"][1],
                )
                func(self)
            except:
                print_exc()
            self.show()
            return
        formLayout = LFormLayout()
        self.setLayout(formLayout)
        regist = []

        def save(callback=None):
            for l in regist:
                l[0][l[1]] = l[2]()
            self.close()
            if callback:
                try:
                    callback()
                except:
                    print_exc()

        def __getv(l):
            return l

        hasrank = []
        hasnorank = []
        for line in lines:
            rank = line.get("rank", None)
            if rank is None:
                hasnorank.append(line)
                continue
            hasrank.append(line)
        hasrank.sort(key=lambda line: line.get("rank", None))
        lines = hasrank + hasnorank
        for line in lines:
            if "d" in line:
                dd = line["d"]
            if "k" in line:
                key = line["k"]
            if line["type"] == "switch_ref":
                continue
            if line["type"] == "label":

                if "islink" in line and line["islink"]:
                    lineW = QLabel(makehtml(dd[key]))
                    lineW.setOpenExternalLinks(True)
                else:
                    lineW = LLabel(dd[key])
            elif line["type"] == "textlist":
                __list = dd[key]
                e = listediterline(line["name"], line["header"], __list)

                regist.append([dd, key, functools.partial(__getv, __list)])
                lineW = QHBoxLayout()
                lineW.addWidget(e)
            elif line["type"] == "combo":
                lineW = LFocusCombo()
                if "list_function" in line:
                    try:
                        func = getattr(
                            importlib.import_module(line["list_function"][0]),
                            line["list_function"][1],
                        )
                        items = func()
                    except:
                        items = []
                else:
                    items = line["list"]
                lineW.addItems(items)
                lineW.setCurrentIndex(dd.get(key, 0))
                lineW.currentIndexChanged.connect(
                    functools.partial(dd.__setitem__, key)
                )
            elif line["type"] == "okcancel":
                lineW = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok
                    | QDialogButtonBox.StandardButton.Cancel
                )
                lineW.rejected.connect(self.close)
                lineW.accepted.connect(
                    functools.partial(save, line.get("callback", None))
                )

                lineW.button(QDialogButtonBox.StandardButton.Ok).setText(_TR("确定"))
                lineW.button(QDialogButtonBox.StandardButton.Cancel).setText(
                    _TR("取消")
                )
            elif line["type"] == "lineedit":
                lineW = QLineEdit(dd[key])
                regist.append([dd, key, lineW.text])
            elif line["type"] == "multiline":
                lineW = QPlainTextEdit(dd[key])
                regist.append([dd, key, lineW.toPlainText])
            elif line["type"] == "file":
                __temp = {"k": dd[key]}
                lineW = getsimplepatheditor(
                    dd[key],
                    line.get("multi", False),
                    line["dir"],
                    line.get("filter", None),
                    callback=functools.partial(__temp.__setitem__, "k"),
                    reflist=__temp["k"],
                    name=line.get("name", ""),
                    header=line.get("name", ""),
                )

                regist.append([dd, key, functools.partial(__temp.__getitem__, "k")])

            elif line["type"] == "switch":
                lineW = MySwitch(sign=dd[key])
                regist.append([dd, key, lineW.isChecked])
                _ = QHBoxLayout()
                _.addStretch()
                _.addWidget(lineW)
                _.addStretch()
                lineW = _
            elif line["type"] == "spin":
                lineW = FocusDoubleSpin()
                lineW.setMinimum(line.get("min", 0))
                lineW.setMaximum(line.get("max", 100))
                lineW.setSingleStep(line.get("step", 0.1))
                lineW.setValue(dd[key])
                lineW.valueChanged.connect(functools.partial(dd.__setitem__, key))

            elif line["type"] == "intspin":
                lineW = FocusSpin()
                lineW.setMinimum(line.get("min", 0))
                lineW.setMaximum(line.get("max", 100))
                lineW.setSingleStep(line.get("step", 1))
                lineW.setValue(dd[key])
                lineW.valueChanged.connect(functools.partial(dd.__setitem__, key))
            elif line["type"] == "split":
                lineW = QLabel()
                lineW.setStyleSheet("background-color: gray;")
                lineW.setFixedHeight(2)
                formLayout.addRow(lineW)
                continue
            refswitch = line.get("refswitch", None)
            if refswitch:
                hbox = QHBoxLayout()
                line_ref = None
                for __ in lines:
                    if __.get("k", None) == refswitch:
                        line_ref = __
                        break
                if line_ref:
                    if "d" in line_ref:
                        dd = line_ref["d"]
                    if "k" in line_ref:
                        key = line_ref["k"]
                    switch = MySwitch(sign=dd[key])
                    regist.append([dd, key, switch.isChecked])
                    switch.clicked.connect(lineW.setEnabled)
                    lineW.setEnabled(dd[key])
                    hbox.addWidget(switch)
                    hbox.addWidget(lineW)
                    lineW = hbox
            if "name" in line:
                formLayout.addRow(line["name"], lineW)
            else:
                formLayout.addRow(lineW)
        self.show()


def getsomepath1(
    parent, title, d, k, label, callback=None, isdir=False, filter1="*.db"
):
    autoinitdialog(
        parent,
        title,
        800,
        [
            {
                "type": "file",
                "name": label,
                "d": d,
                "k": k,
                "dir": isdir,
                "filter": filter1,
            },
            {"type": "okcancel", "callback": callback},
        ],
    )


@Singleton_close
class multicolorset(LDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("颜色设置")
        self.resize(QSize(300, 10))
        formLayout = LFormLayout(self)  # 配置layout
        _hori = QHBoxLayout()
        l = LLabel("不透明度")
        _hori.addWidget(l)
        _s = FocusSpin()
        _s.setValue(globalconfig["showcixing_touming"])
        _s.setMinimum(1)
        _s.setMaximum(100)
        _hori.addWidget(_s)
        formLayout.addRow(_hori)
        _s.valueChanged.connect(
            lambda x: globalconfig.__setitem__("showcixing_touming", x)
        )
        hori = QHBoxLayout()
        hori.addWidget(LLabel("词性"))
        hori.addWidget(LLabel("是否显示"))
        hori.addWidget(LLabel("颜色"))
        for k in globalconfig["cixingcolor"]:
            hori = QHBoxLayout()

            l = LLabel(k)

            hori.addWidget(l)

            b = MySwitch(sign=globalconfig["cixingcolorshow"][k])
            b.clicked.connect(
                functools.partial(globalconfig["cixingcolorshow"].__setitem__, k)
            )

            p = QPushButton(
                qtawesome.icon("fa.paint-brush", color=globalconfig["cixingcolor"][k]),
                "",
            )

            p.setIconSize(QSize(20, 20))

            p.setStyleSheet("background: transparent;")
            p.clicked.connect(
                functools.partial(selectcolor, self, globalconfig["cixingcolor"], k, p)
            )
            hori.addWidget(b)
            hori.addWidget(p)

            formLayout.addRow(hori)
        self.show()


@Singleton_close
class postconfigdialog_(LDialog):
    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.closeevent:
            self.button.setFocus()
            self.apply()
            if self.closecallback:
                self.closecallback()

    def apply(self):
        rows = self.model.rowCount()
        self.configdict.clear()
        for row in range(rows):
            if self.model.item(row, 0).text() == "":
                continue
            self.configdict[(self.model.item(row, 0).text())] = self.model.item(
                row, 1
            ).text()

    def __init__(self, parent, configdict, title, headers, closecallback=None) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.closecallback = closecallback
        self.setWindowTitle(title)
        # self.setWindowModality(Qt.ApplicationModal)
        self.closeevent = False
        formLayout = QVBoxLayout(self)  # 配置layout

        model = LStandardItemModel(len(configdict), 1, self)
        row = 0

        for key1 in configdict:  # 2

            item = QStandardItem(key1)
            model.setItem(row, 0, item)

            item = QStandardItem(configdict[key1])
            model.setItem(row, 1, item)
            row += 1
        model.setHorizontalHeaderLabels(headers)
        table = TableViewW(self)
        table.setModel(model)
        table.setWordWrap(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # table.clicked.connect(self.show_info)
        button = threebuttons(texts=["添加行", "删除行", "立即应用"])

        def clicked1():
            model.insertRow(0, [QStandardItem(), QStandardItem()])

        button.btn1clicked.connect(clicked1)

        def clicked2():
            skip = []
            for index in table.selectedIndexes():
                if index.row() in skip:
                    continue
                skip.append(index.row())
            skip = reversed(sorted(skip))

            for row in skip:
                model.removeRow(row)

        button.btn2clicked.connect(clicked2)
        button.btn3clicked.connect(self.apply)
        self.button = button
        self.model = model
        self.configdict = configdict
        self.closeevent = True
        search = QHBoxLayout()
        searchcontent = QLineEdit()
        search.addWidget(searchcontent)
        button4 = LPushButton("搜索")

        def clicked4():
            text = searchcontent.text()

            rows = model.rowCount()
            cols = model.columnCount()
            for row in range(rows):
                ishide = True
                for c in range(cols):
                    if text in model.item(row, c).text():
                        ishide = False
                        break
                table.setRowHidden(row, ishide)

        button4.clicked.connect(clicked4)
        search.addWidget(button4)

        formLayout.addWidget(table)
        formLayout.addLayout(search)
        formLayout.addWidget(button)
        self.resize(QSize(600, 400))
        self.show()


def postconfigdialog(parent, configdict, title, header):
    postconfigdialog_(parent, configdict, title, header)

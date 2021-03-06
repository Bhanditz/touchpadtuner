#! /usr/bin/python3
# -= encoding=utf-8 =-
'''
Copyright (c) 2018, 2017, shimoda as kuri65536 _dot_ hot mail _dot_ com
                    ( email address: convert _dot_ to . and joint string )

This Source Code Form is subject to the terms of the Mozilla Public License,
v.2.0. If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
'''
from __future__ import print_function
import sys
import os
import subprocess
import logging
from logging import debug as debg, info, warning as warn

import common
from common import (BoolVar, CmbVar, FltVar, IntVar,
                    open_file, )
from xprops import NProp, NPropDb
from xconf import XConfFile

try:
    from typing import (Any, Callable, Dict, IO, Iterable, List, Optional,
                        Text, Tuple, Union, )
    Any, Callable, Dict, IO, Iterable, List, Optional, Text, Tuple, Union
except:
    pass


if sys.version_info[0] == 3:
    import tkinter as tk
    import tkinter.messagebox as messagebox
    from tkinter import ttk
else:
    import Tkinter as tk
    import ttk
    import tkMessageBox as messagebox


def allok(seq):
    # type: (List[Text]) -> bool
    return True


def apply_none(cmd):  # {{{1
    # type: (List[Text]) -> bool
    return False


class NPropGui(object):  # {{{1
    def __init__(self, n):  # {{{1
        # type: (int) -> None
        length = NProp.xinputs[n]
        self.prop = NProp(n, 0)
        self.length = length
        self.typ = "32"
        self.vars = []  # type: List[Any]
        self._cache = []  # type: List[Text]

    def is_loaded(self):  # {{{1
        # type: () -> bool
        return len(self._cache) > 0

    def is_changed(self):  # {{{1
        # type: () -> bool
        if len(self.vars) < self.length:  # gui not loaded
            return False
        if not self.is_loaded():
            self.load()
        cur = self.compose()
        for n, a in enumerate(cur):
            b = self._cache[n]
            if not self.cmp(a, b):
                return True
        return False

    def load(self):  # {{{1
        # type: () -> List[Text]
        ret = self._cache = xi.prop_get(self.prop.n)
        return ret

    def compose(self):  # {{{1
        # type: () -> List[Text]
        assert False, "must be override"

    def cmp(self, a, b):  # {{{1
        # type: (Text, Text) -> bool
        assert False, "must be override"

    def sync(self):  # {{{1
        # type: () -> bool
        args = self.compose()
        xi.prop_set_int(self.prop.n, self.typ, args)
        return False

    def current(self, i):  # {{{1
        # type: (int) -> Text
        if i < len(self.vars):
            var = self.vars[i]
            ret = var.get()
            txt = Text(ret)
            return txt
        if not self.is_loaded():
            self.load()
        txt = self._cache[i]
        return txt


class NPropGuiInt(NPropGui):  # {{{1
    def __init__(self, n, typ):  # {{{1
        # type: (int, int) -> None
        NPropGui.__init__(self, n)
        self.vars = []  # type: List[IntVar]
        self.typ = Text(typ)
        db.regist(self)

    def append(self, var):  # {{{1
        # type: (IntVar) -> 'NPropGuiInt'
        self.vars.append(var)
        return self

    def compose(self):  # {{{1
        # type: () -> List[Text]
        ret = []
        for i in range(self.length):
            n = self.vars[i].get()
            ret.append(Text(n))
        return ret

    def cmp(self, a, b):  # {{{1
        # type: (Text, Text) -> bool
        return a == b


class NPropGuiFlt(NPropGui):   # {{{1
    def __init__(self, n):  # {{{1
        # type: (int) -> None
        NPropGui.__init__(self, n)
        self.vars = []  # type: List[FltVar]
        db.regist(self)

    def append(self, var):  # {{{1
        # type: (FltVar) -> 'NPropGuiFlt'
        self.vars.append(var)
        return self

    def compose(self):  # {{{1
        # type: () -> List[Text]
        ret = []
        for i in range(self.length):
            n = self.vars[i].get()
            ret.append(Text(n))
        return ret

    def cmp(self, a, b):  # {{{1
        # type: (Text, Text) -> bool
        af = float(a)
        bf = float(b)
        df = af - bf
        df = df if df >= 0 else -df
        dgt = NProp.xconfs[self.prop.n].dgts[0]  # TODO: determine index.
        if df < 10 ** -dgt:
            return True
        return False

    def sync(self):  # {{{1
        # type: () -> bool
        args = self.compose()
        # TODO: 8 or 32
        xi.prop_set_flt(self.prop.n, args)
        return False


class NPropGuiBol(NPropGui):   # {{{1
    def __init__(self, n):  # {{{1
        # type: (int) -> None
        NPropGui.__init__(self, n)
        self.typ = "8"
        self.vars = []  # type: List[BoolVar]
        db.regist(self)

    def append(self, var):  # {{{1
        # type: (BoolVar) -> 'NPropGuiBol'
        self.vars.append(var)
        return self

    def compose(self):  # {{{1
        # type: () -> List[Text]
        ret = []
        for i in range(self.length):
            n = self.vars[i].get()
            v = "1" if n else "0"
            ret.append(v)
        return ret

    def cmp(self, a, b):  # {{{1
        # type: (Text, Text) -> bool
        af = a.lower() in ("1", "true")
        bf = b.lower() in ("1", "true")
        return af == bf


class NPropGuiCmb(NPropGui):   # {{{1
    def __init__(self, n, typ):  # {{{1
        # type: (int, int) -> None
        NPropGui.__init__(self, n)
        self.typ = Text(typ)
        self.vars = []  # type: List[CmbVar]
        db.regist(self)

    def append(self, var):  # {{{1
        # type: (CmbVar) -> 'NPropGuiCmb'
        self.vars.append(var)
        return self

    def compose(self):  # {{{1
        # type: () -> List[Text]
        ret = []
        for i in range(self.length):
            n = self.vars[i].get()
            ret.append(Text(n))
        return ret

    def cmp(self, a, b):  # {{{1
        # type: (Text, Text) -> bool
        return a == b


class db(object):  # {{{1
    # {{{1
    db = {}  # type: Dict[int, NPropGui]

    @classmethod  # regist {{{1
    def regist(cls, item):  # {{{1
        # type: (NPropGui) -> None
        cls.db[item.prop.n] = item

    @classmethod  # regist {{{1
    def get(cls, n):  # {{{1
        # type: (int) -> NPropGui
        return cls.db[n]

    @classmethod  # regist {{{1
    def enum(cls):  # {{{1
        # type: () -> Iterable[NPropGui]
        for i in cls.db.values():
            yield i


class XInputDB(object):  # {{{1
    # {{{1
    dev = 11

    f_section = False
    n_section = 0
    cur_section = ""
    sections = {}  # type: Dict[int, Text]

    propsdb = {}  # type: Dict[str, int]
    cmd_bin = u"/usr/bin/xinput"
    cmd_shw = cmd_bin + u" list-props {} | grep '({}):'"
    cmd_int = u"set-int-prop"
    cmd_flt = u"set-float-prop"
    cmd_atm = cmd_bin + u" set-atomt-prop {} {} {} {}"

    cmd_wat = "query-state"

    def __init__(self):
        # type: () -> None
        self._callback = apply_none  # type: Callable[[List[Text]], bool]

        self._edges = NPropGuiInt(NProp.edges, 32)  # 274
        self._finger = NPropGuiInt(NProp.finger, 32)  # 275
        self._taptime = NPropGuiInt(NProp.tap_time, 32)  # 276
        self._tapmove = NPropGuiInt(NProp.tap_move, 32)  # 277
        self._tapdurs = NPropGuiInt(NProp.tap_durations, 32)  # 278
        self._twoprs = NPropGuiInt(NProp.two_finger_pressure, 32)  # 281
        self._twowid = NPropGuiInt(NProp.two_finger_width, 32)  # 282
        self._scrdist = NPropGuiInt(NProp.scrdist, 32)  # 283
        self._edgescrs = NPropGuiBol(NProp.edgescrs)  # 284
        self._twofingerscroll = NPropGuiBol(NProp.two_finger_scrolling)
        self._movespd = NPropGuiFlt(NProp.move_speed)  # 286
        self._lckdrags = NPropGuiBol(NProp.locked_drags)  # 288
        self._lckdragstimeout = NPropGuiInt(NProp.locked_drags_timeout, 32)
        self._taps = NPropGuiCmb(NProp.tap_action, 8)  # 290
        self._clks = NPropGuiCmb(NProp.click_action, 8)  # 291
        self._cirscr = NPropGuiBol(NProp.cirscr)  # 292
        self._cirdis = NPropGuiFlt(NProp.cirdis)  # 293
        self._cirtrg = NPropGuiCmb(NProp.cirtrg, 8)  # 294
        self._cirpad = NPropGuiBol(NProp.cirpad)  # 295
        self._palmDetect = NPropGuiBol(NProp.palm_detection)  # 296
        self._palmDims = NPropGuiInt(NProp.palm_dimensions, 32)  # 297
        self._cstspd = NPropGuiFlt(NProp.coasting_speed)  # 298
        self._prsmot = NPropGuiInt(NProp.pressure_motion, 32)  # 299 ???
        self._prsfct = NPropGuiFlt(NProp.pressure_motion_factor)  # 300
        self._gestures = NPropGuiBol(NProp.gestures)  # 303
        self._softareas = NPropGuiInt(NProp.softareas, 32)  # 307
        self._noise = NPropGuiInt(NProp.noise_cancellation, 32)  # 308

    @classmethod
    def determine_devid(cls):  # cls {{{2
        # type: () -> int
        cmd = cls.cmd_bin + u" list | grep -i TouchPad"
        curb = subprocess.check_output(cmd, shell=True)
        curs = curb.decode("utf-8").strip()
        if curs == "":
            return True
        if "id=" not in curs:
            return True
        curs = curs[curs.find("id="):]
        curs = curs[3:]
        curs = curs.split("\t")[0]  # TODO: use regex for more robust operation
        ret = int(curs)
        return ret

    @classmethod
    def createpropsdb_defaults(cls):  # cls {{{2
        # type: () -> bool
        for name in dir(NProp):
            if name.startswith("_"):
                continue
            v = getattr(NProp, name)
            if not isinstance(v, int):
                continue
            cls.propsdb[name] = v
        return False

    @classmethod
    def createpropsdb(cls):  # cls {{{2
        # type: () -> bool
        if False:
            cls.createpropsdb_defaults()
        propnames = []
        for name in dir(NProp):
            if name.startswith("_"):
                continue
            propnames.append(name)
        n = 0
        cmd = [cls.cmd_bin, "list-props", str(cls.dev)]
        curb = subprocess.check_output(cmd)
        curs = curb.decode("utf-8").strip()
        for line in curs.splitlines():
            if "(" not in line:
                continue
            line = line.strip()
            # print("createdb: {}".format(line))
            n = line.index("(")
            name = line[:n]  # type: ignore  ## TODO: fix for python2
            line = line[n:]
            if ")" not in line:
                continue
            n = line.index(")")
            line = line[:n].strip("( )")
            # print("createdb: {}".format(line))
            if not line.isdigit():
                print("createprops: can't parse: " + line + "\n")
                continue
            name = name.strip("( ").lower()
            name = name.replace(" ", "_")
            name = name.replace("-", "_")
            if name.startswith("synaptics_"):
                name = name[10:]
            if name not in propnames:  # cls.propsdb:
                print("createprops: can't parse: {} is not "
                      "the name of props".format(name))
                continue
            # print("{:20s}: {:3d}".format(name, int(line)))
            n += 1
            cls.propsdb[name] = int(line)
        return n < 1

    @classmethod
    def textprops(cls):  # cls {{{2
        # type: () -> str
        ret = ""
        for name in cls.propsdb:
            ret += "\n{:20s} = {:3d}".format(name, cls.propsdb[name])
        if len(ret) > 0:
            ret = ret[1:]
        return ret

    def prop_get(self, key):  # {{{1
        # type: (int) -> List[Text]
        cmd = self.cmd_shw.format(self.dev, key)
        curb = subprocess.check_output(cmd, shell=True)
        curs = curb.decode("utf-8").strip()
        seq = curs.split(":")[1].split(",")
        return [i.strip() for i in seq]

    def prop_set_int(self, key, typ, seq):  # {{{1
        # type: (int, Text, List[Text]) -> bool
        cmd = [self.cmd_bin, self.cmd_int, Text(self.dev),
               Text(key), typ] + seq
        return self._callback(cmd)

    def prop_set_flt(self, key, seq):  # {{{1
        # type: (int, List[Text]) -> bool
        cmd = [self.cmd_bin, self.cmd_flt, Text(self.dev),
               Text(key)] + seq
        return self._callback(cmd)

    def clks(self, i):  # {{{2
        # type: (int) -> int
        txt = db.get(NProp.click_action).current(i)
        ret = int(txt)
        return ret

    def taps(self, i):  # {{{2
        # type: (int) -> int
        txt = db.get(NProp.tap_action).current(i)
        ret = int(txt)
        return ret

    def tapdurs(self, i):  # {{{2
        # type: (int) -> int
        txt = db.get(NProp.tap_durations).current(i)
        ret = int(txt)
        return ret

    def taptime(self):  # {{{2
        # type: () -> int
        txt = db.get(NProp.tap_time).current(0)
        ret = int(txt)
        return ret

    def tapmove(self):  # {{{2
        # type: () -> int
        txt = db.get(NProp.tap_move).current(0)
        ret = int(txt)
        return ret

    def finger(self, i):  # {{{2
        # type: (int) -> int
        def limit(seq):  # TODO: add to NPropGui
            # type: (List[Text]) -> bool
            low = int(seq[0])
            hig = int(seq[1])
            return low < hig
        txt = db.get(NProp.finger).current(i)
        ret = int(txt)
        return ret

    def twofingerscroll(self, i):  # {{{2
        # type: (int) -> bool
        txt = db.get(NProp.two_finger_scrolling).current(i)
        ret = bool(txt)
        return ret

    def movespd(self, i):  # {{{2
        # type: (int) -> float
        txt = db.get(NProp.move_speed).current(i)
        ret = float(txt)
        return ret

    def lckdrags(self):  # {{{2
        # type: () -> bool
        txt = db.get(NProp.locked_drags).current(0)
        ret = bool(txt)
        return ret

    def lckdragstimeout(self):  # {{{2
        # type: () -> int
        txt = db.get(NProp.locked_drags_timeout).current(0)
        ret = int(txt)
        return ret

    def cirscr(self):  # {{{2
        # type: () -> bool
        txt = db.get(NProp.circular_scrolling).current(0)
        ret = bool(txt)
        return ret

    def cirtrg(self):  # {{{2
        # type: () -> int
        def limit(seq):  # TODO: impl.
            # type: (List[Text]) -> bool
            cur = int(seq[0])
            return 0 <= cur <= 8
        txt = db.get(NProp.circular_scrolling_trigger).current(0)
        ret = int(txt)
        return ret

    def cirpad(self):  # {{{2
        # type: () -> bool
        txt = db.get(NProp.circular_pad).current(0)
        ret = bool(txt)
        return ret

    def cirdis(self):  # {{{2
        # type: () -> float
        txt = db.get(NProp.circular_scrolling_distance).current(0)
        ret = float(txt)
        return ret

    def edges(self, i):  # {{{2
        # type: (int) -> int
        txt = db.get(NProp.edges).current(i)
        ret = int(txt)
        return ret

        """
        assert len(v) in (0, 4)
        n = NProp.edges
        prop = db.get(n)
        if len(v) > 0:
            pass
        elif prop.is_changed():
            pass
        return self.prop_i32(n, i, v)
        """

    def edgescrs(self, i):  # {{{2
        # type: (int) -> bool
        txt = db.get(NProp.edge_scrolling).current(i)
        ret = bool(txt)
        return ret

    def cstspd(self, i):  # {{{2
        # type: (int) -> float
        txt = db.get(NProp.coasting_speed).current(i)
        ret = float(txt)
        return ret

    def prsmot(self, i):  # {{{2
        # type: (int) -> int
        txt = db.get(NProp.pressure_motion).current(i)
        ret = int(txt)
        return ret

    def prsfct(self, i):  # {{{2
        # type: (int) -> float
        txt = db.get(NProp.pressure_motion_factor).current(i)
        ret = float(txt)
        return ret

    def palmDetect(self):  # {{{2
        # type: () -> bool
        txt = db.get(NProp.palm_detection).current(0)
        ret = bool(txt)
        return ret

    def palmDims(self, i):  # {{{2
        # type: (int) -> int
        txt = db.get(NProp.palm_dimensions).current(i)
        ret = int(txt)
        return ret

    def softareas(self, i):  # {{{2
        # type: (int) -> int
        txt = db.get(NProp.soft_button_areas).current(i)
        ret = int(txt)
        return ret

    def twoprs(self):  # {{{2
        # type: () -> int
        txt = db.get(NProp.two_finger_pressure).current(0)
        ret = int(txt)
        return ret

    def twowid(self):  # {{{2
        # type: () -> int
        txt = db.get(NProp.two_finger_width).current(0)
        ret = int(txt)
        return ret

    def scrdist(self, i):  # {{{2
        # type: (int) -> int
        txt = db.get(NProp.scrolling_distance).current(i)
        ret = int(txt)
        return ret

    def gestures(self):  # {{{2
        # type: () -> bool
        txt = db.get(NProp.gestures).current(0)
        ret = bool(txt)
        return ret

    def noise(self, i):  # {{{2
        # type: (int) -> int
        txt = db.get(NProp.noise_cancellation).current(i)
        ret = int(txt)
        return ret

    def props(self):  # {{{2
        # type: () -> Tuple[List[bool], List[int]]
        cmd = [self.cmd_bin, self.cmd_wat, str(self.dev)]
        curb = subprocess.check_output(cmd)
        curs = curb.decode("utf-8")

        _btns = {}  # type: Dict[int, bool]
        _vals = {}  # type: Dict[int, int]
        for line in curs.splitlines():
            line = line.strip()
            if line.startswith("button"):
                try:
                    l, r = line.split("=")
                    idx = int(line.split("[")[1].split("]")[0]) - 1
                    _btns[idx] = True if r == "down" else False
                except:
                    pass
                continue
            if line.startswith("valuator"):
                try:
                    l, r = line.split("=")
                    idx = int(line.split("[")[1].split("]")[0])
                    _vals[idx] = int(r)
                except:
                    pass
                continue
        btns = [_btns.get(i, False) for i in range(max(_btns.keys()) + 1)]
        vals = [_vals.get(i, 0) for i in range(max(_vals.keys()) + 1)]
        return btns, vals

    def apply(self, fn, f_changed):  # {{{1
        # type: (Callable[[List[Text]], bool], bool) -> bool
        info("-------- start apply() function -------------------------------")
        self._callback = fn

        for prop in db.enum():
            if not f_changed:
                pass
            elif not prop.is_changed():
                continue
            info("syncing {}...".format(prop.prop.n))
            prop.sync()

        return False

    @classmethod  # apply_cmd # {{{1
    def apply_cmd(cls, cmd):
        # type: (List[Text]) -> bool
        if not common.opts.fDryrun:
            info("command invoked: " + Text(cmd))
            subprocess.call(cmd)
        return False

    def dump(self):  # {{{2
        # type: () -> List[List[Text]]
        # from GUI.
        ret = []  # type: List[List[Text]]

        def apply_log(cmd):
            # type: (List[Text]) -> bool
            ret.append(cmd)
            return False

        self.apply(apply_log, False)
        return ret

    def dumpdb(self):  # {{{2
        # type: () -> NPropDb
        ret = NPropDb()

        def apply(cmd):
            # type: (List[Text]) -> bool
            prop = NProp.from_cmd(cmd)
            if prop is None:
                return False
            ret[prop.n] = prop
            return False

        self.apply(apply, False)
        return ret

    def dumps(self):  # {{{2
        # type: () -> Text
        # from GUI.
        cmds = []  # type: List[List[Text]]

        def apply_log(cmd):
            # type: (List[Text]) -> bool
            cmds.append(cmd)
            return False

        self.apply(apply_log, False)

        ret = u""
        for line in cmds:
            ret += u'\n' + u' '.join(line)
        if len(ret) > 0:
            ret = ret[1:]

        return ret


# {{{1
xi = XInputDB()
cmdorg = []  # type: List[List[Text]]


# options {{{1
def options():  # {{{1
    # type: () -> Any
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('--verbose', '-v', type=int, default=logging.WARNING,
                   choices=[logging.DEBUG, logging.INFO, logging.WARNING,
                            logging.ERROR, logging.CRITICAL, ])
    p.add_argument('--device-id', '-d', type=int, default=0)
    p.add_argument('--file-encoding', '-e', type=str, default="utf-8")
    p.add_argument('--dry-run', '-n', action="store_true")
    p.add_argument("-o", '--output', dest="fnameOut", type=str,
                   default="99-synaptics.conf")
    p.add_argument("-i", '--input', dest="fnameIn", type=str,
                   default="/usr/share/X11/xorg.conf.d/70-synaptics.conf")
    opts = p.parse_args()

    logging.getLogger().setLevel(opts.verbose)
    logging.getLogger().name = "touchpad"
    if opts.device_id == 0:
        ret = XInputDB.determine_devid()
        if ret is True:
            return None
        print("synaptics was detected as {} device".format(ret))
        xi.dev = ret
    common.opts.fDryrun = opts.dry_run
    common.opts.file_encoding = opts.file_encoding
    common.opts.fnameIn = opts.fnameIn
    common.opts.fnameOut = opts.fnameOut
    return opts


# gui {{{1
class Gui(object):  # {{{1
    def checkbox(self, parent, title, cur):  # {{{2
        # type: (tk.Widget, str, bool) -> BoolVar
        ret = tk.IntVar()
        ret.set(1 if cur else 0)
        tk.Checkbutton(parent, text=title,
                       variable=ret).pack(side=tk.LEFT)
        _ret = BoolVar(ret)
        return _ret

    def slider(self, parent, from_, to, cur):  # {{{2
        # type: (tk.Widget, int, int, int) -> IntVar
        ret = tk.IntVar()
        ret.set(cur)
        wid = tk.Scale(parent, from_=from_, to=to, orient=tk.HORIZONTAL,
                       variable=ret)
        wid.pack(side=tk.LEFT)
        self.lastwid = wid
        _ret = IntVar(ret)
        return _ret

    def slider_flt(self, parent, from_, to, cur):  # {{{2
        # type: (tk.Widget, float, float, float) -> FltVar
        ret = tk.DoubleVar()
        ret.set(cur)
        tk.Scale(parent, from_=from_, to=to, orient=tk.HORIZONTAL,
                 variable=ret, resolution=0.01).pack(side=tk.LEFT)
        _ret = FltVar(ret)
        return _ret

    def combobox(self, parent, seq, cur):  # {{{2
        # type: (tk.Widget, List[str], int) -> CmbVar
        ret = ttk.Combobox(parent, values=seq)
        ret.current(cur)
        ret.pack(side=tk.LEFT)
        _ret = CmbVar(ret)
        return _ret

    def label2(self, parent, txt, n, **kw):  # {{{2
        # type: (tk.Widget, str, int, **Any) -> None
        if len(kw) < 1:
            kw["anchor"] = tk.W
        if "width" in kw:
            ret = tk.Label(parent, text=txt, width=kw["width"])
            del kw["width"]
        else:
            ret = tk.Label(parent, text=txt)
        ret.pack(**kw)
        ret.bind("<Button-1>", self.hint)
        _id = Text(repr(ret))
        NProp.hintnums[_id] = n

    def label3(self, parent, txt, n, **kw):  # {{{2
        # type: (tk.Widget, str, int, **Any) -> None
        if "side" not in kw:
            kw["side"] = tk.LEFT
        self.label2(parent, txt, n, **kw)

    def hint(self, ev):  # {{{2
        # type: (tk.Event) -> None
        wid = getattr(ev, "widget")
        assert isinstance(wid, tk.Widget)
        _id = Text(repr(wid))
        if _id not in NProp.hintnums:
            return
        n = NProp.hintnums[_id]
        txt = NProp.hinttext[n]
        txt = Text(n) + txt
        self.test.delete(1.0, tk.END)
        self.test.insert(tk.END, txt)

    def callback_idle(self):  # {{{2
        # type: () -> None
        btns, vals = xi.props()
        self.txt1.delete(0, tk.END)
        self.txt2.delete(0, tk.END)
        self.txt3.delete(0, tk.END)
        self.txt4.delete(0, tk.END)
        self.txt1.insert(0, "{}".format(vals[0]))
        self.txt2.insert(0, "{}".format(vals[1]))
        self.txt3.insert(0, "{}".format(vals[2]))
        self.txt4.insert(0, "{}".format(vals[3]))
        _btns = ["black" if i else "white" for i in btns]
        gui_canvas(self.mouse, _btns, vals, [])
        self.root.after(100, self.callback_idle)

    def cmdfingerlow(self, ev):  # {{{2
        # type: (tk.Event) -> None
        vl = self.fingerlow.get()
        vh = self.fingerhig.get()
        if vl < vh:
            return
        self.fingerlow.set(vh - 1)

    def cmdfingerhig(self, ev):  # {{{2
        # type: (tk.Event) -> None
        vl = self.fingerlow.get()
        vh = self.fingerhig.get()
        if vl < vh:
            return
        self.fingerhig.set(vl + 1)

    def cmdrestore(self):  # {{{2
        # type: () -> None
        for cmd in cmdorg:
            print("restore: " + str(cmd))
            subprocess.call(cmd)

    def cmdapply(self):  # {{{2
        # type: () -> None
        xi.apply(xi.apply_cmd, True)

    def cmdsave(self):  # {{{2
        # type: () -> None
        opts = common.opts
        xf = XConfFile()
        db = xf.read(opts.fnameIn)
        for n, p in xi.dumpdb().items():
            prop = db[n]
            prop.update(p)
        warn("output saved to {}".format(opts.fnameOut))
        xf.save(opts.fnameOut, opts.fnameIn, db)

    def cmdquit(self):  # {{{2
        # type: () -> None
        self.root.quit()

    def cmdreport(self):  # {{{2
        # type: () -> None
        import sys
        import platform
        from datetime import datetime

        opts = common.opts
        fname = datetime.now().strftime("report-%Y%m%d-%H%M%S.txt")
        enc = opts.file_encoding
        fp = open_file(fname, "a")
        bs = subprocess.check_output("uname -a", shell=True)
        msg = bs.decode(enc)
        fp.write(msg + "\n")
        bs = subprocess.check_output("python3 -m platform", shell=True)
        msg = bs.decode(enc)
        fp.write(msg + "\n")
        fp.write("Python: {}\n".format(str(sys.version_info)))
        if sys.version_info[0] == 2:
            sbld = platform.python_build()  # type: ignore
            scmp = platform.python_compiler()  # type: ignore
        else:
            sbld = platform.python_build()
            scmp = platform.python_compiler()
        fp.write("Python: {} {}\n".format(sbld, scmp))
        bs = subprocess.check_output("xinput list", shell=True)
        msg = bs.decode(enc)
        fp.write(msg + u"\n")
        bs = subprocess.check_output("xinput list-props {}".format(
            xi.dev), shell=True)
        msg = bs.decode(enc)
        fp.write(msg + u"\n")
        fp.write(u"\n\n--- current settings (in app)---\n")
        fp.write(xi.dumps())
        fp.write(u"\n\n--- initial settings (at app startup)---")
        cmds = u""
        for i in cmdorg:
            cmds += u"\n" + u" ".join(i)
        fp.write(cmds + "\n")
        fp.close()

        msg = u"Report: {} was made,\n" \
              u"use this file to report a issue.".format(fname)
        messagebox.showinfo(u"Make a Report", msg)

    def __init__(self, root):  # {{{2
        # type: (tk.Tk) -> None
        self.root = root
        self.fingerlow = self.fingerhig = tk.Scale(root)
        self.mouse = tk.Canvas(root)
        self.test = tk.Text(root)
        self.txt1 = self.txt2 = self.txt3 = self.txt4 = tk.Entry(root)

        self.ex1 = self.ey1 = 0
        self.ex2 = self.ey2 = 0
        self.s1x1 = self.s1y1 = self.s1x2 = self.s1y2 = 0
        self.s2x1 = self.s2y1 = self.s2x2 = self.s2y2 = 0


def buildgui(opts):  # {{{1
    # type: (Any) -> Gui
    global cmdorg
    root = tk.Tk()
    gui = Gui(root)

    root.title("{}".format(
        os.path.splitext(os.path.basename(__file__))[0]))

    # 1st: pad, mouse and indicator {{{2
    frm1 = tk.Frame(root, height=5)

    ''' +--root--------------------+
        |+--frm1------------------+|
        ||+-frm11-+-mouse-+-frm13-+|
        |+--tab-------------------+|
        |+--frm3------------------+|
        +--------------------------+
    '''
    frm11 = tk.Frame(frm1)
    gui.mouse = tk.Canvas(frm1, width=_100, height=_100)
    frm13 = tk.Frame(frm1)

    # gui_canvas(gui.mouse, ["white"] * 7, [0] * 4,
    #            [[xi.edges(i) for i in range(4)],
    #             [xi.softareas(i) for i in range(8)]])

    tk.Label(frm11, text="Information (update to click labels, "
                         "can be used for scroll test)").pack(anchor=tk.W)
    gui.test = tk.Text(frm11, height=10)
    gui.test.pack(padx=5, pady=5, expand=True, fill="x")
    gui.test.insert(tk.END, "Test field\n\n  and click title labels to show "
                    "description of properties.")

    tk.Label(frm13, text="Current", width=7).pack(anchor=tk.W)
    gui.txt1 = tk.Entry(frm13, width=6)
    gui.txt1.pack()
    gui.txt2 = tk.Entry(frm13, width=6)
    gui.txt2.pack()
    gui.txt3 = tk.Entry(frm13, width=6)
    gui.txt3.pack()
    gui.txt4 = tk.Entry(frm13, width=6)
    gui.txt4.pack()

    gui.mouse.pack(side=tk.LEFT, anchor=tk.N)
    frm13.pack(side=tk.LEFT, anchor=tk.N)
    frm11.pack(side=tk.LEFT, anchor=tk.N, expand=True, fill="x")

    # 2nd: tab control
    nb = ttk.Notebook(root)
    page1 = tk.Frame(nb)
    nb.add(page1, text="Tap/Click")
    page4 = tk.Frame(nb)
    nb.add(page4, text="Area")
    page2 = tk.Frame(nb)
    nb.add(page2, text="Two-Fingers")
    page5 = tk.Frame(nb)
    nb.add(page5, text="Misc.")
    page6 = tk.Frame(nb)
    nb.add(page6, text="Information")
    page3 = tk.Frame(nb)
    nb.add(page3, text="About")

    # 3rd: main button
    frm3 = tk.Frame(root)

    btn3 = tk.Button(frm3, text="Quit", command=gui.cmdquit)
    btn3.pack(side=tk.RIGHT, padx=10)
    btn2 = tk.Button(frm3, text="Save", command=gui.cmdsave)
    btn2.pack(side=tk.RIGHT, padx=10)
    btn1 = tk.Button(frm3, text="Apply", command=gui.cmdapply)
    btn1.pack(side=tk.RIGHT, padx=10)
    btn0 = tk.Button(frm3, text="Restore", command=gui.cmdrestore)
    btn0.pack(side=tk.RIGHT, padx=10)

    frm1.pack(expand=1, fill="both")
    nb.pack(expand=1, fill="both")
    frm3.pack(expand=1, fill="both")

    # sub pages {{{2
    # page1 - basic {{{2
    # Click Action
    seq = (["Disabled", "Left-Click", "Middel-Click", "Right-Click"] +
           [str(i) for i in range(4, 10)])
    gui.label2(page1, "Click actions", NProp.click_action)
    frm = tk.Frame(page1)
    frm.pack()
    tk.Label(frm, text="1-Finger").pack(side=tk.LEFT, padx=10)
    xi._clks.append(gui.combobox(frm, seq, xi.clks(0)))
    tk.Label(frm, text="2-Finger").pack(side=tk.LEFT)
    xi._clks.append(gui.combobox(frm, seq, xi.clks(1)))
    tk.Label(frm, text="3-Finger").pack(side=tk.LEFT)
    xi._clks.append(gui.combobox(frm, seq, xi.clks(2)))

    # Tap Action
    gui.label2(page1, "Tap actions", NProp.tap_action)
    frm = tk.Frame(page1)
    frm.pack(anchor=tk.W)
    tk.Label(frm, text="RT", width=10).pack(side=tk.LEFT, padx=10)
    xi._taps.append(gui.combobox(frm, seq, xi.taps(0)))
    tk.Label(frm, text="RB").pack(side=tk.LEFT)
    xi._taps.append(gui.combobox(frm, seq, xi.taps(1)))
    frm = tk.Frame(page1)
    frm.pack(anchor=tk.W)
    tk.Label(frm, text="LT", width=10).pack(side=tk.LEFT, padx=10)
    xi._taps.append(gui.combobox(frm, seq, xi.taps(2)))
    tk.Label(frm, text="LB").pack(side=tk.LEFT)
    xi._taps.append(gui.combobox(frm, seq, xi.taps(3)))
    frm = tk.Frame(page1)
    frm.pack(anchor=tk.W)
    tk.Label(frm, text="1-Finger", width=10).pack(side=tk.LEFT, padx=10)
    xi._taps.append(gui.combobox(frm, seq, xi.taps(4)))
    tk.Label(frm, text="2-Finger").pack(side=tk.LEFT)
    xi._taps.append(gui.combobox(frm, seq, xi.taps(5)))
    tk.Label(frm, text="3-Finger").pack(side=tk.LEFT)
    xi._taps.append(gui.combobox(frm, seq, xi.taps(6)))

    # Tap Threshold
    w = 10
    frm_ = tk.Frame(page1)
    gui.label3(frm_, "FingerLow", NProp.finger, width=w)
    xi._finger.append(gui.slider(frm_, 1, 255, cur=xi.finger(0)))
    gui.fingerlow = gui.lastwid
    gui.lastwid.bind("<ButtonRelease-1>", gui.cmdfingerlow)
    # xii.fingerlow.pack(side=tk.LEFT, expand=True, fill="x")
    # frm_.pack(fill="x")
    # frm_ = tk.Frame(page1)
    tk.Label(frm_, text="FingerHigh", width=10).pack(side=tk.LEFT)
    xi._finger.append(gui.slider(frm_, 1, 255, cur=xi.finger(1)))
    gui.fingerhig = gui.lastwid
    gui.lastwid.bind("<ButtonRelease-1>", gui.cmdfingerhig)
    # gui.fingerhig.pack(side=tk.LEFT, expand=True, fill="x")
    frm_.pack(fill="x", anchor=tk.W)
    v = IntVar(None)
    xi._finger.append(v)  # dummy

    frm = tk.Frame(page1)
    gui.label3(frm, "Tap Time", NProp.tap_time, width=w)
    xi._taptime.append(gui.slider(frm, 1, 255, xi.taptime()))
    tk.Label(frm, text="Tap Move", width=10).pack(side=tk.LEFT)
    xi._tapmove.append(gui.slider(frm, 1, 255, xi.tapmove()))
    frm.pack(anchor=tk.W)
    frm = tk.Frame(page1)
    gui.label3(frm, "Tap Durations", NProp.tap_durations, width=w)
    xi._tapdurs.append(gui.slider(frm, 1, 255, xi.tapdurs(0)))
    xi._tapdurs.append(gui.slider(frm, 1, 255, xi.tapdurs(1)))
    xi._tapdurs.append(gui.slider(frm, 1, 255, xi.tapdurs(2)))
    frm.pack(anchor=tk.W)

    # page4 - Area {{{2
    frm = tk.Frame(page4)
    gui.label3(frm, "Palm detect", NProp.palm_detection)
    xi._palmDetect.append(gui.checkbox(frm, "on", xi.palmDetect()))
    gui.label3(frm, "Palm dimensions", NProp.palm_dimensions)
    xi._palmDims.append(gui.slider(frm, 0, 3100, xi.palmDims(0)))
    xi._palmDims.append(gui.slider(frm, 0, 3100, xi.palmDims(1)))
    frm.pack(anchor=tk.W)

    frm = tk.Frame(page4)
    gui.label3(frm, "Edge-x", NProp.edges)
    xi._edges.append(gui.slider(frm, 0, 3100, xi.edges(0)))
    xi._edges.append(gui.slider(frm, 0, 3100, xi.edges(1)))
    tk.Label(frm, text="Edge-y").pack(side=tk.LEFT)
    xi._edges.append(gui.slider(frm, 0, 1800, xi.edges(2)))
    xi._edges.append(gui.slider(frm, 0, 1800, xi.edges(3)))
    frm.pack(anchor=tk.W)

    gui.label2(page4, "Soft Button Areas "
               "(RB=Right Button, MB=Middle Button)", NProp.soft_button_areas,
               anchor=tk.W)
    frm = tk.Frame(page4)
    tk.Label(frm, text="RB-Left", width=10).pack(side=tk.LEFT, padx=10)
    xi._softareas.append(gui.slider(frm, 0, 3100, xi.softareas(0)))
    tk.Label(frm, text="RB-Right", width=10).pack(side=tk.LEFT)
    xi._softareas.append(gui.slider(frm, 0, 3100, xi.softareas(1)))
    tk.Label(frm, text="RB-Top", width=10).pack(side=tk.LEFT)
    xi._softareas.append(gui.slider(frm, 0, 3100, xi.softareas(2)))
    tk.Label(frm, text="RB-Bottom", width=10).pack(side=tk.LEFT)
    xi._softareas.append(gui.slider(frm, 0, 3100, xi.softareas(3)))
    frm.pack(anchor=tk.W)
    frm = tk.Frame(page4)
    tk.Label(frm, text="MB-Left", width=10).pack(side=tk.LEFT, padx=10)
    xi._softareas.append(gui.slider(frm, 0, 3100, xi.softareas(4)))
    tk.Label(frm, text="MB-Right", width=10).pack(side=tk.LEFT)
    xi._softareas.append(gui.slider(frm, 0, 3100, xi.softareas(5)))
    tk.Label(frm, text="MB-Top", width=10).pack(side=tk.LEFT)
    xi._softareas.append(gui.slider(frm, 0, 3100, xi.softareas(6)))
    tk.Label(frm, text="MB-Bottom", width=10).pack(side=tk.LEFT)
    xi._softareas.append(gui.slider(frm, 0, 3100, xi.softareas(7)))
    frm.pack(anchor=tk.W)

    frm = tk.Frame(page4)
    gui.label3(frm, "Edge scroll", NProp.edge_scrolling)
    xi._edgescrs.append(gui.checkbox(frm, "Vert", xi.edgescrs(0)))
    xi._edgescrs.append(gui.checkbox(frm, "Horz", xi.edgescrs(1)))
    xi._edgescrs.append(gui.checkbox(frm, "Corner Coasting", xi.edgescrs(2)))
    frm.pack(anchor=tk.W)

    # page2 - two-fingers {{{2
    frm = tk.Frame(page2)
    gui.label3(frm, "Two-Finger Scrolling", NProp.two_finger_scrolling)
    xi._twofingerscroll.append(
            gui.checkbox(frm, "Vert", xi.twofingerscroll(0)))
    xi._twofingerscroll.append(
            gui.checkbox(frm, "Horz", xi.twofingerscroll(1)))
    frm.pack(anchor=tk.W)

    frm = tk.Frame(page2)
    gui.label3(frm, "Two-Finger Pressure", NProp.two_finger_pressure)
    xi._twoprs.append(gui.slider(frm, 1, 1000, xi.twoprs()))
    gui.label3(frm, "Two-Finger Width", NProp.two_finger_width)
    xi._twowid.append(gui.slider(frm, 1, 1000, xi.twowid()))
    frm.pack(anchor=tk.W)

    frm = tk.Frame(page2)
    gui.label3(frm, "Scrolling Distance", NProp.scrolling_distance)
    xi._scrdist.append(gui.slider(frm, 1, 1000, xi.scrdist(0)))
    xi._scrdist.append(gui.slider(frm, 1, 1000, xi.scrdist(1)))
    frm.pack(anchor=tk.W)

    # page5 - Misc {{{2
    w = 13
    frm = tk.Frame(page5)
    gui.label3(frm, "Noise Cancel (x-y)", NProp.noise_cancellation, width=w)
    xi._noise.append(gui.slider(frm, 1, 1000, xi.noise(0)))
    xi._noise.append(gui.slider(frm, 1, 1000, xi.noise(1)))
    frm.pack(anchor=tk.W)
    frm = tk.Frame(page5)
    gui.label3(frm, "Move speed", NProp.move_speed, width=w)
    xi._movespd.append(gui.slider_flt(frm, 0, 10, xi.movespd(0)))
    xi._movespd.append(gui.slider_flt(frm, 0, 10, xi.movespd(1)))
    xi._movespd.append(gui.slider_flt(frm, 0, 10, xi.movespd(2)))
    xi._movespd.append(gui.slider_flt(frm, 0, 10, xi.movespd(3)))
    frm.pack(anchor=tk.W)
    frm = tk.Frame(page5)
    gui.label3(frm, "Pressure Motion", NProp.pressure_motion, width=w)
    xi._prsmot.append(gui.slider(frm, 1, 1000, xi.prsmot(0)))
    xi._prsmot.append(gui.slider(frm, 1, 1000, xi.prsmot(1)))
    tk.Label(frm, text="Factor").pack(side=tk.LEFT)
    xi._prsfct.append(gui.slider_flt(frm, 1, 1000, xi.prsfct(0)))
    xi._prsfct.append(gui.slider_flt(frm, 1, 1000, xi.prsfct(1)))
    frm.pack(anchor=tk.W)
    frm = tk.Frame(page5)
    gui.label3(frm, "Coasting speed", NProp.coasting_speed, width=w)
    xi._cstspd.append(gui.slider_flt(frm, 1, 1000, xi.cstspd(0)))
    xi._cstspd.append(gui.slider_flt(frm, 1, 1000, xi.cstspd(1)))
    frm.pack(anchor=tk.W)
    frm = tk.Frame(page5)
    gui.label3(frm, "Locked Drags", NProp.locked_drags, width=w)
    xi._lckdrags.append(gui.checkbox(frm, "on", xi.lckdrags()))
    tk.Label(frm, text="timeout").pack(side=tk.LEFT)
    xi._lckdragstimeout.append(
            gui.slider(frm, 1, 100000, xi.lckdragstimeout()))
    xi._gestures.append(gui.checkbox(frm, "gesture", xi.gestures()))
    frm.pack(anchor=tk.W)
    frm = tk.Frame(page5)
    gui.label3(frm, "Circular scrolling", NProp.circular_scrolling, width=w)
    xi._cirscr.append(gui.checkbox(frm, "on", xi.cirscr()))
    xi._cirpad.append(gui.checkbox(frm, "Circular-pad", xi.cirpad()))
    gui.label3(frm, "  Distance", NProp.circular_scrolling_distance)
    xi._cirdis.append(gui.slider_flt(frm, 0.01, 100, xi.cirdis()))
    gui.label3(frm, "  Trigger", NProp.circular_scrolling_trigger)
    xi._cirtrg.append(gui.combobox(frm, ["0: All Edges",
                                         "1: Top Edge",
                                         "2: Top Right Corner",
                                         "3: Right Edge",
                                         "4: Bottom Right Corner",
                                         "5: Bottom Edge",
                                         "6: Bottom Left Corner",
                                         "7: Left Edge",
                                         "8: Top Left Corner"], xi.cirtrg()))
    frm.pack(anchor=tk.W)

    # page6 - Information {{{2
    frm = tk.Frame(page6)
    tk.Label(frm, text="Capability", width=20).pack(side=tk.LEFT)
    tk.Label(frm, text="...").pack(side=tk.LEFT)
    frm.pack(anchor=tk.W)
    frm = tk.Frame(page6)
    tk.Label(frm, text="Resolution [unit/mm]", width=20).pack(side=tk.LEFT)
    tk.Label(frm, text="...").pack(side=tk.LEFT)
    frm.pack(anchor=tk.W)
    frm = tk.Frame(page6)
    tk.Label(frm, text="XInput2 Keywords", width=20).pack(side=tk.LEFT)
    txt = tk.Text(frm, height=3)
    txt.insert(tk.END, XInputDB.textprops())
    txt.pack(side=tk.LEFT, fill="both", expand=True)
    frm.pack(anchor=tk.W)
    frm = tk.Frame(page6)
    tk.Label(frm, text="Restore", width=20).pack(side=tk.LEFT)
    txt = tk.Text(frm, height=3)
    txt.insert(tk.END, xi.dumps())
    txt.pack(side=tk.LEFT, fill="both", expand=True)
    frm.pack(anchor=tk.W)

    # page3 - About (License information) {{{2
    tk.Label(page3, text="TouchPad Tuner").pack()
    tk.Label(page3, text="Shimoda (kuri65536@hotmail.com)").pack()
    tk.Label(page3, text="License: Mozilla Public License 2.0").pack()
    tk.Button(page3, text="Make log for the report",  # TODO: align right
              command=gui.cmdreport).pack()  # .pack(anchor=tk.N)

    # pad.config(height=4)
    cmdorg = xi.dump()
    return gui


_100 = 150


def gui_scale(x, y):
    # type: (float, float) -> Tuple[int, int]
    rx = int(x) * _100 / 3192
    ry = int(y) * _100 / 1822
    return int(rx), int(ry)


def gui_softarea(seq):
    # type: (List[int]) -> Tuple[int, int, int, int]
    x1, y1 = seq[0], seq[2]
    x2, y2 = seq[1], seq[3]
    if x1 == 0 and y1 == 0 and x2 == 0 and y2 == 0:
        pass
    else:
        if x1 == 0:
            x1 = 0
        if y1 == 0:
            y1 = 0
        if x2 == 0:
            x2 = 3192
        if y2 == 0:
            y2 = 1822
    x1, y1 = gui_scale(x1, y1)
    x2, y2 = gui_scale(x2, y2)
    return x1, y1, x2, y2


def gui_canvas(inst, btns,  # {{{2
               vals, prms):
    # type: (tk.Canvas, List[str], List[int], List[List[int]]) -> None
    if gui is None:
        return
    _20 = 20
    _35 = 35
    _40 = 40
    _45 = 45
    _55 = 55
    _60 = 60
    _65 = 65
    _80 = 80

    inst.create_rectangle(0, 0, _100, _100, fill='white')  # ,stipple='gray25')
    if len(prms) > 0:
        edges = prms[0]
        gui.ex1, gui.ey1 = gui_scale(edges[0], edges[2])
        gui.ex2, gui.ey2 = gui_scale(edges[1], edges[3])
        # print("gui_canvas: edge: ({},{})-({},{})".format(x1, y1, x2, y2))
        areas = prms[1]
        gui.s1x1, gui.s1y1, gui.s1x2, gui.s1y2 = gui_softarea(areas[0:4])
        gui.s2x1, gui.s2y1, gui.s2x2, gui.s2y2 = gui_softarea(areas[4:8])
        print("gui_canvas: RB: ({},{})-({},{})".format(
              gui.s1x1, gui.s1y1, gui.s1x2, gui.s1y2))
        print("gui_canvas: MB: ({},{})-({},{})".format(
              gui.s2x1, gui.s2y1, gui.s2x2, gui.s2y2))

    if gui.s1x1 != gui.s1x2 and gui.s1y1 != gui.s1y2:
        inst.create_rectangle(gui.s1x1, gui.s1y1, gui.s1x2, gui.s1y2,
                              fill="green")  # area for RB
    if gui.s2x1 != gui.s2x2 and gui.s2y1 != gui.s2y2:
        inst.create_rectangle(gui.s2x1, gui.s2y1, gui.s2x2, gui.s2y2,
                              fill="blue")  # area for MB
    inst.create_rectangle(gui.ex1, gui.ey1, gui.ex2, gui.ey2,
                          width=2)

    # +-++++++-+
    # | |||||| |  (60 - 30) / 3 = 10
    inst.create_rectangle(_20, _20, _80, _80, fill='white')
    inst.create_rectangle(_35, _20, _45, _45, fill=btns[0])
    inst.create_rectangle(_45, _20, _55, _45, fill=btns[1])
    inst.create_rectangle(_55, _20, _65, _45, fill=btns[2])
    # inst.create_arc(_20, _20, _80, _40, style='arc', fill='white')
    # inst.create_line(_20, _40, _20, _80, _80, _80, _80, _40)
    inst.create_rectangle(_40, _55, _60, _60, fill=btns[5])
    inst.create_rectangle(_40, _60, _60, _65, fill=btns[6])

    x, y = gui_scale(vals[0], vals[1])
    inst.create_oval(x - 2, y - 2, x + 2, y + 2, fill="black")
    x, y = gui_scale(vals[2], vals[3])
    x, y = x % _100, y % _100
    inst.create_oval(x - 2, y - 2, x + 2, y + 2, fill="red")


# globals {{{1
gui = None  # type: Optional[Gui]


# main {{{1
def main():  # {{{1
    # type: () -> int
    global gui
    debg("fetch settings, options and arguments...")
    opts = options()
    if opts is None:
        print("can't found Synaptics in xinput.")
        return 1
    debg("create properties DB...")
    if XInputDB.createpropsdb():
        print("can't found Synaptics properties in xinput.")
        return 2
    debg("build GUI...")
    gui = buildgui(opts)
    gui.root.after_idle(gui.callback_idle)
    debg("start gui...")
    gui.root.mainloop()
    return 0


if __name__ == "__main__":  # end of file {{{1
    main()
# vi: ft=python:et:fdm=marker:nowrap:tw=80

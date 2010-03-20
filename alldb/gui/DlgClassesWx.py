# -*- coding: utf-8 -*-
# generated by wxGlade HG on Sat Mar 20 17:02:11 2010

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode

# end wxGlade

class DlgClassesWx(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: DlgClassesWx.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.lc_classes = wx.ListCtrl(self, -1, style=wx.LC_LIST|wx.SUNKEN_BORDER)
        self.button_new = wx.Button(self, wx.ID_ADD, "")
        self.button_edit = wx.Button(self, -1, _("&Edit"))
        self.button_delete = wx.Button(self, wx.ID_DELETE, "")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_list_classes_deselect, self.lc_classes)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_list_classes_selected, self.lc_classes)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_classes_activate, self.lc_classes)
        self.Bind(wx.EVT_BUTTON, self._on_btn_new, self.button_new)
        self.Bind(wx.EVT_BUTTON, self._on_btn_edit, self.button_edit)
        self.Bind(wx.EVT_BUTTON, self._on_btn_delete, self.button_delete)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: DlgClassesWx.__set_properties
        self.SetTitle(_("Categories"))
        self.lc_classes.SetMinSize((200,400))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: DlgClassesWx.__do_layout
        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11 = wx.BoxSizer(wx.VERTICAL)
        sizer_10.Add(self.lc_classes, 1, wx.EXPAND, 6)
        sizer_10.Add((6, 100), 0, 0, 0)
        sizer_11.Add(self.button_new, 0, wx.ALL, 3)
        sizer_11.Add((20, 20), 0, 0, 0)
        sizer_11.Add(self.button_edit, 0, wx.ALL, 3)
        sizer_11.Add(self.button_delete, 0, wx.ALL, 3)
        sizer_11.Add((20, 20), 1, 0, 0)
        sizer_10.Add(sizer_11, 0, wx.EXPAND, 0)
        sizer_6.Add(sizer_10, 1, wx.ALL|wx.EXPAND, 12)
        self.SetSizer(sizer_6)
        sizer_6.Fit(self)
        self.Layout()
        # end wxGlade

    def _on_list_classes_deselect(self, event): # wxGlade: DlgClassesWx.<event_handler>
        print "Event handler `_on_list_classes_deselect' not implemented!"
        event.Skip()

    def _on_list_classes_selected(self, event): # wxGlade: DlgClassesWx.<event_handler>
        print "Event handler `_on_list_classes_selected' not implemented!"
        event.Skip()

    def _on_list_classes_activate(self, event): # wxGlade: DlgClassesWx.<event_handler>
        print "Event handler `_on_list_classes_activate' not implemented!"
        event.Skip()

    def _on_btn_new(self, event): # wxGlade: DlgClassesWx.<event_handler>
        print "Event handler `_on_btn_new' not implemented!"
        event.Skip()

    def _on_btn_edit(self, event): # wxGlade: DlgClassesWx.<event_handler>
        print "Event handler `_on_btn_edit' not implemented!"
        event.Skip()

    def _on_btn_delete(self, event): # wxGlade: DlgClassesWx.<event_handler>
        print "Event handler `_on_btn_delete' not implemented!"
        event.Skip()

# end of class DlgClassesWx



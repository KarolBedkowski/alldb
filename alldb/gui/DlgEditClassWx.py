# -*- coding: utf-8 -*-
# generated by wxGlade 0.6.3 on Sun Jan  3 15:16:06 2010

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode

# end wxGlade

class DlgEditClassWx(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: DlgEditClassWx.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_2 = wx.StaticText(self, -1, _("Name:"))
        self.tc_name = wx.TextCtrl(self, -1, "")
        self.cb_show_title = wx.CheckBox(self, -1, _("Show title"))
        self.cb_title_auto = wx.CheckBox(self, -1, _("Auto"))
        self.tc_title = wx.TextCtrl(self, -1, "")
        self.label_3 = wx.StaticText(self, -1, _("Fields:"))
        self.lc_fields = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER)
        self.b_add_field = wx.Button(self, wx.ID_ADD, "")
        self.b_del_field = wx.Button(self, wx.ID_DELETE, "")
        self.button_up = wx.Button(self, wx.ID_UP, "")
        self.button_down = wx.Button(self, wx.ID_DOWN, "")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self._on_title_auto, self.cb_title_auto)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_fields_deselected, self.lc_fields)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_fields_selected, self.lc_fields)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_fields_activated, self.lc_fields)
        self.Bind(wx.EVT_BUTTON, self._on_btn_add_field, self.b_add_field)
        self.Bind(wx.EVT_BUTTON, self._on_btn_del_field, self.b_del_field)
        self.Bind(wx.EVT_BUTTON, self._on_button_up, self.button_up)
        self.Bind(wx.EVT_BUTTON, self._on_button_down, self.button_down)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: DlgEditClassWx.__set_properties
        self.SetTitle(_("Class"))
        self.cb_title_auto.SetValue(1)
        self.lc_fields.SetMinSize((250, 300))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: DlgEditClassWx.__do_layout
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5.Add(self.label_2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 6)
        sizer_5.Add(self.tc_name, 1, wx.ALL, 6)
        sizer_main.Add(sizer_5, 0, wx.EXPAND, 0)
        sizer_main.Add(self.cb_show_title, 0, wx.LEFT|wx.RIGHT|wx.TOP, 6)
        sizer_7.Add(self.cb_title_auto, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_7.Add(self.tc_title, 1, wx.ALL, 6)
        sizer_main.Add(sizer_7, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 6)
        sizer_main.Add(self.label_3, 0, wx.ALL, 6)
        sizer_8.Add(self.lc_fields, 1, wx.ALL|wx.EXPAND, 6)
        sizer_9.Add(self.b_add_field, 0, wx.LEFT|wx.RIGHT, 6)
        sizer_9.Add(self.b_del_field, 0, wx.ALL, 6)
        sizer_9.Add((20, 20), 0, 0, 0)
        sizer_9.Add(self.button_up, 0, wx.ALL, 6)
        sizer_9.Add(self.button_down, 0, wx.LEFT|wx.RIGHT, 6)
        sizer_9.Add((20, 20), 1, 0, 0)
        sizer_8.Add(sizer_9, 0, wx.ALL|wx.EXPAND, 6)
        sizer_main.Add(sizer_8, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_main)
        sizer_main.Fit(self)
        self.Layout()
        self.Centre()
        # end wxGlade

    def _on_title_auto(self, event): # wxGlade: DlgEditClassWx.<event_handler>
        print "Event handler `_on_title_auto' not implemented!"
        event.Skip()

    def _on_fields_deselected(self, event): # wxGlade: DlgEditClassWx.<event_handler>
        print "Event handler `_on_fields_deselected' not implemented!"
        event.Skip()

    def _on_fields_selected(self, event): # wxGlade: DlgEditClassWx.<event_handler>
        print "Event handler `_on_fields_selected' not implemented!"
        event.Skip()

    def _on_fields_activated(self, event): # wxGlade: DlgEditClassWx.<event_handler>
        print "Event handler `_on_fields_activated' not implemented!"
        event.Skip()

    def _on_btn_add_field(self, event): # wxGlade: DlgEditClassWx.<event_handler>
        print "Event handler `_on_btn_add_field' not implemented!"
        event.Skip()

    def _on_btn_del_field(self, event): # wxGlade: DlgEditClassWx.<event_handler>
        print "Event handler `_on_btn_del_field' not implemented!"
        event.Skip()

    def _on_button_up(self, event): # wxGlade: DlgEditClassWx.<event_handler>
        print "Event handler `_on_button_up' not implemented!"
        event.Skip()

    def _on_button_down(self, event): # wxGlade: DlgEditClassWx.<event_handler>
        print "Event handler `_on_button_down' not implemented!"
        event.Skip()

# end of class DlgEditClassWx



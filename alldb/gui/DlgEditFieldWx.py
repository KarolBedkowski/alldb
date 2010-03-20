# -*- coding: utf-8 -*-
# generated by wxGlade HG on Sat Mar 20 17:42:47 2010

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode

# end wxGlade

class DlgEditFieldWx(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: DlgEditFieldWx.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_4 = wx.StaticText(self, -1, _("Name:"))
        self.tc_name = wx.TextCtrl(self, -1, "")
        self.label_5 = wx.StaticText(self, -1, _("Type:"))
        self.rb_type_text = wx.RadioButton(self, -1, _("text"), style=wx.RB_GROUP)
        self.rb_type_checkbox = wx.RadioButton(self, -1, _("checkbox"))
        self.rb_type_multiline = wx.RadioButton(self, -1, _("multiline"))
        self.rb_type_date = wx.RadioButton(self, -1, _("date"))
        self.rb_type_list = wx.RadioButton(self, -1, _("list"))
        self.rb_type_choice = wx.RadioButton(self, -1, _("choice"))
        self.label_6 = wx.StaticText(self, -1, _("Default"))
        self.tc_default = wx.TextCtrl(self, -1, "")
        self.label_7 = wx.StaticText(self, -1, _("Options:"))
        self.cb_show_in_title = wx.CheckBox(self, -1, _("Show in title"))
        self.cb_show_in_list = wx.CheckBox(self, -1, _("Show column in items list"))
        self.btn_values = wx.Button(self, -1, _("Define values"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self._on_rb_type_choice, self.rb_type_choice)
        self.Bind(wx.EVT_BUTTON, self._on_btn_values, self.btn_values)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: DlgEditFieldWx.__set_properties
        self.SetTitle(_("Field"))
        self.btn_values.Enable(False)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: DlgEditFieldWx.__do_layout
        sizer_12 = wx.BoxSizer(wx.VERTICAL)
        sizer_15 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1 = wx.FlexGridSizer(3, 2, 6, 6)
        sizer_14 = wx.BoxSizer(wx.VERTICAL)
        sizer_13 = wx.GridSizer(1, 3, 6, 6)
        grid_sizer_1.Add(self.label_4, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.tc_name, 0, wx.EXPAND, 3)
        grid_sizer_1.Add(self.label_5, 0, 0, 0)
        sizer_13.Add(self.rb_type_text, 0, wx.RIGHT, 6)
        sizer_13.Add(self.rb_type_checkbox, 0, wx.RIGHT, 6)
        sizer_13.Add(self.rb_type_multiline, 0, wx.RIGHT, 6)
        sizer_13.Add(self.rb_type_date, 0, wx.RIGHT, 6)
        sizer_13.Add(self.rb_type_list, 0, 0, 0)
        sizer_13.Add(self.rb_type_choice, 0, 0, 0)
        grid_sizer_1.Add(sizer_13, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(self.label_6, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.tc_default, 0, wx.EXPAND, 3)
        grid_sizer_1.Add(self.label_7, 0, 0, 0)
        sizer_14.Add(self.cb_show_in_title, 0, 0, 0)
        sizer_14.Add(self.cb_show_in_list, 0, wx.TOP, 6)
        grid_sizer_1.Add(sizer_14, 1, wx.EXPAND, 0)
        grid_sizer_1.AddGrowableCol(1)
        sizer_12.Add(grid_sizer_1, 0, wx.ALL|wx.EXPAND, 12)
        sizer_15.Add(self.btn_values, 0, 0, 0)
        sizer_12.Add(sizer_15, 0, wx.ALL|wx.EXPAND, 6)
        self.SetSizer(sizer_12)
        sizer_12.Fit(self)
        self.Layout()
        self.Centre()
        # end wxGlade

    def _on_rb_type_choice(self, event): # wxGlade: DlgEditFieldWx.<event_handler>
        print "Event handler `_on_rb_type_choice' not implemented!"
        event.Skip()

    def _on_btn_values(self, event): # wxGlade: DlgEditFieldWx.<event_handler>
        print "Event handler `_on_btn_values' not implemented!"
        event.Skip()

# end of class DlgEditFieldWx



# -*- coding: utf-8 -*-
# generated by wxGlade 0.6.3 on Wed Dec 30 13:36:54 2009

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode

# end wxGlade

class _MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: _MainFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.window_1 = wx.SplitterWindow(self, -1, style=wx.SP_NOBORDER)
        self.window_2 = wx.SplitterWindow(self.window_1, -1, style=wx.SP_NOBORDER)
        self.panel_details_back = wx.Panel(self.window_2, -1)
        self.panel_info = wx.Panel(self.panel_details_back, -1)
        
        # Menu Bar
        self.main_frame_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(1001, _("&Exit"), "", wx.ITEM_NORMAL)
        self.main_frame_menubar.Append(wxglade_tmp_menu, _("File"))
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(1003, _("New"), "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(1004, _("Delete"), "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(1005, _("Duplicate"), "", wx.ITEM_NORMAL)
        self.main_frame_menubar.Append(wxglade_tmp_menu, _("Item"))
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(1002, _("Manage"), "", wx.ITEM_NORMAL)
        self.main_frame_menubar.Append(wxglade_tmp_menu, _("Categories"))
        self.SetMenuBar(self.main_frame_menubar)
        # Menu Bar end
        self.choice_klasa = wx.Choice(self, -1, choices=[])
        self.searchbox = wx.SearchCtrl(self, -1)
        self.label_info = wx.StaticText(self, -1, _("Items: 0"))
        self.clb_tags = wx.CheckListBox(self.window_1, -1, style=wx.NO_BORDER)
        self.list_items = wx.ListCtrl(self.window_2, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.NO_BORDER)
        self.button_new_item = wx.Button(self.panel_details_back, wx.ID_NEW, "")
        self.button_apply = wx.Button(self.panel_details_back, wx.ID_APPLY, "")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_MENU, self._on_menu_exit, id=1001)
        self.Bind(wx.EVT_MENU, self._on_menu_item_new, id=1003)
        self.Bind(wx.EVT_MENU, self._on_menu_item_delete, id=1004)
        self.Bind(wx.EVT_MENU, self._on_menu_item_duplicate, id=1005)
        self.Bind(wx.EVT_MENU, self._on_menu_categories, id=1002)
        self.Bind(wx.EVT_CHOICE, self._on_class_select, self.choice_klasa)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_item_deselect, self.list_items)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_item_select, self.list_items)
        self.Bind(wx.EVT_BUTTON, self._on_btn_new, self.button_new_item)
        self.Bind(wx.EVT_BUTTON, self._on_btn_apply, self.button_apply)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: _MainFrame.__set_properties
        self.SetTitle(_("frame_1"))
        self.SetSize((916, 612))
        self.choice_klasa.SetMinSize((200, -1))
        self.label_info.SetMinSize((100, -1))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: _MainFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_panel_info = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(self.choice_klasa, 0, wx.ALL, 6)
        sizer_4.Add(self.searchbox, 1, wx.ALL, 6)
        sizer_4.Add(self.label_info, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_1.Add(sizer_4, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 0)
        self.panel_info.SetSizer(sizer_panel_info)
        sizer_2.Add(self.panel_info, 1, wx.ALL|wx.EXPAND, 6)
        sizer_3.Add(self.button_new_item, 0, 0, 0)
        sizer_3.Add((20, 20), 1, 0, 0)
        sizer_3.Add(self.button_apply, 0, wx.ALL, 3)
        sizer_2.Add(sizer_3, 0, wx.ALL|wx.EXPAND, 6)
        self.panel_details_back.SetSizer(sizer_2)
        self.window_2.SplitHorizontally(self.list_items, self.panel_details_back)
        self.window_1.SplitVertically(self.clb_tags, self.window_2, 108)
        sizer_1.Add(self.window_1, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 6)
        self.SetSizer(sizer_1)
        self.Layout()
        self.Centre()
        # end wxGlade

    def _on_menu_exit(self, event): # wxGlade: _MainFrame.<event_handler>
        print "Event handler `_on_menu_exit' not implemented!"
        event.Skip()

    def _on_menu_item_new(self, event): # wxGlade: _MainFrame.<event_handler>
        print "Event handler `_on_menu_item_new' not implemented!"
        event.Skip()

    def _on_menu_item_delete(self, event): # wxGlade: _MainFrame.<event_handler>
        print "Event handler `_on_menu_item_delete' not implemented!"
        event.Skip()

    def _on_menu_item_duplicate(self, event): # wxGlade: _MainFrame.<event_handler>
        print "Event handler `_on_menu_item_duplicate' not implemented!"
        event.Skip()

    def _on_menu_categories(self, event): # wxGlade: _MainFrame.<event_handler>
        print "Event handler `_on_menu_categories' not implemented!"
        event.Skip()

    def _on_class_select(self, event): # wxGlade: _MainFrame.<event_handler>
        print "Event handler `_on_class_select' not implemented!"
        event.Skip()

    def _on_item_deselect(self, event): # wxGlade: _MainFrame.<event_handler>
        print "Event handler `_on_item_deselect' not implemented!"
        event.Skip()

    def _on_item_select(self, event): # wxGlade: _MainFrame.<event_handler>
        print "Event handler `_on_item_select' not implemented!"
        event.Skip()

    def _on_btn_new(self, event): # wxGlade: _MainFrame.<event_handler>
        print "Event handler `_on_btn_new' not implemented!"
        event.Skip()

    def _on_btn_apply(self, event): # wxGlade: _MainFrame.<event_handler>
        print "Event handler `_on_btn_apply' not implemented!"
        event.Skip()

# end of class _MainFrame



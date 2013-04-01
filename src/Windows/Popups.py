from gi.repository import Gtk, Gdk, GObject #@UnresolvedImport
import Globals#@UnresolvedImport

class ErrorPopupWindow(Gtk.Dialog):
    def __init__(self,title,label):
        SettingsLabel = Gtk.Label(label)
        Gtk.Dialog.__init__(self,title,
                                 None,
                                 Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                 (Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        self.connect("response",self.Destroy_Widget)
        self.vbox.pack_start(SettingsLabel,True,True,0)
    def Destroy_Widget(self,widget1,widget2):
        widget1.destroy()
        
class ConfirmationDialog(Gtk.Dialog):
    def __init__(self,title,label):
        SettingsLabel = Gtk.Label(label)
        Gtk.Dialog.__init__(self,title,
                                 None,
                                 Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                 (Gtk.STOCK_NO, Gtk.ResponseType.CANCEL,
                                  Gtk.STOCK_YES, Gtk.ResponseType.ACCEPT))
        self.vbox.pack_start(SettingsLabel,True,True,0)

class ButtonEvent(object):
    '''
    "Pad" is the gamepad number 
    "Button" says whether it's a button, axis, or hat, 1 is button, 0 is axis, 2 is hat
    "Num" is the button or pad number
    '''
    def __init__(self,Pad,Button,Num, Value):
        self.Pad = Pad
        self.Button = Button
        self.Num = Num
        self.Value = Value

class ControlDialog(Gtk.Dialog):
    __gtype_name__ = 'ControlDialog'
    __gsignals__ = {
                'joypad-action-event' : ( GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,) ), #@UndefinedVariable
                }
    def __init__(self, ControlXML):
        label = "Set mapping for {0} {1}".format(ControlXML.tag,ControlXML.get("name"))
        SettingsLabel = Gtk.Label(label)
        
        buttons = []
        if ControlXML.tag == "Button":
            if ControlXML.get("type") == "analog":
                "Stuff will happen here when I get analog working"
            elif ControlXML.get("type") == "digital":
                buttons = ["Mouse Button 1", Gtk.ResponseType.ACCEPT, "Mouse Button 2", Gtk.ResponseType.ACCEPT]
        buttons = tuple(buttons)
        Gtk.Dialog.__init__(self,"Set control...",
                                 None,
                                 Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                 buttons)
        self.vbox.pack_start(SettingsLabel,True,True,0)
        GObject.timeout_add(16,self.on_idle)
        
    def on_idle(self):
            if Globals.JoystickStates:
                for i, joystick in enumerate(Globals.JoystickStates):
                    for j, button in enumerate(joystick["Buttons"]):
                        if button != 0:
                            event = ButtonEvent(i,1,j,button)
                            self.emit("joypad-action-event",event)
                            return False
                    for j, hat in enumerate(joystick["Hats"]):
                        if hat != (0,0):
                            if hat[0] == -1:
                                value = 2
                            elif hat[0] == 1:
                                value = 3
                            elif hat[1] == -1:
                                value = 1
                            elif hat[1] == 1:
                                value = 0
                            event = ButtonEvent(i,2,j,value)
                            self.emit("joypad-action-event",event)
                            return False
                    for j, axis in enumerate(joystick["Axes"]):
                        if axis != 0:
                            event = ButtonEvent(i,0,j,axis)
                            self.emit("joypad-action-event",event)
                            return False
            return True

        
'''class ErrorPopupWindow(Gtk.Window):
    def __init__(self,title,label):
        SettingsLabel = Gtk.Label(label)
   '''     
        
'''class CoreChooserPopupWindow(Gtk.Dialog):
    def __init__(self):
        HBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        SettingsLabel = Gtk.Label("Choose Core:")
        ListStore = Gtk.ListStore([str])
        for i in Globals.Systems:
            ListStore.append(i)
        ComboBox = Gtk.ComboBox.new_with_model_and_entry(ListStore)
        print dir(ComboBox)
        HBox.pack_start(SettingsLabel,True,True,0)
        HBox.pack_start(ComboBox,True,True,0)
        Gtk.Dialog.__init__(self,"Choose Core",
                                 None,
                                 Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                 (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        self.connect("response",self.Destroy_Widget)
        self.vbox.pack_start(HBox,False,True,0)
    def Destroy_Widget(self,widget1,widget2):
        widget1.destroy()'''
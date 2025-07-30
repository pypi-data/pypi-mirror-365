#!/home/twinkle/venv/bin/python

######################################################################
# LIBS

import sdgp.gtk.dialog
from sdgp.gtk.dialog import dialog

######################################################################
# VARS

MessageType = {
     'GTK_MESSAGE_INFO': 0,
  'GTK_MESSAGE_WARNING': 1,
 'GTK_MESSAGE_QUESTION': 2,
    'GTK_MESSAGE_ERROR': 3,
    'GTK_MESSAGE_OTHER': 4,
}

ButtonType = {
      'GTK_BUTTONS_NONE': 0,
        'GTK_BUTTONS_OK': 1,
     'GTK_BUTTONS_CLOSE': 2,
    'GTK_BUTTONS_CANCEL': 3,
    'GTK_BUTTONS_YES_NO': 4,
 'GTK_BUTTONS_OK_CANCEL': 5,
}

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["dialog", "MessageType", "ButtonType"]

""" __DATA__

__END__ """

#include <gtk/gtk.h>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#ifdef WITH_DOC_STRINGS
#define PyDoc_STR(str) str
#else
#define PyDoc_STR(str) ""
#endif

#define Py_RETURN_NONE return Py_None

#define DEFAULT_TITLE "sd-get-prompt"
#define DEFAULT_LABEL "SD Created Info"
#define DEFAULT_MTEXT "Nothing Input Text."

int gdialog(int GTK_MESSAGE_TYPE, int GTK_BUTTON_TYPE, const char *GTK_LABEL_TEXT, const char *msg){

    GtkClipboard *clip;
       GtkWidget *iDlg;
             int  rslt; 

    iDlg = gtk_message_dialog_new(
        NULL,
        GTK_DIALOG_MODAL,
        GTK_MESSAGE_TYPE,
        GTK_BUTTON_TYPE,
        "%s",
        GTK_LABEL_TEXT
    );

    gtk_window_set_skip_taskbar_hint(GTK_WINDOW(iDlg), 0);
    gtk_window_set_position(GTK_WINDOW(iDlg), GTK_WIN_POS_CENTER);
    gtk_window_set_title(GTK_WINDOW(iDlg), DEFAULT_TITLE);
    gtk_message_dialog_format_secondary_text(GTK_MESSAGE_DIALOG(iDlg), "%s", msg);

    rslt = gtk_dialog_run(GTK_DIALOG(iDlg));

    clip = gtk_clipboard_get(GDK_SELECTION_CLIPBOARD);
    gtk_clipboard_store(clip);

    gtk_widget_destroy(iDlg);

    return rslt;

}

/* gtk_message_dialog */
static PyObject *dialog(PyObject *self, PyObject *args)
{
    const char *dtext;
    const char *label;
           int  dtype = GTK_MESSAGE_INFO;
           int  btype = GTK_BUTTONS_OK;
           int  dretv = 0;

    if (!PyArg_ParseTuple(args, "ssii", &dtext, &label, &dtype, &btype)) {
        return NULL; // 引数解析エラー
    }
    // LABEL
    if(dtext == NULL){
        dtext = DEFAULT_MTEXT;
    }
    // LABEL
    if(label == NULL){
        label = DEFAULT_LABEL;
    }

    //printf("%s\n%s\n%d\n%d\n", dtext, label, dtype, btype);

    dretv = gdialog(dtype, btype, label, dtext);

    return Py_BuildValue("i", dretv);

}

// モジュール内のメソッド定義
static PyMethodDef dialog_methods[] = {
    {"dialog", dialog, METH_VARARGS,
     "A simply GTK dialog."},
    {NULL, NULL, 0, NULL} // メソッドリストの終端
};

// モジュール定義
static struct PyModuleDef dialog_module = {
    PyModuleDef_HEAD_INIT,
    "dialog",
    "A simply GTK dialog.", 
    -1, // モジュール状態のサイズ (-1 はサブインタープリタごとに状態を持たないことを示す)
    dialog_methods // メソッドリスト
};

// モジュール初期化関数 (Pythonがインポート時に呼び出す)
PyMODINIT_FUNC PyInit_dialog(void)
{

    PyObject* pModule = PyModule_Create(&dialog_module);
    if (pModule == NULL) {
        return NULL;
    }

    // Gtk初期化
    gtk_init(0, NULL);

    // 変数定義例
    // PyObject* は各変数ごとに新しい名前を使い、適切なフォーマット文字列を使用します。
    // PyModule_AddObject に渡すオブジェクトは、PyModule_AddObject が所有権を奪うため、
    // ここで Py_INCREF/Py_DECREF を行う必要はありません。
    // ただし、PyModule_AddObject が失敗した場合に備えて、オブジェクトを解放する処理が必要です。

    //PyObject_SetAttrString(pModule, "my_variable_str", pValue)

    //int c_true_value = 1; // Cのint型
    //PyObject* py_bool_true = PyBool_FromLong(c_true_value);
    // これで py_bool_true は Python の True オブジェクトになります
    int c_false_value = 0;
    PyObject* py_bool_false = PyBool_FromLong(c_false_value);
    // これで py_bool_false は Python の False オブジェクトになります

    if (PyModule_AddObject(pModule, "GTK_MARKUP", py_bool_false) < 0) {
        Py_DECREF(py_bool_false); // 失敗したらオブジェクトを解放
        Py_DECREF(pModule);
        return NULL;
    }
    // py_bool の参照はPyModule_AddObjectが奪ったため、ここではPy_DECREFは不要

    /* Icon */
    PyObject* pGtkMessageInfo = Py_BuildValue("i", 0);
    if (pGtkMessageInfo == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_MESSAGE_INFO", pGtkMessageInfo) < 0) { Py_DECREF(pGtkMessageInfo); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkMessageWarning = Py_BuildValue("i", 1);
    if (pGtkMessageWarning == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_MESSAGE_WARNING", pGtkMessageWarning) < 0) { Py_DECREF(pGtkMessageWarning); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkMessageQuestion = Py_BuildValue("i", 2);
    if (pGtkMessageQuestion == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_MESSAGE_QUESTION", pGtkMessageQuestion) < 0) { Py_DECREF(pGtkMessageQuestion); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkMessageError = Py_BuildValue("i", 3);
    if (pGtkMessageError == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_MESSAGE_ERROR", pGtkMessageError) < 0) { Py_DECREF(pGtkMessageError); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkMessageOther = Py_BuildValue("i", 4);
    if (pGtkMessageOther == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_MESSAGE_OTHER", pGtkMessageOther) < 0) { Py_DECREF(pGtkMessageOther); Py_DECREF(pModule); return NULL; }

    /* Button */
    PyObject* pGtkButtonsNone = Py_BuildValue("i", 0);
    if (pGtkButtonsNone == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_BUTTONS_NONE", pGtkButtonsNone) < 0) { Py_DECREF(pGtkButtonsNone); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkButtonsOk = Py_BuildValue("i", 1);
    if (pGtkButtonsOk == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_BUTTONS_OK", pGtkButtonsOk) < 0) { Py_DECREF(pGtkButtonsOk); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkButtonsClose = Py_BuildValue("i", 2);
    if (pGtkButtonsClose == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_BUTTONS_CLOSE", pGtkButtonsClose) < 0) { Py_DECREF(pGtkButtonsClose); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkButtonsCancel = Py_BuildValue("i", 3);
    if (pGtkButtonsCancel == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_BUTTONS_CANCEL", pGtkButtonsCancel) < 0) { Py_DECREF(pGtkButtonsCancel); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkButtonsYesNo = Py_BuildValue("i", 4);
    if (pGtkButtonsYesNo == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_BUTTONS_YES_NO", pGtkButtonsYesNo) < 0) { Py_DECREF(pGtkButtonsYesNo); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkButtonsOkCancel = Py_BuildValue("i", 5);
    if (pGtkButtonsOkCancel == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_BUTTONS_OK_CANCEL", pGtkButtonsOkCancel) < 0) { Py_DECREF(pGtkButtonsOkCancel); Py_DECREF(pModule); return NULL; }

    PyObject* pString = Py_BuildValue("s", "Hello from C!");
    if (pString == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "test_string", pString) < 0) {
        Py_DECREF(pString); // 失敗したらオブジェクトを解放
        Py_DECREF(pModule);
        return NULL;
    }

    return pModule; // 正しく作成したモジュールを返す

}

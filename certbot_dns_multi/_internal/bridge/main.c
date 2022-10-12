#include <Python.h>

PyObject *lego_bridge_cmd(PyObject *);

int PyArg_ParseTuple_U(PyObject *args, PyObject **obj)
{
    return PyArg_ParseTuple(args, "U", obj);
}

static struct PyMethodDef methods[] = {
    {"cmd", (PyCFunction)lego_bridge_cmd, METH_VARARGS},
    {NULL, NULL}};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "lego_bridge",
    NULL,
    -1,
    methods};

PyMODINIT_FUNC PyInit_lego_bridge(void)
{
    return PyModule_Create(&module);
}

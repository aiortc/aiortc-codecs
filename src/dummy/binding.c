#include <stdio.h>
#include <Python.h>

#include <opus/opus.h>

#include <vpx/vpx_decoder.h>
#include <vpx/vp8dx.h>


#define MODULE_NAME "dummy.binding"

static PyObject*
test(PyObject *args)
{
    OpusDecoder *opus_decoder;
    int opus_error;
    vpx_codec_ctx_t vpx_decoder;
    vpx_codec_err_t vpx_error;

    // check opus
    opus_decoder = opus_decoder_create(48000, 2, &opus_error);
    if (opus_error != OPUS_OK) {
        PyErr_SetString(PyExc_RuntimeError, "opus_decoder_create failed");
        return NULL;
    }
    opus_decoder_destroy(opus_decoder);

    // check vpx
    vpx_error = vpx_codec_dec_init(&vpx_decoder, vpx_codec_vp8_dx(), NULL, 0);
    if (vpx_error != VPX_CODEC_OK) {
        PyErr_SetString(PyExc_RuntimeError, "vpx_codec_dec_init failed");
        return NULL;
    }
    vpx_codec_destroy(&vpx_decoder);

    fprintf(stderr, "Codecs are OK\n");

    Py_RETURN_NONE;
}

static PyMethodDef module_methods[] = {
    {"test", (PyCFunction)test, METH_NOARGS, ""},
    {NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    MODULE_NAME,                        /* m_name */
    "Dummy bindings for opus and vpx.", /* m_doc */
    -1,                                 /* m_size */
    module_methods,                     /* m_methods */
    NULL,                               /* m_reload */
    NULL,                               /* m_traverse */
    NULL,                               /* m_clear */
    NULL,                               /* m_free */
};

PyMODINIT_FUNC
PyInit_binding(void)
{
    PyObject* m;

    m = PyModule_Create(&moduledef);
    if (m == NULL)
        return NULL;

    return m;
}

#include <Python.h>
#include <openssl/rsa.h>
#include <openssl/bn.h>
#include <openssl/err.h>
#include <stdint.h>


RSA* g_RSA;
char gotkey;

static PyObject* setkeys(PyObject* self, PyObject* args) {
        if(gotkey)
                Py_RETURN_NONE;

        const char* n;
        const char* e;
        const char* d;
        const char* p;
        const char* q;
        if (!PyArg_ParseTuple(args, "sssss", &n, &e, &d, &p, &q))
                return NULL;

        int retno;
        retno = BN_dec2bn(&g_RSA->n, n);
        if(retno)
                retno = BN_dec2bn(&g_RSA->e, e);
        if(retno)
                retno = BN_dec2bn(&g_RSA->d, d);
        if(retno)
                retno = BN_dec2bn(&g_RSA->p, p);
        if(retno)
                retno = BN_dec2bn(&g_RSA->q, q);

        ERR_load_crypto_strings();

        if(retno && RSA_check_key(g_RSA)) {
        } else {
                printf(ERR_error_string(ERR_get_error(), NULL));
                printf("\n");          
        }
 
        gotkey = 1;
        Py_RETURN_NONE;
}

static PyObject* decryptRSA(PyObject* self, PyObject* args) {
        const unsigned char* stream;
        int length;

        if (!PyArg_ParseTuple(args, "s#", &stream, &length))
                return NULL;

        length = RSA_private_decrypt(128, (unsigned char*)stream, (unsigned char*)stream, g_RSA, RSA_NO_PADDING);

        if(ERR_get_error()) {
                printf(ERR_error_string(ERR_get_error(), NULL));
                printf("\n");
                return PyBytes_FromStringAndSize(NULL, 0);
        }
        return PyBytes_FromStringAndSize((char*)stream, length);
}

static PyObject* encryptXTEA(PyObject* self, PyObject* args) {
        PyObject* streamObj;
        char* stream;
        uint32_t k[4];
        int pos = 0;
        Py_ssize_t length = 0;
        uint8_t i;

        if (!PyArg_ParseTuple(args, "O(kkkk)", &streamObj, &k[0], &k[1], &k[2], &k[3]))
                return NULL;

        PyString_AsStringAndSize(streamObj, &stream, &length);
        uint8_t pad = 8 - (length % 8);
        char* mbuffer = PyMem_New(char, (length + pad));

        memcpy(mbuffer, stream, length);
       
        if ((length % 8)) {
                memset((void*)&mbuffer[length], 0x33, pad);
                length += pad;
        }

        uint32_t* buffer = (uint32_t*)mbuffer;
        while(pos < length / 4) {
                uint32_t v0=buffer[pos], v1=buffer[pos + 1], sum=0, delta=0x9E3779B9;
                for (i=0; i < 32; i++) {
                        v0 += (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + k[sum & 3]);
                        sum += delta;
                        v1 += (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum + k[(sum>>11) & 3]);
                }
                buffer[pos]=v0; buffer[pos + 1]=v1;
                pos += 2;
        }
        PyObject* res = PyBytes_FromStringAndSize((char*)mbuffer, length);
        PyMem_Del(mbuffer);
        return res;
}
 
static PyObject* decryptXTEA(PyObject* self, PyObject* args) {
        PyObject* streamObj;
	char* stream;
        uint32_t k[4];
	Py_ssize_t length = 0;
	int i, pos = 0;

        if (!PyArg_ParseTuple(args, "O(kkkk)", &streamObj, &k[0], &k[1], &k[2], &k[3]))
                return NULL;
	PyString_AsStringAndSize(streamObj, &stream, &length);

        uint32_t* buffer = (uint32_t*)stream;

        while(pos < (length / 4)) {
                uint32_t v0=buffer[pos], v1=buffer[pos + 1], delta=0x9E3779B9, sum=delta * 32;
                for (i=0; i < 32; i++) {
                        v1 -= (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum + k[(sum>>11) & 3]);
                        sum -= delta;
                        v0 -= (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + k[sum & 3]);
                }
                buffer[pos]=v0; buffer[pos + 1]=v1;
                pos += 2;
        }

        return PyBytes_FromStringAndSize((char*)buffer, length);
}


static PyMethodDef otcryptoMethods[] = {
        {"setkeys", setkeys, METH_VARARGS, "Initialize OpenSSL"},
        {"decryptRSA", decryptRSA, METH_VARARGS, "Decrypts the string"},
        {"decryptXTEA", decryptXTEA, METH_VARARGS, "Decrypts the string"},
        {"encryptXTEA", encryptXTEA, METH_VARARGS, "Encrypts the string"},
        {NULL, NULL, 0, NULL}
};

/** Used by Python3
static struct PyModuleDef otrsamodule = {
        PyObject_HEAD_INIT(NULL),
        "otrsa",  --  name of module
        NULL, -- module documentation, may be NULL
        -1, --   size of per-interpreter state of the module, or -1 if the module keeps state in global variables.
        otrsaMethods
};
*/

/*PyMODINIT_FUNC
PyInit_otrsa(void)*/
PyMODINIT_FUNC initotcrypto(void) {
        gotkey = 0;
        g_RSA = RSA_new();
        (void)Py_InitModule("otcrypto", otcryptoMethods);
}


/*
 *  ----------------------------------
 * |         libmem - by rdbo         |
 * |      Memory Hacking Library      |
 *  ----------------------------------
 */

/*
 * Copyright (C) 2023    Rdbo
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License version 3
 * as published by the Free Software Foundation.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include <libmem/libmem.h>

#include <Python.h>
#include <structmember.h>

#include "types.h"

/* make sure that 'pymod' and 'global' are declared before using DECL_GLOBAL_* */
#define DECL_GLOBAL_LONG(var) { \
	global = (PyObject *)PyLong_FromLong((long)var); \
	PyObject_SetAttrString(pymod, #var, global); \
	Py_DECREF(global); \
}

#define DECL_GLOBAL_PROT(var) { \
	global = PyObject_CallFunction((PyObject *)&py_lm_prot_t, "i", var); \
	PyObject_SetAttrString(pymod, #var, global); \
	Py_DECREF(global); \
}

#define DECL_GLOBAL_ARCH(var) { \
	global = PyObject_CallFunction((PyObject *)&py_lm_arch_t, "i", var); \
	PyObject_SetAttrString(pymod, #var, global); \
	Py_DECREF(global); \
}

static lm_bool_t
_py_LM_EnumProcessesCallback(lm_process_t *pproc,
			     lm_void_t    *arg)
{
	PyObject *pylist = (PyObject *)arg;
	py_lm_process_obj *pyproc;

	pyproc = (py_lm_process_obj *)PyObject_CallObject((PyObject *)&py_lm_process_t, NULL);
	pyproc->proc = *pproc;
	pyproc->arch = (py_lm_arch_obj *)PyObject_CallFunction((PyObject *)&py_lm_arch_t, "i", pyproc->proc.arch);

	PyList_Append(pylist, (PyObject *)pyproc);

	return LM_TRUE;
}

static PyObject *
py_LM_EnumProcesses(PyObject *self,
		    PyObject *args)
{
	PyObject *pylist = PyList_New(0);
	if (!pylist)
		return NULL;

	if (!LM_EnumProcesses(_py_LM_EnumProcessesCallback, (lm_void_t *)pylist)) {
		Py_DECREF(pylist); /* destroy list */
		pylist = Py_BuildValue("");
	}

	return pylist;
}

/****************************************/

static PyObject *
py_LM_GetProcess(PyObject *self,
		 PyObject *args)
{
	lm_process_t proc;
	py_lm_process_obj *pyproc;

	if (!LM_GetProcess(&proc))
		return Py_BuildValue("");

	pyproc = (py_lm_process_obj *)PyObject_CallObject((PyObject *)&py_lm_process_t, NULL);
	pyproc->proc = proc;
	pyproc->arch = (py_lm_arch_obj *)PyObject_CallFunction((PyObject *)&py_lm_arch_t, "i", pyproc->proc.arch);

	return (PyObject *)pyproc;
}

/****************************************/

static PyObject *
py_LM_GetProcessEx(PyObject *self,
		   PyObject *args)
{
	lm_pid_t pid;
	lm_process_t proc;
	py_lm_process_obj *pyproc;

	if (!PyArg_ParseTuple(args, "i", &pid))
		return NULL;

	if (!LM_GetProcessEx(pid, &proc))
		return Py_BuildValue("");

	pyproc = (py_lm_process_obj *)PyObject_CallObject((PyObject *)&py_lm_process_t, NULL);
	pyproc->proc = proc;
	pyproc->arch = (py_lm_arch_obj *)PyObject_CallFunction((PyObject *)&py_lm_arch_t, "i", pyproc->proc.arch);

	return (PyObject *)pyproc;
}

/****************************************/

static PyObject *
py_LM_GetCommandLine(PyObject *self,
		     PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_char_t **cmdline;
	lm_char_t **ptr;
	PyObject *pylist;
	PyObject *pystr;

	if (!PyArg_ParseTuple(args, "O", &pyproc))
		return NULL;

	cmdline = LM_GetCommandLine(&pyproc->proc);
	if (!cmdline)
		return Py_BuildValue("");

	pylist = PyList_New(0);
	if (!pylist)
		goto FREE_EXIT;

	for (ptr = cmdline; *ptr != NULL; ptr = &ptr[1]) {
		pystr = PyUnicode_FromString(*ptr);
		PyList_Append(pylist, (PyObject *)pystr);
	}
FREE_EXIT:
	LM_FreeCommandLine(cmdline);

	return pylist;
}

/****************************************/

static PyObject *
py_LM_FindProcess(PyObject *self,
		  PyObject *args)
{
	lm_char_t         *procstr;
	lm_process_t       proc;
	py_lm_process_obj *pyproc;

	if (!PyArg_ParseTuple(args, "s", &procstr))
		return NULL;

	if (!LM_FindProcess(procstr, &proc))
		return Py_BuildValue("");

	pyproc = (py_lm_process_obj *)PyObject_CallObject((PyObject *)&py_lm_process_t, NULL);
	pyproc->proc = proc;
	pyproc->arch = (py_lm_arch_obj *)PyObject_CallFunction((PyObject *)&py_lm_arch_t, "i", pyproc->proc.arch);

	return (PyObject *)pyproc;
}

/****************************************/

static PyObject *
py_LM_IsProcessAlive(PyObject *self,
		     PyObject *args)
{
	py_lm_process_obj *pyproc;

	if (!PyArg_ParseTuple(args, "O", &pyproc))
		return NULL;

	if (LM_IsProcessAlive(&pyproc->proc))
		Py_RETURN_TRUE;

	Py_RETURN_FALSE;
}

/****************************************/

static PyObject *
py_LM_GetBits(PyObject *self,
		    PyObject *args)
{
	return PyLong_FromSize_t(LM_GetBits());
}

/****************************************/

static PyObject *
py_LM_GetSystemBits(PyObject *self,
		    PyObject *args)
{
	return PyLong_FromSize_t(LM_GetSystemBits());
}

/****************************************/

static lm_bool_t
_py_LM_EnumThreadsCallback(lm_thread_t *pthr,
			   lm_void_t   *arg)
{
	PyObject *pylist = (PyObject *)arg;
	py_lm_thread_obj *pythread;

	pythread = (py_lm_thread_obj *)PyObject_CallObject((PyObject *)&py_lm_thread_t, NULL);
	pythread->thread = *pthr;

	PyList_Append(pylist, (PyObject *)pythread);

	return LM_TRUE;
}

static PyObject *
py_LM_EnumThreads(PyObject *self,
		  PyObject *args)
{
	PyObject *pylist = PyList_New(0);
	if (!pylist)
		return NULL;

	if (!LM_EnumThreads(_py_LM_EnumThreadsCallback, (lm_void_t *)pylist)) {
		Py_DECREF(pylist); /* destroy list */
		pylist = Py_BuildValue("");
	}

	return pylist;
}

/****************************************/

static PyObject *
py_LM_EnumThreadsEx(PyObject *self,
		    PyObject *args)
{
	py_lm_process_obj *pyproc;
	PyObject *pylist;

	if (!PyArg_ParseTuple(args, "O", &pyproc))
		return NULL;

	pylist = PyList_New(0);
	if (!pylist)
		return NULL;

	if (!LM_EnumThreadsEx(&pyproc->proc, _py_LM_EnumThreadsCallback, (lm_void_t *)pylist)) {
		Py_DECREF(pylist); /* destroy list */
		pylist = Py_BuildValue("");
	}

	return pylist;
}

/****************************************/

static PyObject *
py_LM_GetThread(PyObject *self,
		PyObject *args)
{
	lm_thread_t thread;
	py_lm_thread_obj *pythread;

	if (!LM_GetThread(&thread))
		return Py_BuildValue("");

	pythread = (py_lm_thread_obj *)PyObject_CallObject((PyObject *)&py_lm_thread_t, NULL);
	pythread->thread = thread;

	return (PyObject *)pythread;
}

/****************************************/

static PyObject *
py_LM_GetThreadEx(PyObject *self,
		  PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_thread_t thread;
	py_lm_thread_obj *pythread;

	if (!PyArg_ParseTuple(args, "O", &pyproc))
		return NULL;

	if (!LM_GetThreadEx(&pyproc->proc, &thread))
		return Py_BuildValue("");

	pythread = (py_lm_thread_obj *)PyObject_CallObject((PyObject *)&py_lm_thread_t, NULL);
	pythread->thread = thread;

	return (PyObject *)pythread;
}

/****************************************/

static PyObject *
py_LM_GetThreadProcess(PyObject *self,
		       PyObject *args)
{
	py_lm_thread_obj *pythread;
	lm_process_t proc;
	py_lm_process_obj *pyproc;

	if (!PyArg_ParseTuple(args, "O", &pythread))
		return NULL;

	if (!LM_GetThreadProcess(&pythread->thread, &proc))
		return Py_BuildValue("");

	pyproc = (py_lm_process_obj *)PyObject_CallObject((PyObject *)&py_lm_process_t, NULL);
	pyproc->proc = proc;
	pyproc->arch = (py_lm_arch_obj *)PyObject_CallFunction((PyObject *)&py_lm_arch_t, "i", pyproc->proc.arch);

	return (PyObject *)pyproc;
}

/****************************************/

static lm_bool_t
_py_LM_EnumModulesCallback(lm_module_t *pmod,
			   lm_void_t   *arg)
{
	PyObject *pylist = (PyObject *)arg;
	py_lm_module_obj *pymodule;

	pymodule = (py_lm_module_obj *)PyObject_CallObject((PyObject *)&py_lm_module_t, NULL);
	pymodule->mod = *pmod;

	PyList_Append(pylist, (PyObject *)pymodule);

	return LM_TRUE;
}

static PyObject *
py_LM_EnumModules(PyObject *self,
		  PyObject *args)
{
	PyObject *pylist = PyList_New(0);
	if (!pylist)
		return NULL;

	if (!LM_EnumModules(_py_LM_EnumModulesCallback, (lm_void_t *)pylist)) {
		Py_DECREF(pylist); /* destroy list */
		pylist = Py_BuildValue("");
	}

	return pylist;
}

/****************************************/

static PyObject *
py_LM_EnumModulesEx(PyObject *self,
		    PyObject *args)
{
	py_lm_process_obj *pyproc;
	PyObject *pylist;

	if (!PyArg_ParseTuple(args, "O", &pyproc))
		return NULL;
       
	pylist = PyList_New(0);
	if (!pylist)
		return NULL;

	if (!LM_EnumModulesEx(&pyproc->proc, _py_LM_EnumModulesCallback, (lm_void_t *)pylist)) {
		Py_DECREF(pylist); /* destroy list */
		pylist = Py_BuildValue("");
	}

	return pylist;
}

/****************************************/

static PyObject *
py_LM_FindModule(PyObject *self,
		 PyObject *args)
{
	lm_char_t        *modstr;
	lm_module_t       mod;
	py_lm_module_obj *pymodule;

	if (!PyArg_ParseTuple(args, "s", &modstr))
		return NULL;

	if (!LM_FindModule(modstr, &mod))
		return Py_BuildValue("");

	pymodule = (py_lm_module_obj *)PyObject_CallObject((PyObject *)&py_lm_module_t, NULL);
	pymodule->mod = mod;

	return (PyObject *)pymodule;
}

/****************************************/

static PyObject *
py_LM_FindModuleEx(PyObject *self,
		   PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_char_t         *modstr;
	lm_module_t        mod;
	py_lm_module_obj  *pymodule;

	if (!PyArg_ParseTuple(args, "Os", &pyproc, &modstr))
		return NULL;

	if (!LM_FindModuleEx(&pyproc->proc, modstr, &mod))
		return Py_BuildValue("");

	pymodule = (py_lm_module_obj *)PyObject_CallObject((PyObject *)&py_lm_module_t, NULL);
	pymodule->mod = mod;

	return (PyObject *)pymodule;
}

/****************************************/

static PyObject *
py_LM_LoadModule(PyObject *self,
		 PyObject *args)
{
	lm_char_t        *modpath;
	lm_module_t       mod;
	py_lm_module_obj *pymodule;

	if (!PyArg_ParseTuple(args, "s", &modpath))
		return NULL;

	if (!LM_LoadModule(modpath, &mod))
		return Py_BuildValue("");

	pymodule = (py_lm_module_obj *)PyObject_CallObject((PyObject *)&py_lm_module_t, NULL);
	pymodule->mod = mod;

	return (PyObject *)pymodule;
}

/****************************************/

static PyObject *
py_LM_LoadModuleEx(PyObject *self,
		   PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_char_t         *modpath;
	lm_module_t        mod;
	py_lm_module_obj  *pymodule;

	if (!PyArg_ParseTuple(args, "Os", &pyproc, &modpath))
		return NULL;

	if (!LM_LoadModuleEx(&pyproc->proc, modpath, &mod))
		return Py_BuildValue("");

	pymodule = (py_lm_module_obj *)PyObject_CallObject((PyObject *)&py_lm_module_t, NULL);
	pymodule->mod = mod;

	return (PyObject *)pymodule;
}

/****************************************/

static PyObject *
py_LM_UnloadModule(PyObject *self,
		   PyObject *args)
{
	py_lm_module_obj *pymodule;

	if (!PyArg_ParseTuple(args, "O", &pymodule))
		return NULL;

	if (!LM_UnloadModule(&pymodule->mod))
		Py_RETURN_FALSE;

	Py_RETURN_TRUE;
}

/****************************************/

static PyObject *
py_LM_UnloadModuleEx(PyObject *self,
		     PyObject *args)
{
	py_lm_process_obj *pyproc;
	py_lm_module_obj *pymodule;

	if (!PyArg_ParseTuple(args, "OO", &pyproc, &pymodule))
		return NULL;

	if (!LM_UnloadModuleEx(&pyproc->proc, &pymodule->mod))
		Py_RETURN_FALSE;

	Py_RETURN_TRUE;
}

/****************************************/

static lm_bool_t
_py_LM_EnumSymbolsCallback(lm_symbol_t *psym,
			   lm_void_t   *arg)
{
	PyObject *pylist = (PyObject *)arg;
	py_lm_symbol_obj *pysym;

	pysym = (py_lm_symbol_obj *)PyObject_CallObject((PyObject *)&py_lm_symbol_t, NULL);
	pysym->symbol = *psym;
	pysym->name = PyUnicode_FromString(pysym->symbol.name);

	PyList_Append(pylist, (PyObject *)pysym);

	return LM_TRUE;
}

static PyObject *
py_LM_EnumSymbols(PyObject *self,
		  PyObject *args)
{
	py_lm_module_obj *pymodule;
	PyObject *pylist;

	if (!PyArg_ParseTuple(args, "O", &pymodule))
		return NULL;

	pylist = PyList_New(0);
	if (!pylist)
		return NULL;

	if (!LM_EnumSymbols(&pymodule->mod, _py_LM_EnumSymbolsCallback, (lm_void_t *)pylist)) {
		Py_DECREF(pylist); /* destroy list */
		pylist = Py_BuildValue("");
	}

	return pylist;
}

/****************************************/

static PyObject *
py_LM_FindSymbolAddress(PyObject *self,
			PyObject *args)
{
	py_lm_module_obj *pymodule;
	lm_char_t        *symname;
	lm_address_t      symaddr;

	if (!PyArg_ParseTuple(args, "Os", &pymodule, &symname))
		return NULL;

	symaddr = LM_FindSymbolAddress(&pymodule->mod, symname);
	if (symaddr == LM_ADDRESS_BAD)
		return Py_BuildValue("");

	return (PyObject *)PyLong_FromSize_t(symaddr);
}

/****************************************/

static PyObject *
py_LM_DemangleSymbol(PyObject *self,
		     PyObject *args)
{
	lm_char_t  *symbol;
	lm_char_t  *newsym;
	PyObject    *pynewsym;

	if (!PyArg_ParseTuple(args, "s", &symbol))
		return NULL;

	newsym = LM_DemangleSymbol(symbol, (lm_char_t *)LM_NULLPTR, 0);
	if (!newsym)
		return Py_BuildValue("");

	pynewsym = PyUnicode_FromString(newsym);

	LM_FreeDemangledSymbol(newsym);

	return pynewsym;
}

/****************************************/

static PyObject *
py_LM_EnumSymbolsDemangled(PyObject *self,
			   PyObject *args)
{
	py_lm_module_obj *pymodule;
	PyObject *pylist;

	if (!PyArg_ParseTuple(args, "O", &pymodule))
		return NULL;

	pylist = PyList_New(0);
	if (!pylist)
		return NULL;

	if (!LM_EnumSymbolsDemangled(&pymodule->mod, _py_LM_EnumSymbolsCallback, (lm_void_t *)pylist)) {
		Py_DECREF(pylist); /* destroy list */
		pylist = Py_BuildValue("");
	}

	return pylist;
}

/****************************************/

static PyObject *
py_LM_FindSymbolAddressDemangled(PyObject *self,
				 PyObject *args)
{
	py_lm_module_obj *pymodule;
	lm_char_t       *symname;
	lm_address_t      symaddr;

	if (!PyArg_ParseTuple(args, "Os", &pymodule, &symname))
		return NULL;

	symaddr = LM_FindSymbolAddressDemangled(&pymodule->mod, symname);
	if (symaddr == LM_ADDRESS_BAD)
		return Py_BuildValue("");

	return (PyObject *)PyLong_FromSize_t(symaddr);
}

/****************************************/

static lm_bool_t
_py_LM_EnumSegmentsCallback(lm_segment_t *psegment,
			    lm_void_t *arg)
{
	PyObject *pylist = (PyObject *)arg;
	py_lm_segment_obj *pysegment;

	pysegment = (py_lm_segment_obj *)PyObject_CallObject((PyObject *)&py_lm_segment_t, NULL);
	pysegment->segment = *psegment;
	pysegment->prot = (py_lm_prot_obj *)PyObject_CallFunction((PyObject *)&py_lm_prot_t, "i", pysegment->segment.prot);

	PyList_Append(pylist, (PyObject *)pysegment);

	return LM_TRUE;
}

static PyObject *
py_LM_EnumSegments(PyObject *self,
		PyObject *args)
{
	PyObject *pylist = PyList_New(0);
	if (!pylist)
		return NULL;

	if (!LM_EnumSegments(_py_LM_EnumSegmentsCallback, (lm_void_t *)pylist)) {
		Py_DECREF(pylist); /* destroy list */
		pylist = Py_BuildValue("");
	}

	return pylist;
}

/****************************************/

static PyObject *
py_LM_EnumSegmentsEx(PyObject *self,
		  PyObject *args)
{
	py_lm_process_obj *pyproc;
	PyObject *pylist;

	if (!PyArg_ParseTuple(args, "O", &pyproc))
		return NULL;
	
	pylist = PyList_New(0);
	if (!pylist)
		return NULL;

	if (!LM_EnumSegmentsEx(&pyproc->proc, _py_LM_EnumSegmentsCallback, (lm_void_t *)pylist)) {
		Py_DECREF(pylist); /* destroy list */
		pylist = Py_BuildValue("");
	}

	return pylist;
}

/****************************************/

static PyObject *
py_LM_FindSegment(PyObject *self,
		  PyObject *args)
{
	lm_address_t address;
	lm_segment_t segment;
	py_lm_segment_obj *pysegment;

	if (!PyArg_ParseTuple(args, "n", &address))
		return NULL;

	if (!LM_FindSegment(address, &segment))
		return Py_BuildValue("");

	pysegment = (py_lm_segment_obj *)PyObject_CallObject((PyObject *)&py_lm_segment_t, NULL);
	pysegment->segment = segment;
	pysegment->prot = (py_lm_prot_obj *)PyObject_CallFunction((PyObject *)&py_lm_prot_t, "i", pysegment->segment.prot);

	return (PyObject *)pysegment;
}

/****************************************/

static PyObject *
py_LM_FindSegmentEx(PyObject *self,
		PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_address_t address;
	lm_segment_t segment;
	py_lm_segment_obj *pysegment;

	if (!PyArg_ParseTuple(args, "On", &pyproc, &address))
		return NULL;

	if (!LM_FindSegmentEx(&pyproc->proc, address, &segment))
		return Py_BuildValue("");

	pysegment = (py_lm_segment_obj *)PyObject_CallObject((PyObject *)&py_lm_segment_t, NULL);
	pysegment->segment = segment;
	pysegment->prot = (py_lm_prot_obj *)PyObject_CallFunction((PyObject *)&py_lm_prot_t, "i", pysegment->segment.prot);

	return (PyObject *)pysegment;
}

/****************************************/

static PyObject *
py_LM_ReadMemory(PyObject *self,
		 PyObject *args)
{
	lm_address_t src;
	lm_size_t size;
	lm_byte_t *dst;
	PyObject *pybuf;

	if (!PyArg_ParseTuple(args, "nn", &src, &size))
		return NULL;

	dst = malloc(size);
	if (!dst)
		return Py_BuildValue("");

	if (LM_ReadMemory(src, dst, size) == size) {
		pybuf = PyByteArray_FromStringAndSize((const char *)dst, size);
	} else {
		pybuf = Py_BuildValue("");
	}

	free(dst);

	return pybuf;
}

/****************************************/

static PyObject *
py_LM_ReadMemoryEx(PyObject *self,
		   PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_address_t src;
	lm_size_t size;
	lm_byte_t *dst;
	PyObject *pybuf;

	if (!PyArg_ParseTuple(args, "Onn", &pyproc, &src, &size))
		return NULL;

	dst = malloc(size);
	if (!dst)
		return Py_BuildValue("");

	if (LM_ReadMemoryEx(&pyproc->proc, src, dst, size) == size) {
		pybuf = PyByteArray_FromStringAndSize((const char *)dst, size);
	} else {
		pybuf = Py_BuildValue("");
	}

	free(dst);

	return pybuf;
}

/****************************************/

static PyObject *
py_LM_WriteMemory(PyObject *self,
		  PyObject *args)
{
	lm_address_t dst;
	PyObject *pysrc;
	lm_bytearray_t src;
	lm_size_t size;

	if (!PyArg_ParseTuple(args, "nY", &dst, &pysrc))
		return NULL;

	src = (lm_bytearray_t)PyByteArray_AsString(pysrc);
	size = (lm_size_t)PyByteArray_Size(pysrc);

	if (LM_WriteMemory(dst, src, size) != size)
		Py_RETURN_FALSE;

	Py_RETURN_TRUE;
}

/****************************************/

static PyObject *
py_LM_WriteMemoryEx(PyObject *self,
		    PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_address_t dst;
	PyObject *pysrc;
	lm_bytearray_t src;
	lm_size_t size;

	if (!PyArg_ParseTuple(args, "OnY", &pyproc, &dst, &pysrc))
		return NULL;

	src = (lm_bytearray_t)PyByteArray_AsString(pysrc);
	size = (lm_size_t)PyByteArray_Size(pysrc);

	if (LM_WriteMemoryEx(&pyproc->proc, dst, src, size) != size)
		Py_RETURN_FALSE;

	Py_RETURN_TRUE;
}

/****************************************/

static PyObject *
py_LM_SetMemory(PyObject *self,
		PyObject *args)
{
	lm_address_t dst;
	lm_byte_t byte;
	lm_size_t size;

	if (!PyArg_ParseTuple(args, "ncn", &dst, &byte, &size))
		return NULL;

	if (LM_SetMemory(dst, byte, size) != size)
		Py_RETURN_FALSE;

	Py_RETURN_TRUE;
}

/****************************************/

static PyObject *
py_LM_SetMemoryEx(PyObject *self,
		  PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_address_t dst;
	lm_byte_t byte;
	lm_size_t size;

	if (!PyArg_ParseTuple(args, "ncn", &pyproc, &dst, &byte, &size))
		return NULL;

	if (LM_SetMemoryEx(&pyproc->proc, dst, byte, size) != size)
		Py_RETURN_FALSE;

	Py_RETURN_TRUE;
}

/****************************************/

static PyObject *
py_LM_ProtMemory(PyObject *self,
		 PyObject *args)
{
	lm_address_t addr;
	lm_size_t size;
	py_lm_prot_obj *pyprot;
	lm_prot_t oldprot;
	py_lm_prot_obj *pyoldprot;

	if (!PyArg_ParseTuple(args, "nnO", &addr, &size, &pyprot))
		return NULL;

	if (!LM_ProtMemory(addr, size, pyprot->prot, &oldprot))
		return Py_BuildValue("");

	pyoldprot = (py_lm_prot_obj *)PyObject_CallFunction((PyObject *)&py_lm_prot_t, "i", oldprot);

	return (PyObject *)pyoldprot;
}

/****************************************/

static PyObject *
py_LM_ProtMemoryEx(PyObject *self,
		   PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_address_t addr;
	lm_size_t size;
	py_lm_prot_obj *pyprot;
	lm_prot_t oldprot;
	py_lm_prot_obj *pyoldprot;

	if (!PyArg_ParseTuple(args, "OnnO", &pyproc, &addr, &size, &pyprot))
		return NULL;

	if (!LM_ProtMemoryEx(&pyproc->proc, addr, size, pyprot->prot, &oldprot))
		return Py_BuildValue("");

	pyoldprot = (py_lm_prot_obj *)PyObject_CallFunction((PyObject *)&py_lm_prot_t, "i", oldprot);

	return (PyObject *)pyoldprot;
}

/****************************************/

static PyObject *
py_LM_AllocMemory(PyObject *self,
		  PyObject *args)
{
	lm_size_t size;
	py_lm_prot_obj *pyprot;
	lm_address_t alloc;

	if (!PyArg_ParseTuple(args, "nO", &size, &pyprot))
		return NULL;


	alloc = LM_AllocMemory(size, pyprot->prot);
	if (alloc == LM_ADDRESS_BAD)
		return Py_BuildValue("");

	return PyLong_FromSize_t(alloc);
}

/****************************************/

static PyObject *
py_LM_AllocMemoryEx(PyObject *self,
		    PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_size_t size;
	py_lm_prot_obj *pyprot;
	lm_address_t alloc;

	if (!PyArg_ParseTuple(args, "OnO", &pyproc, &size, &pyprot))
		return NULL;


	alloc = LM_AllocMemoryEx(&pyproc->proc, size, pyprot->prot);
	if (alloc == LM_ADDRESS_BAD)
		return Py_BuildValue("");

	return PyLong_FromSize_t(alloc);
}

/****************************************/

static PyObject *
py_LM_FreeMemory(PyObject *self,
		 PyObject *args)
{
	lm_address_t alloc;
	lm_size_t size;

	if (!PyArg_ParseTuple(args, "nn", &alloc, &size))
		return NULL;


	if (!LM_FreeMemory(alloc, size))
		Py_RETURN_FALSE;

	Py_RETURN_TRUE;
}

/****************************************/

static PyObject *
py_LM_FreeMemoryEx(PyObject *self,
		   PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_address_t alloc;
	lm_size_t size;

	if (!PyArg_ParseTuple(args, "Onn", &pyproc, &alloc, &size))
		return NULL;


	if (!LM_FreeMemoryEx(&pyproc->proc, alloc, size))
		Py_RETURN_FALSE;

	Py_RETURN_TRUE;
}

/****************************************/

static PyObject *
py_LM_DeepPointer(PyObject *self,
		  PyObject *args)
{
	lm_address_t  base;
	PyObject     *pyoffsets;
	lm_address_t *offsets;
	lm_size_t     noffsets;
	lm_address_t  pointer;
	lm_size_t     i;

	if (!PyArg_ParseTuple(args, "nO", &base, &pyoffsets))
		return NULL;

	noffsets = PyList_Size(pyoffsets);
	if (noffsets == 0)
		return PyLong_FromSize_t(base);

	offsets = calloc(sizeof(lm_address_t), noffsets);
	if (!offsets)
		return NULL;

	for (i = 0; i < noffsets; ++i) {
		offsets[i] = (lm_address_t)PyLong_AsSize_t(PyList_GetItem(pyoffsets, i));
	}

	pointer = LM_DeepPointer(base, offsets, noffsets);

	free(offsets);

	if (pointer == LM_ADDRESS_BAD)
		return Py_BuildValue("");

	return PyLong_FromSize_t(pointer);
}

/****************************************/

static PyObject *
py_LM_DeepPointerEx(PyObject *self,
		    PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_address_t  base;
	PyObject     *pyoffsets;
	lm_address_t *offsets;
	lm_size_t     noffsets;
	lm_address_t  pointer;
	lm_size_t     i;

	if (!PyArg_ParseTuple(args, "OnO", &pyproc, &base, &pyoffsets))
		return NULL;

	noffsets = PyList_Size(pyoffsets);
	if (noffsets == 0)
		return PyLong_FromSize_t(base);

	offsets = calloc(sizeof(lm_address_t), noffsets);
	if (!offsets)
		return NULL;

	for (i = 0; i < noffsets; ++i) {
		offsets[i] = (lm_address_t)PyLong_AsSize_t(PyList_GetItem(pyoffsets, i));
	}

	pointer = LM_DeepPointerEx(&pyproc->proc, base, offsets, noffsets);

	free(offsets);

	if (pointer == LM_ADDRESS_BAD)
		return Py_BuildValue("");

	return PyLong_FromSize_t(pointer);
}

/****************************************/

static PyObject *
py_LM_DataScan(PyObject *self,
	       PyObject *args)
{
	PyObject *pydata;
	lm_address_t addr;
	lm_size_t scansize;
	lm_bytearray_t data;
	lm_size_t size;
	lm_address_t scan_match;

	if (!PyArg_ParseTuple(args, "Ynn", &pydata, &addr, &scansize))
		return NULL;

	data = (lm_bytearray_t)PyByteArray_AsString(pydata);
	size = (lm_size_t)PyByteArray_Size(pydata);

	scan_match = LM_DataScan(data, size, addr, scansize);
	if (scan_match == LM_ADDRESS_BAD)
		return Py_BuildValue("");

	return PyLong_FromSize_t(scan_match);
}

/****************************************/

static PyObject *
py_LM_DataScanEx(PyObject *self,
		 PyObject *args)
{
	py_lm_process_obj *pyproc;
	PyObject *pydata;
	lm_address_t addr;
	lm_size_t scansize;
	lm_bytearray_t data;
	lm_size_t size;
	lm_address_t scan_match;

	if (!PyArg_ParseTuple(args, "OYnn", &pyproc, &pydata, &addr, &scansize))
		return NULL;

	data = (lm_bytearray_t)PyByteArray_AsString(pydata);
	size = (lm_size_t)PyByteArray_Size(pydata);

	scan_match = LM_DataScanEx(&pyproc->proc, data, size, addr, scansize);
	if (scan_match == LM_ADDRESS_BAD)
		return Py_BuildValue("");

	return PyLong_FromSize_t(scan_match);
}

/****************************************/

static PyObject *
py_LM_PatternScan(PyObject *self,
		  PyObject *args)
{
	PyObject *pypattern;
	lm_char_t *mask;
	lm_address_t addr;
	lm_size_t scansize;
	lm_bytearray_t pattern;
	lm_address_t scan_match;

	if (!PyArg_ParseTuple(args, "Ysnn", &pypattern, &mask, &addr, &scansize))
		return NULL;

	pattern = (lm_bytearray_t)PyByteArray_AsString(pypattern);

	scan_match = LM_PatternScan(pattern, mask, addr, scansize);
	if (scan_match == LM_ADDRESS_BAD)
		return Py_BuildValue("");

	return PyLong_FromSize_t(scan_match);
}

/****************************************/

static PyObject *
py_LM_PatternScanEx(PyObject *self,
		    PyObject *args)
{
	py_lm_process_obj *pyproc;
	PyObject *pypattern;
	lm_char_t *mask;
	lm_address_t addr;
	lm_size_t scansize;
	lm_bytearray_t pattern;
	lm_address_t scan_match;

	if (!PyArg_ParseTuple(args, "OYsnn", &pyproc, &pypattern, &mask, &addr, &scansize))
		return NULL;

	pattern = (lm_bytearray_t)PyByteArray_AsString(pypattern);

	scan_match = LM_PatternScanEx(&pyproc->proc, pattern, mask, addr, scansize);
	if (scan_match == LM_ADDRESS_BAD)
		return Py_BuildValue("");

	return PyLong_FromSize_t(scan_match);
}

/****************************************/

static PyObject *
py_LM_SigScan(PyObject *self,
	      PyObject *args)
{
	lm_char_t *sig;
	lm_address_t addr;
	lm_size_t scansize;
	lm_address_t scan_match;

	if (!PyArg_ParseTuple(args, "snn", &sig, &addr, &scansize))
		return NULL;

	scan_match = LM_SigScan(sig, addr, scansize);
	if (scan_match == LM_ADDRESS_BAD)
		return Py_BuildValue("");

	return PyLong_FromSize_t(scan_match);
}

/****************************************/

static PyObject *
py_LM_SigScanEx(PyObject *self,
		PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_char_t *sig;
	lm_address_t addr;
	lm_size_t scansize;
	lm_address_t scan_match;

	if (!PyArg_ParseTuple(args, "Osnn", &pyproc, &sig, &addr, &scansize))
		return NULL;

	scan_match = LM_SigScanEx(&pyproc->proc, sig, addr, scansize);
	if (scan_match == LM_ADDRESS_BAD)
		return Py_BuildValue("");

	return PyLong_FromSize_t(scan_match);
}

/****************************************/

static PyObject *
py_LM_GetArchitecture(PyObject *self,
		      PyObject *args)
{
	return PyObject_CallFunction((PyObject *)&py_lm_arch_t, "i", LM_GetArchitecture());
}

/****************************************/

static PyObject *
py_LM_Assemble(PyObject *self,
	       PyObject *args)
{
	lm_string_t code;
	lm_inst_t inst;
	py_lm_inst_obj *pyinst;

	if (!PyArg_ParseTuple(args, "s", &code))
		return NULL;

	if (!LM_Assemble(code, &inst))
		return Py_BuildValue("");

	pyinst = (py_lm_inst_obj *)PyObject_CallObject((PyObject *)&py_lm_inst_t, NULL);
	pyinst->inst = inst;

	return (PyObject *)pyinst;
}

/****************************************/

static PyObject *
py_LM_AssembleEx(PyObject *self,
		 PyObject *args)
{
	lm_string_t code;
	py_lm_arch_obj *pyarch;
	lm_address_t runtime_addr;
	lm_byte_t *codebuf;
	lm_size_t codelen;
	PyObject *pycodebuf;

	if (!PyArg_ParseTuple(args, "sOn", &code, &pyarch, &runtime_addr))
		return NULL;

	codelen = LM_AssembleEx(code, pyarch->arch, runtime_addr, &codebuf);
	if (!codelen)
		return Py_BuildValue("");

	pycodebuf = PyByteArray_FromStringAndSize((const char *)codebuf, codelen);

	LM_FreePayload(codebuf);

	return pycodebuf;
}

/****************************************/

static PyObject *
py_LM_Disassemble(PyObject *self,
		  PyObject *args)
{
	lm_address_t code;
	lm_inst_t inst;
	py_lm_inst_obj *pyinst;

	if (!PyArg_ParseTuple(args, "n", &code))
		return NULL;

	if (!LM_Disassemble(code, &inst))
		return Py_BuildValue("");

	pyinst = (py_lm_inst_obj *)PyObject_CallObject((PyObject *)&py_lm_inst_t, NULL);
	pyinst->inst = inst;

	return (PyObject *)pyinst;
}

/****************************************/

static PyObject *
py_LM_DisassembleEx(PyObject *self,
		    PyObject *args)
{
	lm_address_t code;
	py_lm_arch_obj *pyarch;
	lm_size_t size;
	lm_size_t count;
	lm_address_t runtime_addr;
	lm_inst_t *insts;
	lm_size_t inst_count;
	PyObject *pyinsts;
	lm_size_t i;
	py_lm_inst_obj *pyinst;

	if (!PyArg_ParseTuple(args, "nOnnn", &code, &pyarch, &size, &count, &runtime_addr))
		return NULL;

	inst_count = LM_DisassembleEx(code, pyarch->arch, size, count, runtime_addr, &insts);
	if (!inst_count)
		return Py_BuildValue("");

	pyinsts = PyList_New((Py_ssize_t)inst_count);
	for (i = 0; i < inst_count; ++i) {
		pyinst = (py_lm_inst_obj *)PyObject_CallObject((PyObject *)&py_lm_inst_t, NULL);
		pyinst->inst = insts[i];
		PyList_SetItem(pyinsts, i, (PyObject *)pyinst);
	}

	LM_FreeInstructions(insts);

	return pyinsts;
}

/****************************************/

static PyObject *
py_LM_CodeLength(PyObject *self,
		 PyObject *args)
{
	lm_address_t code;
	lm_size_t minlength;
	lm_size_t aligned_length;

	if (!PyArg_ParseTuple(args, "nn", &code, &minlength))
		return NULL;

	aligned_length = LM_CodeLength(code, minlength);
	if (!aligned_length)
		return Py_BuildValue("");

	return (PyObject *)PyLong_FromSize_t(aligned_length);
}

/****************************************/

static PyObject *
py_LM_CodeLengthEx(PyObject *self,
		   PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_address_t code;
	lm_size_t minlength;
	lm_size_t aligned_length;

	if (!PyArg_ParseTuple(args, "Onn", &pyproc, &code, &minlength))
		return NULL;

	aligned_length = LM_CodeLengthEx(&pyproc->proc, code, minlength);
	if (!aligned_length)
		return Py_BuildValue("");

	return (PyObject *)PyLong_FromSize_t(aligned_length);
}

/****************************************/

static PyObject *
py_LM_HookCode(PyObject *self,
	       PyObject *args)
{
	lm_address_t from;
	lm_address_t to;
	lm_address_t trampoline;
	lm_size_t    size;

	if (!PyArg_ParseTuple(args, "nn", &from, &to))
		return NULL;

	size = LM_HookCode(from, to, &trampoline);
	if (!size)
		return Py_BuildValue("");

	return Py_BuildValue("(nn)", trampoline, size);
}

/****************************************/

static PyObject *
py_LM_HookCodeEx(PyObject *self,
		 PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_address_t from;
	lm_address_t to;
	lm_address_t trampoline;
	lm_size_t    size;

	if (!PyArg_ParseTuple(args, "Onn", &pyproc, &from, &to))
		return NULL;

	size = LM_HookCodeEx(&pyproc->proc, from, to, &trampoline);
	if (!size)
		return Py_BuildValue("");

	return Py_BuildValue("(nn)", trampoline, size);
}

/****************************************/

static PyObject *
py_LM_UnhookCode(PyObject *self,
		 PyObject *args)
{
	lm_address_t from;
	lm_address_t trampoline;
	lm_size_t    size;

	if (!PyArg_ParseTuple(args, "n(nn)", &from, &trampoline, &size))
		return NULL;

	if (!LM_UnhookCode(from, trampoline, size))
		Py_RETURN_FALSE;

	Py_RETURN_TRUE;
}

/****************************************/

static PyObject *
py_LM_UnhookCodeEx(PyObject *self,
		   PyObject *args)
{
	py_lm_process_obj *pyproc;
	lm_address_t from;
	lm_address_t trampoline;
	lm_size_t    size;

	if (!PyArg_ParseTuple(args, "On(nn)", &pyproc, &from, &trampoline, &size))
		return NULL;

	if (!LM_UnhookCodeEx(&pyproc->proc, from, trampoline, size))
		Py_RETURN_FALSE;

	Py_RETURN_TRUE;
}

/****************************************/

static PyMethodDef libmem_methods[] = {
	{ "LM_EnumProcesses", py_LM_EnumProcesses, METH_NOARGS, "Lists all current living processes" },
	{ "LM_GetProcess", py_LM_GetProcess, METH_NOARGS, "Gets information about the calling process" },
	{ "LM_GetProcessEx", py_LM_GetProcessEx, METH_VARARGS, "Gets information about a process from a process ID" },
	{ "LM_GetCommandLine", py_LM_GetCommandLine, METH_VARARGS, "Retrieves the command line arguments of a process" },
	{ "LM_FindProcess", py_LM_FindProcess, METH_VARARGS, "Searches for an existing process" },
	{ "LM_IsProcessAlive", py_LM_IsProcessAlive, METH_VARARGS, "Checks if a process is alive" },
	{ "LM_GetBits", py_LM_GetBits, METH_VARARGS, "Checks if a process is alive" },
	{ "LM_GetSystemBits", py_LM_GetSystemBits, METH_VARARGS, "Checks if a process is alive" },
	/****************************************/
	{ "LM_EnumThreads", py_LM_EnumThreads, METH_NOARGS, "Lists all threads from the calling process" },
	{ "LM_EnumThreadsEx", py_LM_EnumThreadsEx, METH_VARARGS, "Lists all threads from the calling process" },
	{ "LM_GetThread", py_LM_GetThread, METH_NOARGS, "Get information about the calling thread" },
	{ "LM_GetThreadEx", py_LM_GetThreadEx, METH_VARARGS, "Get information about a remote thread" },
	{ "LM_GetThreadProcess", py_LM_GetThreadProcess, METH_VARARGS, "Gets information about a process from a thread" },
	/****************************************/
	{ "LM_EnumModules", py_LM_EnumModules, METH_NOARGS, "Lists all modules from the calling process" },
	{ "LM_EnumModulesEx", py_LM_EnumModulesEx, METH_VARARGS, "Lists all modules from a remote process" },
	{ "LM_FindModule", py_LM_FindModule, METH_VARARGS, "Searches for a module in the current process" },
	{ "LM_FindModuleEx", py_LM_FindModuleEx, METH_VARARGS, "Searches for a module in a remote process" },
	{ "LM_LoadModule", py_LM_LoadModule, METH_VARARGS, "Loads a module into the current process" },
	{ "LM_LoadModuleEx", py_LM_LoadModuleEx, METH_VARARGS, "Loads a module into a remote process" },
	{ "LM_UnloadModule", py_LM_UnloadModule, METH_VARARGS, "Unloads a module from the current process" },
	{ "LM_UnloadModuleEx", py_LM_UnloadModuleEx, METH_VARARGS, "Unloads a module from a remote process" },
	/****************************************/
	{ "LM_EnumSymbols", py_LM_EnumSymbols, METH_VARARGS, "Lists all symbols from a module" },
	{ "LM_FindSymbolAddress", py_LM_FindSymbolAddress, METH_VARARGS, "Searches for a symbol in a module" },
	{ "LM_DemangleSymbol", py_LM_DemangleSymbol, METH_VARARGS, "Demangles a mangled symbol from a module" },
	{ "LM_EnumSymbolsDemangled", py_LM_EnumSymbolsDemangled, METH_VARARGS, "Lists all demangled symbols from a module" },
	{ "LM_FindSymbolAddressDemangled", py_LM_FindSymbolAddressDemangled, METH_VARARGS, "Searches for a demangled symbol in a module" },
	/****************************************/
	{ "LM_EnumSegments", py_LM_EnumSegments, METH_NOARGS, "Lists all segments from the calling process" },
	{ "LM_EnumSegmentsEx", py_LM_EnumSegmentsEx, METH_VARARGS, "Lists all segments from a remote process" },
	{ "LM_FindSegment", py_LM_FindSegment, METH_VARARGS, "Get information about the segment of an address in the current process" },
	{ "LM_FindSegmentEx", py_LM_FindSegmentEx, METH_VARARGS, "Get information about the segment of an address in a remote process" },
	/****************************************/
	{ "LM_ReadMemory", py_LM_ReadMemory, METH_VARARGS, "Read memory from the calling process" },
	{ "LM_ReadMemoryEx", py_LM_ReadMemoryEx, METH_VARARGS, "Read memory from a remote process" },
	{ "LM_WriteMemory", py_LM_WriteMemory, METH_VARARGS, "Write memory to the calling process" },
	{ "LM_WriteMemoryEx", py_LM_WriteMemoryEx, METH_VARARGS, "Write memory to a remote process" },
	{ "LM_SetMemory", py_LM_SetMemory, METH_VARARGS, "Set memory to a byte in the current process" },
	{ "LM_SetMemoryEx", py_LM_SetMemoryEx, METH_VARARGS, "Set memory to a byte in a remote process" },
	{ "LM_ProtMemory", py_LM_ProtMemory, METH_VARARGS, "Change memory protection flags of a region in the current process" },
	{ "LM_ProtMemoryEx", py_LM_ProtMemoryEx, METH_VARARGS, "Change memory protection flags of a region in a remote process" },
	{ "LM_AllocMemory", py_LM_AllocMemory, METH_VARARGS, "Allocate memory in the current process" },
	{ "LM_AllocMemoryEx", py_LM_AllocMemoryEx, METH_VARARGS, "Allocate memory in a remote process" },
	{ "LM_FreeMemory", py_LM_FreeMemory, METH_VARARGS, "Free memory in the current process" },
	{ "LM_FreeMemoryEx", py_LM_FreeMemoryEx, METH_VARARGS, "Free memory in a remote process" },
	{ "LM_DeepPointer", py_LM_DeepPointer, METH_VARARGS, "Dereference a deep pointer in the current process, usually result of a pointer map or pointer scan" },
	{ "LM_DeepPointerEx", py_LM_DeepPointerEx, METH_VARARGS, "Dereference a deep pointer in a remote process, usually result of a pointer map or pointer scan" },
	/****************************************/
	{ "LM_DataScan", py_LM_DataScan, METH_VARARGS, "Search for a byte array in the current process" },
	{ "LM_DataScanEx", py_LM_DataScanEx, METH_VARARGS, "Search for a byte array in a remote process" },
	{ "LM_PatternScan", py_LM_PatternScan, METH_VARARGS, "Search for a byte pattern with a mask filter in the current process" },
	{ "LM_PatternScanEx", py_LM_PatternScanEx, METH_VARARGS, "Search for a byte pattern with a mask filter in a remote process" },
	{ "LM_SigScan", py_LM_SigScan, METH_VARARGS, "Search for a byte signature that can contain filters in the current process" },
	{ "LM_SigScanEx", py_LM_SigScanEx, METH_VARARGS, "Search for a byte signature that can contain filters in a remote process" },
	/****************************************/
	{ "LM_HookCode", py_LM_HookCode, METH_VARARGS, "Hook/detour code in the current process, returning a gateway/trampoline" },
	{ "LM_HookCodeEx", py_LM_HookCodeEx, METH_VARARGS, "Hook/detour code in a remote process, returning a gateway/trampoline" },
	{ "LM_UnhookCode", py_LM_UnhookCode, METH_VARARGS, "Unhook/restore code in the current process" },
	{ "LM_UnhookCodeEx", py_LM_UnhookCodeEx, METH_VARARGS, "Unhook/restore code in a remote process" },
	/****************************************/
	{ "LM_GetArchitecture", py_LM_GetArchitecture, METH_VARARGS, "Gets the current processor architecture" },
	{ "LM_Assemble", py_LM_Assemble, METH_VARARGS, "Assemble instruction from text" },
	{ "LM_AssembleEx", py_LM_AssembleEx, METH_VARARGS, "Assemble instructions from text" },
	{ "LM_Disassemble", py_LM_Disassemble, METH_VARARGS, "Disassemble instruction from an address in the current process" },
	{ "LM_DisassembleEx", py_LM_DisassembleEx, METH_VARARGS, "Disassemble instructions from an address in the current process" },
	{ "LM_CodeLength", py_LM_CodeLength, METH_VARARGS, "Get the minimum instruction aligned length for a code region in the current process" },
	{ "LM_CodeLengthEx", py_LM_CodeLengthEx, METH_VARARGS, "Get the minimum instruction aligned length for a code region in a remote process" },
	{ NULL, NULL, 0, NULL }
};

static PyModuleDef libmem_mod = {
	PyModuleDef_HEAD_INIT,
	"_libmem",
	NULL,
	-1,
	libmem_methods
};

PyMODINIT_FUNC
PyInit__libmem(void)
{
	PyObject *pymod;
	PyObject *global; /* used in the DECL_GLOBAL macro */

	if (PyType_Ready(&py_lm_process_t) < 0)
		goto ERR_PYMOD;

	if (PyType_Ready(&py_lm_thread_t) < 0)
		goto ERR_PYMOD;

	if (PyType_Ready(&py_lm_module_t) < 0)
		goto ERR_PYMOD;

	if (PyType_Ready(&py_lm_symbol_t) < 0)
		goto ERR_PYMOD;

	if (PyType_Ready(&py_lm_prot_t) < 0)
		goto ERR_PYMOD;

	if (PyType_Ready(&py_lm_segment_t) < 0)
		goto ERR_PYMOD;

	if (PyType_Ready(&py_lm_inst_t) < 0)
		goto ERR_PYMOD;

	if (PyType_Ready(&py_lm_vmt_t) < 0)
		goto ERR_PYMOD;

	if (PyType_Ready(&py_lm_arch_t) < 0)
		goto ERR_PYMOD;

	pymod = PyModule_Create(&libmem_mod);
	if (!pymod)
		goto ERR_PYMOD;
	
	/* types */
	Py_INCREF(&py_lm_process_t);
	if (PyModule_AddObject(pymod, "lm_process_t",
			       (PyObject *)&py_lm_process_t) < 0)
		goto ERR_PROCESS;

	Py_INCREF(&py_lm_thread_t);
	if (PyModule_AddObject(pymod, "lm_thread_t",
			       (PyObject *)&py_lm_thread_t) < 0)
		goto ERR_THREAD;

	Py_INCREF(&py_lm_module_t);
	if (PyModule_AddObject(pymod, "lm_module_t",
			       (PyObject *)&py_lm_module_t) < 0)
		goto ERR_MODULE;

	Py_INCREF(&py_lm_symbol_t);
	if (PyModule_AddObject(pymod, "lm_symbol_t",
			       (PyObject *)&py_lm_symbol_t) < 0)
		goto ERR_SYMBOL;

	Py_INCREF(&py_lm_prot_t);
	if (PyModule_AddObject(pymod, "lm_prot_t",
			       (PyObject *)&py_lm_prot_t) < 0)
		goto ERR_PROT;

	Py_INCREF(&py_lm_segment_t);
	if (PyModule_AddObject(pymod, "lm_segment_t",
			       (PyObject *)&py_lm_segment_t) < 0)
		goto ERR_SEGMENT;

	Py_INCREF(&py_lm_inst_t);
	if (PyModule_AddObject(pymod, "lm_inst_t",
			       (PyObject *)&py_lm_inst_t) < 0)
		goto ERR_INST;

	Py_INCREF(&py_lm_vmt_t);
	if (PyModule_AddObject(pymod, "lm_vmt_t",
			       (PyObject *)&py_lm_vmt_t) < 0)
		goto ERR_VMT;

	Py_INCREF(&py_lm_arch_t);
	if (PyModule_AddObject(pymod, "lm_arch_t",
			       (PyObject *)&py_lm_arch_t) < 0)
		goto ERR_ARCH;

	/* global variables */
	DECL_GLOBAL_PROT(LM_PROT_X);
	DECL_GLOBAL_PROT(LM_PROT_R);
	DECL_GLOBAL_PROT(LM_PROT_W);
	DECL_GLOBAL_PROT(LM_PROT_XR);
	DECL_GLOBAL_PROT(LM_PROT_XW);
	DECL_GLOBAL_PROT(LM_PROT_RW);
	DECL_GLOBAL_PROT(LM_PROT_XRW);

	DECL_GLOBAL_ARCH(LM_ARCH_GENERIC);

	DECL_GLOBAL_ARCH(LM_ARCH_ARMV7);
	DECL_GLOBAL_ARCH(LM_ARCH_ARMV8);
	DECL_GLOBAL_ARCH(LM_ARCH_THUMBV7);
	DECL_GLOBAL_ARCH(LM_ARCH_THUMBV8);

	DECL_GLOBAL_ARCH(LM_ARCH_ARMV7EB);
	DECL_GLOBAL_ARCH(LM_ARCH_THUMBV7EB);
	DECL_GLOBAL_ARCH(LM_ARCH_ARMV8EB);
	DECL_GLOBAL_ARCH(LM_ARCH_THUMBV8EB);

	DECL_GLOBAL_ARCH(LM_ARCH_AARCH64);

	DECL_GLOBAL_ARCH(LM_ARCH_MIPS);
	DECL_GLOBAL_ARCH(LM_ARCH_MIPS64);
	DECL_GLOBAL_ARCH(LM_ARCH_MIPSEL);
	DECL_GLOBAL_ARCH(LM_ARCH_MIPSEL64);

	DECL_GLOBAL_ARCH(LM_ARCH_X86_16);
	DECL_GLOBAL_ARCH(LM_ARCH_X86);
	DECL_GLOBAL_ARCH(LM_ARCH_X64);

	DECL_GLOBAL_ARCH(LM_ARCH_PPC32);
	DECL_GLOBAL_ARCH(LM_ARCH_PPC64);
	DECL_GLOBAL_ARCH(LM_ARCH_PPC64LE);

	DECL_GLOBAL_ARCH(LM_ARCH_SPARC);
	DECL_GLOBAL_ARCH(LM_ARCH_SPARC64);
	DECL_GLOBAL_ARCH(LM_ARCH_SPARCEL);

	DECL_GLOBAL_ARCH(LM_ARCH_SYSZ);

	DECL_GLOBAL_ARCH(LM_ARCH_MAX);

	goto EXIT; /* no errors */

ERR_ARCH:
	Py_DECREF(&py_lm_arch_t);
	Py_DECREF(pymod);
ERR_VMT:
	Py_DECREF(&py_lm_vmt_t);
	Py_DECREF(pymod);
ERR_INST:
	Py_DECREF(&py_lm_inst_t);
	Py_DECREF(pymod);
ERR_PROT:
	Py_DECREF(&py_lm_prot_t);
	Py_DECREF(pymod);
ERR_SEGMENT:
	Py_DECREF(&py_lm_segment_t);
	Py_DECREF(pymod);
ERR_SYMBOL:
	Py_DECREF(&py_lm_symbol_t);
	Py_DECREF(pymod);
ERR_MODULE:
	Py_DECREF(&py_lm_module_t);
	Py_DECREF(pymod);
ERR_THREAD:
	Py_DECREF(&py_lm_thread_t);
	Py_DECREF(pymod);
ERR_PROCESS:
	Py_DECREF(&py_lm_process_t);
	Py_DECREF(pymod);
ERR_PYMOD:
	pymod = (PyObject *)NULL;
EXIT:
	return pymod;
}


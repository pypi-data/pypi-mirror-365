/*
 * Copyright (c) 2020-2025 Qianqian Fang <q.fang at neu.edu>. All rights reserved.
 * Copyright (c) 2016-2019 Iotic Labs Ltd. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://github.com/NeuroJSON/pybj/blob/master/LICENSE
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#pragma once

#define NO_IMPORT_ARRAY
#define PY_ARRAY_UNIQUE_SYMBOL bjdata_numpy_array
#define NPY_NO_DEPRECATED_API 0
#include <numpy/arrayobject.h>

#if defined (__cplusplus)
extern "C" {
#endif

// NumPy 2.0 compatibility layer
#if NPY_API_VERSION >= 0x0000000f

// Type constants
#ifndef PyArray_FLOAT
#define PyArray_FLOAT NPY_FLOAT32
#endif
#ifndef PyArray_DOUBLE
#define PyArray_DOUBLE NPY_FLOAT64
#endif
#ifndef PyArray_LONG
#define PyArray_LONG NPY_LONG
#endif
#ifndef PyArray_BOOL
#define PyArray_BOOL NPY_BOOL
#endif
#ifndef PyArray_HALF
#define PyArray_HALF NPY_HALF
#endif
#ifndef PyArray_BYTE
#define PyArray_BYTE NPY_BYTE
#endif
#ifndef PyArray_UBYTE
#define PyArray_UBYTE NPY_UBYTE
#endif
#ifndef PyArray_SHORT
#define PyArray_SHORT NPY_SHORT
#endif
#ifndef PyArray_USHORT
#define PyArray_USHORT NPY_USHORT
#endif
#ifndef PyArray_INT
#define PyArray_INT NPY_INT
#endif
#ifndef PyArray_UINT
#define PyArray_UINT NPY_UINT
#endif
#ifndef PyArray_LONGLONG
#define PyArray_LONGLONG NPY_LONGLONG
#endif
#ifndef PyArray_ULONGLONG
#define PyArray_ULONGLONG NPY_ULONGLONG
#endif
#ifndef PyArray_STRING
#define PyArray_STRING NPY_STRING
#endif
#ifndef PyArray_USERDEF
#define PyArray_USERDEF NPY_USERDEF
#endif

#endif

#if defined (__cplusplus)
}
#endif


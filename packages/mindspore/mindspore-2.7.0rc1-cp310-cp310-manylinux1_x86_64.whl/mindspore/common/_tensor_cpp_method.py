# Copyright 2024 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Add tensor cpp methods for stub tensor"""

tensor_cpp_methods = ['baddbmm', 'isneginf', 'log1p', 'fmod', 'acos', 'arccos', 'mm', 'repeat_interleave', 'nansum', 'floor_divide', 'new_empty', 'frac', 'minimum', 'where', 'type_as', 'fill_', 'add', '__add__', 'tan', 'cosh', 'bitwise_not', 'cos', 'expm1', 'repeat', 'fill_diagonal_', 'erf', 'floor', 'gather', 'sum', 'sub_', '__isub__', 'log', 'remainder', 'cumsum', 'clamp', 'clip', '_to', 'exp', 'reciprocal', 'bitwise_xor', '__xor__', 'reshape', 'asin', 'arcsin', 'any', 'logsumexp', 'gcd', 'all', 'neg', 'negative', 'sigmoid', 'unsqueeze', 'topk', 'scatter', 'square', 'index_add', 'argsort', 'mean', 'new_zeros', 'addmm', '__mod__', 'clone', 'count_nonzero', 'isinf', 'roll', 'histc', 'max', 'bincount', 'tril', 'argmax', 'diag', 'lerp', 'logaddexp2', 'argmin', 'put_', 'std', 'addcdiv', 'sinh', 'outer', 'ceil', 'log_', 'sub', '__sub__', 'logaddexp', 'unique', 'copy_', 'log10', 'transpose', 'isclose', 'sqrt', 'logical_and', 'greater_equal', 'ge', 'chunk', 'hardshrink', 'inverse', 'log2', 'matmul', 'flatten', 'bitwise_or', '__or__', 'pow', '__pow__', 'tile', 'scatter_', 'div', 'divide', 'expand_as', 'tanh', 'allclose', 'round', 'narrow', 'view_as', 'atan2', 'arctan2', 'floor_divide_', '__ifloordiv__', 'median', 'logical_xor', 't', 'bitwise_and', '__and__', 'greater', 'gt', 'logical_not', 'abs', '__abs__', 'absolute', 'asinh', 'arcsinh', 'new_full', 'mul', 'masked_fill', 'index_select', 'mul_', '__imul__', 'masked_fill_', 'new_ones', 'div_', '__itruediv__', 'atan', 'arctan', 'add_', '__iadd__', 'subtract', 'select', 'unbind', 'var', 'less', 'lt', 'sinc', 'rsqrt', 'sort', 'isfinite', 'maximum', 'kthvalue', 'atanh', 'arctanh', 'true_divide', 'nan_to_num', 'masked_select', 'sin', 'erfc', 'dot', 'eq', 'split', 'trunc', 'scatter_add', 'less_equal', 'le', 'xlogy', 'addmv', 'acosh', 'arccosh', 'min', 'triu', 'take', 'logical_or', 'prod', 'addbmm', 'not_equal', 'ne', 'exp_']

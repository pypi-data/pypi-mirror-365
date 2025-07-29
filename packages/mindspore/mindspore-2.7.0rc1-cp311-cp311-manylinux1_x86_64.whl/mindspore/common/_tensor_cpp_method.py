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

tensor_cpp_methods = ['minimum', 'log', 'isneginf', 'view_as', 'erfc', 'kthvalue', 'new_zeros', 'index_add', 'true_divide', 'all', 'sub_', '__isub__', 'div_', '__itruediv__', 'bitwise_and', '__and__', 'remainder', 'addcdiv', 'less_equal', 'le', 'addmm', 'tril', 'nansum', 'masked_fill_', 'repeat', 'masked_fill', 'dot', '_to', 'chunk', 'sub', '__sub__', 'mm', 'round', 'matmul', 'log_', 'inverse', 'gather', 'argmin', 'unique', 'any', 'select', 'take', 'eq', 'logaddexp2', 'mul_', '__imul__', 'floor', 'new_empty', 'isclose', 'put_', 'greater', 'gt', 'sum', 'exp', 'isfinite', 'maximum', 'argsort', 'rsqrt', 'logical_or', 'fill_diagonal_', 'std', 'add', '__add__', 'diag', 'topk', 'outer', 'addmv', 'median', 'log1p', 'where', 'tan', 'logical_xor', 'div', 'divide', 'scatter_', 'less', 'lt', 'logaddexp', 'gcd', 'ceil', 'sort', 'exp_', 'clamp', 'clip', 'erf', 'hardshrink', 'lerp', 'addbmm', 'square', 'scatter', 'asinh', 'arcsinh', 'sinh', 'scatter_add', 'reshape', 'expand_as', 'pow', '__pow__', 'log10', 'new_ones', 'isinf', 'frac', 'new_full', 'sinc', 'asin', 'arcsin', 'masked_select', 'neg', 'negative', 'acosh', 'arccosh', 'cosh', 'floor_divide_', '__ifloordiv__', 'atanh', 'arctanh', 'mul', 'transpose', 'count_nonzero', 'atan2', 'arctan2', 'xlogy', 'acos', 'arccos', 'greater_equal', 'ge', 'mean', 'histc', 'cos', 'log2', 'unsqueeze', 'logical_not', 'tanh', 'min', 'triu', 'floor_divide', 'baddbmm', 'add_', '__iadd__', 'argmax', 'var', 'bitwise_xor', '__xor__', 'trunc', 'repeat_interleave', 'index_select', 'sqrt', 'fill_', 'bincount', 'sigmoid', 'atan', 'arctan', 'bitwise_or', '__or__', 'clone', 'not_equal', 'ne', 'prod', 'allclose', 'cumsum', 't', 'expm1', 'narrow', 'subtract', 'logsumexp', 'split', 'max', '__mod__', 'roll', 'copy_', 'nan_to_num', 'sin', 'flatten', 'reciprocal', 'tile', 'fmod', 'abs', 'absolute', '__abs__', 'unbind', 'type_as', 'bitwise_not', 'logical_and']

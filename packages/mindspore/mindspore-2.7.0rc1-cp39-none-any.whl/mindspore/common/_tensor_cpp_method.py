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

tensor_cpp_methods = ['fill_', 'sum', 'all', 'sinh', 'isclose', 'split', 'std', 'sqrt', 'any', 'view_as', 'unbind', 'count_nonzero', 'masked_select', 'minimum', 'nansum', 'sub', '__sub__', 'argsort', 'cosh', 'cumsum', 'log1p', 'exp_', 'atan2', 'arctan2', 'fmod', 'atanh', 'arctanh', 'prod', 'acos', 'arccos', 'addmm', 'new_full', 'greater', 'gt', 'ceil', 'min', 'tan', 'subtract', 'masked_fill', 'log2', 'type_as', 'nan_to_num', 'acosh', 'arccosh', 'clone', 'put_', 'isfinite', 'asinh', 'arcsinh', 'floor_divide', 'max', 'new_ones', 'inverse', 'sub_', '__isub__', 'exp', 'chunk', 'new_zeros', 'less', 'lt', 'abs', 'absolute', '__abs__', 'masked_fill_', 'sigmoid', 'mean', 'tile', 'pow', '__pow__', 'log_', 'addcdiv', 'reciprocal', 'sinc', 'logical_xor', 'fill_diagonal_', 'reshape', 'div_', '__itruediv__', 'erfc', 'outer', 'repeat_interleave', 'not_equal', 'ne', 'repeat', 'mm', 'narrow', 'bitwise_xor', '__xor__', 'median', 'gcd', 'lerp', 'div', 'divide', 'baddbmm', 'sin', 'matmul', 'hardshrink', 'scatter_', 'index_add', 'isinf', 'tril', 'gather', 'argmax', 'unique', 'logsumexp', 'flatten', 'square', 'unsqueeze', 'remainder', 'mul', 'xlogy', 'trunc', 'kthvalue', 'rsqrt', 'tanh', 't', 'less_equal', 'le', '__mod__', 'topk', 'var', '_to', 'atan', 'arctan', 'log10', 'erf', 'bitwise_or', '__or__', 'logical_or', 'mul_', '__imul__', 'floor_divide_', '__ifloordiv__', 'greater_equal', 'ge', 'dot', 'logaddexp2', 'argmin', 'add', '__add__', 'floor', 'roll', 'select', 'copy_', 'scatter_add', 'neg', 'negative', 'sort', 'eq', 'new_empty', 'expand_as', 'round', 'diag', 'addbmm', 'addmv', 'logaddexp', 'log', 'index_select', 'scatter', 'frac', 'true_divide', 'expm1', 'allclose', 'add_', '__iadd__', 'logical_and', 'clamp', 'clip', 'where', 'transpose', 'bitwise_and', '__and__', 'asin', 'arcsin', 'maximum', 'take', 'triu', 'isneginf', 'histc', 'bitwise_not', 'cos', 'logical_not', 'bincount']

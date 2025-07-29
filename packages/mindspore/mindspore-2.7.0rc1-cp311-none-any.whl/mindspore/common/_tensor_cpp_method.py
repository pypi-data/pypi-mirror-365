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

tensor_cpp_methods = ['prod', 'repeat', 'bitwise_or', '__or__', 'new_zeros', 'unbind', 'clamp', 'clip', 'neg', 'negative', 'tanh', 'sqrt', 'sin', 'logical_or', 'new_full', 'log2', 'floor', 'cumsum', 'lerp', 'argsort', 'index_select', 'diag', 'mul', 'sub_', '__isub__', 'exp_', 'roll', 'isinf', 'true_divide', 'mul_', '__imul__', 'tile', 'transpose', 'sort', 'floor_divide', 'log', 'put_', 'hardshrink', 'inverse', 't', 'max', 'histc', 'square', 'not_equal', 'ne', 'topk', 'addcdiv', 'scatter_add', 'repeat_interleave', 'any', 'atanh', 'arctanh', 'maximum', 'scatter', 'eq', 'xlogy', 'log_', 'tan', 'addbmm', 'gcd', 'greater', 'gt', 'greater_equal', 'ge', 'scatter_', 'div_', '__itruediv__', 'dot', 'std', 'cosh', 'logsumexp', 'where', 'erfc', 'isclose', '_to', 'logical_and', 'frac', 'exp', 'subtract', 'argmax', 'acosh', 'arccosh', 'add_', '__iadd__', 'rsqrt', 'isneginf', 'erf', 'cos', 'addmm', 'round', 'fill_diagonal_', 'sinh', 'isfinite', 'mm', 'var', 'bitwise_xor', '__xor__', 'remainder', 'fill_', 'index_add', 'reshape', '__mod__', 'mean', 'bitwise_and', '__and__', 'ceil', 'acos', 'arccos', 'expm1', 'sum', 'add', '__add__', 'div', 'divide', 'minimum', 'all', 'tril', 'min', 'reciprocal', 'allclose', 'log10', 'argmin', 'less', 'lt', 'masked_select', 'new_empty', 'baddbmm', 'kthvalue', 'logical_xor', 'addmv', 'abs', 'absolute', '__abs__', 'pow', '__pow__', 'atan', 'arctan', 'gather', 'clone', 'floor_divide_', '__ifloordiv__', 'asin', 'arcsin', 'atan2', 'arctan2', 'narrow', 'nan_to_num', 'new_ones', 'matmul', 'trunc', 'take', 'less_equal', 'le', 'masked_fill_', 'bitwise_not', 'triu', 'split', 'log1p', 'sigmoid', 'masked_fill', 'logaddexp2', 'flatten', 'asinh', 'arcsinh', 'unique', 'bincount', 'logaddexp', 'sinc', 'outer', 'nansum', 'fmod', 'median', 'view_as', 'logical_not', 'sub', '__sub__', 'expand_as', 'count_nonzero', 'select', 'unsqueeze', 'copy_', 'type_as', 'chunk']

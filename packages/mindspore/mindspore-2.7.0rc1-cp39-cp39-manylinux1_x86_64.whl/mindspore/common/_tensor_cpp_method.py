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

tensor_cpp_methods = ['addmv', 'trunc', 'greater', 'gt', 'logaddexp', 'atanh', 'arctanh', 'unbind', 'greater_equal', 'ge', 'masked_select', 'round', 'sigmoid', 'mm', 'scatter_add', 'tile', 'sub', '__sub__', 'chunk', 'max', 'xlogy', 'allclose', 'erf', 'sum', 'logical_xor', 'std', 'add', '__add__', '__mod__', 'mul', 'square', 'sinc', 'log2', 'tan', 'narrow', 'baddbmm', 'cosh', 'sinh', 'clamp', 'clip', 'diag', 'neg', 'negative', 'expand_as', 'split', 'isneginf', 'mul_', '__imul__', 'fmod', 'gcd', 'masked_fill_', 'addmm', 'scatter', 'sort', 'subtract', 'copy_', 'addcdiv', 'unique', 'matmul', 'frac', 'triu', 'logical_and', 'argmin', 'index_select', 'rsqrt', 'kthvalue', 'bitwise_xor', '__xor__', 'hardshrink', 'unsqueeze', 'outer', 'eq', 'ceil', 'isclose', 'logical_not', 'var', 't', 'minimum', 'lerp', 'atan2', 'arctan2', 'sqrt', 'log', 'nan_to_num', 'new_empty', 'sin', 'not_equal', 'ne', 'less_equal', 'le', '_to', 'tril', 'asin', 'arcsin', 'new_ones', 'abs', '__abs__', 'absolute', 'reshape', 'logsumexp', 'logaddexp2', 'expm1', 'floor_divide', 'isfinite', 'div_', '__itruediv__', 'exp', 'clone', 'cos', 'min', 'logical_or', 'type_as', 'argmax', 'all', 'bitwise_not', 'log10', 'prod', 'bitwise_or', '__or__', 'floor', 'maximum', 'exp_', 'repeat', 'gather', 'median', 'index_add', 'erfc', 'div', 'divide', 'pow', '__pow__', 'put_', 'log1p', 'take', 'tanh', 'mean', 'where', 'true_divide', 'select', 'repeat_interleave', 'less', 'lt', 'floor_divide_', '__ifloordiv__', 'addbmm', 'cumsum', 'add_', '__iadd__', 'isinf', 'acos', 'arccos', 'inverse', 'fill_diagonal_', 'acosh', 'arccosh', 'asinh', 'arcsinh', 'fill_', 'transpose', 'view_as', 'new_full', 'bitwise_and', '__and__', 'flatten', 'reciprocal', 'masked_fill', 'remainder', 'count_nonzero', 'argsort', 'atan', 'arctan', 'new_zeros', 'roll', 'topk', 'dot', 'histc', 'bincount', 'scatter_', 'any', 'nansum', 'sub_', '__isub__', 'log_']

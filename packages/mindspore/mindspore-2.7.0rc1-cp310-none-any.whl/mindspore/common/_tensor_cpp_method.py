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

tensor_cpp_methods = ['addbmm', 'log_', 'lerp', 'isclose', 'max', 'sum', 'isneginf', 'fill_diagonal_', 'roll', 'floor_divide', 'tile', 'cosh', 'add_', '__iadd__', 'bitwise_xor', '__xor__', 'new_zeros', 'expm1', 'view_as', 'narrow', 'abs', 'absolute', '__abs__', 'argsort', 'sub', '__sub__', 'exp_', 'greater', 'gt', 'index_add', 'tanh', 'masked_fill', 'logical_and', 'allclose', 'log10', 'less', 'lt', 'any', 'new_empty', 'put_', 'log1p', 'topk', 'prod', 'transpose', 'logical_xor', 'frac', 'repeat', 'mm', 'mean', 'isinf', 'logaddexp2', 'atan', 'arctan', 'div_', '__itruediv__', 'add', '__add__', 'all', 'fill_', 'nan_to_num', 'round', 'acosh', 'arccosh', 'std', 'inverse', 'not_equal', 'ne', 'masked_fill_', 'addmv', 'addcdiv', 'argmax', 'new_full', 'histc', 'eq', 'tan', 'logsumexp', 'minimum', 'reshape', 'var', 'new_ones', 'select', 'cumsum', 'div', 'divide', 'sinc', 'triu', 'masked_select', 'sigmoid', 'logical_or', 'cos', 'gather', 'nansum', 'copy_', 'matmul', 'floor_divide_', '__ifloordiv__', 'remainder', '_to', 'hardshrink', 'dot', 'isfinite', 'outer', 'count_nonzero', 'logaddexp', 'tril', 'split', 'unsqueeze', 'scatter_', 'type_as', 'subtract', 'neg', 'negative', 'erf', 'sub_', '__isub__', 'log', 'bincount', 'true_divide', 'min', 'sin', 'unbind', 'asin', 'arcsin', 'flatten', 'repeat_interleave', 'argmin', 'scatter_add', 'gcd', 'maximum', 'atan2', 'arctan2', 'log2', 'median', 't', 'atanh', 'arctanh', 'fmod', 'where', 'take', 'rsqrt', '__mod__', 'reciprocal', 'sort', 'chunk', 'bitwise_not', 'baddbmm', 'addmm', 'erfc', 'ceil', 'logical_not', 'mul', 'sqrt', 'clone', 'mul_', '__imul__', 'unique', 'acos', 'arccos', 'greater_equal', 'ge', 'less_equal', 'le', 'trunc', 'bitwise_or', '__or__', 'pow', '__pow__', 'sinh', 'kthvalue', 'xlogy', 'clamp', 'clip', 'asinh', 'arcsinh', 'floor', 'expand_as', 'square', 'scatter', 'index_select', 'bitwise_and', '__and__', 'exp', 'diag']

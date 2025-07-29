/**
 * Copyright 2024 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef MS_KERNELS_INTERNAL_KERNEL_TILING_UTILS_H_
#define MS_KERNELS_INTERNAL_KERNEL_TILING_UTILS_H_

#include <cstdint>
#include <functional>
#include <memory>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

#include "include/internal_op.h"

namespace mindspore {
namespace internal {
struct RuningInfo {
  internal::ShapeInfoList input_shapes;
  internal::InputsImmutableInfoList input_infos;
  internal::ShapeInfoList output_shapes;
  internal::InputsImmutableInfoList output_infos;
};

class Tunable {
 public:
  Tunable() = default;
  virtual ~Tunable() = default;
  virtual InternalOpPtr CreateOpByKey(const std::vector<int64_t> &key) = 0;
  virtual RuningInfo GetRuningInfo(const std::vector<int64_t> &key) const = 0;
};
using TunablePtr = std::shared_ptr<Tunable>;

using TunableCreator = std::function<TunablePtr()>;
class TunableBuilder {
 public:
  ~TunableBuilder() = default;
  TunableBuilder(const TunableBuilder &) = delete;
  TunableBuilder &operator=(const TunableBuilder &) = delete;
  static TunableBuilder &Instance();

  void Register(const std::string &op_name, TunableCreator &&creator);
  TunablePtr Create(const std::string &op_name) const;

 private:
  TunableBuilder() = default;
  std::unordered_map<std::string, TunableCreator> tunable_creators_;
};

class TuneRegister {
 public:
  TuneRegister(const std::string &op_name, TunableCreator creator) noexcept {
    TunableBuilder::Instance().Register(op_name, std::move(creator));
  }
  ~TuneRegister() = default;
};

#define REG_OP_TUNABLE(op_name, TargetClass)                                                                  \
  static_assert(std::is_base_of<Tunable, TargetClass>::value, #TargetClass " must be derived from Tunable!"); \
  static const TuneRegister g_##op_name##_tunable_reg(#op_name,                                               \
                                                      []() -> TunablePtr { return std::make_shared<TargetClass>(); })
}  // namespace internal
}  // namespace mindspore

#endif  // MS_KERNELS_INTERNAL_KERNEL_TILING_UTILS_H_

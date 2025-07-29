/**
 * Copyright 2023-2025 Huawei Technologies Co., Ltd
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
#ifndef MINDSPORE_CORE_OP_NAME_B_H_
#define MINDSPORE_CORE_OP_NAME_B_H_

namespace mindspore::ops {
constexpr auto kNameBatchNormStats = "BatchNormStats";
constexpr auto kNameBatchNormGatherStatsWithCounts = "BatchNormGatherStatsWithCounts";
constexpr auto kNameBatchNormElemt = "BatchNormElemt";
constexpr auto kNameBiasAdd = "BiasAdd";
constexpr auto kNameBatchNormGrad = "BatchNormGrad";
constexpr auto kNameBatchNorm = "BatchNorm";
constexpr auto kNameBitwiseNot = "BitwiseNot";
constexpr auto kNameBitwiseXorScalar = "BitwiseXorScalar";
constexpr auto kNameBernoulliExt = "BernoulliExt";
constexpr auto kNameBatchMatMul = "BatchMatMul";
constexpr auto kNameBCEWithLogitsLoss = "BCEWithLogitsLoss";
constexpr auto kNameBitwiseXorTensor = "BitwiseXorTensor";
constexpr auto kNameBatchNormGradGrad = "BatchNormGradGrad";
constexpr auto kNameBitwiseAndTensor = "BitwiseAndTensor";
constexpr auto kNameBiasAddGrad = "BiasAddGrad";
constexpr auto kNameBatchNormGradWithActivation = "BatchNormGradWithActivation";
constexpr auto kNameBetainc = "Betainc";
constexpr auto kNameBatchNormReduceGrad = "BatchNormReduceGrad";
constexpr auto kNameBaddbmm = "Baddbmm";
constexpr auto kNameBroadcastToView = "BroadcastToView";
constexpr auto kNameBatchNormWithActivation = "BatchNormWithActivation";
constexpr auto kNameBincountExt = "BincountExt";
constexpr auto kNameBatchNormWithAddAndActivation = "BatchNormWithAddAndActivation";
constexpr auto kNameBroadcastTo = "BroadcastTo";
constexpr auto kNameBatchNormExt = "BatchNormExt";
constexpr auto kNameBatchNormGradWithAddAndActivation = "BatchNormGradWithAddAndActivation";
constexpr auto kNameBatchNormElemtGrad = "BatchNormElemtGrad";
constexpr auto kNameBatchNormGradExt = "BatchNormGradExt";
constexpr auto kNameBitwiseOrTensor = "BitwiseOrTensor";
constexpr auto kNameBitwiseOrScalar = "BitwiseOrScalar";
constexpr auto kNameBitwiseAndScalar = "BitwiseAndScalar";
constexpr auto kNameBoolNot = "BoolNot";
constexpr auto kNameBatchMatMulExt = "BatchMatMulExt";
constexpr auto kNameBinaryCrossEntropyWithLogitsBackward = "BinaryCrossEntropyWithLogitsBackward";
constexpr auto kNameBinaryCrossEntropyGrad = "BinaryCrossEntropyGrad";
constexpr auto kNameBinaryCrossEntropy = "BinaryCrossEntropy";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_B_H_

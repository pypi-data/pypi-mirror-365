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
#ifndef MINDSPORE_CORE_OP_NAME_I_H_
#define MINDSPORE_CORE_OP_NAME_I_H_

namespace mindspore::ops {
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInplaceSiLU = "InplaceSiLU";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameInplaceMatmulAdd = "InplaceMatmulAdd";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameInnerMoeTokenUnpermute = "InnerMoeTokenUnpermute";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameInplaceExponential = "InplaceExponential";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_

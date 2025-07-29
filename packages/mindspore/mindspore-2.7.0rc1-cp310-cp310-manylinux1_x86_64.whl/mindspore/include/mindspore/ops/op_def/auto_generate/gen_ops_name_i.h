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
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameInplaceSiLU = "InplaceSiLU";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameInnerMoeTokenUnpermute = "InnerMoeTokenUnpermute";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameInplaceMatmulAdd = "InplaceMatmulAdd";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameInplaceExponential = "InplaceExponential";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_

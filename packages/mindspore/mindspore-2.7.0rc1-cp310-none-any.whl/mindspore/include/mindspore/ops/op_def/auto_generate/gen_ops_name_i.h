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
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameInplaceMatmulAdd = "InplaceMatmulAdd";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameInnerMoeTokenUnpermute = "InnerMoeTokenUnpermute";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInplaceSiLU = "InplaceSiLU";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameInplaceExponential = "InplaceExponential";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_

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
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameInplaceSiLU = "InplaceSiLU";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameInnerMoeTokenUnpermute = "InnerMoeTokenUnpermute";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameInplaceMatmulAdd = "InplaceMatmulAdd";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInplaceExponential = "InplaceExponential";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_

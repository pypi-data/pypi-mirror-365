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

#ifndef MINDSPORE_MINDSPORE_OPS_KERNEL_FUNCTIONS_AUTO_GENERATE_AUTO_GRAD_OP_REG_H_
#define MINDSPORE_MINDSPORE_OPS_KERNEL_FUNCTIONS_AUTO_GENERATE_AUTO_GRAD_OP_REG_H_

#include <functional>
#include <any>
#include <unordered_map>
#include "mindspore/ccsrc/pyboost/op_runner.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
enum class OpType {
  kAvgPool3DGradExt = 0,
  kMSELossGradExt = 1,
  kTake = 2,
  kMaxPoolGradWithIndices = 3,
  kDiagExt = 4,
  kRound = 5,
  kReshapeAndCache = 6,
  kAllFinite = 7,
  kLogSigmoid = 8,
  kTExt = 9,
  kIncreFlashAttention = 10,
  kDistCommBatchIsendIrecv = 11,
  kBatchNormElemtGrad = 12,
  kNonZeroExt = 13,
  kNewZeros = 14,
  kCosh = 15,
  kAvgPool2D = 16,
  kTile = 17,
  kSmoothL1LossGrad = 18,
  kArgMinExt = 19,
  kNotEqual = 20,
  kLog10 = 21,
  kOnes = 22,
  kSplit = 23,
  kLog = 24,
  kEmptyLike = 25,
  kLinSpaceExt = 26,
  kReciprocal = 27,
  kIm2ColExt = 28,
  kGridSampler2D = 29,
  kInplaceFillTensor = 30,
  kIsClose = 31,
  kReduceAll = 32,
  kZerosLikeExt = 33,
  kConvTranspose2D = 34,
  kSoftmaxBackward = 35,
  kUpsampleNearest3D = 36,
  kXlogy = 37,
  kAcoshExt = 38,
  kArange = 39,
  kErf = 40,
  kReshape = 41,
  kMeshgrid = 42,
  kGenerator = 43,
  kRepeatInterleaveInt = 44,
  kInplaceClampTensor = 45,
  kBatchNormGradExt = 46,
  kTransposeExtView = 47,
  kHardtanhGrad = 48,
  kConv1DExt = 49,
  kHSwishGrad = 50,
  kClampScalar = 51,
  kDropoutGradExt = 52,
  kGroupNorm = 53,
  kSliceExt = 54,
  kSelect = 55,
  kSoftplusExt = 56,
  kBinaryCrossEntropy = 57,
  kFloorDiv = 58,
  kMaxPoolGradWithMask = 59,
  kArgMaxWithValue = 60,
  kRandpermExt = 61,
  kHSwish = 62,
  kMv = 63,
  kReplicationPad1DGrad = 64,
  kDistCommAllToAllVSingle = 65,
  kNewOnes = 66,
  kExp2 = 67,
  kTanhGrad = 68,
  kSqueeze = 69,
  kAddmm = 70,
  kAllGatherMatmul = 71,
  kSumExt = 72,
  kNormalTensorFloat = 73,
  kEmbeddingDenseBackward = 74,
  kScatter = 75,
  kAdaptiveAvgPool2DExt = 76,
  kMultiScaleDeformableAttn = 77,
  kFlashAttentionScore = 78,
  kLessEqual = 79,
  kElu = 80,
  kFloorDivScalar = 81,
  kAdaptiveMaxPool1D = 82,
  kCos = 83,
  kUpsampleLinear1DGrad = 84,
  kContiguous = 85,
  kInplaceCopy = 86,
  kRepeat = 87,
  kFillTensor = 88,
  kMaximum = 89,
  kLerp = 90,
  kDropoutDoMaskExt = 91,
  kSpeedFusionAttention = 92,
  kConvolution = 93,
  kNormalTensorTensor = 94,
  kSwigluGrad = 95,
  kPagedAttention = 96,
  kUnstackExtView = 97,
  kInplaceScatterAdd = 98,
  kSoftShrink = 99,
  kConv2DExt = 100,
  kInnerCommIsend = 101,
  kDivMods = 102,
  kDiv = 103,
  kLogicalAnd = 104,
  kBroadcastToView = 105,
  kSliceExtView = 106,
  kInplaceGroupedMatmulAdd = 107,
  kBCEWithLogitsLoss = 108,
  kMultiScaleDeformableAttnGrad = 109,
  kGeLU = 110,
  kSigmoid = 111,
  kAddcmulExt = 112,
  kRemainderScalarTensor = 113,
  kDistCommAllToAllV = 114,
  kRmsNorm = 115,
  kInplaceUniform = 116,
  kInplaceElu = 117,
  kInplaceFloor = 118,
  kThreshold = 119,
  kSoftmax = 120,
  kMoeTokenPermuteGrad = 121,
  kSearchSorted = 122,
  kInplaceDivs = 123,
  kGatherDGradV2 = 124,
  kSplitTensor = 125,
  kEluGradExt = 126,
  kBaddbmm = 127,
  kNLLLoss = 128,
  kEmbedding = 129,
  kInplaceScatterValue = 130,
  kConv3DPadding = 131,
  kSplitTensorView = 132,
  kRandExt = 133,
  kTrunc = 134,
  kSubExt = 135,
  kInplaceThreshold = 136,
  kDistCommReduceScatter = 137,
  kNarrowView = 138,
  kBitwiseXorTensor = 139,
  kInnerCommReduceScatter = 140,
  kUniformExt = 141,
  kAddScalar = 142,
  kInnerIndex = 143,
  kIsNegInf = 144,
  kReverseV2 = 145,
  kIndexSelect = 146,
  kOnesLikeExt = 147,
  kReflectionPad3D = 148,
  kBatchMatMul = 149,
  kFmodTensor = 150,
  kAbs = 151,
  kTopkExt = 152,
  kSeluGrad = 153,
  kUpsampleBilinear2D = 154,
  kConvolutionStrGrad = 155,
  kBitwiseAndTensor = 156,
  kXLogYScalarSelf = 157,
  kMishExt = 158,
  kNLLLoss2dGrad = 159,
  kCountNonZero = 160,
  kFlashAttentionScoreGrad = 161,
  kDistCommReduceScatterTensor = 162,
  kStdMean = 163,
  kLogSoftmaxExt = 164,
  kMoeDistributeCombine = 165,
  kCummax = 166,
  kInnerCommAllReduce = 167,
  kDistCommGatherIntoTensor = 168,
  kNLLLoss2d = 169,
  kReflectionPad1D = 170,
  kMatmulReduceScatter = 171,
  kSilentCheckV2 = 172,
  kRandn = 173,
  kRoll = 174,
  kBinaryCrossEntropyWithLogitsBackward = 175,
  kDense = 176,
  kSelectV2 = 177,
  kRemainderTensorScalar = 178,
  kMaxPoolWithIndices = 179,
  kReplicationPad1D = 180,
  kDistCommBroadcast = 181,
  kMSELossExt = 182,
  kMedianDim = 183,
  kSinc = 184,
  kBernoulliExt = 185,
  kInplaceErfinv = 186,
  kMaskedSelectGrad = 187,
  kExp = 188,
  kCross = 189,
  kLogSigmoidGrad = 190,
  kZeros = 191,
  kFrac = 192,
  kReduceAny = 193,
  kMuls = 194,
  kSlice = 195,
  kInplaceScatterValueReduce = 196,
  kLogicalNot = 197,
  kDistCommAllGather = 198,
  kErfc = 199,
  kGatherD = 200,
  kInnerCommIrecv = 201,
  kExpm1 = 202,
  kSortExt = 203,
  kReflectionPad1DGrad = 204,
  kTranspose = 205,
  kAdaptiveAvgPool3DExt = 206,
  kUpsampleNearest2D = 207,
  kInplaceNormal = 208,
  kGcd = 209,
  kReplicationPad3DGrad = 210,
  kInplaceMul = 211,
  kInplaceAddsExt = 212,
  kDropoutGenMaskExt = 213,
  kBatchMatMulExt = 214,
  kUpsampleNearest1DGrad = 215,
  kEye = 216,
  kSilentCheckV3 = 217,
  kNeScalar = 218,
  kIndexFillTensor = 219,
  kInplaceZero = 220,
  kLogicalXor = 221,
  kMax = 222,
  kTan = 223,
  kPow = 224,
  kThresholdGrad = 225,
  kInplaceClampScalar = 226,
  kRotaryPositionEmbeddingGrad = 227,
  kTrilExt = 228,
  kDivs = 229,
  kUniqueConsecutive = 230,
  kMaxPoolWithMask = 231,
  kAtanh = 232,
  kInnerCommAllToAllV = 233,
  kInplaceFillScalar = 234,
  kInplaceRandom = 235,
  kLerpScalar = 236,
  kMinimum = 237,
  kFmodScalar = 238,
  kClampTensor = 239,
  kSiLU = 240,
  kPromptFlashAttention = 241,
  kExpandAs = 242,
  kCustomExt = 243,
  kLayerNormExt = 244,
  kInplaceFillDiagonal = 245,
  kOuter = 246,
  kReluGrad = 247,
  kConv3DExt = 248,
  kIndex = 249,
  kAddmv = 250,
  kOneHotExt = 251,
  kGridSampler3DGrad = 252,
  kLog1p = 253,
  kUpsampleTrilinear3D = 254,
  kInplaceDivMods = 255,
  kArgSort = 256,
  kMin = 257,
  kDot = 258,
  kInplaceFloorDivides = 259,
  kInplaceScatterSrcReduce = 260,
  kCeil = 261,
  kMatMul = 262,
  kInplaceSubExt = 263,
  kMul = 264,
  kConv1DPadding = 265,
  kFillScalar = 266,
  kKLDiv = 267,
  kPowTensorScalar = 268,
  kFloor = 269,
  kMoeDistributeDispatch = 270,
  kAddRmsNorm = 271,
  kInplaceExp = 272,
  kLogSumExp = 273,
  kSoftMarginLossGrad = 274,
  kReplicationPad2DGrad = 275,
  kInplaceLog = 276,
  kStd = 277,
  kHShrink = 278,
  kChunk = 279,
  kAddcdivExt = 280,
  kSigmoidGrad = 281,
  kAsinExt = 282,
  kRotaryPositionEmbedding = 283,
  kMishGradExt = 284,
  kIsFinite = 285,
  kNormalFloatTensor = 286,
  kCol2ImExt = 287,
  kReflectionPad2D = 288,
  kInplaceSubScalar = 289,
  kInplaceDiv = 290,
  kGluGrad = 291,
  kReduceMax = 292,
  kNanToNum = 293,
  kView = 294,
  kCopy = 295,
  kRandInt = 296,
  kBinaryCrossEntropyGrad = 297,
  kSqrt = 298,
  kEqualExt = 299,
  kIndexAddExt = 300,
  kInplaceFloorDivide = 301,
  kPolar = 302,
  kHShrinkGrad = 303,
  kRemainderTensorTensor = 304,
  kNorm = 305,
  kNeg = 306,
  kSinh = 307,
  kAvgPool3DExt = 308,
  kAdaptiveAvgPool3DGradExt = 309,
  kHistcExt = 310,
  kTensorScatterElements = 311,
  kSelectExtView = 312,
  kMultinomialExt = 313,
  kDistCommScatter = 314,
  kIsInf = 315,
  kTanh = 316,
  kUpsampleNearest2DGrad = 317,
  kBatchNormElemt = 318,
  kPowScalarTensor = 319,
  kDistCommReduce = 320,
  kBatchNormExt = 321,
  kBatchNormStats = 322,
  kReplicationPad3D = 323,
  kEluExt = 324,
  kDistCommAllGatherIntoTensor = 325,
  kExpandDimsView = 326,
  kUpsampleBicubic2D = 327,
  kAsinhExt = 328,
  kKLDivGrad = 329,
  kAdaptiveMaxPool2D = 330,
  kInplaceDivMod = 331,
  kInplaceMuls = 332,
  kSiLUGrad = 333,
  kCumsumExt = 334,
  kProdExt = 335,
  kSoftShrinkGrad = 336,
  kRepeatInterleaveGrad = 337,
  kMoeTokenPermute = 338,
  kRepeatInterleaveTensor = 339,
  kNewEmpty = 340,
  kGeluExt = 341,
  kBitwiseOrScalar = 342,
  kUpsampleBilinear2DGrad = 343,
  kCumminExt = 344,
  kDistCommAllReduce = 345,
  kInplaceSiLU = 346,
  kBatchNormGatherStatsWithCounts = 347,
  kLinalgQr = 348,
  kKthvalue = 349,
  kStackExt = 350,
  kTraceExt = 351,
  kMaxDim = 352,
  kGeluGradExt = 353,
  kPReLUGrad = 354,
  kInplaceMaskedFillTensor = 355,
  kConvolutionStr = 356,
  kSquare = 357,
  kIndexFillScalar = 358,
  kSoftplusGradExt = 359,
  kUpsampleBicubic2DGrad = 360,
  kLayerNormGradExt = 361,
  kGeLUGrad = 362,
  kMoeTokenUnpermuteGrad = 363,
  kAdaptiveAvgPool1D = 364,
  kBincountExt = 365,
  kApplyRotaryPosEmb = 366,
  kMm = 367,
  kTriangularSolve = 368,
  kUpsampleTrilinear3DGrad = 369,
  kBroadcastTo = 370,
  kTransposeView = 371,
  kLeakyReLUGradExt = 372,
  kNLLLossGrad = 373,
  kViewAs = 374,
  kChunkView = 375,
  kTriu = 376,
  kRandIntLike = 377,
  kMinDim = 378,
  kAdamW = 379,
  kConcat = 380,
  kGreaterEqual = 381,
  kSpeedFusionAttentionGrad = 382,
  kReLU = 383,
  kDistCommIsend = 384,
  kMaskedSelect = 385,
  kReflectionPad2DGrad = 386,
  kAsStrided = 387,
  kRsqrt = 388,
  kScatterAddExt = 389,
  kExpandDims = 390,
  kConv2DPadding = 391,
  kNarrow = 392,
  kEqual = 393,
  kRmsNormGrad = 394,
  kInplaceHardtanh = 395,
  kGroupNormGrad = 396,
  kUpsampleLinear1D = 397,
  kConvolutionGrad = 398,
  kLeakyReLUExt = 399,
  kDiagonalView = 400,
  kIdentity = 401,
  kXLogYScalarOther = 402,
  kSubScalar = 403,
  kConstantPadND = 404,
  kHSigmoidGrad = 405,
  kMatrixInverseExt = 406,
  kLinalgVectorNorm = 407,
  kAddLayerNormGrad = 408,
  kBitwiseAndScalar = 409,
  kReflectionPad3DGrad = 410,
  kArgMinWithValue = 411,
  kReduceMin = 412,
  kInnerMoeTokenUnpermute = 413,
  kSin = 414,
  kUpsampleNearest1D = 415,
  kDistCommScatterTensor = 416,
  kBatchNormReduceGrad = 417,
  kLogicalOr = 418,
  kInplaceReLU = 419,
  kInnerNonZero = 420,
  kSub = 421,
  kAddbmm = 422,
  kAvgPool1D = 423,
  kCast = 424,
  kSoftMarginLoss = 425,
  kInplaceAddmm = 426,
  kVar = 427,
  kEmpty = 428,
  kMaxUnpool2DExt = 429,
  kSign = 430,
  kBitwiseOrTensor = 431,
  kScatterValue = 432,
  kDistCommGather = 433,
  kAddLayerNormV2 = 434,
  kInplacePut = 435,
  kDropoutExt = 436,
  kInplaceAddExt = 437,
  kErfinv = 438,
  kArgMaxExt = 439,
  kUpsampleNearest3DGrad = 440,
  kAvgPool2DGrad = 441,
  kInplaceScatterSrc = 442,
  kNormalFloatFloat = 443,
  kInplaceIndexAddExt = 444,
  kTypeAs = 445,
  kLogAddExp = 446,
  kInplaceIndexPut = 447,
  kClone = 448,
  kInplaceStopGradient = 449,
  kDistCommBarrier = 450,
  kBitwiseNot = 451,
  kGLU = 452,
  kAdd = 453,
  kInplaceMatmulAdd = 454,
  kGreater = 455,
  kMaskedFill = 456,
  kDivMod = 457,
  kLogSoftmax = 458,
  kSwiglu = 459,
  kMatMulExt = 460,
  kInplaceMaskedFillScalar = 461,
  kAtanExt = 462,
  kHardtanh = 463,
  kNonZero = 464,
  kMedianExt = 465,
  kMeanExt = 466,
  kSplitWithSizeView = 467,
  kFFNExt = 468,
  kGridSampler3D = 469,
  kAcosExt = 470,
  kAdaptiveAvgPool2DGradExt = 471,
  kInnerInplaceIndexPut = 472,
  kInplaceTanh = 473,
  kLogAddExp2 = 474,
  kUnique2 = 475,
  kGridSampler2DGrad = 476,
  kGreaterEqualScalar = 477,
  kLess = 478,
  kSplitWithSize = 479,
  kCol2ImGrad = 480,
  kReplicationPad2D = 481,
  kNewFull = 482,
  kRandnLike = 483,
  kL1LossExt = 484,
  kUniqueDim = 485,
  kFullLike = 486,
  kL1LossBackwardExt = 487,
  kDistCommIrecv = 488,
  kSeLUExt = 489,
  kNansum = 490,
  kRandLikeExt = 491,
  kFlattenExt = 492,
  kBitwiseXorScalar = 493,
  kHSigmoid = 494,
  kSmoothL1Loss = 495,
  kVarMean = 496,
  kInnerCommAllGather = 497,
  kPReLU = 498,
  kLogSoftmaxGrad = 499,
  kAtan2Ext = 500,
  kAddExt = 501,
  kLog2 = 502,
  kMoeGatingTopKSoftmax = 503,
  kQuantBatchMatmul = 504,
  kAddRmsNormQuantV2 = 505,
  kGroupedMatmul = 506,
  kDynamicQuantExt = 507,
  kQuantMatmul = 508,
  kMoeInitRouting = 509,
  kMoeInitRoutingQuantV2 = 510,
  kMoeComputeExpertTokens = 511,
  kGroupedMatmulV2 = 512,
  kWeightQuantBatchMatmul = 513,
  kFusedInferAttentionScore = 514,
  kMoeFinalizeRouting = 515,
  kGroupedMatmulV4 = 516,
  kMoeInitRoutingV2 = 517,
  kQuantV2 = 518,
  kMatmulAllReduceAddRmsNorm = 519,
  kKVCacheScatterUpdate = 520,
  kAnyExt = 521,
  kGmmBackward = 522,
  kInplaceExponential = 523,
  kGmmV2 = 524,
  kAny = 525,
  kPixelShuffle = 526,
  kGmmV2Backward = 527,
  kFuncMaxPool2D = 528,
  kGmm = 529,
  kGmmBackwardFusion = 530,
  kGmmV2BackwardFusion = 531,
  kMoeTokenUnpermute = 532,
  kEinsumExt = 533,
};

using AvgPool3DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MSELossGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using TakeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using MaxPoolGradWithIndicesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using DiagExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using RoundGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using ReshapeAndCacheGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using AllFiniteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &)>;
using LogSigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using TExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using IncreFlashAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using DistCommBatchIsendIrecvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::StringImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using BatchNormElemtGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using NonZeroExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using NewZerosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using CoshGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using AvgPool2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using TileGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using SmoothL1LossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using ArgMinExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using NotEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using Log10GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using OnesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SplitGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using LogGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using EmptyLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LinSpaceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReciprocalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using Im2ColExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using GridSampler2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using IsCloseGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using ReduceAllGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using ZerosLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ConvTranspose2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using SoftmaxBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using UpsampleNearest3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using XlogyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AcoshExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ArangeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ErfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ReshapeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using MeshgridGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const int64_t &)>;
using GeneratorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using RepeatInterleaveIntGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceClampTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using BatchNormGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::ValueTuplePtr &)>;
using TransposeExtViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using HardtanhGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using Conv1DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using HSwishGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ClampScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ScalarPtr> &, const std::optional<mindspore::ScalarPtr> &)>;
using DropoutGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using GroupNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::FP32ImmPtr &)>;
using SliceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &, const int64_t &, const int64_t &)>;
using SelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SoftplusExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using BinaryCrossEntropyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using FloorDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using MaxPoolGradWithMaskGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using ArgMaxWithValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using RandpermExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using HSwishGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using MvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ReplicationPad1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using DistCommAllToAllVSingleGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using NewOnesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using Exp2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using TanhGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SqueezeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using AddmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using AllGatherMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using SumExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using NormalTensorFloatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using EmbeddingDenseBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using ScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using AdaptiveAvgPool2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using MultiScaleDeformableAttnGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using FlashAttentionScoreGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using LessEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using EluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using FloorDivScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using AdaptiveMaxPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using CosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleLinear1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using ContiguousGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceCopyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using RepeatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using FillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MaximumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using LerpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using DropoutDoMaskExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using SpeedFusionAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using ConvolutionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using NormalTensorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SwigluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using PagedAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using UnstackExtViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &)>;
using InplaceScatterAddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SoftShrinkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using Conv2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using InnerCommIsendGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &)>;
using DivModsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using DivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using LogicalAndGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using BroadcastToViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using SliceExtViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &, const int64_t &, const int64_t &)>;
using InplaceGroupedMatmulAddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using BCEWithLogitsLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using MultiScaleDeformableAttnGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using GeLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using AddcmulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using RemainderScalarTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &)>;
using DistCommAllToAllVGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using RmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using InplaceUniformGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceEluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using InplaceFloorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ThresholdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using SoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using MoeTokenPermuteGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using SearchSortedGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceDivsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using GatherDGradV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SplitTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using EluGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using BaddbmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using NLLLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using EmbeddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceScatterValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using Conv3DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using SplitTensorViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using RandExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using TruncGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SubExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceThresholdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using DistCommReduceScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &, const mindspore::StringImmPtr &)>;
using NarrowViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &, const int64_t &)>;
using BitwiseXorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InnerCommReduceScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &, const mindspore::StringImmPtr &)>;
using UniformExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AddScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using InnerIndexGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using IsNegInfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ReverseV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using IndexSelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &)>;
using OnesLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReflectionPad3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using BatchMatMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using FmodTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AbsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using TopkExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using SeluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleBilinear2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using ConvolutionStrGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using BitwiseAndTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using XLogYScalarSelfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &)>;
using MishExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using NLLLoss2dGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &)>;
using CountNonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using FlashAttentionScoreGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using DistCommReduceScatterTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &, const mindspore::StringImmPtr &)>;
using StdMeanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using LogSoftmaxExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MoeDistributeCombineGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::StringImmPtr> &, const std::optional<mindspore::StringImmPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using CummaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using InnerCommAllReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::StringImmPtr &)>;
using DistCommGatherIntoTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using NLLLoss2dGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using ReflectionPad1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using MatmulReduceScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using SilentCheckV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using RandnGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using RollGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using BinaryCrossEntropyWithLogitsBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using DenseGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using SelectV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using RemainderTensorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using MaxPoolWithIndicesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using ReplicationPad1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using DistCommBroadcastGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using MSELossExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using MedianDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using SincGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using BernoulliExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceErfinvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using MaskedSelectGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using CrossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using LogSigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ZerosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using FracGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ReduceAnyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using MulsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using SliceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &, const std::vector<int64_t> &)>;
using InplaceScatterValueReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &)>;
using LogicalNotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using DistCommAllGatherGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using ErfcGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using GatherDGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &)>;
using InnerCommIrecvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &)>;
using Expm1GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SortExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using ReflectionPad1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using TransposeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using AdaptiveAvgPool3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using UpsampleNearest2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using InplaceNormalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using GcdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ReplicationPad3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceAddsExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using DropoutGenMaskExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using BatchMatMulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleNearest1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using EyeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using SilentCheckV3GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using NeScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using IndexFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using LogicalXorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using MaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using TanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using PowGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ThresholdGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceClampScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ScalarPtr> &, const std::optional<mindspore::ScalarPtr> &)>;
using RotaryPositionEmbeddingGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using TrilExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using DivsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using UniqueConsecutiveGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MaxPoolWithMaskGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using AtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using InnerCommAllToAllVGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceRandomGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using LerpScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using MinimumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using FmodScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using ClampTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using SiLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using PromptFlashAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using ExpandAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using CustomExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &)>;
using LayerNormExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::FP32ImmPtr &)>;
using InplaceFillDiagonalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::BoolImmPtr &)>;
using OuterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ReluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using Conv3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using IndexGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using AddmvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using OneHotExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using GridSampler3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &)>;
using Log1pGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleTrilinear3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using InplaceDivModsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ArgSortGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using MinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using DotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceFloorDividesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceScatterSrcReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using CeilGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using MatMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceSubExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using MulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using Conv1DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using FillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using KLDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using PowTensorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using FloorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using MoeDistributeDispatchGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::StringImmPtr> &, const std::optional<mindspore::StringImmPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using AddRmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using InplaceExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using LogSumExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using SoftMarginLossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using ReplicationPad2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceLogGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using StdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using HShrinkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using ChunkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using AddcdivExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using SigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AsinExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using RotaryPositionEmbeddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using MishGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using IsFiniteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using NormalFloatTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using Col2ImExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using ReflectionPad2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceSubScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using InplaceDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using GluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using ReduceMaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using NanToNumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::FP32ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &)>;
using ViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using CopyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using RandIntGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using BinaryCrossEntropyGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using SqrtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using EqualExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using IndexAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceFloorDivideGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using PolarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using HShrinkGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using RemainderTensorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using NormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using NegGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SinhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using AvgPool3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using AdaptiveAvgPool3DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using HistcExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using TensorScatterElementsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using SelectExtViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using MultinomialExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using DistCommScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using IsInfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using TanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleNearest2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using BatchNormElemtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::FP32ImmPtr &)>;
using PowScalarTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &)>;
using DistCommReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using BatchNormExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &)>;
using BatchNormStatsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using ReplicationPad3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using EluExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using DistCommAllGatherIntoTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using ExpandDimsViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &)>;
using UpsampleBicubic2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using AsinhExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using KLDivGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using AdaptiveMaxPool2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceDivModGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceMulsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using SiLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using CumsumExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ProdExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SoftShrinkGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using RepeatInterleaveGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using MoeTokenPermuteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using RepeatInterleaveTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using NewEmptyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using GeluExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using BitwiseOrScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using UpsampleBilinear2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using CumminExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using DistCommAllReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::StringImmPtr &, const mindspore::StringImmPtr &)>;
using InplaceSiLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using BatchNormGatherStatsWithCountsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using LinalgQrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using KthvalueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using StackExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using TraceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using MaxDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using GeluGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using PReLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceMaskedFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ConvolutionStrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using SquareGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using IndexFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using SoftplusGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using UpsampleBicubic2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using LayerNormGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using GeLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using MoeTokenUnpermuteGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using AdaptiveAvgPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using BincountExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using ApplyRotaryPosEmbGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using MmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using TriangularSolveGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using UpsampleTrilinear3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using BroadcastToGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using TransposeViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &)>;
using LeakyReLUGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::BoolImmPtr &)>;
using NLLLossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using ViewAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ChunkViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &)>;
using TriuGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using RandIntLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MinDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using AdamWGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using ConcatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using GreaterEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SpeedFusionAttentionGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using ReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using DistCommIsendGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &)>;
using MaskedSelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ReflectionPad2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using AsStridedGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &, const std::vector<int64_t> &, const int64_t &)>;
using RsqrtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ScatterAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ExpandDimsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &)>;
using Conv2DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using NarrowGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &, const int64_t &)>;
using EqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using RmsNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceHardtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using GroupNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using UpsampleLinear1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using ConvolutionGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using LeakyReLUExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using DiagonalViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const int64_t &, const int64_t &, const int64_t &)>;
using IdentityGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using XLogYScalarOtherGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using SubScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using ConstantPadNDGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ScalarPtr &)>;
using HSigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using MatrixInverseExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using LinalgVectorNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using AddLayerNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using BitwiseAndScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using ReflectionPad3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using ArgMinWithValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using ReduceMinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using InnerMoeTokenUnpermuteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using SinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using UpsampleNearest1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using DistCommScatterTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using BatchNormReduceGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using LogicalOrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using InnerNonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SubGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AddbmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using AvgPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using CastGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using SoftMarginLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceAddmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using VarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using EmptyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MaxUnpool2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using SignGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using BitwiseOrTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using ScatterValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &)>;
using DistCommGatherGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using AddLayerNormV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using InplacePutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &)>;
using DropoutExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using ErfinvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using ArgMaxExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using UpsampleNearest3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using AvgPool2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceScatterSrcGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using NormalFloatFloatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceIndexAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using TypeAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using LogAddExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceIndexPutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &)>;
using CloneGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceStopGradientGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using DistCommBarrierGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::StringImmPtr &)>;
using BitwiseNotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using GLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using AddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceMatmulAddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using GreaterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using MaskedFillGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using DivModGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LogSoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using SwigluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using MatMulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InplaceMaskedFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using AtanExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using HardtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using NonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using MedianExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using MeanExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SplitWithSizeViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &, const int64_t &)>;
using FFNExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using GridSampler3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using AcosExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using AdaptiveAvgPool2DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using InnerInplaceIndexPutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &)>;
using InplaceTanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using LogAddExp2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using Unique2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using GridSampler2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &)>;
using GreaterEqualScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using LessGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using SplitWithSizeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::vector<int64_t> &, const int64_t &)>;
using Col2ImGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using ReplicationPad2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &)>;
using NewFullGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using RandnLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using L1LossExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using UniqueDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using FullLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using L1LossBackwardExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using DistCommIrecvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using SeLUExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using NansumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using RandLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using FlattenExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using BitwiseXorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using HSigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using SmoothL1LossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using VarMeanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using InnerCommAllGatherGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::StringImmPtr &)>;
using PReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using LogSoftmaxGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using Atan2ExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using AddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &)>;
using Log2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using MoeGatingTopKSoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using QuantBatchMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using AddRmsNormQuantV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &)>;
using GroupedMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using DynamicQuantExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using QuantMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using MoeInitRoutingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using MoeInitRoutingQuantV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using MoeComputeExpertTokensGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using GroupedMatmulV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using WeightQuantBatchMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using FusedInferAttentionScoreGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeFinalizeRoutingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::tensor::TensorPtr> &)>;
using GroupedMatmulV4GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeInitRoutingV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using QuantV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MatmulAllReduceAddRmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using KVCacheScatterUpdateGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using AnyExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using GmmBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &)>;
using InplaceExponentialGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &)>;
using GmmV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using AnyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &)>;
using PixelShuffleGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::Int64ImmPtr &)>;
using GmmV2BackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using FuncMaxPool2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using GmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using GmmBackwardFusionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &)>;
using GmmV2BackwardFusionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::Int64ImmPtr &)>;
using MoeTokenUnpermuteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::TensorPtr &, const mindspore::tensor::TensorPtr &, const std::optional<mindspore::tensor::TensorPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using EinsumExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::StringImmPtr &, const mindspore::ValueTuplePtr &)>;

struct OpsAutoGradRegisters {
  AvgPool3DGradExtGradFunc AvgPool3DGradExtGradFuncObj;
  MSELossGradExtGradFunc MSELossGradExtGradFuncObj;
  TakeGradFunc TakeGradFuncObj;
  MaxPoolGradWithIndicesGradFunc MaxPoolGradWithIndicesGradFuncObj;
  DiagExtGradFunc DiagExtGradFuncObj;
  RoundGradFunc RoundGradFuncObj;
  ReshapeAndCacheGradFunc ReshapeAndCacheGradFuncObj;
  AllFiniteGradFunc AllFiniteGradFuncObj;
  LogSigmoidGradFunc LogSigmoidGradFuncObj;
  TExtGradFunc TExtGradFuncObj;
  IncreFlashAttentionGradFunc IncreFlashAttentionGradFuncObj;
  DistCommBatchIsendIrecvGradFunc DistCommBatchIsendIrecvGradFuncObj;
  BatchNormElemtGradGradFunc BatchNormElemtGradGradFuncObj;
  NonZeroExtGradFunc NonZeroExtGradFuncObj;
  NewZerosGradFunc NewZerosGradFuncObj;
  CoshGradFunc CoshGradFuncObj;
  AvgPool2DGradFunc AvgPool2DGradFuncObj;
  TileGradFunc TileGradFuncObj;
  SmoothL1LossGradGradFunc SmoothL1LossGradGradFuncObj;
  ArgMinExtGradFunc ArgMinExtGradFuncObj;
  NotEqualGradFunc NotEqualGradFuncObj;
  Log10GradFunc Log10GradFuncObj;
  OnesGradFunc OnesGradFuncObj;
  SplitGradFunc SplitGradFuncObj;
  LogGradFunc LogGradFuncObj;
  EmptyLikeGradFunc EmptyLikeGradFuncObj;
  LinSpaceExtGradFunc LinSpaceExtGradFuncObj;
  ReciprocalGradFunc ReciprocalGradFuncObj;
  Im2ColExtGradFunc Im2ColExtGradFuncObj;
  GridSampler2DGradFunc GridSampler2DGradFuncObj;
  InplaceFillTensorGradFunc InplaceFillTensorGradFuncObj;
  IsCloseGradFunc IsCloseGradFuncObj;
  ReduceAllGradFunc ReduceAllGradFuncObj;
  ZerosLikeExtGradFunc ZerosLikeExtGradFuncObj;
  ConvTranspose2DGradFunc ConvTranspose2DGradFuncObj;
  SoftmaxBackwardGradFunc SoftmaxBackwardGradFuncObj;
  UpsampleNearest3DGradFunc UpsampleNearest3DGradFuncObj;
  XlogyGradFunc XlogyGradFuncObj;
  AcoshExtGradFunc AcoshExtGradFuncObj;
  ArangeGradFunc ArangeGradFuncObj;
  ErfGradFunc ErfGradFuncObj;
  ReshapeGradFunc ReshapeGradFuncObj;
  MeshgridGradFunc MeshgridGradFuncObj;
  GeneratorGradFunc GeneratorGradFuncObj;
  RepeatInterleaveIntGradFunc RepeatInterleaveIntGradFuncObj;
  InplaceClampTensorGradFunc InplaceClampTensorGradFuncObj;
  BatchNormGradExtGradFunc BatchNormGradExtGradFuncObj;
  TransposeExtViewGradFunc TransposeExtViewGradFuncObj;
  HardtanhGradGradFunc HardtanhGradGradFuncObj;
  Conv1DExtGradFunc Conv1DExtGradFuncObj;
  HSwishGradGradFunc HSwishGradGradFuncObj;
  ClampScalarGradFunc ClampScalarGradFuncObj;
  DropoutGradExtGradFunc DropoutGradExtGradFuncObj;
  GroupNormGradFunc GroupNormGradFuncObj;
  SliceExtGradFunc SliceExtGradFuncObj;
  SelectGradFunc SelectGradFuncObj;
  SoftplusExtGradFunc SoftplusExtGradFuncObj;
  BinaryCrossEntropyGradFunc BinaryCrossEntropyGradFuncObj;
  FloorDivGradFunc FloorDivGradFuncObj;
  MaxPoolGradWithMaskGradFunc MaxPoolGradWithMaskGradFuncObj;
  ArgMaxWithValueGradFunc ArgMaxWithValueGradFuncObj;
  RandpermExtGradFunc RandpermExtGradFuncObj;
  HSwishGradFunc HSwishGradFuncObj;
  MvGradFunc MvGradFuncObj;
  ReplicationPad1DGradGradFunc ReplicationPad1DGradGradFuncObj;
  DistCommAllToAllVSingleGradFunc DistCommAllToAllVSingleGradFuncObj;
  NewOnesGradFunc NewOnesGradFuncObj;
  Exp2GradFunc Exp2GradFuncObj;
  TanhGradGradFunc TanhGradGradFuncObj;
  SqueezeGradFunc SqueezeGradFuncObj;
  AddmmGradFunc AddmmGradFuncObj;
  AllGatherMatmulGradFunc AllGatherMatmulGradFuncObj;
  SumExtGradFunc SumExtGradFuncObj;
  NormalTensorFloatGradFunc NormalTensorFloatGradFuncObj;
  EmbeddingDenseBackwardGradFunc EmbeddingDenseBackwardGradFuncObj;
  ScatterGradFunc ScatterGradFuncObj;
  AdaptiveAvgPool2DExtGradFunc AdaptiveAvgPool2DExtGradFuncObj;
  MultiScaleDeformableAttnGradFunc MultiScaleDeformableAttnGradFuncObj;
  FlashAttentionScoreGradFunc FlashAttentionScoreGradFuncObj;
  LessEqualGradFunc LessEqualGradFuncObj;
  EluGradFunc EluGradFuncObj;
  FloorDivScalarGradFunc FloorDivScalarGradFuncObj;
  AdaptiveMaxPool1DGradFunc AdaptiveMaxPool1DGradFuncObj;
  CosGradFunc CosGradFuncObj;
  UpsampleLinear1DGradGradFunc UpsampleLinear1DGradGradFuncObj;
  ContiguousGradFunc ContiguousGradFuncObj;
  InplaceCopyGradFunc InplaceCopyGradFuncObj;
  RepeatGradFunc RepeatGradFuncObj;
  FillTensorGradFunc FillTensorGradFuncObj;
  MaximumGradFunc MaximumGradFuncObj;
  LerpGradFunc LerpGradFuncObj;
  DropoutDoMaskExtGradFunc DropoutDoMaskExtGradFuncObj;
  SpeedFusionAttentionGradFunc SpeedFusionAttentionGradFuncObj;
  ConvolutionGradFunc ConvolutionGradFuncObj;
  NormalTensorTensorGradFunc NormalTensorTensorGradFuncObj;
  SwigluGradGradFunc SwigluGradGradFuncObj;
  PagedAttentionGradFunc PagedAttentionGradFuncObj;
  UnstackExtViewGradFunc UnstackExtViewGradFuncObj;
  InplaceScatterAddGradFunc InplaceScatterAddGradFuncObj;
  SoftShrinkGradFunc SoftShrinkGradFuncObj;
  Conv2DExtGradFunc Conv2DExtGradFuncObj;
  InnerCommIsendGradFunc InnerCommIsendGradFuncObj;
  DivModsGradFunc DivModsGradFuncObj;
  DivGradFunc DivGradFuncObj;
  LogicalAndGradFunc LogicalAndGradFuncObj;
  BroadcastToViewGradFunc BroadcastToViewGradFuncObj;
  SliceExtViewGradFunc SliceExtViewGradFuncObj;
  InplaceGroupedMatmulAddGradFunc InplaceGroupedMatmulAddGradFuncObj;
  BCEWithLogitsLossGradFunc BCEWithLogitsLossGradFuncObj;
  MultiScaleDeformableAttnGradGradFunc MultiScaleDeformableAttnGradGradFuncObj;
  GeLUGradFunc GeLUGradFuncObj;
  SigmoidGradFunc SigmoidGradFuncObj;
  AddcmulExtGradFunc AddcmulExtGradFuncObj;
  RemainderScalarTensorGradFunc RemainderScalarTensorGradFuncObj;
  DistCommAllToAllVGradFunc DistCommAllToAllVGradFuncObj;
  RmsNormGradFunc RmsNormGradFuncObj;
  InplaceUniformGradFunc InplaceUniformGradFuncObj;
  InplaceEluGradFunc InplaceEluGradFuncObj;
  InplaceFloorGradFunc InplaceFloorGradFuncObj;
  ThresholdGradFunc ThresholdGradFuncObj;
  SoftmaxGradFunc SoftmaxGradFuncObj;
  MoeTokenPermuteGradGradFunc MoeTokenPermuteGradGradFuncObj;
  SearchSortedGradFunc SearchSortedGradFuncObj;
  InplaceDivsGradFunc InplaceDivsGradFuncObj;
  GatherDGradV2GradFunc GatherDGradV2GradFuncObj;
  SplitTensorGradFunc SplitTensorGradFuncObj;
  EluGradExtGradFunc EluGradExtGradFuncObj;
  BaddbmmGradFunc BaddbmmGradFuncObj;
  NLLLossGradFunc NLLLossGradFuncObj;
  EmbeddingGradFunc EmbeddingGradFuncObj;
  InplaceScatterValueGradFunc InplaceScatterValueGradFuncObj;
  Conv3DPaddingGradFunc Conv3DPaddingGradFuncObj;
  SplitTensorViewGradFunc SplitTensorViewGradFuncObj;
  RandExtGradFunc RandExtGradFuncObj;
  TruncGradFunc TruncGradFuncObj;
  SubExtGradFunc SubExtGradFuncObj;
  InplaceThresholdGradFunc InplaceThresholdGradFuncObj;
  DistCommReduceScatterGradFunc DistCommReduceScatterGradFuncObj;
  NarrowViewGradFunc NarrowViewGradFuncObj;
  BitwiseXorTensorGradFunc BitwiseXorTensorGradFuncObj;
  InnerCommReduceScatterGradFunc InnerCommReduceScatterGradFuncObj;
  UniformExtGradFunc UniformExtGradFuncObj;
  AddScalarGradFunc AddScalarGradFuncObj;
  InnerIndexGradFunc InnerIndexGradFuncObj;
  IsNegInfGradFunc IsNegInfGradFuncObj;
  ReverseV2GradFunc ReverseV2GradFuncObj;
  IndexSelectGradFunc IndexSelectGradFuncObj;
  OnesLikeExtGradFunc OnesLikeExtGradFuncObj;
  ReflectionPad3DGradFunc ReflectionPad3DGradFuncObj;
  BatchMatMulGradFunc BatchMatMulGradFuncObj;
  FmodTensorGradFunc FmodTensorGradFuncObj;
  AbsGradFunc AbsGradFuncObj;
  TopkExtGradFunc TopkExtGradFuncObj;
  SeluGradGradFunc SeluGradGradFuncObj;
  UpsampleBilinear2DGradFunc UpsampleBilinear2DGradFuncObj;
  ConvolutionStrGradGradFunc ConvolutionStrGradGradFuncObj;
  BitwiseAndTensorGradFunc BitwiseAndTensorGradFuncObj;
  XLogYScalarSelfGradFunc XLogYScalarSelfGradFuncObj;
  MishExtGradFunc MishExtGradFuncObj;
  NLLLoss2dGradGradFunc NLLLoss2dGradGradFuncObj;
  CountNonZeroGradFunc CountNonZeroGradFuncObj;
  FlashAttentionScoreGradGradFunc FlashAttentionScoreGradGradFuncObj;
  DistCommReduceScatterTensorGradFunc DistCommReduceScatterTensorGradFuncObj;
  StdMeanGradFunc StdMeanGradFuncObj;
  LogSoftmaxExtGradFunc LogSoftmaxExtGradFuncObj;
  MoeDistributeCombineGradFunc MoeDistributeCombineGradFuncObj;
  CummaxGradFunc CummaxGradFuncObj;
  InnerCommAllReduceGradFunc InnerCommAllReduceGradFuncObj;
  DistCommGatherIntoTensorGradFunc DistCommGatherIntoTensorGradFuncObj;
  NLLLoss2dGradFunc NLLLoss2dGradFuncObj;
  ReflectionPad1DGradFunc ReflectionPad1DGradFuncObj;
  MatmulReduceScatterGradFunc MatmulReduceScatterGradFuncObj;
  SilentCheckV2GradFunc SilentCheckV2GradFuncObj;
  RandnGradFunc RandnGradFuncObj;
  RollGradFunc RollGradFuncObj;
  BinaryCrossEntropyWithLogitsBackwardGradFunc BinaryCrossEntropyWithLogitsBackwardGradFuncObj;
  DenseGradFunc DenseGradFuncObj;
  SelectV2GradFunc SelectV2GradFuncObj;
  RemainderTensorScalarGradFunc RemainderTensorScalarGradFuncObj;
  MaxPoolWithIndicesGradFunc MaxPoolWithIndicesGradFuncObj;
  ReplicationPad1DGradFunc ReplicationPad1DGradFuncObj;
  DistCommBroadcastGradFunc DistCommBroadcastGradFuncObj;
  MSELossExtGradFunc MSELossExtGradFuncObj;
  MedianDimGradFunc MedianDimGradFuncObj;
  SincGradFunc SincGradFuncObj;
  BernoulliExtGradFunc BernoulliExtGradFuncObj;
  InplaceErfinvGradFunc InplaceErfinvGradFuncObj;
  MaskedSelectGradGradFunc MaskedSelectGradGradFuncObj;
  ExpGradFunc ExpGradFuncObj;
  CrossGradFunc CrossGradFuncObj;
  LogSigmoidGradGradFunc LogSigmoidGradGradFuncObj;
  ZerosGradFunc ZerosGradFuncObj;
  FracGradFunc FracGradFuncObj;
  ReduceAnyGradFunc ReduceAnyGradFuncObj;
  MulsGradFunc MulsGradFuncObj;
  SliceGradFunc SliceGradFuncObj;
  InplaceScatterValueReduceGradFunc InplaceScatterValueReduceGradFuncObj;
  LogicalNotGradFunc LogicalNotGradFuncObj;
  DistCommAllGatherGradFunc DistCommAllGatherGradFuncObj;
  ErfcGradFunc ErfcGradFuncObj;
  GatherDGradFunc GatherDGradFuncObj;
  InnerCommIrecvGradFunc InnerCommIrecvGradFuncObj;
  Expm1GradFunc Expm1GradFuncObj;
  SortExtGradFunc SortExtGradFuncObj;
  ReflectionPad1DGradGradFunc ReflectionPad1DGradGradFuncObj;
  TransposeGradFunc TransposeGradFuncObj;
  AdaptiveAvgPool3DExtGradFunc AdaptiveAvgPool3DExtGradFuncObj;
  UpsampleNearest2DGradFunc UpsampleNearest2DGradFuncObj;
  InplaceNormalGradFunc InplaceNormalGradFuncObj;
  GcdGradFunc GcdGradFuncObj;
  ReplicationPad3DGradGradFunc ReplicationPad3DGradGradFuncObj;
  InplaceMulGradFunc InplaceMulGradFuncObj;
  InplaceAddsExtGradFunc InplaceAddsExtGradFuncObj;
  DropoutGenMaskExtGradFunc DropoutGenMaskExtGradFuncObj;
  BatchMatMulExtGradFunc BatchMatMulExtGradFuncObj;
  UpsampleNearest1DGradGradFunc UpsampleNearest1DGradGradFuncObj;
  EyeGradFunc EyeGradFuncObj;
  SilentCheckV3GradFunc SilentCheckV3GradFuncObj;
  NeScalarGradFunc NeScalarGradFuncObj;
  IndexFillTensorGradFunc IndexFillTensorGradFuncObj;
  InplaceZeroGradFunc InplaceZeroGradFuncObj;
  LogicalXorGradFunc LogicalXorGradFuncObj;
  MaxGradFunc MaxGradFuncObj;
  TanGradFunc TanGradFuncObj;
  PowGradFunc PowGradFuncObj;
  ThresholdGradGradFunc ThresholdGradGradFuncObj;
  InplaceClampScalarGradFunc InplaceClampScalarGradFuncObj;
  RotaryPositionEmbeddingGradGradFunc RotaryPositionEmbeddingGradGradFuncObj;
  TrilExtGradFunc TrilExtGradFuncObj;
  DivsGradFunc DivsGradFuncObj;
  UniqueConsecutiveGradFunc UniqueConsecutiveGradFuncObj;
  MaxPoolWithMaskGradFunc MaxPoolWithMaskGradFuncObj;
  AtanhGradFunc AtanhGradFuncObj;
  InnerCommAllToAllVGradFunc InnerCommAllToAllVGradFuncObj;
  InplaceFillScalarGradFunc InplaceFillScalarGradFuncObj;
  InplaceRandomGradFunc InplaceRandomGradFuncObj;
  LerpScalarGradFunc LerpScalarGradFuncObj;
  MinimumGradFunc MinimumGradFuncObj;
  FmodScalarGradFunc FmodScalarGradFuncObj;
  ClampTensorGradFunc ClampTensorGradFuncObj;
  SiLUGradFunc SiLUGradFuncObj;
  PromptFlashAttentionGradFunc PromptFlashAttentionGradFuncObj;
  ExpandAsGradFunc ExpandAsGradFuncObj;
  CustomExtGradFunc CustomExtGradFuncObj;
  LayerNormExtGradFunc LayerNormExtGradFuncObj;
  InplaceFillDiagonalGradFunc InplaceFillDiagonalGradFuncObj;
  OuterGradFunc OuterGradFuncObj;
  ReluGradGradFunc ReluGradGradFuncObj;
  Conv3DExtGradFunc Conv3DExtGradFuncObj;
  IndexGradFunc IndexGradFuncObj;
  AddmvGradFunc AddmvGradFuncObj;
  OneHotExtGradFunc OneHotExtGradFuncObj;
  GridSampler3DGradGradFunc GridSampler3DGradGradFuncObj;
  Log1pGradFunc Log1pGradFuncObj;
  UpsampleTrilinear3DGradFunc UpsampleTrilinear3DGradFuncObj;
  InplaceDivModsGradFunc InplaceDivModsGradFuncObj;
  ArgSortGradFunc ArgSortGradFuncObj;
  MinGradFunc MinGradFuncObj;
  DotGradFunc DotGradFuncObj;
  InplaceFloorDividesGradFunc InplaceFloorDividesGradFuncObj;
  InplaceScatterSrcReduceGradFunc InplaceScatterSrcReduceGradFuncObj;
  CeilGradFunc CeilGradFuncObj;
  MatMulGradFunc MatMulGradFuncObj;
  InplaceSubExtGradFunc InplaceSubExtGradFuncObj;
  MulGradFunc MulGradFuncObj;
  Conv1DPaddingGradFunc Conv1DPaddingGradFuncObj;
  FillScalarGradFunc FillScalarGradFuncObj;
  KLDivGradFunc KLDivGradFuncObj;
  PowTensorScalarGradFunc PowTensorScalarGradFuncObj;
  FloorGradFunc FloorGradFuncObj;
  MoeDistributeDispatchGradFunc MoeDistributeDispatchGradFuncObj;
  AddRmsNormGradFunc AddRmsNormGradFuncObj;
  InplaceExpGradFunc InplaceExpGradFuncObj;
  LogSumExpGradFunc LogSumExpGradFuncObj;
  SoftMarginLossGradGradFunc SoftMarginLossGradGradFuncObj;
  ReplicationPad2DGradGradFunc ReplicationPad2DGradGradFuncObj;
  InplaceLogGradFunc InplaceLogGradFuncObj;
  StdGradFunc StdGradFuncObj;
  HShrinkGradFunc HShrinkGradFuncObj;
  ChunkGradFunc ChunkGradFuncObj;
  AddcdivExtGradFunc AddcdivExtGradFuncObj;
  SigmoidGradGradFunc SigmoidGradGradFuncObj;
  AsinExtGradFunc AsinExtGradFuncObj;
  RotaryPositionEmbeddingGradFunc RotaryPositionEmbeddingGradFuncObj;
  MishGradExtGradFunc MishGradExtGradFuncObj;
  IsFiniteGradFunc IsFiniteGradFuncObj;
  NormalFloatTensorGradFunc NormalFloatTensorGradFuncObj;
  Col2ImExtGradFunc Col2ImExtGradFuncObj;
  ReflectionPad2DGradFunc ReflectionPad2DGradFuncObj;
  InplaceSubScalarGradFunc InplaceSubScalarGradFuncObj;
  InplaceDivGradFunc InplaceDivGradFuncObj;
  GluGradGradFunc GluGradGradFuncObj;
  ReduceMaxGradFunc ReduceMaxGradFuncObj;
  NanToNumGradFunc NanToNumGradFuncObj;
  ViewGradFunc ViewGradFuncObj;
  CopyGradFunc CopyGradFuncObj;
  RandIntGradFunc RandIntGradFuncObj;
  BinaryCrossEntropyGradGradFunc BinaryCrossEntropyGradGradFuncObj;
  SqrtGradFunc SqrtGradFuncObj;
  EqualExtGradFunc EqualExtGradFuncObj;
  IndexAddExtGradFunc IndexAddExtGradFuncObj;
  InplaceFloorDivideGradFunc InplaceFloorDivideGradFuncObj;
  PolarGradFunc PolarGradFuncObj;
  HShrinkGradGradFunc HShrinkGradGradFuncObj;
  RemainderTensorTensorGradFunc RemainderTensorTensorGradFuncObj;
  NormGradFunc NormGradFuncObj;
  NegGradFunc NegGradFuncObj;
  SinhGradFunc SinhGradFuncObj;
  AvgPool3DExtGradFunc AvgPool3DExtGradFuncObj;
  AdaptiveAvgPool3DGradExtGradFunc AdaptiveAvgPool3DGradExtGradFuncObj;
  HistcExtGradFunc HistcExtGradFuncObj;
  TensorScatterElementsGradFunc TensorScatterElementsGradFuncObj;
  SelectExtViewGradFunc SelectExtViewGradFuncObj;
  MultinomialExtGradFunc MultinomialExtGradFuncObj;
  DistCommScatterGradFunc DistCommScatterGradFuncObj;
  IsInfGradFunc IsInfGradFuncObj;
  TanhGradFunc TanhGradFuncObj;
  UpsampleNearest2DGradGradFunc UpsampleNearest2DGradGradFuncObj;
  BatchNormElemtGradFunc BatchNormElemtGradFuncObj;
  PowScalarTensorGradFunc PowScalarTensorGradFuncObj;
  DistCommReduceGradFunc DistCommReduceGradFuncObj;
  BatchNormExtGradFunc BatchNormExtGradFuncObj;
  BatchNormStatsGradFunc BatchNormStatsGradFuncObj;
  ReplicationPad3DGradFunc ReplicationPad3DGradFuncObj;
  EluExtGradFunc EluExtGradFuncObj;
  DistCommAllGatherIntoTensorGradFunc DistCommAllGatherIntoTensorGradFuncObj;
  ExpandDimsViewGradFunc ExpandDimsViewGradFuncObj;
  UpsampleBicubic2DGradFunc UpsampleBicubic2DGradFuncObj;
  AsinhExtGradFunc AsinhExtGradFuncObj;
  KLDivGradGradFunc KLDivGradGradFuncObj;
  AdaptiveMaxPool2DGradFunc AdaptiveMaxPool2DGradFuncObj;
  InplaceDivModGradFunc InplaceDivModGradFuncObj;
  InplaceMulsGradFunc InplaceMulsGradFuncObj;
  SiLUGradGradFunc SiLUGradGradFuncObj;
  CumsumExtGradFunc CumsumExtGradFuncObj;
  ProdExtGradFunc ProdExtGradFuncObj;
  SoftShrinkGradGradFunc SoftShrinkGradGradFuncObj;
  RepeatInterleaveGradGradFunc RepeatInterleaveGradGradFuncObj;
  MoeTokenPermuteGradFunc MoeTokenPermuteGradFuncObj;
  RepeatInterleaveTensorGradFunc RepeatInterleaveTensorGradFuncObj;
  NewEmptyGradFunc NewEmptyGradFuncObj;
  GeluExtGradFunc GeluExtGradFuncObj;
  BitwiseOrScalarGradFunc BitwiseOrScalarGradFuncObj;
  UpsampleBilinear2DGradGradFunc UpsampleBilinear2DGradGradFuncObj;
  CumminExtGradFunc CumminExtGradFuncObj;
  DistCommAllReduceGradFunc DistCommAllReduceGradFuncObj;
  InplaceSiLUGradFunc InplaceSiLUGradFuncObj;
  BatchNormGatherStatsWithCountsGradFunc BatchNormGatherStatsWithCountsGradFuncObj;
  LinalgQrGradFunc LinalgQrGradFuncObj;
  KthvalueGradFunc KthvalueGradFuncObj;
  StackExtGradFunc StackExtGradFuncObj;
  TraceExtGradFunc TraceExtGradFuncObj;
  MaxDimGradFunc MaxDimGradFuncObj;
  GeluGradExtGradFunc GeluGradExtGradFuncObj;
  PReLUGradGradFunc PReLUGradGradFuncObj;
  InplaceMaskedFillTensorGradFunc InplaceMaskedFillTensorGradFuncObj;
  ConvolutionStrGradFunc ConvolutionStrGradFuncObj;
  SquareGradFunc SquareGradFuncObj;
  IndexFillScalarGradFunc IndexFillScalarGradFuncObj;
  SoftplusGradExtGradFunc SoftplusGradExtGradFuncObj;
  UpsampleBicubic2DGradGradFunc UpsampleBicubic2DGradGradFuncObj;
  LayerNormGradExtGradFunc LayerNormGradExtGradFuncObj;
  GeLUGradGradFunc GeLUGradGradFuncObj;
  MoeTokenUnpermuteGradGradFunc MoeTokenUnpermuteGradGradFuncObj;
  AdaptiveAvgPool1DGradFunc AdaptiveAvgPool1DGradFuncObj;
  BincountExtGradFunc BincountExtGradFuncObj;
  ApplyRotaryPosEmbGradFunc ApplyRotaryPosEmbGradFuncObj;
  MmGradFunc MmGradFuncObj;
  TriangularSolveGradFunc TriangularSolveGradFuncObj;
  UpsampleTrilinear3DGradGradFunc UpsampleTrilinear3DGradGradFuncObj;
  BroadcastToGradFunc BroadcastToGradFuncObj;
  TransposeViewGradFunc TransposeViewGradFuncObj;
  LeakyReLUGradExtGradFunc LeakyReLUGradExtGradFuncObj;
  NLLLossGradGradFunc NLLLossGradGradFuncObj;
  ViewAsGradFunc ViewAsGradFuncObj;
  ChunkViewGradFunc ChunkViewGradFuncObj;
  TriuGradFunc TriuGradFuncObj;
  RandIntLikeGradFunc RandIntLikeGradFuncObj;
  MinDimGradFunc MinDimGradFuncObj;
  AdamWGradFunc AdamWGradFuncObj;
  ConcatGradFunc ConcatGradFuncObj;
  GreaterEqualGradFunc GreaterEqualGradFuncObj;
  SpeedFusionAttentionGradGradFunc SpeedFusionAttentionGradGradFuncObj;
  ReLUGradFunc ReLUGradFuncObj;
  DistCommIsendGradFunc DistCommIsendGradFuncObj;
  MaskedSelectGradFunc MaskedSelectGradFuncObj;
  ReflectionPad2DGradGradFunc ReflectionPad2DGradGradFuncObj;
  AsStridedGradFunc AsStridedGradFuncObj;
  RsqrtGradFunc RsqrtGradFuncObj;
  ScatterAddExtGradFunc ScatterAddExtGradFuncObj;
  ExpandDimsGradFunc ExpandDimsGradFuncObj;
  Conv2DPaddingGradFunc Conv2DPaddingGradFuncObj;
  NarrowGradFunc NarrowGradFuncObj;
  EqualGradFunc EqualGradFuncObj;
  RmsNormGradGradFunc RmsNormGradGradFuncObj;
  InplaceHardtanhGradFunc InplaceHardtanhGradFuncObj;
  GroupNormGradGradFunc GroupNormGradGradFuncObj;
  UpsampleLinear1DGradFunc UpsampleLinear1DGradFuncObj;
  ConvolutionGradGradFunc ConvolutionGradGradFuncObj;
  LeakyReLUExtGradFunc LeakyReLUExtGradFuncObj;
  DiagonalViewGradFunc DiagonalViewGradFuncObj;
  IdentityGradFunc IdentityGradFuncObj;
  XLogYScalarOtherGradFunc XLogYScalarOtherGradFuncObj;
  SubScalarGradFunc SubScalarGradFuncObj;
  ConstantPadNDGradFunc ConstantPadNDGradFuncObj;
  HSigmoidGradGradFunc HSigmoidGradGradFuncObj;
  MatrixInverseExtGradFunc MatrixInverseExtGradFuncObj;
  LinalgVectorNormGradFunc LinalgVectorNormGradFuncObj;
  AddLayerNormGradGradFunc AddLayerNormGradGradFuncObj;
  BitwiseAndScalarGradFunc BitwiseAndScalarGradFuncObj;
  ReflectionPad3DGradGradFunc ReflectionPad3DGradGradFuncObj;
  ArgMinWithValueGradFunc ArgMinWithValueGradFuncObj;
  ReduceMinGradFunc ReduceMinGradFuncObj;
  InnerMoeTokenUnpermuteGradFunc InnerMoeTokenUnpermuteGradFuncObj;
  SinGradFunc SinGradFuncObj;
  UpsampleNearest1DGradFunc UpsampleNearest1DGradFuncObj;
  DistCommScatterTensorGradFunc DistCommScatterTensorGradFuncObj;
  BatchNormReduceGradGradFunc BatchNormReduceGradGradFuncObj;
  LogicalOrGradFunc LogicalOrGradFuncObj;
  InplaceReLUGradFunc InplaceReLUGradFuncObj;
  InnerNonZeroGradFunc InnerNonZeroGradFuncObj;
  SubGradFunc SubGradFuncObj;
  AddbmmGradFunc AddbmmGradFuncObj;
  AvgPool1DGradFunc AvgPool1DGradFuncObj;
  CastGradFunc CastGradFuncObj;
  SoftMarginLossGradFunc SoftMarginLossGradFuncObj;
  InplaceAddmmGradFunc InplaceAddmmGradFuncObj;
  VarGradFunc VarGradFuncObj;
  EmptyGradFunc EmptyGradFuncObj;
  MaxUnpool2DExtGradFunc MaxUnpool2DExtGradFuncObj;
  SignGradFunc SignGradFuncObj;
  BitwiseOrTensorGradFunc BitwiseOrTensorGradFuncObj;
  ScatterValueGradFunc ScatterValueGradFuncObj;
  DistCommGatherGradFunc DistCommGatherGradFuncObj;
  AddLayerNormV2GradFunc AddLayerNormV2GradFuncObj;
  InplacePutGradFunc InplacePutGradFuncObj;
  DropoutExtGradFunc DropoutExtGradFuncObj;
  InplaceAddExtGradFunc InplaceAddExtGradFuncObj;
  ErfinvGradFunc ErfinvGradFuncObj;
  ArgMaxExtGradFunc ArgMaxExtGradFuncObj;
  UpsampleNearest3DGradGradFunc UpsampleNearest3DGradGradFuncObj;
  AvgPool2DGradGradFunc AvgPool2DGradGradFuncObj;
  InplaceScatterSrcGradFunc InplaceScatterSrcGradFuncObj;
  NormalFloatFloatGradFunc NormalFloatFloatGradFuncObj;
  InplaceIndexAddExtGradFunc InplaceIndexAddExtGradFuncObj;
  TypeAsGradFunc TypeAsGradFuncObj;
  LogAddExpGradFunc LogAddExpGradFuncObj;
  InplaceIndexPutGradFunc InplaceIndexPutGradFuncObj;
  CloneGradFunc CloneGradFuncObj;
  InplaceStopGradientGradFunc InplaceStopGradientGradFuncObj;
  DistCommBarrierGradFunc DistCommBarrierGradFuncObj;
  BitwiseNotGradFunc BitwiseNotGradFuncObj;
  GLUGradFunc GLUGradFuncObj;
  AddGradFunc AddGradFuncObj;
  InplaceMatmulAddGradFunc InplaceMatmulAddGradFuncObj;
  GreaterGradFunc GreaterGradFuncObj;
  MaskedFillGradFunc MaskedFillGradFuncObj;
  DivModGradFunc DivModGradFuncObj;
  LogSoftmaxGradFunc LogSoftmaxGradFuncObj;
  SwigluGradFunc SwigluGradFuncObj;
  MatMulExtGradFunc MatMulExtGradFuncObj;
  InplaceMaskedFillScalarGradFunc InplaceMaskedFillScalarGradFuncObj;
  AtanExtGradFunc AtanExtGradFuncObj;
  HardtanhGradFunc HardtanhGradFuncObj;
  NonZeroGradFunc NonZeroGradFuncObj;
  MedianExtGradFunc MedianExtGradFuncObj;
  MeanExtGradFunc MeanExtGradFuncObj;
  SplitWithSizeViewGradFunc SplitWithSizeViewGradFuncObj;
  FFNExtGradFunc FFNExtGradFuncObj;
  GridSampler3DGradFunc GridSampler3DGradFuncObj;
  AcosExtGradFunc AcosExtGradFuncObj;
  AdaptiveAvgPool2DGradExtGradFunc AdaptiveAvgPool2DGradExtGradFuncObj;
  InnerInplaceIndexPutGradFunc InnerInplaceIndexPutGradFuncObj;
  InplaceTanhGradFunc InplaceTanhGradFuncObj;
  LogAddExp2GradFunc LogAddExp2GradFuncObj;
  Unique2GradFunc Unique2GradFuncObj;
  GridSampler2DGradGradFunc GridSampler2DGradGradFuncObj;
  GreaterEqualScalarGradFunc GreaterEqualScalarGradFuncObj;
  LessGradFunc LessGradFuncObj;
  SplitWithSizeGradFunc SplitWithSizeGradFuncObj;
  Col2ImGradGradFunc Col2ImGradGradFuncObj;
  ReplicationPad2DGradFunc ReplicationPad2DGradFuncObj;
  NewFullGradFunc NewFullGradFuncObj;
  RandnLikeGradFunc RandnLikeGradFuncObj;
  L1LossExtGradFunc L1LossExtGradFuncObj;
  UniqueDimGradFunc UniqueDimGradFuncObj;
  FullLikeGradFunc FullLikeGradFuncObj;
  L1LossBackwardExtGradFunc L1LossBackwardExtGradFuncObj;
  DistCommIrecvGradFunc DistCommIrecvGradFuncObj;
  SeLUExtGradFunc SeLUExtGradFuncObj;
  NansumGradFunc NansumGradFuncObj;
  RandLikeExtGradFunc RandLikeExtGradFuncObj;
  FlattenExtGradFunc FlattenExtGradFuncObj;
  BitwiseXorScalarGradFunc BitwiseXorScalarGradFuncObj;
  HSigmoidGradFunc HSigmoidGradFuncObj;
  SmoothL1LossGradFunc SmoothL1LossGradFuncObj;
  VarMeanGradFunc VarMeanGradFuncObj;
  InnerCommAllGatherGradFunc InnerCommAllGatherGradFuncObj;
  PReLUGradFunc PReLUGradFuncObj;
  LogSoftmaxGradGradFunc LogSoftmaxGradGradFuncObj;
  Atan2ExtGradFunc Atan2ExtGradFuncObj;
  AddExtGradFunc AddExtGradFuncObj;
  Log2GradFunc Log2GradFuncObj;
  MoeGatingTopKSoftmaxGradFunc MoeGatingTopKSoftmaxGradFuncObj;
  QuantBatchMatmulGradFunc QuantBatchMatmulGradFuncObj;
  AddRmsNormQuantV2GradFunc AddRmsNormQuantV2GradFuncObj;
  GroupedMatmulGradFunc GroupedMatmulGradFuncObj;
  DynamicQuantExtGradFunc DynamicQuantExtGradFuncObj;
  QuantMatmulGradFunc QuantMatmulGradFuncObj;
  MoeInitRoutingGradFunc MoeInitRoutingGradFuncObj;
  MoeInitRoutingQuantV2GradFunc MoeInitRoutingQuantV2GradFuncObj;
  MoeComputeExpertTokensGradFunc MoeComputeExpertTokensGradFuncObj;
  GroupedMatmulV2GradFunc GroupedMatmulV2GradFuncObj;
  WeightQuantBatchMatmulGradFunc WeightQuantBatchMatmulGradFuncObj;
  FusedInferAttentionScoreGradFunc FusedInferAttentionScoreGradFuncObj;
  MoeFinalizeRoutingGradFunc MoeFinalizeRoutingGradFuncObj;
  GroupedMatmulV4GradFunc GroupedMatmulV4GradFuncObj;
  MoeInitRoutingV2GradFunc MoeInitRoutingV2GradFuncObj;
  QuantV2GradFunc QuantV2GradFuncObj;
  MatmulAllReduceAddRmsNormGradFunc MatmulAllReduceAddRmsNormGradFuncObj;
  KVCacheScatterUpdateGradFunc KVCacheScatterUpdateGradFuncObj;
  AnyExtGradFunc AnyExtGradFuncObj;
  GmmBackwardGradFunc GmmBackwardGradFuncObj;
  InplaceExponentialGradFunc InplaceExponentialGradFuncObj;
  GmmV2GradFunc GmmV2GradFuncObj;
  AnyGradFunc AnyGradFuncObj;
  PixelShuffleGradFunc PixelShuffleGradFuncObj;
  GmmV2BackwardGradFunc GmmV2BackwardGradFuncObj;
  FuncMaxPool2DGradFunc FuncMaxPool2DGradFuncObj;
  GmmGradFunc GmmGradFuncObj;
  GmmBackwardFusionGradFunc GmmBackwardFusionGradFuncObj;
  GmmV2BackwardFusionGradFunc GmmV2BackwardFusionGradFuncObj;
  MoeTokenUnpermuteGradFunc MoeTokenUnpermuteGradFuncObj;
  EinsumExtGradFunc EinsumExtGradFuncObj;
};
}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_MINDSPORE_OPS_KERNEL_FUNCTIONS_AUTO_GENERATE_AUTO_GRAD_OP_REG_H_

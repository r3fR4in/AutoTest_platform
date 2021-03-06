import axios from 'axios';
import {loginreq, getReq, postReq, putReq, deleteReq, getFile} from './axiosFun';

/**
 * 提测申请管理
 **/
// 获取提测列表
export const submittedTestsList = (params) => { return getReq("/submittedTests/submittedTestsList", params) };
// 获取冒烟测试不通过原因
export const getReasonOption = (params) => { return getReq("/submittedTests/getReasonOption", params) };
// 获取查询条件下拉框选项
export const getSubmittedTestOptions = (params) => { return getReq("/submittedTests/getSubmittedTestOptions", params) };
// 保存提测申请
export const addSubmittedTest = (params) => { return postReq("/submittedTests/saveSubmittedTest", params) };
// 保存提测申请
export const editSubmittedTest = (params) => { return putReq("/submittedTests/saveSubmittedTest", params) };
// 删除提测申请
export const deleteSubmittedTest = (params) => { return deleteReq("/submittedTests/deleteSubmittedTest", params) };
// 保存冒烟测试结果
export const saveSmokeTestingResult = (params) => { return putReq("/submittedTests/saveSmokeTestingResult", params) };
// 保存最终测试结果
export const saveTestResult = (params) => { return putReq("/submittedTests/saveTestResult", params) };
// 删除上传文件
export const deleteUploadFile = (params) => { return deleteReq("/submittedTests/deleteUploadFile", params) };
// 下载上传文件
export const downloadFile = (params) => { return getFile("/submittedTests/downloadFile", params) };

/**
 * 完成提测冒烟测试排名
 **/
// 完成提测冒烟测试排名
export const smokeTestingRankReport = (params) => { return getReq("/submittedTestsReport/smokeTestingRankReport", params) };

/**
 * 项目非一次性通过原因分析
 **/
// 完成提测冒烟测试排名
export const smokeTestingFailReasonAnalysisReport = (params) => { return getReq("/submittedTestsReport/smokeTestingFailReasonAnalysisReport", params) };

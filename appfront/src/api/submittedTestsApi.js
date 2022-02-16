import axios from 'axios';
import {loginreq, getReq, postReq, deleteReq} from './axiosFun';

/**
 * 提测申请管理
 **/
// 获取提测列表
export const submittedTestsList = (params) => { return getReq("/submittedTests/submittedTestsList", params) };
// 获取冒烟测试不通过原因
export const getReasonOption = (params) => { return getReq("/submittedTests/getReasonOption", params) };
// 保存提测申请
export const saveSubmittedTest = (params) => { return postReq("/submittedTests/saveSubmittedTest", params) };
// 删除提测申请
export const deleteSubmittedTest = (params) => { return deleteReq("/submittedTests/deleteSubmittedTest", params) };
// 保存冒烟测试结果
export const saveSmokeTestingResult = (params) => { return postReq("/submittedTests/saveSmokeTestingResult", params) };
// 保存最终测试结果
export const saveTestResult = (params) => { return postReq("/submittedTests/saveTestResult", params) };

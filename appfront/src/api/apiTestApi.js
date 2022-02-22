import axios from 'axios';
import {loginreq, getReq, postReq, deleteReq, getFile} from './axiosFun';

/**
 * 功能模块管理
 **/
// 下拉框获取项目环境列表
export const getAllProjectEnvironment = (params) => { return getReq("/apiTest/getAllProjectEnvironment", params) };
// 获取功能模块列表
export const apiModuleList = (params) => { return getReq("/apiTest/apiModuleList", params) };
// 保存功能模块
export const saveApiModule = (params) => { return postReq("/apiTest/saveApiModule", params) };
// 删除功能模块
export const deleteApiModule = (params) => { return deleteReq("/apiTest/deleteApiModule", params) };

/**
 * 接口管理
 **/
// 根据项目环境配置的id查找module
export const getAllApiModule = (params) => { return getReq("/apiTest/getAllApiModule", params) };
// 获取api列表
export const apiList = (params) => { return getReq("/apiTest/apiList", params) };
// 保存api
export const saveApi = (params) => { return postReq("/apiTest/saveApi", params) };
// 删除api
export const deleteApi = (params) => { return deleteReq("/apiTest/deleteApi", params) };
// 获取环境变量
export const getEnvironmentVariable = (params) => { return getReq("/apiTest/getEnvironmentVariable", params) };
// 保存环境变量
export const saveEnvironmentVariable = (params) => { return postReq("/apiTest/saveEnvironmentVariable", params) };
// 删除环境变量
export const deleteEnvironmentVariable = (params) => { return deleteReq("/apiTest/deleteEnvironmentVariable", params) };
// api上移
export const upApi = (params) => { return getReq("/apiTest/upApi", params) };
// api下移
export const downApi = (params) => { return getReq("/apiTest/downApi", params) };
// 状态启用/禁用
export const changeApiStatus = (params) => { return getReq("/apiTest/changeApiStatus", params) };

/**
 * 测试用例管理
 **/
// 获取apiTestcase列表
export const apiTestcaseList = (params) => { return getReq("/apiTest/apiTestcaseList", params) };
// 删除testcase
export const deleteApiTestcase = (params) => { return deleteReq("/apiTest/deleteApiTestcase", params) };
// 复制testcase
export const copyTestcase = (params) => { return getReq("/apiTest/copyTestcase", params) };

/**
 * 工作台
 **/
// 获取apiTestcase数据
export const apiTestcaseData = (params) => { return getReq("/apiTest/apiTestcaseData", params) };
// 保存apiTestcase数据
export const saveApiTestcase = (params) => { return postReq("/apiTest/saveApiTestcase", params) };
// 调试
export const debugApi = (params) => { return postReq("/apiTest/debugApi", params) };
// 删除上传文件
export const deleteUploadFile = (params) => { return deleteReq("/apiTest/deleteUploadFile", params) };
// 下载上传文件
export const downloadFile = (params) => { return getFile("/apiTest/downloadFile", params) };

/**
 * 测试任务
 **/
// 获取api测试任务记录
export const apiTestTaskList = (params) => { return getReq("/apiTest/apiTestTaskList", params) };
// 提交api测试任务
export const addApiTestTask = (params) => { return postReq("/apiTest/addApiTestTask", params) };
// 删除api测试任务
export const deleteApiTestTask = (params) => { return deleteReq("/apiTest/deleteApiTestTask", params) };
// 跳转api测试报告
export const apiTestReport = (params) => { return getReq("/apiTest/apiTestReport", params) };

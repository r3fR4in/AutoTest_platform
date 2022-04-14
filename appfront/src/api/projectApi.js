import axios from 'axios';
import {loginreq, getReq, postReq, deleteReq} from './axiosFun';

/**
 * 项目管理
 **/
// 获取项目列表
export const projectList = (params) => { return getReq("/project/projectList", params) };
// 保存项目信息
export const saveProject = (params) => { return postReq("/project/saveProject", params) };
// 删除项目
export const deleteProject = (params) => { return deleteReq("/project/deleteProject", params) };

/**
 * 项目环境配置
 **/
// 获取项目环境配置列表
export const projectEnvironmentList = (params) => { return getReq("/project/projectEnvironmentList", params) };
// 搜索框获取所有项目
export const getAllProject = (params) => { return getReq("/project/getAllProject", params) };
// 保存项目环境配置信息
export const saveProjectEnvironment = (params) => { return postReq("/project/saveProjectEnvironment", params) };
// 删除项目环境配置
export const deleteProjectEnvironment = (params) => { return deleteReq("/project/deleteProjectEnvironment", params) };
// 复制项目环境
export const copyEnvironment = (params) => { return getReq("/project/copyEnvironment", params) };

/**
 * 项目模块
 **/
// 获取模块列表
export const projectModuleList = (params) => { return getReq("/project/projectModuleList", params) };
// 保存模块
export const saveProjectModule = (params) => { return postReq("/project/saveProjectModule", params) };
// 删除模块
export const deleteProjectModule = (params) => { return deleteReq("/project/deleteProjectModule", params) };
// 下拉框获取项目环境列表
export const getAllProjectEnvironment = (params) => { return getReq("/project/getAllProjectEnvironment", params) };

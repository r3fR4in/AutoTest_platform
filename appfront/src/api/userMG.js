import axios from 'axios';
import { loginreq, req, getReq, putReq, postReq, deleteReq } from './axiosFun';

// 登录接口
export const login = (params) => { return loginreq("post", "/user/login", params) };
// 获取用户菜单
export const menu = (params) => { return getReq("/user/menu")};
// 退出接口
export const logout = () => { return getReq("/user/logout") };

/**
 * 用户管理
 **/
// 获取用户列表
export const userList = (params) => { return getReq("/user/userList", params) };
// 获取用户权限的code
export const getRoleCode = (params) => { return getReq("/user/getRoleCode", params) };
// 用户保存（添加编辑）
export const addUser = (params) => { return postReq("/user/saveUser", params) };
// 用户保存（添加编辑）
export const editUser = (params) => { return putReq("/user/saveUser", params) };
// 修改用户状态
export const changeUserStatus = (params) => { return putReq("/user/changeUserStatus", params) };
// 删除用户
export const userDelete = (params) => { return deleteReq("/user/deleteUser", params) };
// 用户重置密码
export const resetPwd = (params) => { return putReq("/user/resetPwd", params) };
// 获取项目权限列表
export const projectPermissionsList = (params) => { return getReq("/user/projectPermissionsList", params) };
// 保存项目权限
export const projectPermissionsSave = (params) => { return postReq("/user/projectPermissionsSave", params) };
// 保存项目权限
export const modifyPwd = (params) => { return postReq("/user/modifyPwd", params) };
// 获取用户下拉选项
export const getUserOptions = (params) => { return getReq("/user/getUserOptions", params) };


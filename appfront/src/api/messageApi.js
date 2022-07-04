import axios from 'axios';
import { loginreq, req, getReq, putReq, postReq, deleteReq } from './axiosFun';

// 获取消息列表
export const getMessage = (params) => { return getReq("/message/getMessage", params) };
// 批量清空未读提示
export const clearUnreadMessage = (params) => { return getReq("/message/clearUnreadMessage", params) };
// 获取未推送消息
export const pushMessage = (params) => { return getReq("/message/pushMessage", params) };

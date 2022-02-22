import axios from 'axios';

// 登录请求方法
const loginreq = (method, url, params) => {
    return axios({
        method: method,
        url: url,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data: params,
        traditional: true,
        transformRequest: [
            function(data) {
                let ret = '';
                for (let it in data) {
                    ret +=
                        encodeURIComponent(it) +
                        '=' +
                        encodeURIComponent(data[it]) +
                        '&'
                }
                return ret
            }
        ]
    }).then(res => res.data);
};
// 通用公用方法
const req = (method, url, params) => {
    return axios({
        method: method,
        url: url,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': localStorage.getItem('logintoken')
        },
        data: params,
        traditional: true,
        transformRequest: [
            function(data) {
                let ret = '';
                for (let it in data) {
                    ret +=
                        encodeURIComponent(it) +
                        '=' +
                        encodeURIComponent(data[it]) +
                        '&'
                }
                return ret
            }
        ]
    }).then(res => res.data);
};

// 通用公用方法
const postReq = (url, params) => {
    return axios({
        method: 'post',
        url: url,
        headers: {
            // 'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': localStorage.getItem('logintoken')
        },
        data: params,
        // traditional: true,
        // transformRequest: [
        //     function(data) {
        //         let ret = '';
        //         for (let it in data) {
        //             ret +=
        //                 encodeURIComponent(it) +
        //                 '=' +
        //                 encodeURIComponent(data[it]) +
        //                 '&'
        //         }
        //         return ret
        //     }
        // ]
    }).then(res => res.data);
};

// 通用公用方法
const getReq = (url, params) => {
    return axios({
        method: 'get',
        url: url,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': localStorage.getItem('logintoken')
        },
        params: params,
        traditional: true,
        transformRequest: [
            function(data) {
                let ret = '';
                for (let it in data) {
                    ret +=
                        encodeURIComponent(it) +
                        '=' +
                        encodeURIComponent(data[it]) +
                        '&'
                }
                return ret
            }
        ]
    }).then(res => res.data);
};

const getFile = (url, params) => {
    return axios({
        method: 'get',
        url: url,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': localStorage.getItem('logintoken')
        },
        params: params,
        traditional: true,
        responseType: 'blob',
        transformRequest: [
            function(data) {
                let ret = '';
                for (let it in data) {
                    ret +=
                        encodeURIComponent(it) +
                        '=' +
                        encodeURIComponent(data[it]) +
                        '&'
                }
                return ret
            }
        ]
    }).then(res => res);
};

// 通用公用方法
const deleteReq = (url, params) => {
    return axios({
        method: 'delete',
        url: url,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': localStorage.getItem('logintoken')
        },
        params: params,
        traditional: true,
        transformRequest: [
            function(data) {
                let ret = '';
                for (let it in data) {
                    ret +=
                        encodeURIComponent(it) +
                        '=' +
                        encodeURIComponent(data[it]) +
                        '&'
                }
                return ret
            }
        ]
    }).then(res => res.data);
};

export {
    loginreq,
    req,
    postReq,
    getReq,
    deleteReq,
    getFile
}

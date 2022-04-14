/**
 * 时间戳
 * @param {*} timestamp  时间戳
 */
const timestampToTime = (timestamp) => {
    let date = new Date(timestamp) //时间戳为10位需*1000，时间戳为13位的话不需乘1000
    let Y = date.getFullYear() + '-'
    let M =
        (date.getMonth() + 1 < 10 ?
            '0' + (date.getMonth() + 1) :
            date.getMonth() + 1) + '-'
    let D =
        (date.getDate() < 10 ? '0' + date.getDate() : date.getDate()) + ' '
    let h =
        (date.getHours() < 10 ? '0' + date.getHours() : date.getHours()) + ':'
    let m =
        (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()) +
        ':'
    let s =
        date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds()
    return Y + M + D + h + m + s
};
/**
 * 存储localStorage
 */
const setStore = (name, content) => {
    if (!name) return;
    if (typeof content !== 'string') {
        content = JSON.stringify(content);
    }
    window.localStorage.setItem(name, content);
}

/**
 * 获取localStorage
 */
const getStore = name => {
    if (!name) return;
    return window.localStorage.getItem(name);
}

/**
 * 删除localStorage
 */
const removeStore = name => {
    if (!name) return;
    window.localStorage.removeItem(name);
}

/**
 * 设置cookie
 **/
function setCookie(name, value, day) {
    let date = new Date();
    date.setDate(date.getDate() + day);
    document.cookie = name + '=' + value + ';expires=' + date;
};

/**
 * 获取cookie
 **/
function getCookie(name) {
    let reg = RegExp(name + '=([^;]+)');
    let arr = document.cookie.match(reg);
    if (arr) {
        return arr[1];
    } else {
        return '';
    }
};

/**
 * 删除cookie
 **/
function delCookie(name) {
    setCookie(name, null, -1);
};

// 将后端返回模块数据转成下拉选项option
function list_to_option(data){
  let list = [];
  for (let i = 0; i < data.length; i++){
    let row = data[i];
    list.push({'label': row.module_name, 'value': row.id});
  }
      return list;
}
// 将后端返回模块数据转成el-tree的格式
function list_to_tree(data){
  let res = {};
  for (let i = 0; i < data.length; i++) {
    let row = data[i];
    // 此行代码用以统一根节点的paren_id, 跟节点的parent_id 可以为 0 或 null
    row.parent_id = row.parent_id ? row.parent_id : 0;
    if (res[row.id]) {
      Object.assign(res[row.id], {id: row.id, module_name: row.module_name, module_description: row.module_description, parent_id: row.parent_id});
    } else {
      res[row.id] = {id: row.id, module_name: row.module_name, module_description: row.module_description, parent_id: row.parent_id, children: []};
    }
    if (res[row.parent_id]) {
      res[row.parent_id].children.push(res[row.id]);
    } else {
      res[row.parent_id] = {children: [res[row.id]]};
    }
  }
  return res[0].children;
}

/**
 * 导出
 **/
export {
    timestampToTime,
    setStore,
    getStore,
    removeStore,
    setCookie,
    getCookie,
    delCookie,
    list_to_option,
    list_to_tree
}

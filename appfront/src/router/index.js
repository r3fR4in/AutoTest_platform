// 导入组件
import Vue from 'vue';
import Router from 'vue-router';
// 登录
import login from '@/views/login';
// 首页
import index from '@/views/index';
/**
 * 系统管理
 */
// 用户管理
import user from '@/views/system/user';
// 修改密码
import modifyPwd from '@/views/system/modifyPwd';


/**
 * 项目管理
 */
// 项目管理界面
import project from '@/views/project/project';
// 项目环境配置
import projectEnvironment from '@/views/project/projectEnvironment';
// 模块管理
import projectModule from '@/views/project/projectModule';

/**
 * 提测管理
 */
// 提测管理界面
import submittedTestsManagement from '@/views/submittedTests/submittedTestsManagement';
// 完成提测冒烟测试排名
import smokeTestingRankReport from '@/views/submittedTests/smokeTestingRankReport';
// 项目非一次性通过原因分析
import smokeTestingFailReasonAnalysisReport from '@/views/submittedTests/smokeTestingFailReasonAnalysisReport';

/**
 * 接口测试
 */
// 功能模块管理界面
import apiModule from '@/views/apiTest/apiModule';
// 接口管理界面
import apiManagement from "@/views/apiTest/apiManagement";
// 测试用例界面
import apiTestCase from "@/views/apiTest/apiTestCase";
// 工作台界面
import workbench from "@/views/apiTest/workbench";
// 接口测试任务界面
import apiTestTask from "@/views/apiTest/apiTestTask";
// 接口测试报告界面
import apiTestReport from "@/views/apiTest/apiTestReport";
// 接口导入界面
import apiImport from "@/views/apiTest/apiImport";

// 处理路由跳转报错问题
const originalPush = Router.prototype.push;
Router.prototype.push = function push(location, resolve, reject) {
    if ( resolve || reject ) return originalPush.call(this, location, resolve, reject)
    return originalPush.call(this, location).catch((e)=>{})
};

// 启用路由
Vue.use(Router);

// 导出路由
export default new Router({
    routes: [{
        path: '/',
        name: '',
        component: login,
        hidden: true,
        meta: {
                requireAuth: false,
                keepAlive: false
        }
    }, {
        path: '/login',
        name: '登录',
        component: login,
        hidden: true,
        meta: {
                requireAuth: false,
                keepAlive: false
        }
    }, {
        path: '/index',
        name: '首页',
        component: index,
        iconCls: 'el-icon-tickets',
        children: [ {
            path: '/system/user',
            name: '用户管理',
            component: user,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        },{
            path: '/system/modifyPwd',
            name: '修改密码',
            component: modifyPwd,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }, {
            path: '/project/project',
            name: '项目管理',
            component: project,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }, {
            path: '/project/projectEnvironment',
            name: '项目环境配置',
            component: projectEnvironment,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }, {
            path: '/project/projectModule',
            name: '项目环境配置',
            component: projectModule,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }, {
            path: '/apiTest/apiModule',
            name: '功能模块管理',
            component: apiModule,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }, {
            path: '/apiTest/apiManagement',
            name: '接口管理',
            component: apiManagement,
            meta: {
                requireAuth: true,
                keepAlive: true
            }
        }, {
            path: '/apiTest/apiManagement/apiTestCase',
            name: '测试用例管理',
            component: apiTestCase,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }, {
            path: '/apiTest/apiManagement/apiTestCase/workbench',
            name: '工作台',
            component: workbench,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }, {
            path: '/apiTest/apiTestTask',
            name: '测试任务',
            component: apiTestTask,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }, {
            path: '/apiTest/apiTestTask/apiTestReport',
            name: '测试报告',
            component: apiTestReport,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }, {
            path: '/apiTest/apiImport',
            name: '接口导入',
            component: apiImport,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }, {
            path: '/submittedTests/submittedTestsManagement',
            name: '提测申请管理',
            component: submittedTestsManagement,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }, {
            path: '/submittedTests/smokeTestingRankReport',
            name: '完成提测冒烟测试排名',
            component: smokeTestingRankReport,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }, {
            path: '/submittedTests/smokeTestingFailReasonAnalysisReport',
            name: '项目非一次性通过原因分析',
            component: smokeTestingFailReasonAnalysisReport,
            meta: {
                requireAuth: true,
                keepAlive: false
            }
        }]
    }]
})

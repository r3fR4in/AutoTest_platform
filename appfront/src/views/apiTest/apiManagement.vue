<template>
    <div>
      <!-- 面包屑导航 -->
      <el-breadcrumb separator-class="el-icon-arrow-right">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>接口管理</el-breadcrumb-item>
      </el-breadcrumb>
      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="formInline" class="user-search">
        <el-form-item label="项目名称：">
          <el-autocomplete size="small" v-model="formInline.projectName" placeholder="输入项目名称" @select="handleSelect1" :fetch-suggestions="querySearchAsync1" @input="inputChange"></el-autocomplete>
        </el-form-item>
        <el-form-item label="项目环境名称：">
          <el-select size="small" v-model="value" clearable placeholder="请选择" @change="handleChange">
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="接口名称：">
          <el-input size="small" v-model="formInline.apiName" placeholder="输入接口名称"></el-input>
        </el-form-item>
        <el-form-item label="url：">
          <el-input size="small" v-model="formInline.url" placeholder="输入url"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button size="small" type="primary" icon="el-icon-search" @click="search">搜索</el-button>
          <el-button size="small" type="primary" icon="el-icon-plus" @click="handleEdit()">添加</el-button>
          <el-button size="small" type="primary" icon="el-icon-plus" @click="handleEnvironmentVariable()">环境变量</el-button>
        </el-form-item>
      </el-form>
      <!--列表-->
      <el-row :gutter="20">
        <el-col :span="4">
          <el-card class="box-card;">
            <el-input
              size="small"
              placeholder="输入关键字进行过滤"
              v-model="filterText">
            </el-input>
            <div style="margin: 20px;"></div>
            <el-tree
              class="filter-tree"
              :data="module_list"
              :props="defaultProps"
              node-key="id"
              default-expand-all
              :highlight-current="true"
              :filter-node-method="filterNode"
              @node-click="handleNodeClick"
              ref="tree">
            </el-tree>
          </el-card>
        </el-col>
        <el-col :span="20">
          <el-table size="small" :data="listData" highlight-current-row v-loading="loading" border element-loading-text="拼命加载中" style="width: 100%;">
            <el-table-column prop="id" label="api Id" v-if=false>
            </el-table-column>
            <el-table-column prop="apiModule_id" label="模块id" v-if=false>
            </el-table-column>
            <el-table-column prop="seq" label="排序号" v-if=false>
            </el-table-column>
            <el-table-column sortable prop="module_name" label="所属模块" width="200">
            </el-table-column>
            <el-table-column sortable prop="api_name" label="接口名称" width="200">
            </el-table-column>
            <el-table-column sortable prop="request_method" label="请求方法" width="100">
            </el-table-column>
            <el-table-column sortable prop="url" label="url" width="250">
            </el-table-column>
            <el-table-column prop="independent" label="是否为独立接口" width="150" align="center">
              <template scope="scope">
                <p v-if="scope.row.independent===false">否</p>
                <p v-if="scope.row.independent===true">是</p>
              </template>
            </el-table-column>
            <el-table-column sortable prop="summary" label="概述" width="250">
            </el-table-column>
            <el-table-column sortable prop="status" label="状态" width="75" align="center">
              <template slot-scope="scope">
                <el-switch
                  v-model="scope.row.status"
                  @change="changeStatus(scope.$index, scope.row)"
                  active-color="#13ce66"
                  inactive-color="#ff4949">
                </el-switch>
              </template>
            </el-table-column>
            <el-table-column align="center" label="操作" min-width="300" fixed="right">
              <template slot-scope="scope">
                <el-button size="mini" type="primary" @click="toTestCase(scope.row)">测试用例</el-button>
                <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
                <el-button size="mini" type="danger" @click="apiDelete(scope.$index, scope.row)">删除</el-button>
                <el-button-group>
                  <el-button size="mini" @click="upLayer(scope.$index, scope.row)">上移</el-button>
                  <el-button size="mini" @click="downLayer(scope.$index, scope.row)">下移</el-button>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
          <!-- 分页组件 -->
          <Pagination v-bind:child-msg="pageparm" @callFather="callFather"></Pagination>
        </el-col>
      </el-row>
      <!-- 编辑界面 -->
      <el-dialog :title="title" :visible.sync="editFormVisible" width="30%" @click="closeDialog">
        <el-form label-width="120px" :model="editForm" :rules="rules" ref="editForm">
          <el-form-item label="所属模块" prop="module_id">
            <el-select size="small" v-model="editForm.module_id" clearable placeholder="请选择" @change="m_handleChange">
              <el-option
                v-for="item in m_options"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="接口名称" prop="api_name">
            <el-input size="small" v-model="editForm.api_name" auto-complete="off" placeholder="请输入接口名称"></el-input>
          </el-form-item>
          <el-form-item label="请求方法" prop="request_method">
            <el-select v-model="editForm.request_method" size="small" placeholder="请选择">
              <el-option
                v-for="item in request_method_options"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="url" prop="url">
            <el-input size="small" v-model="editForm.url" auto-complete="off" placeholder="请输入url"></el-input>
          </el-form-item>
          <el-form-item label="是否为独立接口" prop="independent">
            <el-radio-group v-model="editForm.independent">
              <el-radio :label=false>否</el-radio>
              <el-radio :label=true>是</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="概述" prop="summary">
            <el-input type="textarea" size="small" v-model="editForm.summary" auto-complete="off" placeholder="请输入概述"></el-input>
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="closeDialog">取消</el-button>
          <el-button size="small" type="primary" :loading="loading" class="title" @click="submitForm('editForm')">保存</el-button>
        </div>
      </el-dialog>
      <!-- 环境变量页面 -->
      <el-dialog title="环境变量" :visible.sync="environmentVariableVisible" width="55%" @click="closeDialog">
        <el-button size="small" type="primary" icon="el-icon-plus" @click="e_handleEdit()">添加</el-button>
        <el-table size="small" :data="environmentVariableData" highlight-current-row v-loading="loading" border element-loading-text="拼命加载中" style="width: 100%;margin-top: 20px">
          <el-table-column align="center" type="selection" width="60">
          </el-table-column>
          <el-table-column prop="id" label="id" v-if=false>
          </el-table-column>
          <el-table-column prop="e_id" label="项目环境id" v-if=false>
          </el-table-column>
          <el-table-column sortable prop="name" label="变量名" width="300">
          </el-table-column>
          <el-table-column sortable prop="value" label="变量值" width="300">
          </el-table-column>
          <el-table-column align="center" label="操作" min-width="300">
            <template slot-scope="scope">
              <el-button size="mini" @click="e_handleEdit(scope.$index, scope.row)">编辑</el-button>
              <el-button size="mini" type="danger" @click="EnvironmentVariableDelete(scope.$index, scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <!-- 分页组件 -->
        <Pagination v-bind:child-msg="e_pageparm" @callFather="e_callFather"></Pagination>
      </el-dialog>
      <!-- 编辑界面 -->
      <el-dialog :title="e_title" :visible.sync="e_editFormVisible" width="30%" @click="e_editFormVisible = false">
        <el-form label-width="120px" :model="e_editForm" ref="e_editForm">
          <el-form-item label="变量名" prop="name">
            <el-input size="small" v-model="e_editForm.name" auto-complete="off" placeholder="请输入变量名"></el-input>
          </el-form-item>
          <el-form-item label="变量值" prop="value">
             <el-input size="small" v-model="e_editForm.value" auto-complete="off" placeholder="请输入变量值"></el-input>
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="e_editFormVisible = false">取消</el-button>
          <el-button size="small" type="primary" :loading="loading" class="title" @click="e_submitForm('e_editForm')">保存</el-button>
        </div>
      </el-dialog>
    </div>
</template>

<script>
  import {getAllProject, projectModuleList, getAllProjectEnvironment} from '../../api/projectApi'
  import {apiList, deleteApi, deleteEnvironmentVariable, downApi, getEnvironmentVariable
    , addApi, editApi, addEnvironmentVariable, editEnvironmentVariable, upApi, changeApiStatus} from '../../api/apiTestApi'
  import Pagination from '../../components/Pagination'
  import { list_to_option, list_to_tree } from '../../utils/util'

  export default {
   name: "apiManagement",
   data() {
    return {
      nshow: true, //switch开启
      fshow: false, //switch关闭
      loading: false, //是显示加载
      editFormVisible: false, //控制编辑页面显示与隐藏
      environmentVariableVisible: false, //控制环境变量页面显示与隐藏
      e_editFormVisible: false,
      title: '添加',
      e_title: '添加',
      editForm: {
        id: '',
        module_name: '',
        module_id: '',
        request_method: '',
        api_name:'',
        url: '',
        summary: '',
        independent: false
      },
      e_editForm: {
        id: '',
        e_id: '',
        name: '',
        value: ''
      },
      // rules表单验证
      rules: {
        module_id: [{ required: true, message: '请输入模块名称', trigger: 'blur' }],
        request_method: [{ required: true, message: '请选择请求方法', trigger: 'blur' }],
        api_name: [{ required: true, message: '请输入接口名称', trigger: 'blur' }],
        url: [{ required: true, message: '请输入url', trigger: 'blur' }],
        independent: [{ required: true, message: '请选择是否为独立接口', trigger: 'blur' }]
      },
      projects: '',
      state: '',
      api_modules: '',
      module_list: '',
      defaultProps: {
        children: 'children',
        label: 'module_name'
      },
      current_module_id: '',
      filterText: '',
      formInline: {
        page: 1,
        limit: 10,
        varLable: '',
        varName: '',
        projectName:'',
        projectEnvironment_id: '',
        projectEnvironment_name: '',
        module_id: '',
        module_name: '',
        apiName: '',
        url: ''
      },
      e_formInline: {
        page: 1,
        limit: 10,
        projectEnvironment_id: '',
      },
      userparm: [], //搜索权限
      listData: [], //项目环境数据
      // 分页参数
      pageparm: {
        currentPage: 1,
        pageSize: 10,
        oldPageSize: 10,
        total: 10
      },
      e_pageparm: {
        currentPage: 1,
        pageSize: 10,
        oldPageSize: 10,
        total: 10
      },
      // 下拉框选项
      options: '',
      value: '',
      // 编辑页模块下拉框选项
      m_options: '',
      request_method_options: [{
        value: 'GET',
        label: 'GET'
      },{
        value: 'POST',
        label: 'POST'
      },{
        value: 'PUT',
        label: 'PUT'
      },{
        value: 'DELETE',
        label: 'DELETE'
      }],
      environmentVariableData: []
    }
  },
  // 注册组件
  components: {
    Pagination
  },
  /**
   * 创建完毕
   */
  created() {
    this.loadAllProject();
  },
  /**
   * 里面的方法只有被调用才会执行
   */
  methods: {
    // 获取模块列表
    getModuleData(parameter) {
      parameter = {
        projectEnvironment_id : this.formInline.projectEnvironment_id
      };
      projectModuleList(parameter)
        .then(res => {
          if (res.success === false) {
            this.$message({
              type: 'info',
              message: res.msg
            })
          } else {
            this.originData = res.data;
            if (res.data !== []) {
              this.m_options = list_to_option(this.originData);
              this.module_list = list_to_tree(this.originData);
            }
          }
        })
        .catch(err => {
          this.loading = false;
          console.log(err);
          this.$message.error('模块加载失败，请稍后再试！')
        })
    },
    // 获取api列表
    getdata(parameter) {
      this.loading = true;
      this.pageparm.currentPage = this.formInline.page;
      this.pageparm.pageSize = this.formInline.limit;
      parameter = {
        currentPage: this.pageparm.currentPage,
        pageSize: this.pageparm.pageSize,
        projectEnvironmentId: this.formInline.projectEnvironment_id,
        apiModuleId: this.formInline.module_id,
        apiName: this.formInline.apiName,
        url: this.formInline.url
      };
      /***
       * 调用接口，注释上面模拟数据 取消下面注释
       */
      apiList(parameter)
        .then(res => {
          this.loading = false;
          if (res.success === false) {
            this.$message({
              type: 'info',
              message: res.msg
            })
          } else {
            this.listData = res.data;
            this.pageparm.total = res.count;
          }
        })
        .catch(err => {
          this.loading = false;
          console.log(err);
          this.$message.error('菜单加载失败，请稍后再试！')
        })
    },
    // 分页插件事件
    callFather(parm) {
      if(this.pageparm.pageSize !== parm.pageSize){
        this.formInline.page = 1;
        this.formInline.limit = parm.pageSize;
        this.getdata(this.formInline)
      }else {
        this.formInline.page = parm.currentPage;
        this.formInline.limit = parm.pageSize;
        this.getdata(this.formInline)
      }
    },
    // 分页插件事件
    e_callFather(parm) {
      if(this.e_pageparm.pageSize !== parm.pageSize){
        this.e_formInline.page = 1;
        this.e_formInline.limit = parm.pageSize;
        this.handleEnvironmentVariable()
      }else {
        this.e_formInline.page = parm.currentPage;
        this.e_formInline.limit = parm.pageSize;
        this.handleEnvironmentVariable()
      }
    },
    // 搜索事件
    search() {
      this.formInline.page = 1;
      this.formInline.module_id = '';
      this.getModuleData(this.formInline);
      this.getdata(this.formInline);
    },
    //显示编辑界面
    handleEdit: function(index, row) {
      this.editFormVisible = true;
      if (row != undefined && row != 'undefined') {
        this.title = '修改';
        this.editForm.id = row.id;
        this.editForm.module_id = row.apiModule_id;
        this.editForm.request_method = row.request_method;
        this.editForm.api_name = row.api_name;
        this.editForm.url = row.url;
        this.editForm.independent = row.independent;
        this.editForm.summary = row.summary;
      } else {
        this.title = '添加';
        this.editForm.id = '';
        this.editForm.module_id = this.current_module_id;
        this.editForm.request_method = '';
        this.editForm.api_name = '';
        this.editForm.url = '';
        this.editForm.summary = '';
      }
    },
    e_handleEdit: function(index, row) {
      this.e_editFormVisible = true;
      if (row != undefined && row != 'undefined') {
        this.e_title = '修改';
        this.e_editForm.id = row.id;
        this.e_editForm.e_id = this.formInline.projectEnvironment_id;
        this.e_editForm.name = row.name;
        this.e_editForm.value = row.value;
      } else {
        this.e_title = '添加';
        this.e_editForm.id = '';
        this.e_editForm.e_id = this.formInline.projectEnvironment_id;
        this.e_editForm.name = '';
        this.e_editForm.value = '';
      }
    },
    //显示环境变量编辑页
    handleEnvironmentVariable() {
      this.e_formInline.projectEnvironment_id = this.formInline.projectEnvironment_id;
      this.e_pageparm.currentPage = this.e_formInline.page;
      this.e_pageparm.pageSize = this.e_formInline.limit;
      let param = {
        currentPage: this.e_pageparm.currentPage,
        pageSize: this.e_pageparm.pageSize,
        e_id: this.e_formInline.projectEnvironment_id
      };
      getEnvironmentVariable(param)
        .then(res => {
          if (res.success){
            this.environmentVariableData = res.data;
            this.environmentVariableVisible = true;
            this.e_pageparm.total = res.count;
          }else {
            this.$message({
              type: 'info',
              message: res.msg
            })
          }
        })
        .catch(err => {
          this.loading = false;
          this.$message.error('环境变量获取失败，请稍后再试！')
        });
    },
    // 编辑、增加页面保存方法
    submitForm(editData) {
      this.$refs[editData].validate(valid => {
        if (valid) {
          if (this.editForm.id === ''){
            let param = this.editForm;
            delete param['id'];
            addApi(param)
              .then(res => {
                this.editFormVisible = false;
                this.loading = false;
                if (res.success) {
                  this.getdata(this.formInline);
                  this.$message({
                    type: 'success',
                    message: res.msg
                  })
                } else {
                  this.$message({
                    type: 'info',
                    message: res.msg
                  })
                }
              })
              .catch(err => {
                this.editFormVisible = false;
                this.loading = false;
                this.$message.error('项目保存失败，请稍后再试！')
              })
          } else {
            let param = this.editForm;
            editApi(param)
              .then(res => {
                this.editFormVisible = false;
                this.loading = false;
                if (res.success) {
                  this.getdata(this.formInline);
                  this.$message({
                    type: 'success',
                    message: res.msg
                  })
                } else {
                  this.$message({
                    type: 'info',
                    message: res.msg
                  })
                }
              })
              .catch(err => {
                this.editFormVisible = false;
                this.loading = false;
                this.$message.error('项目保存失败，请稍后再试！')
              })
          }
        } else {
          return false
        }
      })
    },
    e_submitForm(e_editData) {
      this.$refs[e_editData].validate(valid => {
        if (valid) {
          if (this.e_editForm.id === ''){
            let param = this.e_editForm;
            delete param['id'];
            addEnvironmentVariable(param)
              .then(res => {
                this.e_editFormVisible = false;
                this.loading = false;
                if (res.success) {
                  this.handleEnvironmentVariable();
                  this.$message({
                    type: 'success',
                    message: res.msg
                  })
                } else {
                  this.$message({
                    type: 'info',
                    message: res.msg
                  })
                }
              })
              .catch(err => {
                this.editFormVisible = false;
                this.loading = false;
                this.$message.error('环境变量失败，请稍后再试！')
              })
          } else {
            let param = this.e_editForm;
            editEnvironmentVariable(param)
              .then(res => {
                this.e_editFormVisible = false;
                this.loading = false;
                if (res.success) {
                  this.handleEnvironmentVariable();
                  this.$message({
                    type: 'success',
                    message: res.msg
                  })
                } else {
                  this.$message({
                    type: 'info',
                    message: res.msg
                  })
                }
              })
              .catch(err => {
                this.editFormVisible = false;
                this.loading = false;
                this.$message.error('环境变量失败，请稍后再试！')
              })
          }
        } else {
          return false
        }
      })
    },
    // 关闭编辑、增加弹出框
    closeDialog() {
      this.editFormVisible = false;
    },
    // 删除api模块
    apiDelete(index, row) {
      this.$confirm('确定要删除吗?', '信息', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          let parameter = {
            id: row.id,
            seq: row.seq,
            apiModule_id: row.apiModule_id
          };
          deleteApi(parameter)
            .then(res => {
              if (res.success) {
                this.$message({
                  type: 'success',
                  message: res.msg
                });
                this.getdata(this.formInline)
              } else {
                this.$message({
                  type: 'info',
                  message: res.msg
                })
              }
            })
            .catch(err => {
              console.log(err);
              this.loading = false;
              this.$message.error('项目删除失败，请稍后再试！')
            })
        })
        .catch((err) => {
          console.log(err)
        })
    },
    // 删除环境变量
    EnvironmentVariableDelete(index, row) {
      this.$confirm('确定要删除吗?', '信息', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          let parameter = {
            id: row.id
          };
          deleteEnvironmentVariable(parameter)
            .then(res => {
              if (res.success) {
                this.$message({
                  type: 'success',
                  message: res.msg
                });
                this.handleEnvironmentVariable()
              } else {
                this.$message({
                  type: 'info',
                  message: res.msg
                })
              }
            })
            .catch(err => {
              console.log(err);
              this.loading = false;
              this.$message.error('项目删除失败，请稍后再试！')
            })
        })
        .catch((err) => {
          console.log(err)
        })
    },
    // 跳转测试用例管理页面
    toTestCase(row){
      // // 将搜索条件存入cookie
      this.$router.push({
        path: '/apiTest/apiManagement/apiTestCase',
        query: {
          api_id: row.id
        }
      })
    },
    // 获取所有项目信息
    loadAllProject(){
      getAllProject().then(
        res => {
          this.projects = res;
        }
      )
    },
    querySearchAsync1(queryString, cb) {
      var projects = this.projects;
      var results = queryString ? projects.filter(this.createStateFilter(queryString)) : projects;

      cb(results);
    },
    createStateFilter(queryString) {
      return (state) => {
        return (state.value.toLowerCase().indexOf(queryString.toLowerCase()) === 0);
      };
    },
    handleSelect1(item) {
      this.options = '';
      this.value = '';
      this.loadAllProjectEnvironment(item);
      this.formInline.module_id = '';
      this.formInline.module_name = '';
    },
    inputEvent(){
      if(this.formInline.module_name === ''){
        this.formInline.module_id = '';
        this.editForm.module_id = '';
        this.editForm.module_name = '';
      }
    },
    // 选择项目名称后，获取项目环境名称
    loadAllProjectEnvironment(item){
      var params = {
        name: item.value
      };
      getAllProjectEnvironment(params).then(
        res => {
          this.options = res;
        }
      )
    },
    // 选择项目环境名称后，获取api模块列表
    handleChange(val){
      this.formInline.module_name = '';
      this.formInline.module_id = '';
      this.formInline.projectEnvironment_id = val;
    },
    //項目名稱修改后清空環境選擇
    inputChange(){
      this.formInline.projectEnvironment_id = '';
      this.formInline.projectEnvironment_name = '';
      this.options = '';
      this.value = '';
      this.formInline.module_id = '';
      this.formInline.module_name = '';
    },
    m_handleChange(val){
      this.editForm.module_id = val;
    },
    //上移
    upLayer(index, row){
      let that = this;
      if (index === 0) {
        that.$message({
          message: "处于顶端，不能继续上移",
          type: "warning"
        });
      } else {
        let params = {
          apiModule_id: row.apiModule_id,
          seq: row.seq,
          form_apiModule_name: this.formInline.module_name
        };
        upApi(params)
          .then(res => {
            if (res.success === false) {
              this.$message({
                type: 'info',
                message: res.msg
              })
          } else {
              this.getdata(this.formInline);
              let upDate = that.listData[index - 1];
              that.listData.splice(index - 1, 1);
              that.listData.splice(index, 0, upDate);
          }
          });
      }
    },
    //下移
    downLayer(index, row){
      let that = this;
      if (index + 1 === that.listData.length) {
        that.$message({
          message: "处于末端端，不能继续下移",
          type: "warning"
        });
      } else {
        let params = {
          apiModule_id: row.apiModule_id,
          seq: row.seq,
          form_apiModule_name: this.formInline.module_name
        };
        downApi(params)
          .then(res => {
            if (res.success === false) {
              this.$message({
                type: 'info',
                message: res.msg
              })
          } else {
              this.getdata(this.formInline);
              let downDate = that.listData[index + 1];
              that.listData.splice(index + 1, 1);
              that.listData.splice(index, 0, downDate);
          }
        });
      }
    },
    //变更状态
    changeStatus(index, row){
      let params = {
        id: row.id,
        status: row.status
      };
      changeApiStatus(params)
        .then(res => {
          if (res.success === false) {
            this.$message({
              type: 'info',
              message: res.msg
            })
          }
        })
    },
    closeEnvironmentVariableDialog(){
      this.environmentVariableVisible = false;
    },
    filterNode(value, data) {
      if (!value) return true;
      return data.module_name.indexOf(value) !== -1;
    },
    handleNodeClick(data) {
      console.log(data);
      this.formInline.module_id = data.id;
      this.formInline.module_name = data.module_name;
      this.current_module_id = data.id;
      this.getdata(this.formInline);
    },
  }
}
</script>

<style scoped>
.user-search {
  margin-top: 20px;
}
.userRole {
  width: 100%;
}
/deep/ textarea {
  font-family: "Helvetica Neue",Helvetica,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","微软雅黑",Arial,sans-serif !important;
}
.add-table {
  height: 50px;
  line-height: 50px;
  border-left: 1px solid #EBEEF5;
  border-right: 1px solid #EBEEF5;
  border-bottom: 1px solid #EBEEF5;
  color: dodgerblue;
}
</style>

<template>
    <div>
      <!-- 面包屑导航 -->
      <el-breadcrumb separator-class="el-icon-arrow-right">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>模块管理</el-breadcrumb-item>
      </el-breadcrumb>
      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="formInline" class="user-search">
        <el-form-item label="项目名称：">
          <el-autocomplete size="small" v-model="formInline.projectName" placeholder="输入项目名称" @select="handleSelect" :fetch-suggestions="querySearchAsync" @input="inputChange"></el-autocomplete>
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
        <el-form-item>
          <el-button size="small" type="primary" icon="el-icon-search" @click="search">搜索</el-button>
          <el-button size="small" type="primary" icon="el-icon-plus" @click="handleEdit()">添加</el-button>
        </el-form-item>
      </el-form>
      <!--列表-->
      <el-table size="small" :data="listData" highlight-current-row v-loading="loading" border element-loading-text="拼命加载中" style="width: 100%;">
        <el-table-column align="center" type="selection" width="60">
        </el-table-column>
        <el-table-column prop="id" label="模块id" v-if=false>
        </el-table-column>
        <el-table-column prop="projectEnvironment_id" label="项目环境id" v-if=false>
        </el-table-column>
        <el-table-column sortable prop="module_name" label="模块名称" width="300">
        </el-table-column>
        <el-table-column sortable prop="module_description" label="模块描述" width="300">
        </el-table-column>
        <el-table-column sortable prop="create_time" label="创建时间" width="300">
        </el-table-column>
        <el-table-column align="center" label="操作" min-width="300" fixed="right">
          <template slot-scope="scope">
            <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
            <el-button size="mini" type="danger" @click="apiModuleDelete(scope.$index, scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 分页组件 -->
      <Pagination v-bind:child-msg="pageparm" @callFather="callFather"></Pagination>
      <!-- 编辑界面 -->
      <el-dialog :title="title" :visible.sync="editFormVisible" width="30%" @click="closeDialog">
        <el-form label-width="120px" :model="editForm" :rules="rules" ref="editForm">
          <el-form-item label="环境名称" prop="e_name">
            <el-input size="small" v-model="editForm.e_name" auto-complete="off" placeholder="请输入环境名称" :disabled=disabled></el-input>
          </el-form-item>
          <el-form-item label="模块名称" prop="m_name">
            <el-input size="small" v-model="editForm.m_name" auto-complete="off" placeholder="请输入模块名称"></el-input>
          </el-form-item>
          <el-form-item label="模块描述" prop="m_description">
            <el-input type="textarea" size="small" v-model="editForm.m_description" auto-complete="off" placeholder="请输入模块描述"></el-input>
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="closeDialog">取消</el-button>
          <el-button size="small" type="primary" :loading="loading" class="title" @click="submitForm('editForm')">保存</el-button>
        </div>
      </el-dialog>
    </div>
</template>

<script>
import { getAllProject, getAllProjectEnvironment } from '../../api/projectApi'
import { apiModuleList, saveApiModule, deleteApiModule } from '../../api/apiTestApi'
import Pagination from '../../components/Pagination'
export default {
  data() {
    return {
      nshow: true, //switch开启
      fshow: false, //switch关闭
      loading: false, //是显示加载
      editFormVisible: false, //控制编辑页面显示与隐藏
      title: '添加',
      disabled: false,
      editForm: {
        id: '',
        e_id: '',
        e_name: '',
        m_name: '',
        m_description: '',
        create_time: ''
      },
      // rules表单验证
      rules: {
        e_name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }],
        m_name: [{ required: true, message: '请输入模塊名称', trigger: 'blur' }],
        m_description: [{ required: true, message: '请输入模塊描述', trigger: 'blur' }]
      },
      projects: '',
      state: '',
      formInline: {
        page: 1,
        limit: 10,
        varLable: '',
        varName: '',
        projectName:'',
        projectEnvironment_id: '',
        projectEnvironment_name: '',
        token: localStorage.getItem('logintoken')
      },
      // 删除项目
      seletedata: {
        ids: '',
        token: localStorage.getItem('logintoken')
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
      // 下拉框选项
      options: '',
      value: ''
    }
  },
  // 注册组件
  components: {
    Pagination
  },
  /**
   * 数据发生改变
   */

  /**
   * 创建完毕
   */
  created() {
    this.loadAllProject();
  },
  // mounted(){
  //   this.projects = this.getAllProject;
  // },

  /**
   * 里面的方法只有被调用才会执行
   */
  methods: {
    // 获取功能模块列表
    getdata(parameter) {
      this.loading = true;
      this.pageparm.currentPage = this.formInline.page;
      this.pageparm.pageSize = this.formInline.limit;
      parameter = {
        currentPage: this.pageparm.currentPage,
        pageSize: this.pageparm.pageSize,
        projectEnvironment_id : this.formInline.projectEnvironment_id
      };
      /***
       * 调用接口，注释上面模拟数据 取消下面注释
       */
      apiModuleList(parameter)
        .then(res => {
          this.loading = false;
          if (res.success === false) {
            this.$message({
              type: 'info',
              message: res.msg
            })
          } else {
            this.listData = res.data;
            // 分页赋值
            // this.pageparm.currentPage = this.formInline.page;
            // this.pageparm.pageSize = this.formInline.limit;
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
      if(this. pageparm.pageSize !== parm.pageSize){
        this.formInline.page = 1;
        this.formInline.limit = parm.pageSize;
        this.getdata(this.formInline)
      }else {
        this.formInline.page = parm.currentPage;
        this.formInline.limit = parm.pageSize;
        this.getdata(this.formInline)
      }
    },
    // 搜索事件
    search() {
      this.formInline.page = 1;
      this.getdata(this.formInline)
    },
    //显示编辑界面
    handleEdit: function(index, row) {
      this.editFormVisible = true;
      if (row != undefined && row != 'undefined') {
        this.title = '修改';
        this.disabled = true;
        this.editForm.id = row.id;
        this.editForm.e_id = this.formInline.projectEnvironment_id;
        this.editForm.e_name = this.formInline.projectEnvironment_name;
        this.editForm.m_name = row.module_name;
        this.editForm.m_description = row.module_description;
      } else {
        this.title = '添加';
        this.disabled = true;
        this.editForm.id = '';
        this.editForm.e_id = this.formInline.projectEnvironment_id;
        this.editForm.e_name = this.formInline.projectEnvironment_name;
        this.editForm.m_name = '';
        this.editForm.m_description = '';
      }
    },
    // 关闭编辑、增加弹出框
    closeDialog() {
      this.editFormVisible = false
    },
    // 编辑、增加页面保存方法
    submitForm(editData) {
      this.$refs[editData].validate(valid => {
        if (valid) {
          saveApiModule(this.editForm)
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
          return false
        }
      })
    },
    // 删除api模块
    apiModuleDelete(index, row) {
      this.$confirm('确定要删除吗?', '信息', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          let parameter = {
            id: row.id
          };
          deleteApiModule(parameter)
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
    // 获取所有项目信息
    loadAllProject(){
      getAllProject().then(
        res => {
          this.projects = res;
        }
      )
    },
    querySearchAsync(queryString, cb) {
      var projects = this.projects;
      var results = queryString ? projects.filter(this.createStateFilter(queryString)) : projects;

      cb(results);
    },
    createStateFilter(queryString) {
      return (state) => {
        return (state.value.toLowerCase().indexOf(queryString.toLowerCase()) === 0);
      };
    },
    handleSelect(item) {
      this.loadAllProjectEnvironment(item);
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
      this.formInline.projectEnvironment_id = val;
      let obj = {};
      obj = this.options.find((item) => {
        return item.value === val;
      });
      if(obj !== undefined){
        this.formInline.projectEnvironment_name = obj.label;
      }
      this.getdata(this.formInline);
    },
    //項目名稱修改后清空環境選擇
    inputChange(){
      this.formInline.projectEnvironment_id = '';
      this.formInline.projectEnvironment_name = '';
      this.options = '';
      this.value = '';
    }
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
</style>

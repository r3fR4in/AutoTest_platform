/**
 * 项目管理
 */
<template>
  <div>
    <!-- 面包屑导航 -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>项目管理</el-breadcrumb-item>
    </el-breadcrumb>
    <!-- 搜索筛选 -->
    <el-form :inline="true" :model="formInline" class="user-search">
      <el-form-item label="搜索：">
        <el-input size="small" v-model="formInline.projectName" placeholder="输入项目名称"></el-input>
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
      <el-table-column prop="id" label="项目id" v-if=false>
      </el-table-column>
      <el-table-column sortable prop="projectName" label="项目名称" width="300">
      </el-table-column>
      <el-table-column sortable prop="projectDescription" label="项目描述" width="300">
      </el-table-column>
      <el-table-column sortable prop="create_time" label="创建时间" width="300">
        <!--<template slot-scope="scope">-->
          <!--<div>{{scope.row.editTime|timestampToTime}}</div>-->
        <!--</template>-->
      </el-table-column>
      <el-table-column align="center" label="操作" min-width="300">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="projectDelete(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页组件 -->
    <Pagination v-bind:child-msg="pageparm" @callFather="callFather"></Pagination>
    <!-- 编辑界面 -->
    <el-dialog :title="title" :visible.sync="editFormVisible" width="30%" @click="closeDialog">
      <el-form label-width="120px" :model="editForm" :rules="rules" ref="editForm">
        <el-form-item label="项目名称" prop="projectName">
          <el-input size="small" v-model="editForm.projectName" auto-complete="off" placeholder="请输入项目名称"></el-input>
        </el-form-item>
        <el-form-item label="项目描述" prop="projectDescription">
          <el-input type="textarea" size="small" v-model="editForm.projectDescription" auto-complete="off" placeholder="请输入项目描述"></el-input>
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
import { projectList, addProject, editProject, deleteProject } from '../../api/projectApi'
import Pagination from '../../components/Pagination'
export default {
  data() {
    return {
      nshow: true, //switch开启
      fshow: false, //switch关闭
      loading: false, //是显示加载
      editFormVisible: false, //控制编辑页面显示与隐藏
      title: '添加',
      editForm: {
        id: '',
        projectName: '',
        projectDescription: ''
      },
      // rules表单验证
      rules: {
        projectName: [
          { required: true, message: '请输入项目名称', trigger: 'blur' }
        ],
        projectDescription: [{ required: true, message: '请输入项目描述', trigger: 'blur' }]
      },
      formInline: {
        page: 1,
        limit: 10,
        varLable: '',
        varName: '',
        projectName: '',
        token: localStorage.getItem('logintoken')
      },
      // 删除项目
      seletedata: {
        ids: '',
        token: localStorage.getItem('logintoken')
      },
      userparm: [], //搜索权限
      listData: [], //项目数据
      // 分页参数
      pageparm: {
        currentPage: 1,
        pageSize: 10,
        oldPageSize: 10,
        total: 10
      }
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
    this.getdata(this.formInline)
  },

  /**
   * 里面的方法只有被调用才会执行
   */
  methods: {
    // 获取项目列表
    getdata(parameter) {
      this.loading = true;
      this.pageparm.currentPage = this.formInline.page;
      this.pageparm.pageSize = this.formInline.limit;
      parameter = {
        currentPage: this.pageparm.currentPage,
        pageSize: this.pageparm.pageSize,
        projectName : this.formInline.projectName
      };
      // // 模拟数据开始
      // let res = {
      //   code: 0,
      //   msg: null,
      //   count: 5,
      //   data: [
      //     {
      //       addUser: null,
      //       editUser: null,
      //       addTime: 1521062371000,
      //       editTime: 1526700200000,
      //       projectId: 2,
      //       name: 'XX分公司',
      //       projectDecription: '1',
      //       parentId: 1
      //     },
      //     {
      //       addUser: null,
      //       editUser: null,
      //       addTime: 1521063247000,
      //       editTime: 1526652291000,
      //       projectId: 3,
      //       name: '上海测试',
      //       projectDecription: '02',
      //       parentId: 1
      //     },
      //     {
      //       addUser: null,
      //       editUser: null,
      //       addTime: 1526349555000,
      //       editTime: 1526349565000,
      //       projectId: 12,
      //       name: '1',
      //       projectDecription: '11',
      //       parentId: 1
      //     },
      //     {
      //       addUser: null,
      //       editUser: null,
      //       addTime: 1526373178000,
      //       editTime: 1526373178000,
      //       projectId: 13,
      //       name: '5',
      //       projectDecription: '5',
      //       parentId: 1
      //     },
      //     {
      //       addUser: null,
      //       editUser: null,
      //       addTime: 1526453107000,
      //       editTime: 1526453107000,
      //       projectId: 17,
      //       name: 'v',
      //       projectDecription: 'v',
      //       parentId: 1
      //     }
      //   ]
      // }
      // this.loading = false
      // this.listData = res.data
      // this.pageparm.currentPage = this.formInline.page
      // this.pageparm.pageSize = this.formInline.limit
      // this.pageparm.total = res.count
      // 模拟数据结束

      /***
       * 调用接口，注释上面模拟数据 取消下面注释
       */
      projectList(parameter)
        .then(res => {
          this.loading = false;
          if (res.success == false) {
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
    // 关闭编辑、增加弹出框
    closeDialog() {
      this.editFormVisible = false
    },
    //显示编辑界面
    handleEdit: function(index, row) {
      this.editFormVisible = true;
      if (row != undefined && row != 'undefined') {
        this.title = '修改';
        this.editForm.id = row.id;
        this.editForm.projectName = row.projectName;
        this.editForm.projectDescription = row.projectDescription
      } else {
        this.title = '添加';
        this.editForm.id = '';
        this.editForm.projectName = '';
        this.editForm.projectDescription = ''
      }
    },
    // 编辑、增加页面保存方法
    submitForm(editData) {
      this.$refs[editData].validate(valid => {
        if (valid) {
          if (this.editForm.id === '') {
            let param = this.editForm;
            delete param['id'];
            addProject(param)
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
            editProject(param)
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
    // 删除项目
    projectDelete(index, row) {
      this.$confirm('确定要删除吗?', '信息', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          let parameter = {
            id: row.id
          };
          deleteProject(parameter)
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
              this.loading = false;
              this.$message.error('项目删除失败，请稍后再试！')
            })
        })
        .catch((err) => {
          console.log(err)
        })
    },
    // 关闭编辑、增加弹出框
    closeDialog1() {
      this.editFormVisible = false
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



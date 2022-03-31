/**
 * 系统管理 用户管理
 */
<template>
  <div>
    <!-- 面包屑导航 -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>用户管理</el-breadcrumb-item>
    </el-breadcrumb>
    <!-- 搜索筛选 -->
    <el-form :inline="true" :model="formInline" class="user-search">
      <el-form-item label="搜索：">
      </el-form-item>
      <el-form-item label="">
        <el-input size="small" v-model="formInline.nickname" placeholder="输入姓名"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button size="small" type="primary" icon="el-icon-search" @click="search">搜索</el-button>
        <el-button size="small" type="primary" icon="el-icon-plus" @click="handleEdit()">添加</el-button>
      </el-form-item>
    </el-form>
    <!--列表-->
    <el-table size="small" :data="userData" highlight-current-row v-loading="loading" border element-loading-text="拼命加载中" style="width: 100%;">
      <el-table-column prop="id" label="用户id" v-if=false>
      </el-table-column>
      <el-table-column prop="role" label="用户权限" v-if=false>
      </el-table-column>
      <el-table-column align="center" sortable prop="username" label="用户名" width="200">
      </el-table-column>
      <el-table-column align="center" sortable prop="nickname" label="姓名" width="200">
      </el-table-column>
      <el-table-column align="center" sortable prop="phone" label="手机号" width="200">
      </el-table-column>
      <el-table-column align="center" sortable prop="email" label="邮箱" min-width="120">
      </el-table-column>
      <el-table-column align="center" sortable prop="status" label="状态" min-width="50">
        <template slot-scope="scope">
          <el-switch v-model="scope.row.status=='1'?nshow:fshow" active-color="#13ce66" inactive-color="#ff4949" @change="editStatus(scope.$index, scope.row)">
          </el-switch>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="150">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button size="mini" @click="getProjectPermissionList(scope.$index, scope.row)" v-if="scope.row.role === 'dev_role'">权限配置</el-button>
          <el-button size="mini" type="success" @click="resetpwd(scope.$index, scope.row)">重置密码</el-button>
          <el-button size="mini" type="danger" @click="deleteUser(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页组件 -->
    <Pagination v-bind:child-msg="pageparm" @callFather="callFather"></Pagination>
    <!-- 编辑界面 -->
    <el-dialog :title="title" :visible.sync="editFormVisible" width="30%" @click='closeDialog()'>
      <el-form label-width="80px" ref="editForm" :model="editForm" :rules="rules">
        <el-form-item label="用户名" prop="username">
          <el-input size="small" v-model="editForm.username" auto-complete="off" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="姓名" prop="nickname">
          <el-input size="small" v-model="editForm.nickname" auto-complete="off" placeholder="请输入姓名"></el-input>
        </el-form-item>
        <el-form-item label="角色" prop="role_code">
          <el-select v-model="editForm.role_code" size="small" placeholder="请选择">
              <el-option
                v-for="item in role_option"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
        </el-form-item>
        <el-form-item label="手机号" prop="userMobile">
          <el-input size="small" v-model="editForm.phone" placeholder="请输入手机号"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="userEmail">
          <el-input size="small" v-model="editForm.email" placeholder="请输入邮箱地址"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button size="small" @click='closeDialog()'>取消</el-button>
        <el-button size="small" type="primary" :loading="loading" class="title" @click="submitForm('editForm')">保存</el-button>
      </div>
    </el-dialog>
    <!-- 权限配置界面 -->
    <el-dialog title="权限配置" :visible.sync="projectPermissionVisible" width="30%" @click='closeDialog()'>
      <el-table size="small"
                ref="projectPermissionTable"
                :data="projectPermissionData"
                highlight-current-row v-loading="loading"
                border element-loading-text="拼命加载中"
                @selection-change="(selection)=>{handleSelectChange(selection)}"
                style="width: 100%;">
        <el-table-column align="center" type="selection" width="50">
        </el-table-column>
        <el-table-column prop="project_id" label="项目id" v-if=false>
        </el-table-column>
        <el-table-column align="center" sortable prop="projectName" label="项目名称">
        </el-table-column>
      </el-table>
      <div slot="footer" class="dialog-footer">
        <el-button size="small" type="primary" @click='projectPermissionsSave()'>保存</el-button>
        <el-button size="small" @click='closeDialog()'>取消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// 导入请求方法
import {
  userList,
  getRoleCode,
  userSave,
  userDelete,
  resetPwd,
  changeUserStatus,
  projectPermissionsList,
  projectPermissionsSave
} from '../../api/userMG'
import Pagination from '../../components/Pagination'
export default {
  data() {
    return {
      nshow: true, //switch开启
      fshow: false, //switch关闭
      loading: false, //是显示加载
      title: '添加用户',
      editFormVisible: false, //控制编辑页面显示与隐藏
      projectPermissionVisible: false, //控制权限配置页面显示与隐藏
      current_user_id: '',
      projectPermissionSelection: '',
      // 编辑与添加
      editForm: {
        id: '',
        username: '',
        nickname: '',
        role_code: '',
        phone: '',
        email: '',
        token: localStorage.getItem('logintoken')
      },
      // 角色下拉选项
      role_option: '',
      // rules表单验证
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        nickname: [
          { required: true, message: '请输入姓名', trigger: 'blur' }
        ],
        role_code: [{ required: true, message: '请选择角色', trigger: 'blur' }],
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          {
            pattern: /^1(3\d|47|5((?!4)\d)|7(0|1|[6-8])|8\d)\d{8,8}$/,
            required: true,
            message: '请输入正确的手机号',
            trigger: 'blur'
          }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          {
            pattern: /^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/,
            required: true,
            message: '请输入正确的邮箱',
            trigger: 'blur'
          }
        ]
      },
      // 删除用户
      seletedata: {
        ids: '',
        token: localStorage.getItem('logintoken')
      },
      // 请求数据参数
      formInline: {
        page: 1,
        limit: 10,
        nickname: '',
        isLock: ''
      },
      //用户数据
      userData: [],
      //项目权限数据
      projectPermissionData: [],
      // 分页参数
      pageparm: {
        currentPage: 1,
        pageSize: 10,
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
  watch: {},

  /**
   * 创建完毕
   */
  created() {
    this.getdata(this.formInline);
    this.getRoleCode();
  },

  /**
   * 里面的方法只有被调用才会执行
   */
  methods: {
    // 获取数据方法
    getdata(parameter) {
      /***
       * 调用接口，注释上面模拟数据 取消下面注释
       */
      this.loading = true;
      this.pageparm.currentPage = this.formInline.page;
      this.pageparm.pageSize = this.formInline.limit;
      parameter = {
        currentPage: this.pageparm.currentPage,
        pageSize: this.pageparm.pageSize,
        nickname : this.formInline.nickname
      };
      // 获取用户列表
      userList(parameter).then(res => {
        this.loading = false;
        if (res.success === false) {
          this.$message({
            type: 'info',
            message: res.msg
          })
        } else {
          this.userData = res.data;
          // 分页赋值
          this.pageparm.currentPage = this.formInline.page;
          this.pageparm.pageSize = this.formInline.limit;
          this.pageparm.total = res.count;
        }
      })
    },
    // 分页插件事件
    callFather(param) {
      this.formInline.page = param.currentPage;
      this.formInline.limit = param.pageSize;
      this.getdata(this.formInline);
    },
    //搜索事件
    search() {
      this.getdata(this.formInline)
    },
    // 获取角色权限code
    getRoleCode(){
      getRoleCode().then(res => {
        this.role_option = res.data;
      })
    },
    // 关闭编辑、增加弹出框
    closeDialog() {
      this.editFormVisible = false;
      this.projectPermissionVisible = false;
    },
    // 修改状态
    editStatus: function(index, row) {
      this.loading = true;
      let param = {
        status: '',
        id: '',
      };
      param.id = row.id;
      let status = row.status;
      if (status === 2) {
        param.status = '1'
      } else {
        param.status = '2'
      }
      // 修改状态
      changeUserStatus(param).then(res => {
        this.loading = false;
        if (res.success === false) {
          this.$message({
            type: 'info',
            message: res.msg
          })
        } else {
          this.$message({
            type: 'success',
            message: '状态修改成功'
          });
          this.getdata(this.formInline)
        }
      })
    },
    //显示编辑界面
    handleEdit: function(index, row) {
      this.editFormVisible = true;
      if (row !== undefined && row !== 'undefined') {
        this.title = '修改用户';
        this.editForm.id = row.id;
        this.editForm.username = row.username;
        this.editForm.nickname = row.nickname;
        this.editForm.role_code = row.role;
        this.editForm.phone = row.phone;
        this.editForm.email = row.email;
      } else {
        this.title = '添加用户';
        this.editForm.id = '';
        this.editForm.username = '';
        this.editForm.nickname = '';
        this.editForm.role_code = '';
        this.editForm.phone = '';
        this.editForm.email = '';
      }
    },
    // 编辑、添加提交方法
    submitForm(editData) {
      this.$refs[editData].validate(valid => {
        if (valid) {
          // 请求方法
          userSave(this.editForm)
            .then(res => {
              this.editFormVisible = false;
              this.loading = false;
              if (res.success) {
                this.getdata(this.formInline);
                this.$message({
                  type: 'success',
                  message: '保存成功！'
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
              this.$message.error('保存失败，请稍后再试！')
            })
        } else {
          return false
        }
      })
    },
    // 删除用户
    deleteUser(index, row) {
      this.$confirm('确定要删除吗?', '信息', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          let parameter = {
            id: row.id
          };
          // 删除
          userDelete(parameter)
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
              this.$message.error('数据删除失败，请稍后再试！');
            })
        })
        .catch(() => {
          this.$message({
            type: 'info',
            message: '已取消删除！'
          })
        })
    },
    //显示项目权限界面
    getProjectPermissionList: function(index, row) {
      this.projectPermissionVisible = true;
      this.current_user_id = row.id;
      let param = {
        id: this.current_user_id
      };
      projectPermissionsList(param).then(res => {
          this.loading = false;
          if (res.success === false) {
            this.$message({
              type: 'info',
              message: res.msg
            })
          } else {
            this.projectPermissionData = res.data;
            this.toggleSelection();
          }
        })
        .catch(err => {
          this.loading = false;
          console.log(err);
          this.$message.error('数据获取失败')
        });
    },
    toggleSelection(){
      this.$nextTick(() => {
        this.projectPermissionData.forEach(item => {
          if(item.user_id != null){
            this.$refs.projectPermissionTable.toggleRowSelection(item, true);
          }
        })
      });
    },
    // 表格选择事件
    handleSelectChange(selection){
      this.projectPermissionSelection = selection;
    },
    // 保存项目权限
    projectPermissionsSave(){
      this.projectPermissionSelection.forEach(item => {
        delete item.user_id;
      });
      let param = {
        id: this.current_user_id,
        list: this.projectPermissionSelection
      };
      projectPermissionsSave(param).then(res => {
          this.loading = false;
          if (res.success === false) {
            this.$message({
              type: 'info',
              message: res.msg
            })
          } else {
            this.projectPermissionVisible = false;
            this.$message({
              type: 'success',
              message: '保存成功！'
            })
          }
        })
        .catch(err => {
          this.loading = false;
          console.log(err);
          this.$message.error('保存失败')
        });
    },
    // 重置密码
    resetpwd(index, row) {
      this.$confirm('确定要重置密码吗?', '信息', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          let param = {
            id: row.id
          };
          resetPwd(param)
            .then(res => {
              if (res.success) {
                this.$message({
                  type: 'success',
                  message: '重置密码成功！'
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
              this.$message.error('重置密码失败，请稍后再试！')
            })
        })
        .catch(() => {
          this.$message({
            type: 'info',
            message: '取消重置密码！'
          })
        })
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
</style>


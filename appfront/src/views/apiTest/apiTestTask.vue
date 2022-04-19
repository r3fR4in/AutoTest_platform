<template>
  <div>
    <!-- 面包屑导航 -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>测试任务</el-breadcrumb-item>
    </el-breadcrumb>
    <!-- 搜索筛选 -->
    <el-form :inline="true" :model="formInline" class="user-search">
      <el-form-item label="所属项目：">
        <el-autocomplete size="small" v-model="formInline.projectName" placeholder="输入项目名称" @select="handleSelect1" :fetch-suggestions="querySearchAsync1"></el-autocomplete>
      </el-form-item>
      <el-form-item label="标题：">
        <el-input size="small" v-model="formInline.title" placeholder="输入标题"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button size="small" type="primary" icon="el-icon-search" @click="search">搜索</el-button>
        <el-button size="small" type="primary" icon="el-icon-plus" @click="handleAdd()">添加任务</el-button>
      </el-form-item>
    </el-form>
    <!--列表-->
    <el-table size="small" :data="taskData" highlight-current-row v-loading="loading" border element-loading-text="拼命加载中" style="width: 100%;">
      <!--<el-table-column align="center" type="selection" width="60">-->
      <!--</el-table-column>-->
      <el-table-column prop="id" label="任务id" v-if=false>
      </el-table-column>
      <el-table-column sortable prop="title" label="任务标题" width="300">
      </el-table-column>
      <el-table-column prop="projectId" label="项目id" v-if=false>
      </el-table-column>
      <el-table-column sortable prop="projectName" label="所属项目" width="300">
      </el-table-column>
      <el-table-column sortable prop="summary" label="任务描述" width="300">
      </el-table-column>
      <el-table-column sortable prop="create_time" label="创建时间" width="300">
      </el-table-column>
      <el-table-column sortable prop="status" label="状态" width="80" align="center">
        <template scope="scope">
          <p v-if="scope.row.status===0">待执行</p>
          <p v-if="scope.row.status===1">执行中</p>
          <p v-if="scope.row.status===2">执行完成</p>
          <p v-if="scope.row.status===3">执行失败</p>
        </template>
      </el-table-column>
      <el-table-column align="center" label="操作" min-width="300">
        <template slot-scope="scope">
          <el-button size="mini" @click="toTestReport(scope.row)">测试报告</el-button>
          <el-button size="mini" type="danger" @click="apiTestTaskDelete(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页组件 -->
    <Pagination v-bind:child-msg="pageparm" @callFather="callFather"></Pagination>
    <!-- 添加界面1 -->
    <el-dialog :title="title" :visible.sync="addFormVisible1" width="40%" @click="closeDialog1">
      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="a_formInline" class="user-search">
        <el-form-item label="项目名称：">
          <el-autocomplete size="small" v-model="a_formInline.projectName" placeholder="输入项目名称" @select="handleSelect1" :fetch-suggestions="querySearchAsync1"></el-autocomplete>
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
          <el-button size="small" type="primary" icon="el-icon-search" @click="a_search">搜索</el-button>
        </el-form-item>
      </el-form>
      <!--列表-->
      <el-table size="small" :data="listData" highlight-current-row v-loading="loading" border element-loading-text="拼命加载中" max-height="400"
                style="width: 100%;" @selection-change="handleSelectionChange" ref="moduleTable">
        <el-table-column align="center" type="selection" width="60">
        </el-table-column>
        <el-table-column prop="id" label="模块id" v-if=false>
        </el-table-column>
        <el-table-column prop="projectEnvironment_id" label="项目环境id" v-if=false>
        </el-table-column>
        <el-table-column sortable prop="module_name" label="模块名称" width="300">
        </el-table-column>
        <el-table-column sortable prop="module_description" label="模块描述">
        </el-table-column>
      </el-table>
      <div slot="footer" class="dialog-footer" align="center">
          <el-button size="small" @click="closeDialog1">取消</el-button>
          <el-button size="small" type="primary" :loading="loading" class="title" @click="submit1">确定</el-button>
        </div>
    </el-dialog>
    <!-- 添加界面2 -->
    <el-dialog :title="title" :visible.sync="addFormVisible2" width="30%" @click="closeDialog2">
      <el-form label-width="120px" :model="a_formInline" :rules="rules" ref="a_formInline">
        <el-form-item label="任务标题" prop="title">
          <el-input size="small" v-model="a_formInline.title" auto-complete="off" placeholder="请输入任务标题"></el-input>
        </el-form-item>
        <el-form-item label="任务描述" prop="summary">
          <el-input size="small" v-model="a_formInline.summary" auto-complete="off" placeholder="请输入任务描述"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button size="small" @click="closeDialog2">取消</el-button>
        <el-button size="small" type="primary" :loading="loading" class="title" @click="submit2('a_formInline')">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
    import { apiTestTaskList, apiModuleList, addApiTestTask, deleteApiTestTask } from '../../api/apiTestApi'
    import { getAllProject, projectModuleList, getAllProjectEnvironment } from '../../api/projectApi'
    import Pagination from '../../components/Pagination'

    export default {
      data() {
        return {
          nshow: true, //switch开启
          fshow: false, //switch关闭
          loading: false, //是显示加载
          addFormVisible1: false, //控制添加页面显示与隐藏
          addFormVisible2: false, //控制添加页面显示与隐藏
          title: '添加',
          addForm: {
            token: localStorage.getItem('logintoken')
          },
          projects: '',
          formInline: {
            page: 1,
            limit: 10,
            varLable: '',
            varName: '',
            projectName:'',
            title: '',
            token: localStorage.getItem('logintoken')
          },
          a_formInline: {
            projectName:'',
            projectEnvironment_id: '',
            projectEnvironment_name: '',
            title: '',
            summary: '',
            moduleSelection: [], //选择的模块
            token: localStorage.getItem('logintoken')
          },
          // rules表单验证
          rules: {
            title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }]
          },
          // 分页参数
          pageparm: {
            currentPage: 1,
            pageSize: 10,
            oldPageSize: 10,
            total: 10
          },
          taskData: [], //任务数据
          listData: [], //模块数据
          // 下拉框选项
          options: '',
          value: ''
        }
      },
      // 注册组件
      components: {
        Pagination
      },
      created() {
        this.getdata(this.formInline);
        this.loadAllProject();
      },
      methods: {
        // 获取测试任务列表
        getdata(parameter) {
          this.loading = true;
          this.pageparm.currentPage = this.formInline.page;
          this.pageparm.pageSize = this.formInline.limit;
          parameter = {
            currentPage: this.pageparm.currentPage,
            pageSize: this.pageparm.pageSize,
            projectName : this.formInline.projectName,
            title : this.formInline.title
          };
          apiTestTaskList(parameter)
            .then(res => {
              this.loading = false;
              if (res.success === false) {
                this.$message({
                  type: 'info',
                  message: res.msg
                })
              } else {
                this.taskData = res.data;
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
        // 获取功能模块列表
        getModuledata(parameter) {
          this.loading = true;
          parameter = {
            projectEnvironment_id : this.a_formInline.projectEnvironment_id
          };
          /***
          * 调用接口，注释上面模拟数据 取消下面注释
          */
          projectModuleList(parameter)
            .then(res => {
              this.loading = false;
              if (res.success === false) {
                this.$message({
                  type: 'info',
                  message: res.msg
                })
              } else {
                this.listData = res.data;
              }
            })
            .catch(err => {
              this.loading = false;
              console.log(err);
              this.$message.error('菜单加载失败，请稍后再试！')
            })
        },
        handleSelect1(item) {
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
        // 获取所有项目信息
        loadAllProject(){
          getAllProject().then(
            res => {
              this.projects = res;
            }
          )
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
        // 搜索事件
        search() {
          this.formInline.page = 1;
          this.getdata(this.formInline)
        },
        a_search() {
          this.getModuledata(this.a_formInline);
        },
        // 选择项目环境名称后，获取api模块列表
        handleChange(val){
          this.a_formInline.projectEnvironment_id = val;
          let obj = {};
          obj = this.options.find((item) => {
            return item.value === val;
          });
          this.a_formInline.projectEnvironment_name = obj.label;
          this.getModuledata(this.a_formInline);
        },
        //显示编辑界面
        handleAdd: function(index, row) {
          this.addFormVisible1 = true;
          this.title = '添加任务';
        },
        // 关闭添加弹出框
        closeDialog1() {
          this.addFormVisible1 = false;
          this.$refs.moduleTable.clearSelection();
        },
        // 关闭添加弹出框
        closeDialog2() {
          this.addFormVisible2 = false;
        },
        // 选择模块
        handleSelectionChange(val) {
          this.a_formInline.moduleSelection = val;
        },
        // 选择模块后提交
        submit1(){
          if (this.a_formInline.moduleSelection.length === 0) {
            this.$message({
              type: 'info',
              message: '未选择模块'
            })
          } else {
            this.addFormVisible2 = true;
          }
        },
        submit2(a_formInline){
          this.$refs[a_formInline].validate(valid => {
            if (valid) {
              addApiTestTask(this.a_formInline)
                .then(res => {
                  this.addFormVisible1 = false;
                  this.addFormVisible2 = false;
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
                  this.addFormVisible1 = false;
                  this.addFormVisible2 = false;
                  this.loading = false;
                  this.$message.error('任务提交失败，请稍后再试！')
                });
              console.log(this.a_formInline);
            } else {
              return false
            }
          })
        },
        // 删除api测试任务
        apiTestTaskDelete(index, row) {
          this.$confirm('确定要删除吗?', '信息', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          })
            .then(() => {
              let parameter = {
                id: row.id
              };
              deleteApiTestTask(parameter)
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
                  this.$message.error('任务删除失败，请稍后再试！')
                })
            })
            .catch((err) => {
              console.log(err)
            })
        },
        // 跳转测试报告页面
        toTestReport(row){
          this.$router.push({
            path: '/apiTest/apiTestTask/apiTestReport',
            query: {
              task_id: row.id
            }
          })
        },
      }
    }
</script>

<style scoped>

</style>

<template>
  <div>
    <!-- 面包屑导航 -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: '/apiTest/apiManagement' }">接口管理</el-breadcrumb-item>
      <el-breadcrumb-item>测试用例</el-breadcrumb-item>
    </el-breadcrumb>
    <!-- 搜索筛选 -->
    <el-form :inline="true" :model="formInline" class="user-search">
      <el-form-item>
        <el-button size="small" type="primary" icon="el-icon-plus" @click="handleEdit()">添加</el-button>
      </el-form-item>
    </el-form>
    <!--列表-->
    <el-table size="small" :data="listData" highlight-current-row v-loading="loading" border element-loading-text="拼命加载中" style="width: 100%;">
      <el-table-column align="center" type="selection" width="60">
      </el-table-column>
      <el-table-column prop="id" label="id" v-if="false">
      </el-table-column>
      <el-table-column sortable prop="title" label="标题" width="300">
      </el-table-column>
      <el-table-column sortable prop="url" label="url" width="300">
      </el-table-column>
      <el-table-column align="center" label="操作" min-width="300">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button size="mini" @click="copy(scope.$index, scope.row)">复制</el-button>
          <el-button size="mini" type="danger" @click="apiTestcaseDelete(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页组件 -->
    <Pagination v-bind:child-msg="pageparm" @callFather="callFather"></Pagination>
  </div>
</template>

<script>
import { apiTestcaseList, deleteApiTestcase, copyTestcase } from '../../api/apiTestApi'
import Pagination from '../../components/Pagination'
export default {
  data() {
    return{
      nshow: true, //switch开启
      fshow: false, //switch关闭
      loading: false, //是显示加载
      api_id: '',
      formInline: {
        page: 1,
        limit: 10,
        token: localStorage.getItem('logintoken')
      },
      // 分页参数
      pageparm: {
        currentPage: 1,
        pageSize: 10,
        oldPageSize: 10,
        total: 10
      },
      listData: [], //测试用例数据
    }
  },
  // 注册组件
  components: {
    Pagination
  },
  created() {
    this.getParams();
    this.getdata(this.formInline);
  },
  methods: {
    getdata(parameter) {
      this.loading = true;
      this.pageparm.currentPage = this.formInline.page;
      this.pageparm.pageSize = this.formInline.limit;
      parameter = {
        currentPage: this.pageparm.currentPage,
        pageSize: this.pageparm.pageSize,
        api_id : this.api_id
      };
      apiTestcaseList(parameter)
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
    getParams(){
      // 取到路由带过来的参数
      this.api_id = this.$route.query.api_id;
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
    // 删除api模块
    apiTestcaseDelete(index, row) {
      this.$confirm('确定要删除吗?', '信息', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          let parameter = {
            id: row.id
          };
          deleteApiTestcase(parameter)
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
    //显示编辑界面
    handleEdit: function(index, row) {
      if (row != undefined && row != 'undefined') {
        this.$router.push({
          path: '/apiTest/apiManagement/apiTestCase/workbench',
          query: {
            id: row.id,
            api_id: this.api_id
          }
        })
      }else {
        this.$router.push({
          path: '/apiTest/apiManagement/apiTestCase/workbench',
          query: {
            id: '',
            api_id: this.api_id
          }
        })
      }
    },
    //复制测试用例
    copy(index, row){
      this.$confirm('确定要复制吗?', '信息', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          let parameter = {
            id: row.id
          };
          copyTestcase(parameter)
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
              this.$message.error('复制失败，请稍后再试！')
            })
        })
        .catch((err) => {
          console.log(err)
        })
    }
  }
}
</script>

<style scoped>

</style>

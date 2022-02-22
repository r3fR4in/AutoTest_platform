<template>
  <div>
    <!-- 面包屑导航 -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>提测申请管理</el-breadcrumb-item>
    </el-breadcrumb>
    <!-- 搜索筛选 -->
    <el-form :inline="true" :model="formInline" class="user-search">
      <el-form-item label="项目名称：">
        <el-autocomplete size="small" v-model="formInline.projectName" placeholder="输入项目名称" @select="handleSelect" :fetch-suggestions="querySearchAsync"></el-autocomplete>
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
      <el-table-column prop="id" label="提测id" v-if=false>
      </el-table-column>
      <el-table-column prop="project_id" label="项目id" v-if=false>
      </el-table-column>
      <el-table-column sortable prop="projectName" label="项目名称" min-width="150">
      </el-table-column>
      <el-table-column sortable prop="submitted_test_name" label="提测名称" min-width="150">
      </el-table-column>
      <el-table-column sortable prop="submitted_date" label="提测时间" min-width="150">
      </el-table-column>
      <el-table-column sortable prop="submitted_test_director" label="提测负责人" min-width="150">
      </el-table-column>
      <el-table-column sortable prop="test_director" label="测试负责人" min-width="150">
      </el-table-column>
      <el-table-column sortable prop="test_status" label="测试状态" min-width="150">
        <template scope="scope">
          <el-tag v-if="scope.row.test_status===1">已提测</el-tag>
          <el-tag type="success" v-if="scope.row.test_status===2">测试完成</el-tag>
          <el-tag type="danger" v-if="scope.row.test_status===3">退回</el-tag>
        </template>
      </el-table-column>
      <el-table-column sortable prop="smoke_testing_result" label="冒烟测试结果" min-width="150">
        <template scope="scope">
          <el-tag v-if="scope.row.smoke_testing_result===0">—</el-tag>
          <el-tag type="success" v-if="scope.row.smoke_testing_result===1">测试通过</el-tag>
          <el-tag type="danger" v-if="scope.row.smoke_testing_result===2">测试不通过</el-tag>
        </template>
      </el-table-column>
      <el-table-column sortable prop="test_result" label="最终测试结果" min-width="150">
        <template scope="scope">
          <el-tag v-if="scope.row.test_result===0">—</el-tag>
          <el-tag type="success" v-if="scope.row.test_result===1">测试通过</el-tag>
          <el-tag type="danger" v-if="scope.row.test_result===2">测试不通过</el-tag>
        </template>
      </el-table-column>
      <el-table-column sortable prop="complete_date" label="完成时间" min-width="150">
      </el-table-column>
      <el-table-column prop="submitted_test_detail" label="提测详情" v-if=false>
      </el-table-column>
      <el-table-column prop="smoke_testing_fail_reason_category" label="冒烟测试不通过原因分类" v-if=false>
      </el-table-column>
      <el-table-column prop="smoke_testing_fail_reason_detail" label="冒烟测试不通过原因分析" v-if=false>
      </el-table-column>
      <el-table-column align="center" label="操作" min-width="350">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.$index, scope.row, 'check')">查看</el-button>
          <el-button size="mini" @click="handleEdit(scope.$index, scope.row, 'edit')">编辑</el-button>
          <el-button size="mini" @click="smokeTesting(scope.$index, scope.row)" v-if="scope.row.smoke_testing_result===0">冒烟测试标记</el-button>
          <el-button size="mini" @click="completeTesting(scope.$index, scope.row)" v-if="scope.row.smoke_testing_result===1 && scope.row.test_result===0">完成标记</el-button>
          <el-button size="mini" type="danger" @click="submittedTestDelete(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页组件 -->
    <Pagination v-bind:child-msg="pageparm" @callFather="callFather"></Pagination>
    <!-- 编辑界面 -->
    <el-dialog :title="title" :visible.sync="editFormVisible" width="45%" @click="closeDialog">
      <el-form label-width="120px" :model="editForm" :rules="rules" ref="editForm">
        <el-form-item label="项目名称" prop="projectName">
          <el-autocomplete size="small" v-model="editForm.projectName" @select="handleSelect" :fetch-suggestions="querySearchAsync" placeholder="请输入项目名称" :disabled=editFormControl.projectName_disabled></el-autocomplete>
        </el-form-item>
        <el-form-item label="提测名称" prop="submitted_test_name">
          <el-input size="small" v-model="editForm.submitted_test_name" auto-complete="off" placeholder="请输入提测名称" :disabled=editFormControl.submitted_test_name_disabled></el-input>
        </el-form-item>
        <el-form-item label="提测时间" prop="submitted_date">
          <el-date-picker
            v-model="editForm.submitted_date"
            type="date"
            value-format="yyyy-MM-dd"
            :disabled=editFormControl.submitted_date_disabled
            placeholder="选择日期">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="提测负责人" prop="submitted_test_director">
          <el-input size="small" v-model="editForm.submitted_test_director" auto-complete="off" placeholder="请输入提测负责人" :disabled=editFormControl.submitted_test_director_disabled></el-input>
        </el-form-item>
        <el-form-item label="提测说明" prop="submitted_test_detail">
          <el-input type="textarea" size="medium" v-model="editForm.submitted_test_detail" auto-complete="off" placeholder="请输入提测详情" :disabled=editFormControl.submitted_test_detail_disabled></el-input>
        </el-form-item>
        <el-form-item label="测试负责人" prop="test_director">
          <el-input size="small" v-model="editForm.test_director" auto-complete="off" placeholder="请输入测试负责人" :disabled=editFormControl.test_director_disabled></el-input>
        </el-form-item>
        <el-form-item label="测试状态" prop="test_status" v-if=editFormControl.test_status_show>
          <el-tag v-if="editForm.test_status===1">测试中</el-tag>
          <el-tag v-if="editForm.test_status===2">测试完成</el-tag>
          <el-tag type="danger" v-if="editForm.test_status===3">退回</el-tag>
        </el-form-item>
        <el-form-item label="冒烟测试结果" prop="smoke_testing_result" v-if=editFormControl.smoke_testing_result_show>
          <el-tag v-if="editForm.smoke_testing_result===0">—</el-tag>
          <el-tag type="success" v-if="editForm.smoke_testing_result===1">测试通过</el-tag>
          <el-tag type="danger" v-if="editForm.smoke_testing_result===2">测试不通过</el-tag>
        </el-form-item>
        <el-form-item label="不通过原因" v-if="editForm.smoke_testing_result === 2 && editFormControl.smoke_testing_result_show === true"  disabled="true">
          <el-cascader v-model="editForm.smoke_testing_fail_reason" :options="reason_option" size="small" placeholder="请选择" disabled>
            </el-cascader>
        </el-form-item>
        <el-form-item label="最终测试结果" prop="test_result" v-if=editFormControl.test_result_show>
          <el-tag v-if="editForm.test_result===0">—</el-tag>
          <el-tag type="success" v-if="editForm.test_result===1">测试通过</el-tag>
          <el-tag type="danger" v-if="editForm.test_result===2">测试不通过</el-tag>
        </el-form-item>
        <el-form-item label="附件" prop="file_name">
          <el-upload
              class="upload-demo"
              action="/submittedTests/uploadFile"
              ref="upload"
              :disabled="editFormControl.upload_show"
              :headers="uploadToken"
              :data="{'id': editForm.id}"
              :with-credentials="true"
              :on-remove="removeFile"
              :on-preview="handlePreview"
              :on-success="uploadSuccess"
              :before-remove="beforeRemove"
              :file-list="editForm.file_name">
              <el-button size="small" type="primary" v-if="editFormControl.upload_button_show">点击上传</el-button>
            </el-upload>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button size="small" @click="closeDialog">取消</el-button>
        <el-button size="small" type="primary" :loading="loading" class="title" @click="submitForm('editForm')" v-if=editFormControl.submit_show>保存</el-button>
      </div>
    </el-dialog>
    <!-- 冒烟测试标记界面 -->
    <el-dialog title="冒烟测试标记" :visible.sync="smokeTestFormVisible" width="30%" @click="closeDialog">
      <el-form label-width="120px" :model="smokeTestForm" :rules="rules" ref="smokeTestForm">
        <el-form-item label="冒烟测试结果" prop="smoke_testing_result">
          <el-radio-group v-model="smokeTestForm.smoke_testing_result">
            <el-radio :label="1">测试通过</el-radio>
            <el-radio :label="2">测试不通过</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="不通过原因" prop="smoke_testing_fail_reason" v-if="smokeTestForm.smoke_testing_result === 2">
          <el-cascader v-model="smokeTestForm.smoke_testing_fail_reason" :options="reason_option" size="small" placeholder="请选择">
            </el-cascader>
        </el-form-item>
        <el-form-item label="完成时间" prop="complete_date" v-if="smokeTestForm.smoke_testing_result === 2">
          <el-date-picker
            v-model="smokeTestForm.complete_date"
            type="date"
            value-format="yyyy-MM-dd"
            placeholder="选择日期">
          </el-date-picker>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button size="small" @click="closeDialog">取消</el-button>
        <el-button size="small" type="primary" :loading="loading" class="title" @click="submitSmokeTest('smokeTestForm')">保存</el-button>
      </div>
    </el-dialog>
    <!-- 完成测试标记界面 -->
    <el-dialog title="冒烟测试标记" :visible.sync="completeTestFormVisible" width="30%" @click="closeDialog">
      <el-form label-width="120px" :model="editForm" :rules="rules" ref="editForm">
        <el-form-item label="最终测试结果" prop="test_result">
          <el-radio-group v-model="editForm.test_result">
            <el-radio :label="1">测试通过</el-radio>
            <el-radio :label="2">测试不通过</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="完成时间" prop="complete_date">
          <el-date-picker
            v-model="editForm.complete_date"
            type="date"
            value-format="yyyy-MM-dd"
            placeholder="选择日期">
          </el-date-picker>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button size="small" @click="closeDialog">取消</el-button>
        <el-button size="small" type="primary" :loading="loading" class="title" @click="submitTestResult('editForm')">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import Pagination from '../../components/Pagination'
import { getAllProject } from '../../api/projectApi'
import { submittedTestsList, getReasonOption, saveSubmittedTest, deleteSubmittedTest, saveSmokeTestingResult, saveTestResult, deleteUploadFile, downloadFile } from '../../api/submittedTestsApi'
export default {
  data() {
    return {
      nshow: true, //switch开启
      fshow: false, //switch关闭
      loading: false, //是显示加载
      editFormVisible: false, //控制编辑页面显示与隐藏
      title: '添加',
      disabled: false,
      reason_option: '',
      editFormControl: {
        projectName_disabled: false,
        submitted_test_name_disabled: false,
        submitted_date_disabled: false,
        submitted_test_director_disabled: false,
        submitted_test_detail_disabled: false,
        test_director_disabled: false,
        test_status_show: false,
        smoke_testing_result_show: false,
        test_result_show: false,
        submit_show: false,
        upload_show: false,
        upload_button_show: true
      },
      editForm: {
        id: '',
        projectName: '',
        submitted_test_name: '',
        submitted_date: '',
        submitted_test_director: '',
        submitted_test_detail: '',
        test_director: '',
        test_status: '',
        smoke_testing_result: '',
        smoke_testing_fail_reason: [],
        test_result: '',
        complete_date: '',
        file_name: ''
      },
      smokeTestFormVisible: false,
      smokeTestForm: {
        id: '',
        smoke_testing_result: '',
        smoke_testing_fail_reason: [],
        complete_date: ''
      },
      completeTestFormVisible: false,
      // rules表单验证
      rules: {
        projectName: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
        submitted_test_name: [{ required: true, message: '请输入提测名称', trigger: 'blur' }],
        submitted_date: [{ required: true, message: '请选择提测时间', trigger: 'change' }],
        submitted_test_director: [{ required: true, message: '请输入提测负责人', trigger: 'blur' }],
        submitted_test_detail: [{ required: true, message: '请输入提测详情', trigger: 'blur' }],
        test_director: [{ required: true, message: '请输入测试负责人', trigger: 'blur' }],
        smoke_testing_result: [{ required: true, message: '请选择冒烟测试结果', trigger: 'blur' }],
        smoke_testing_fail_reason: [{ required: true, message: '请选择不通过原因', trigger: 'blur' }],
        complete_date: [{ required: true, message: '请选择完成时间', trigger: 'blur' }]
      },
      projects: '',
      state: '',
      formInline: {
        page: 1,
        limit: 10,
        varLable: '',
        varName: '',
        projectName: '',
        token: localStorage.getItem('logintoken')
      },
      listData: [], //提测申请数据
      // 分页参数
      pageparm: {
        currentPage: 1,
        pageSize: 10,
        oldPageSize: 10,
        total: 10
      },
      // 獲取緩存中的token
      uploadToken:{'Authorization': localStorage.getItem('logintoken')}
    }
  },
  // 注册组件
  components: {
    Pagination
  },
  created() {
    this.getdata(this.formInline);
    this.loadAllProject();
    this.getReasonOption();
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
      submittedTestsList(parameter)
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
    // 获取冒烟测试不通过原因
    getReasonOption(){
      getReasonOption().then(res => {
        this.reason_option = res.data;
      })
    },
    // 搜索事件
    search() {
      this.formInline.page = 1;
      this.getdata(this.formInline)
    },
    // 关闭编辑、增加弹出框
    closeDialog() {
      this.editFormVisible = false;
      this.smokeTestFormVisible = false;
      this.completeTestFormVisible = false;
      this.clearEditForm();
    },
    // 清除editform
    clearEditForm() {
      this.editForm.id = '';
      this.editForm.projectName = '';
      this.editForm.submitted_test_name = '';
      this.editForm.submitted_date = '';
      this.editForm.submitted_test_director = '';
      this.editForm.submitted_test_detail = '';
      this.editForm.test_director = '';
      this.editForm.test_status = '';
      this.editForm.smoke_testing_result = '';
      this.editForm.smoke_testing_fail_reason = [];
      this.editForm.test_result = '';
      this.editForm.file_name = '';
    },
    // 获取所有项目信息
    loadAllProject(){
      getAllProject().then(
        res => {
          this.projects = res;
        }
      )
    },
    //显示编辑界面
    handleEdit: function(index, row, option) {
      this.editFormVisible = true;
      // this.$refs["editForm"].clearValidate();
      if (row === undefined || row === 'undefined') {
        this.title = '添加';
        // 控制组件显示和是否禁用
        this.editFormControl.projectName_disabled = false;
        this.editFormControl.submitted_test_name_disabled = false;
        this.editFormControl.submitted_date_disabled = false;
        this.editFormControl.submitted_test_director_disabled = false;
        this.editFormControl.submitted_test_detail_disabled = false;
        this.editFormControl.test_director_disabled = false;
        this.editFormControl.test_status_show = false;
        this.editFormControl.smoke_testing_result_show = false;
        this.editFormControl.test_result_show = false;
        this.editFormControl.submit_show = true;
        this.editFormControl.upload_show = false;
        this.editFormControl.upload_button_show = true;
        // 清除editform
        this.clearEditForm();
        console.log(this.$refs);
        this.$refs.upload.clearFiles();
      } else {
        if (option === 'check'){
          this.title = '查看';
          // 控制组件显示和是否禁用
          this.editFormControl.projectName_disabled = true;
          this.editFormControl.submitted_test_name_disabled = true;
          this.editFormControl.submitted_date_disabled = true;
          this.editFormControl.submitted_test_director_disabled = true;
          this.editFormControl.submitted_test_detail_disabled = true;
          this.editFormControl.test_director_disabled = true;
          this.editFormControl.test_status_show = true;
          this.editFormControl.smoke_testing_result_show = true;
          this.editFormControl.test_result_show = true;
          this.editFormControl.submit_show = false;
          this.editFormControl.upload_show = true;
          this.editFormControl.upload_button_show = false;
          // 赋值
          this.editForm.id = row.id;
          this.editForm.projectName = row.projectName;
          this.editForm.submitted_test_name = row.submitted_test_name;
          this.editForm.submitted_date = row.submitted_date;
          this.editForm.submitted_test_director = row.submitted_test_director;
          this.editForm.submitted_test_detail = row.submitted_test_detail;
          this.editForm.test_director = row.test_director;
          this.editForm.test_status = row.test_status;
          this.editForm.smoke_testing_result = row.smoke_testing_result;
          this.editForm.smoke_testing_fail_reason = [row.smoke_testing_fail_reason_category, row.smoke_testing_fail_reason_detail];
          this.editForm.test_result = row.test_result;
          this.editForm.file_name = row.file_name;
        }else {
          this.title = '编辑';
          // 控制组件显示和是否禁用
          this.editFormControl.projectName_disabled = true;
          this.editFormControl.submitted_test_name_disabled = false;
          this.editFormControl.submitted_date_disabled = false;
          this.editFormControl.submitted_test_director_disabled = false;
          this.editFormControl.submitted_test_detail_disabled = false;
          this.editFormControl.test_director_disabled = false;
          this.editFormControl.test_status_show = false;
          this.editFormControl.smoke_testing_result_show = false;
          this.editFormControl.test_result_show = false;
          this.editFormControl.submit_show = true;
          this.editFormControl.upload_show = false;
          this.editFormControl.upload_button_show = true;
          // 赋值
          this.editForm.id = row.id;
          this.editForm.projectName = row.projectName;
          this.editForm.submitted_test_name = row.submitted_test_name;
          this.editForm.submitted_date = row.submitted_date;
          this.editForm.submitted_test_director = row.submitted_test_director;
          this.editForm.submitted_test_detail = row.submitted_test_detail;
          this.editForm.test_director = row.test_director;
          this.editForm.test_status = row.test_status;
          this.editForm.smoke_testing_result = row.smoke_testing_result;
          this.editForm.smoke_testing_fail_reason = [row.smoke_testing_fail_reason_category, row.smoke_testing_fail_reason_detail];
          this.editForm.test_result = row.test_result;
          this.editForm.file_name = row.file_name;
        }
      }
    },
    // 编辑、增加页面保存方法
    submitForm(editData) {
      this.$refs[editData].validate(valid => {
        if (valid) {
          saveSubmittedTest(this.editForm)
            .then(res => {
              this.editFormVisible = false;
              this.loading = false;
              if (res.success) {
                this.getdata(this.formInline);
                this.clearEditForm();
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
              this.$message.error('提测申请保存失败，请稍后再试！')
            })
        } else {
          return false
        }
      })
    },
    //上传成功的钩子
    uploadSuccess(res, file, fileList, row){
      if (this.editForm.file_name === ''){
          this.editForm.file_name = [];
      }
      if (this.editForm.id === ''){
        // 新增
        this.editForm.file_name.push({name: res.file_name, realname: res.real_file_name});
      } else {
        // 编辑
        this.editForm.file_name.push({name: res.file_name, realname: res.real_file_name});
        this.getdata(this.formInline);
      }
    },
    beforeRemove(file, fileList) {
        return this.$confirm(`确定移除 ${ file.name }？`)
    },
    removeFile(file, fileList){
      let parameter = {
        id: this.editForm.id,
        file: file.realname
      };
      deleteUploadFile(parameter)
        .then(res => {
          if (res.success) {
            this.$message({
              type: 'success',
              message: res.msg
            });
            this.editForm.file_name.some((item, i) => {
              if (item.name === file.name) {
                this.editForm.file_name.splice(this.editForm.file_name.indexOf(i), 1);
                return true;
              }
            });
            this.getdata(this.formInline);
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
          this.$message.error('移除文件失败，请稍后再试！')
        })
    },
    // 实现点击下载文件
    handlePreview(file, fileList){
      let parameter = {
        file: file.realname
      };
      downloadFile(parameter)
        .then(res => {
          const content = res.data;
          const blob = new Blob([content]);
          // console.log(blob);
          // let fileName = res.headers["content-disposition"].split("=")[1];
          if (window.navigator.msSaveOrOpenBlob) {
            window.navigator.msSaveOrOpenBlob(blob, file.name);
          }
          // console.log(file.name);
          // console.log(response.data);
          let url = window.URL.createObjectURL(blob);
          // console.log(url)
          let a = document.createElement("a");
          document.body.appendChild(a);
          a.href = url;
          a.download = decodeURI(file.name); //命名下载名称
          a.click(); //点击触发下载
          window.URL.revokeObjectURL(url);  //下载完成进行释放
        })
    },
    // 显示冒烟测试标记页面
    smokeTesting: function(index, row) {
      this.smokeTestFormVisible = true;
      this.smokeTestForm.id = row.id;
    },
    // 保存冒烟测试结果
    submitSmokeTest(editData) {
      this.$refs[editData].validate(valid => {
        if (valid) {
          saveSmokeTestingResult(this.smokeTestForm)
            .then(res => {
              this.smokeTestFormVisible = false;
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
              this.smokeTestFormVisible = false;
              this.loading = false;
              this.$message.error('冒烟测试结果保存失败，请稍后再试！')
            })
        } else {
          return false
        }
      });
    },
    //保存最终测试结果
    submitTestResult(editData) {
      this.$refs[editData].validate(valid => {
        if (valid) {
          let param = {
            id: this.editForm.id,
            test_result: this.editForm.test_result,
            complete_date: this.editForm.complete_date
          };
          saveTestResult(param)
            .then(res => {
              this.completeTestFormVisible = false;
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
              this.completeTestFormVisible = false;
              this.loading = false;
              this.$message.error('最终测试结果保存失败，请稍后再试！')
            })
        } else {
          return false
        }
      });
    },
    // 显示完成标记页面
    completeTesting: function(index, row) {
      this.completeTestFormVisible = true;
      this.editForm.id = row.id;
    },
    // 删除提测申请
    submittedTestDelete(index, row) {
      this.$confirm('确定要删除吗?', '信息', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          let parameter = {
            id: row.id
          };
          deleteSubmittedTest(parameter)
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
              this.$message.error('提测申请失败，请稍后再试！')
            })
        })
        .catch((err) => {
          console.log(err)
        })
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
      console.log(item);
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

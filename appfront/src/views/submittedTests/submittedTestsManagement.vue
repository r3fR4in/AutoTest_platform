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
        <el-autocomplete size="small" v-model="formInline.projectName" placeholder="输入项目名称" @select="handleSelect" :fetch-suggestions="querySearchAsync" style="width: 150px"></el-autocomplete>
      </el-form-item>
      <el-form-item label="测试状态：">
        <el-select size="small" v-model="test_status_value" clearable placeholder="请选择" style="width: 100px">
          <el-option
            v-for="item in test_status_option"
            :key="item.value"
            :label="item.label"
            :value="item.value">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="冒烟测试结果：">
        <el-select size="small" v-model="smoke_testing_result_value" clearable placeholder="请选择" style="width: 120px">
          <el-option
            v-for="item in smoke_testing_result_option"
            :key="item.value"
            :label="item.label"
            :value="item.value">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="最终测试结果：">
        <el-select size="small" v-model="test_result_value" clearable placeholder="请选择" style="width: 120px">
          <el-option
            v-for="item in test_result_option"
            :key="item.value"
            :label="item.label"
            :value="item.value">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="申请日期：">
        <el-date-picker
          v-model="formInline.date"
          size="small"
          type="daterange"
          value-format="yyyy-MM-dd"
          unlink-panels
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期">
        </el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button size="small" type="primary" icon="el-icon-search" @click="search">搜索</el-button>
        <el-button size="small" type="primary" icon="el-icon-plus" @click="handleEdit()">添加</el-button>
      </el-form-item>
    </el-form>
    <!--列表-->
    <el-table size="small" :data="listData" highlight-current-row v-loading="loading" border element-loading-text="拼命加载中" style="width: 100%;">
      <!--<el-table-column align="center" type="selection" width="60">-->
      <!--</el-table-column>-->
      <el-table-column prop="id" label="提测id" v-if=false>
      </el-table-column>
      <el-table-column prop="project_id" label="项目id" v-if=false>
      </el-table-column>
      <el-table-column sortable prop="projectName" label="项目名称" min-width="150">
      </el-table-column>
      <el-table-column sortable prop="submitted_test_name" label="提测名称" min-width="150">
      </el-table-column>
      <el-table-column sortable prop="submitted_date" label="申请日期" min-width="120">
      </el-table-column>
      <el-table-column sortable prop="test_date" label="提交测试日期" min-width="120">
      </el-table-column>
      <el-table-column sortable prop="online_date" label="项目上线日期" min-width="120">
      </el-table-column>
      <el-table-column sortable prop="submitted_test_director" label="提测负责人" min-width="120">
      </el-table-column>
      <el-table-column sortable prop="fix_bug_director" label="缺陷修复处理人员" min-width="150">
      </el-table-column>
      <el-table-column sortable prop="test_director" label="测试负责人" min-width="120">
      </el-table-column>
      <el-table-column sortable prop="test_status" label="测试状态" min-width="120">
        <template scope="scope">
          <el-tag v-if="scope.row.test_status===1">已提测</el-tag>
          <el-tag type="success" v-if="scope.row.test_status===2">测试完成</el-tag>
          <el-tag type="danger" v-if="scope.row.test_status===3">退回</el-tag>
        </template>
      </el-table-column>
      <el-table-column sortable prop="smoke_testing_result" label="冒烟测试结果" min-width="120">
        <template scope="scope">
          <el-tag v-if="scope.row.smoke_testing_result===0">—</el-tag>
          <el-tag type="success" v-if="scope.row.smoke_testing_result===1">测试通过</el-tag>
          <el-tag type="danger" v-if="scope.row.smoke_testing_result===2">测试不通过</el-tag>
        </template>
      </el-table-column>
      <el-table-column sortable prop="test_result" label="最终测试结果" min-width="120">
        <template scope="scope">
          <el-tag v-if="scope.row.test_result===0">—</el-tag>
          <el-tag type="success" v-if="scope.row.test_result===1">测试通过</el-tag>
          <el-tag type="danger" v-if="scope.row.test_result===2">测试不通过</el-tag>
        </template>
      </el-table-column>
      <el-table-column sortable prop="complete_date" label="完成时间" min-width="120">
      </el-table-column>
      <el-table-column prop="submitted_test_detail" label="提测详情" v-if=false>
      </el-table-column>
      <el-table-column prop="smoke_testing_fail_reason_category" label="冒烟测试不通过原因分类" v-if=false>
      </el-table-column>
      <el-table-column prop="smoke_testing_fail_reason_detail" label="冒烟测试不通过原因分析" v-if=false>
      </el-table-column>
      <el-table-column align="center" label="操作" min-width="350" fixed="right">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.$index, scope.row, 'check')">查看</el-button>
          <el-button size="mini" @click="handleEdit(scope.$index, scope.row, 'edit')">编辑</el-button>
          <el-button size="mini" @click="smokeTesting(scope.$index, scope.row)" v-if="scope.row.smoke_testing_result===0 && user_role !== 'dev_role'">冒烟测试标记</el-button>
          <el-button size="mini" @click="completeTesting(scope.$index, scope.row)" v-if="scope.row.smoke_testing_result===1 && scope.row.test_result===0 && user_role !== 'dev_role'">完成标记</el-button>
          <el-button size="mini" type="danger" @click="submittedTestDelete(scope.$index, scope.row)" v-if="user_role !== 'dev_role'">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页组件 -->
    <Pagination v-bind:child-msg="pageparm" @callFather="callFather"></Pagination>
    <!-- 编辑界面 -->
    <el-dialog :title="title" :visible.sync="editFormVisible" width="45%" @click="closeDialog">
      <el-form label-width="140px" :model="editForm" :rules="rules" ref="editForm">
        <el-form-item label="测试系统" prop="projectName">
          <el-autocomplete size="small" v-model="editForm.projectName" @select="handleSelect" :fetch-suggestions="querySearchAsync" placeholder="请输入项目名称" :disabled=editFormControl.projectName_disabled></el-autocomplete>
        </el-form-item>
        <el-form-item label="提测名称" prop="submitted_test_name">
          <el-input size="small" v-model="editForm.submitted_test_name" auto-complete="off" placeholder="请输入提测名称" :readonly=editFormControl.submitted_test_name_disabled></el-input>
        </el-form-item>
        <el-form-item label="申请日期" prop="submitted_date">
          <el-date-picker
            v-model="editForm.submitted_date"
            type="date"
            value-format="yyyy-MM-dd"
            :readonly=editFormControl.submitted_date_disabled
            placeholder="选择日期">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="提交测试日期" prop="test_date">
          <el-date-picker
            v-model="editForm.test_date"
            type="date"
            value-format="yyyy-MM-dd"
            :readonly=editFormControl.test_date_disabled
            placeholder="选择日期">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="项目上线日期" prop="online_date">
          <el-date-picker
            v-model="editForm.online_date"
            type="date"
            value-format="yyyy-MM-dd"
            :readonly=editFormControl.online_date_disabled
            placeholder="选择日期">
          </el-date-picker>
        </el-form-item>
        <!--<el-form-item label="提测负责人" prop="submitted_test_director">-->
          <!--<el-input size="small" v-model="editForm.submitted_test_director" auto-complete="off" placeholder="请输入提测负责人" :readonly=editFormControl.submitted_test_director_disabled></el-input>-->
        <!--</el-form-item>-->
        <el-form-item label="提测负责人" prop="submitted_test_director">
          <el-select size="small" v-model="editForm.submitted_test_director_id" filterable placeholder="请选择提测负责人" @change ="selectChange1"
                     :disabled=editFormControl.submitted_test_director_disabled :filter-method="pinyinMatch" @focus="resetOptions">
            <el-option
              v-for="item in user_options"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <!--<el-form-item label="缺陷修复处理人员" prop="fix_bug_director">-->
          <!--<el-input size="small" v-model="editForm.fix_bug_director" auto-complete="off" placeholder="请输入缺陷修复处理人员" :readonly=editFormControl.fix_bug_director_disabled></el-input>-->
        <!--</el-form-item>-->
        <el-form-item label="缺陷修复处理人员" prop="fix_bug_director">
          <el-select size="small" v-model="editForm.fix_bug_director_id" filterable multiple placeholder="请选择缺陷修复处理人员" @change ="selectChange2"
                     :disabled=editFormControl.fix_bug_director_disabled :filter-method="pinyinMatch" @focus="resetOptions">
            <el-option
              v-for="item in user_options"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="自测报告地址" prop="self_test_report_url">
          <el-input size="small" v-model="editForm.self_test_report_url" auto-complete="off" placeholder="请输入自测报告地址" :readonly=editFormControl.self_test_report_url_disabled></el-input>
        </el-form-item>
        <el-form-item label="测试地址" prop="test_url">
          <el-input size="small" v-model="editForm.test_url" auto-complete="off" placeholder="请输入测试地址" :readonly=editFormControl.test_url_disabled></el-input>
        </el-form-item>
        <el-form-item label="测试范围" prop="test_scope">
          <el-input type="textarea"
                    size="medium"
                    v-model="editForm.test_scope"
                    auto-complete="off"
                    placeholder="请输入测试范围"
                    :rows="5"
                    :readonly=editFormControl.test_scope_disabled></el-input>
        </el-form-item>
        <el-form-item label="影响范围" prop="influence_scope">
          <el-input type="textarea"
                    size="medium"
                    v-model="editForm.influence_scope"
                    auto-complete="off"
                    placeholder="请输入影响范围"
                    :rows="5"
                    :readonly=editFormControl.influence_scope_disabled></el-input>
        </el-form-item>
        <el-form-item label="注意事项" prop="points_for_attention">
          <el-input type="textarea"
                    size="medium"
                    v-model="editForm.points_for_attention"
                    auto-complete="off"
                    placeholder="请输入注意事项"
                    :rows="5"
                    :readonly=editFormControl.points_for_attention_disabled></el-input>
        </el-form-item>
        <el-form-item label="配置路径" prop="config_url">
          <el-input type="textarea"
                    size="medium"
                    v-model="editForm.config_url"
                    auto-complete="off"
                    placeholder="请输入配置路径"
                    :rows="5"
                    :readonly=editFormControl.config_url_disabled></el-input>
        </el-form-item>
        <el-form-item label="脚本路径" prop="script_url">
          <el-input type="textarea"
                    size="medium"
                    v-model="editForm.script_url"
                    auto-complete="off"
                    placeholder="请输入脚本路径"
                    :rows="5"
                    :readonly=editFormControl.script_url_disabled></el-input>
        </el-form-item>
        <el-form-item label="兼容说明" prop="compatibility_desc">
          <el-input type="textarea"
                    size="medium"
                    v-model="editForm.compatibility_desc"
                    auto-complete="off"
                    placeholder="请输入兼容说明"
                    :rows="5"
                    :readonly=editFormControl.compatibility_desc_disabled></el-input>
        </el-form-item>
        <!--<el-form-item label="测试负责人" prop="test_director">-->
          <!--<el-input size="small" v-model="editForm.test_director" auto-complete="off" placeholder="请输入测试负责人" :readonly=editFormControl.test_director_disabled></el-input>-->
        <!--</el-form-item>-->
        <el-form-item label="测试负责人" prop="test_director">
          <el-select size="small" v-model="editForm.test_director_id" filterable placeholder="请选择测试负责人" @change="selectChange3"
                     :disabled=editFormControl.test_director_disabled :filter-method="pinyinMatch" @focus="resetOptions">
            <el-option
              v-for="item in user_options"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
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
  import {getAllProject} from '../../api/projectApi'
  import {getUserOptions} from '../../api/userMG'
  import {addSubmittedTest, deleteSubmittedTest, deleteUploadFile, downloadFile, editSubmittedTest, getReasonOption, getSubmittedTestOptions, saveSmokeTestingResult, saveTestResult, submittedTestsList} from '../../api/submittedTestsApi'
  import pinyin from 'pinyin-match'

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
      user_role: '',
      editFormControl: {
        projectName_disabled: false,
        submitted_test_name_disabled: false,
        submitted_date_disabled: false,
        test_date_disabled: false,
        online_date_disabled: false,
        submitted_test_director_disabled: false,
        fix_bug_director_disabled: false,
        test_director_disabled: false,
        self_test_report_url_disabled: false,
        test_url_disabled: false,
        test_scope_disabled: false,
        influence_scope_disabled: false,
        points_for_attention_disabled: false,
        config_url_disabled: false,
        script_url_disabled: false,
        compatibility_desc_disabled: false,
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
        test_date: '',
        online_date: '',
        submitted_test_director_id: '',
        submitted_test_director: '',
        fix_bug_director_id: [],
        fix_bug_director: '',
        test_director_id: '',
        test_director: '',
        self_test_report_url: '',
        test_url: '',
        test_scope: '',
        influence_scope: '',
        points_for_attention: '',
        config_url: '',
        script_url: '',
        compatibility_desc: '',
        test_status: '',
        smoke_testing_result: '',
        smoke_testing_fail_reason: [],
        test_result: '',
        complete_date: '',
        file_name: ''
      },
      user_options: '',
      fix_bug_director_label: [],
      copy_user_options: '',
      smokeTestFormVisible: false,
      smokeTestForm: {
        id: '',
        smoke_testing_result: 1,
        smoke_testing_fail_reason: [],
        complete_date: ''
      },
      completeTestFormVisible: false,
      // rules表单验证
      rules: {
        projectName: [{ required: true, message: '请输入测试系统', trigger: 'blur' }],
        submitted_test_name: [{ required: true, message: '请输入提测名称', trigger: 'blur' }],
        submitted_date: [{ required: true, message: '请选择申请日期', trigger: 'change' }],
        test_date: [{ required: true, message: '请选择提交测试日期', trigger: 'change' }],
        submitted_test_director: [{ required: true, message: '请选择提测负责人', trigger: 'blur' }],
        fix_bug_director: [{ required: true, message: '请选择缺陷修复处理人员', trigger: 'blur' }],
        // test_director: [{ required: true, message: '请输入测试负责人', trigger: 'blur' }],
        smoke_testing_result: [{ required: true, message: '请选择冒烟测试结果', trigger: 'blur' }],
        smoke_testing_fail_reason: [{ required: true, message: '请选择不通过原因', trigger: 'blur' }],
        complete_date: [{ required: true, message: '请选择完成时间', trigger: 'blur' }]
      },
      projects: '',
      state: '',
      formInline: {
        page: 1,
        limit: 10,
        projectName: '',
        date: ''
      },
      smoke_testing_result_option: '',
      smoke_testing_result_value: '',
      test_result_option: '',
      test_result_value: '',
      test_status_option: '',
      test_status_value: '',
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
    this.user_role = JSON.parse(localStorage.getItem('userdata')).role;
    this.getdata(this.formInline);
    this.loadAllProject();
    this.getReasonOption();
    this.getSubmittedTestOptions();
    this.getUserOptions();
  },
  /**
   * 里面的方法只有被调用才会执行
   */
  methods: {
    // 获取用户下拉选项
    getUserOptions(){
      getUserOptions().then(res => {
        this.user_options = res.data;
        this.copy_user_options = res.data;
      })
    },
    // 获取项目列表
    getdata(parameter) {
      this.loading = true;
      this.pageparm.currentPage = this.formInline.page;
      this.pageparm.pageSize = this.formInline.limit;
      if (this.formInline.date === undefined || this.formInline.date === null){
        parameter = {
          currentPage: this.pageparm.currentPage,
          pageSize: this.pageparm.pageSize,
          projectName : this.formInline.projectName,
          test_status: this.test_status_value,
          smoke_testing_result: this.smoke_testing_result_value,
          test_result: this.test_result_value,
          start_date: '',
          end_date: ''
        };
      } else {
        parameter = {
          currentPage: this.pageparm.currentPage,
          pageSize: this.pageparm.pageSize,
          projectName : this.formInline.projectName,
          test_status: this.test_status_value,
          smoke_testing_result: this.smoke_testing_result_value,
          test_result: this.test_result_value,
          start_date: this.formInline.date[0],
          end_date: this.formInline.date[1]
        };
      }
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
    // 获取查询条件下拉框选项
    getSubmittedTestOptions(){
      getSubmittedTestOptions().then(res => {
        this.smoke_testing_result_option = res.data.smoke_testing_result_option;
        this.test_result_option = res.data.test_result_option;
        this.test_status_option = res.data.test_status_option;
      })
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
      this.editForm.test_date = '';
      this.editForm.online_date = '';
      this.editForm.submitted_test_director_id = '';
      this.editForm.submitted_test_director = '';
      this.editForm.fix_bug_director_id = '';
      this.editForm.fix_bug_director = '';
      this.editForm.self_test_report_url = '';
      this.editForm.test_url = '';
      this.editForm.test_scope = '';
      this.editForm.influence_scope = '';
      this.editForm.points_for_attention = '';
      this.editForm.config_url = '';
      this.editForm.script_url = '';
      this.editForm.compatibility_desc = '';
      this.editForm.test_director_id = '';
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
        this.editFormControl.test_date_disabled = false;
        this.editFormControl.online_date_disabled = false;
        this.editFormControl.submitted_test_director_disabled = false;
        this.editFormControl.fix_bug_director_disabled = false;
        this.editFormControl.self_test_report_url_disabled = false;
        this.editFormControl.test_url_disabled = false;
        this.editFormControl.test_scope_disabled = false;
        this.editFormControl.influence_scope_disabled = false;
        this.editFormControl.points_for_attention_disabled = false;
        this.editFormControl.config_url_disabled = false;
        this.editFormControl.script_url_disabled = false;
        this.editFormControl.compatibility_desc_disabled = false;
        this.editFormControl.test_director_disabled = false;
        this.editFormControl.test_status_show = false;
        this.editFormControl.smoke_testing_result_show = false;
        this.editFormControl.test_result_show = false;
        this.editFormControl.submit_show = true;
        this.editFormControl.upload_show = false;
        this.editFormControl.upload_button_show = true;
        // 清除editform
        this.clearEditForm();
        this.editForm.submitted_test_director = JSON.parse(localStorage.getItem('userdata')).nickname;
        this.$refs.upload.clearFiles();
      } else {
        if (option === 'check'){
          this.title = '查看';
          // 控制组件显示和是否禁用
          this.editFormControl.projectName_disabled = true;
          this.editFormControl.submitted_test_name_disabled = true;
          this.editFormControl.submitted_date_disabled = true;
          this.editFormControl.test_date_disabled = true;
          this.editFormControl.online_date_disabled = true;
          this.editFormControl.submitted_test_director_disabled = true;
          this.editFormControl.fix_bug_director_disabled = true;
          this.editFormControl.self_test_report_url_disabled = true;
          this.editFormControl.test_url_disabled = true;
          this.editFormControl.test_scope_disabled = true;
          this.editFormControl.influence_scope_disabled = true;
          this.editFormControl.points_for_attention_disabled = true;
          this.editFormControl.config_url_disabled = true;
          this.editFormControl.script_url_disabled = true;
          this.editFormControl.compatibility_desc_disabled = true;
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
          this.editForm.test_date = row.test_date;
          this.editForm.online_date = row.online_date;
          this.editForm.submitted_test_director_id = row.submitted_test_director_id;
          this.editForm.submitted_test_director = row.submitted_test_director;
          this.editForm.fix_bug_director_id = row.fix_bug_director_id;
          this.editForm.fix_bug_director = row.fix_bug_director;
          this.editForm.self_test_report_url = row.self_test_report_url;
          this.editForm.test_url = row.test_url;
          this.editForm.test_scope = row.test_scope;
          this.editForm.influence_scope = row.influence_scope;
          this.editForm.points_for_attention = row.points_for_attention;
          this.editForm.config_url = row.config_url;
          this.editForm.script_url = row.script_url;
          this.editForm.compatibility_desc = row.compatibility_desc;
          this.editForm.test_director_id = row.test_director_id;
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
          this.editFormControl.test_date_disabled = false;
          this.editFormControl.online_date_disabled = false;
          this.editFormControl.submitted_test_director_disabled = false;
          this.editFormControl.fix_bug_director_disabled = false;
          this.editFormControl.self_test_report_url_disabled = false;
          this.editFormControl.test_url_disabled = false;
          this.editFormControl.test_scope_disabled = false;
          this.editFormControl.influence_scope_disabled = false;
          this.editFormControl.points_for_attention_disabled = false;
          this.editFormControl.config_url_disabled = false;
          this.editFormControl.script_url_disabled = false;
          this.editFormControl.compatibility_desc_disabled = false;
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
          this.editForm.test_date = row.test_date;
          this.editForm.online_date = row.online_date;
          this.editForm.submitted_test_director_id = row.submitted_test_director_id;
          this.editForm.submitted_test_director = row.submitted_test_director;
          this.editForm.fix_bug_director_id = row.fix_bug_director_id;
          this.editForm.fix_bug_director = row.fix_bug_director;
          this.fix_bug_director_label = row.fix_bug_director.split(',');
          this.editForm.self_test_report_url = row.self_test_report_url;
          this.editForm.test_url = row.test_url;
          this.editForm.test_scope = row.test_scope;
          this.editForm.influence_scope = row.influence_scope;
          this.editForm.points_for_attention = row.points_for_attention;
          this.editForm.config_url = row.config_url;
          this.editForm.script_url = row.script_url;
          this.editForm.compatibility_desc = row.compatibility_desc;
          this.editForm.test_director_id = row.test_director_id;
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
          if (this.editForm.id === ''){
            let param = this.editForm;
            delete param['id'];
            addSubmittedTest(param)
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
            let param = this.editForm;
            editSubmittedTest(param)
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
          }
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
      this.editForm.test_result = 1;
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
    },
    selectChange1(val) {
      this.editForm.submitted_test_director = this.user_options.find(item => item.value === val).label;
    },
    selectChange2(val) {
      this.fix_bug_director_label = [];
      for (let i=0;i<=val.length-1;i++) {
        this.user_options.find((item) => {
          if (item.value === val[i]){
            this.fix_bug_director_label.push(item.label)
          }
        })
      }
      this.editForm.fix_bug_director = this.fix_bug_director_label.join(",");
    },
    selectChange3(val) {
      this.editForm.test_director = this.user_options.find(item => item.value === val).label;
    },
    pinyinMatch(val) {
      if (val) {
        let result = [];//声明一个空数组保存搜索内容
        this.copy_user_options.forEach(e => {//循环判断内容和拼音首字母是否匹配
          let m = pinyin.match(e.label, val);
          if (m) {
            result.push(e)
          }
        });
        this.user_options = result; //返回匹配的数组
      } else {
        this.user_options = this.copy_user_options //未输入返回开始copy的原数组
      }
    },
    resetOptions(){
      this.user_options = this.copy_user_options;
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
